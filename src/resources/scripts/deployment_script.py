import json
import os
import re
import shutil
import traceback
import zipfile

import boto3
from botocore.config import Config

from src.resources.version.version import Version


def zip_files(folder_path, zip_name):
    if not os.path.exists(os.path.dirname(zip_name)):
        os.mkdir(os.path.dirname(zip_name))
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders_, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                if "\\.idea\\" in file_path or "\\__pycache__\\" in file_path or "temp\\" in file_path or "\\.git\\" in file_path or "\\unit_tests\\" in file_path or "\\venv\\" in file_path or "\\build\\" in file_path or ".egg-info\\" in file_path:
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


def update_version_theme(version_file_path, theme):
    """Rewrite version.py to set self.theme to the given Theme."""
    with open(version_file_path, 'r') as f:
        content = f.read()
    content = re.sub(
        r'self\.theme = Theme\.\w+',
        f'self.theme = Theme.{theme.name}',
        content
    )
    with open(version_file_path, 'w') as f:
        f.write(content)


version = Version()
use_case = version.getUseCase()
major_version = version.getMajorVersion()
minor_version = version.getMinorVersion()
zip_name = f'DesktopApp_v{major_version}.{minor_version}.zip'
zip_file_path = f'../temp/{zip_name}'
release_notes_name = f'v{major_version}.{minor_version}.json'
release_notes_source_fp = f"../{version.getReleaseNotesFilePath()}"
release_notes_temp_fp = f'../temp/{release_notes_name}'
release_notes_bucket = f'release-notes/{use_case}'

version_file_path = os.path.join(os.path.dirname(__file__), '../version/version.py')

# Read original version.py so we can restore it after deployment
with open(version_file_path, 'r') as f:
    original_version_content = f.read()

try:
    # Load use-case-specific release notes file
    print(f" > Loading release notes for {use_case} from {release_notes_source_fp}")
    with open(release_notes_source_fp, 'r') as f:
        use_case_notes = json.load(f)

    # Create temporary release notes file for deployment
    if not os.path.exists(os.path.dirname(release_notes_temp_fp)):
        os.mkdir(os.path.dirname(release_notes_temp_fp))
    with open(release_notes_temp_fp, 'w') as f:
        json.dump(use_case_notes, f, indent=2)

    # Deploy to each theme folder
    deployment_themes = Version.getDeploymentThemes()
    for theme in deployment_themes:
        version.theme = theme
        release_bucket = version.getReleaseBucket()
        software_releases_bucket = f'software-releases/{release_bucket}'

        print(f"\n{'='*60}")
        print(f" > Deploying {theme.value}/{use_case} v{major_version}.{minor_version}")
        print(f" > Target: {software_releases_bucket}")
        print(f"{'='*60}")

        if not check_before_overwrite(software_releases_bucket, zip_name):
            print(f" > Skipping {theme.value} to avoid overwriting the current release files.")
            continue

        # Update version.py with this theme before zipping
        update_version_theme(version_file_path, theme)

        # Zip up the whole package (includes the updated version.py)
        print(f" > Zipping Files for {theme.value}/{use_case} v{major_version}.{minor_version}")
        zip_files('../../..', zip_file_path)

        # Upload the zip file to AWS in the skroot-data/software-releases bucket
        print(f" > Uploading Zip as '{zip_name}' to '{software_releases_bucket}'")
        s3_upload_file(
            zip_file_path,
            zip_name,
            software_releases_bucket,
            tag_str=f'major_version={major_version}&minor_version={minor_version}'
        )

        # Clean up zip before next iteration
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

        print(f" > Deployment complete for {theme.value}/{use_case} v{major_version}.{minor_version}")

    # Upload release notes once (shared across themes)
    print(f"\n > Uploading Release Notes as '{release_notes_name}' to '{release_notes_bucket}'")
    s3_upload_file(
        release_notes_temp_fp,
        release_notes_name,
        release_notes_bucket
    )
    print(f"\n > All deployments complete for {use_case} v{major_version}.{minor_version}")
except:
    traceback.print_exc()
finally:
    # Restore original version.py
    with open(version_file_path, 'w') as f:
        f.write(original_version_content)

    # Look for the temp folder and delete it if it exists
    if os.path.exists(os.path.dirname(zip_file_path)):
        print(" > Deleting Temp Files")
        shutil.rmtree(os.path.dirname(zip_file_path))


