"""

- Zip all of the files into a DesktopApp_v{major_version}.{minor_version}.zip file
- All of the files should be directly inside (don't zip the folder, zip the files)
- Upload the zip file to AWS in the skroot-data/software-releases bucket
    - Tag the file with major_version = major_version and minor_version = minor_version
- Upload the resources/release-notes.json file to the bucket skroot-data/release-notes
    - Filename should be v{major_version}.{minor_version}.json
- major_version and minor_version are variables currently passed into the mainShared via the main_cell.py file
- Don't worry about permissions, just assume the computer being used has permission to do this

"""

import os
import json
import zipfile
import traceback

import boto3

def zip_files(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders_, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def s3_upload_file(file_path, file_name, aws_folder_name):
    s3 = boto3.resource('s3')
    b = s3.Bucket('skroot-data')
    res = b.upload_file(file_path, f'{aws_folder_name}/{file_name}')

with open('./resources/version.json') as j_file:
    version = json.load(j_file)

major_version = version['major_version']
minor_version = version['minor_version']
zip_name = f"DesktopApp_v{major_version}.{minor_version}_TEST.zip"
zip_file_path = f"../__TEST__/{zip_name}"
release_notes_name = f'v{major_version}.{minor_version}_TEST.json'
release_notes_fp = './resources/release-notes.json'
try:
    # zip up the whole package
    print(f"===> Zipping Files")
    zip_files('.', zip_file_path)
    # Upload the zip file to AWS in the skroot-data/software-releases bucket
    print(f"===> Uploading Zip as '{zip_name}' from '{zip_file_path}'")
    s3_upload_file(zip_file_path, zip_name, 'software-releases')
    # Upload the resources/release-notes.json file to the bucket skroot-data/release-notes
    print(f"===> Uploading Release Notes as '{release_notes_name}' from '{release_notes_fp}'")
    s3_upload_file(release_notes_fp, release_notes_name, 'release-notes')
except:
    traceback.print_exc()
finally:
    # look for the zip file and delete it if it exists
    if os.path.exists(zip_file_path):
        print("===> Deleting Zip")
        os.remove(zip_file_path)