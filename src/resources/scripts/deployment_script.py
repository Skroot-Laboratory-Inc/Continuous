import os
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


version = Version()
major_version = version.getMajorVersion()
minor_version = version.getMinorVersion()
release_bucket = version.getReleaseBucket()
zip_name = f'DesktopApp_v{major_version}.{minor_version}.zip'
zip_file_path = f'../temp/{zip_name}'
release_notes_name = f'v{major_version}.{minor_version}.json'
release_notes_fp = '../version/release-notes.json'

software_releases_bucket = f'software-releases/{release_bucket}'
# Eventually we want this to be release specific, but will require some timing and app updates.
release_notes_bucket = f'release-notes/{version.getUseCase()}'

try:
    # zip up the whole package
    print(f" > Zipping Files")
    if not check_before_overwrite(software_releases_bucket, zip_name):
        raise Exception("Did not perform update to avoid overwriting the current release files.")
    zip_files('../../..', zip_file_path)
    # Upload the zip file to AWS in the skroot-data/software-releases bucket
    print(f" > Uploading Zip as '{zip_name}' from '{zip_file_path}'")
    s3_upload_file(
        zip_file_path, 
        zip_name, 
        software_releases_bucket, 
        tag_str=f'major_version={major_version}&minor_version={minor_version}'
    )
    print(f" > Uploading Release Notes as '{release_notes_name}' from '{release_notes_fp}'")
    s3_upload_file(
        release_notes_fp, 
        release_notes_name, 
        release_notes_bucket
    )
except:
    traceback.print_exc()
finally:
    # look for the zip file and delete it if it exists
    if os.path.exists(os.path.dirname(zip_file_path)):
        print(" > Deleting Zip")
        shutil.rmtree(os.path.dirname(zip_file_path))


