import argparse
import json
import os
import shutil
import traceback
import zipfile

import boto3
from botocore.config import Config

from src.resources.version.version import Version, UseCase


def zip_files(folder_path, zip_name):
    if not os.path.exists(os.path.dirname(zip_name)):
        os.mkdir(os.path.dirname(zip_name))
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders_, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                excluded = ['.idea', '__pycache__', 'temp', '.git', 'unit_tests', 'venv', 'build']
                if any(f'{os.sep}{exc}{os.sep}' in file_path or file_path.endswith(f'{os.sep}{exc}') for exc in excluded):
                    continue
                if '.egg-info' + os.sep in file_path:
                    continue
                arcname = os.path.relpath(file_path, folder_path)
                print(file_path, arcname)
                zipf.write(file_path, arcname)


def s3_upload_file(file_path, file_name, aws_folder_name, tag_str=''):
    s3 = boto3.resource('s3')
    b = s3.Bucket('skroot-data')
    b.upload_file(
        file_path, f'{aws_folder_name}/{file_name}',
        ExtraArgs={'Tagging': tag_str}
    )


def check_before_overwrite(bucket, zip_name):
    try:
        config = Config(connect_timeout=5, read_timeout=5)
        s3 = boto3.client('s3', config=config)
        allReleases = s3.list_objects_v2(Bucket='skroot-data', Prefix=bucket)
        for item in allReleases['Contents']:
            print(item)
            filename = item['Key']
            if zip_name in filename:
                should_continue = input(f'This will overwrite the current release for {zip_name}\nAre you sure you wish to continue? (y)es or (n)o\n')
                if should_continue == 'n' or should_continue == 'N' or should_continue == 'no' or should_continue == 'No':
                    return False
        return True
    except:
        raise


def deploy_use_case(use_case: UseCase, skip_overwrite_check=False):
    """Deploy a single use case to S3."""
    version = Version()
    # Override the active use case for this deployment
    version.useCase = use_case
    version.theme = version.use_case_themes[use_case]

    use_case_name = version.getUseCase()
    major_version = version.getMajorVersion()
    minor_version = version.getMinorVersion()
    release_bucket = version.getReleaseBucket()
    zip_name = f'DesktopApp_v{major_version}.{minor_version}.zip'
    zip_file_path = f'../temp/{zip_name}'
    release_notes_name = f'v{major_version}.{minor_version}.json'
    release_notes_source_fp = f"../{version.getReleaseNotesFilePath()}"
    release_notes_temp_fp = f'../temp/{release_notes_name}'

    software_releases_bucket = f'software-releases/{release_bucket}'
    release_notes_bucket = f'release-notes/{use_case_name}'

    try:
        print(f" > Zipping Files for {use_case_name} v{major_version}.{minor_version}")
        if not skip_overwrite_check:
            if not check_before_overwrite(software_releases_bucket, zip_name):
                raise Exception("Did not perform update to avoid overwriting the current release files.")
        zip_files('../../..', zip_file_path)

        print(f" > Loading release notes for {use_case_name} from {release_notes_source_fp}")
        with open(release_notes_source_fp, 'r') as f:
            use_case_notes = json.load(f)

        if not os.path.exists(os.path.dirname(release_notes_temp_fp)):
            os.mkdir(os.path.dirname(release_notes_temp_fp))
        with open(release_notes_temp_fp, 'w') as f:
            json.dump(use_case_notes, f, indent=2)

        print(f" > Uploading Zip as '{zip_name}' from '{zip_file_path}'")
        s3_upload_file(
            zip_file_path,
            zip_name,
            software_releases_bucket,
            tag_str=f'major_version={major_version}&minor_version={minor_version}'
        )
        print(f" > Uploading Release Notes as '{release_notes_name}' from '{release_notes_temp_fp}'")
        s3_upload_file(
            release_notes_temp_fp,
            release_notes_name,
            release_notes_bucket
        )
        print(f" > Deployment complete for {use_case_name} v{major_version}.{minor_version}")
    except:
        traceback.print_exc()
    finally:
        if os.path.exists(os.path.dirname(zip_file_path)):
            print(" > Deleting Temp Files")
            shutil.rmtree(os.path.dirname(zip_file_path))


def main():
    parser = argparse.ArgumentParser(description="Deploy use cases to S3")
    parser.add_argument(
        '--use-case', type=str, default=None,
        help='Deploy a specific use case by name (e.g., Continuous, FlowCell). Omit to deploy all.'
    )
    parser.add_argument(
        '--skip-overwrite-check', action='store_true',
        help='Skip the interactive overwrite confirmation (for CI).'
    )
    args = parser.parse_args()

    if args.use_case:
        try:
            uc = UseCase[args.use_case]
        except KeyError:
            try:
                uc = UseCase(args.use_case)
            except ValueError:
                valid = ', '.join([uc.name for uc in UseCase])
                print(f"Unknown use case '{args.use_case}'. Valid options: {valid}")
                return
        deploy_use_case(uc, args.skip_overwrite_check)
    else:
        for uc in UseCase:
            print(f"\n{'=' * 60}")
            print(f"Deploying {uc.value}...")
            print(f"{'=' * 60}")
            deploy_use_case(uc, args.skip_overwrite_check)


if __name__ == '__main__':
    main()
