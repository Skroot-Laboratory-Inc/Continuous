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
from botocore.exceptions import ClientError


def zip_files(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders_, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

with open('./resources/version.json') as j_file:
    version = json.load(j_file)

major_version = version['major_version']
minor_version = version['minor_version']
name = f"DesktopApp_v{major_version}.{minor_version}.zip"
zip_file_path = f"../__TEST__/{name}"
try:
    # zip up the whole package
    zip_files('.', zip_file_path)
    # Upload the zip file to AWS in the skroot-data/software-releases bucket
    s3 = boto3.resource('s3')
    bucket = 'skroot-data'
    s3.Bucket(bucket).upload_file(zip_file_path, f"software-releases/{name}")
    # upload_file(zip_file_path, 'skroot-data/software-releases')
except:
    traceback.print_exc()
finally:
    # look for the zip file and delete it if it exists
    if os.path.exists(zip_file_path):
        print("Deleting zip file...")
        os.remove(zip_file_path)
