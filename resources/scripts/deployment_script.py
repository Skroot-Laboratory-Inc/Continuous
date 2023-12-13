import os
import json
import shutil
import zipfile
import traceback

import boto3
from botocore.config import Config


def zip_files(folder_path, zip_name):
    if not os.path.exists(os.path.dirname(zip_name)):
        os.mkdir(os.path.dirname(zip_name))
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders_, filenames in os.walk(f"../../{folder_path}"):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                if "/.idea/" in file_path or "./__pycache__/" in file_path or "/.git/" in file_path or  "/unit_tests/" in file_path or "/temp/" in file_path:
                    continue
                print(file_path)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def s3_upload_file(file_path, file_name, aws_folder_name, tag_str=''):
    s3 = boto3.resource('s3')
    b = s3.Bucket('skroot-data')
    b.upload_file(
        file_path, f'{aws_folder_name}/{file_name}',
        ExtraArgs={'Tagging': tag_str}
    )

def check_before_overwrite(bucket, zip_name):
    config = Config(connect_timeout=5, read_timeout=5)
    s3 = boto3.client('s3', config=config)
    allReleases = s3.list_objects_v2(Bucket='skroot-data', Prefix=bucket)
    for item in allReleases['Contents']:
        print(item)
        filename = item['Key']
        if zip_name in filename:
            should_continue = input(f'This will overwrite the current release for {zip_name}\nAre you sure you wish to continue? (y)es or (n)o\n')
            if should_continue == 'y' or should_continue == 'Y' or should_continue == 'yes' or should_continue == 'Yes':
                return True
    return False

with open('../version.json') as j_file:
    version = json.load(j_file)

major_version = version['major_version']
minor_version = version['minor_version']
zip_name = f'DesktopApp_v{major_version}.{minor_version}.zip'
zip_file_path = f'../temp/{zip_name}'
release_notes_name = f'v{major_version}.{minor_version}.json'
release_notes_fp = '../release-notes.json'

software_releases_bucket = 'software-releases'
release_notes_bucket = 'release-notes'

try:
    # zip up the whole package
    print(f" > Zipping Files")
    if not check_before_overwrite(software_releases_bucket, zip_name):
        raise Exception("Did not perform update to avoid overwriting the current release files.")
    zip_files('.', zip_file_path)
    # Upload the zip file to AWS in the skroot-data/software-releases bucket
    print(f" > Uploading Zip as '{zip_name}' from '{zip_file_path}'")
    s3_upload_file(
        zip_file_path, 
        zip_name, 
        software_releases_bucket, 
        tag_str=f'major_version={major_version}&minor_version={minor_version}'
    )
    # Upload the resources/release-notes.json file to the bucket skroot-data/release-notes
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


