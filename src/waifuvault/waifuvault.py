__base_url__ = "https://waifuvault.moe/rest"

import json
import os
from io import BytesIO

import requests
from requests_toolbelt import MultipartEncoder

from .waifumodels import FileResponse, FileUpload, FileOptions, BucketResponse


# Create Bucket
def create_bucket():
    url = f"{__base_url__}/bucket/create"
    response = requests.get(url)
    __check_error(response, False)
    return __bucket_to_obj(json.loads(response.text))


# Delete Bucket
def delete_bucket(token: str):
    url = f"{__base_url__}/bucket/{token}"
    response = requests.delete(url)
    __check_error(response, False)
    return True if response.text == "true" else False


# Get Bucket
def get_bucket(token: str):
    url = f"{__base_url__}/bucket/get"
    data = {"bucket_token": token}
    response = requests.post(url, json=data)
    __check_error(response, False)
    return __bucket_to_obj(json.loads(response.text))


# Upload File
def upload_file(file_obj: FileUpload):
    url = __base_url__
    if file_obj.bucket_token:
        url += f"/{file_obj.bucket_token}"
    fields = {}
    if file_obj.password:
        fields['password'] = file_obj.password
    if file_obj.is_buffer():
        fields['file'] = (file_obj.target_name, file_obj.target)
        multipart_data = MultipartEncoder(
            fields=fields
        )
        header_data = {'Content-Type': multipart_data.content_type}
    elif file_obj.is_url():
        fields['url'] = file_obj.target
        multipart_data = fields
        header_data = None
    else:
        fields['file'] = (os.path.basename(file_obj.target), open(file_obj.target, 'rb'))
        multipart_data = MultipartEncoder(
            fields=fields
        )
        header_data = {'Content-Type': multipart_data.content_type}

    response = requests.put(
        url,
        params=file_obj.build_parameters(),
        data=multipart_data,
        headers=header_data)
    __check_error(response, False)
    return __dict_to_obj(json.loads(response.text))


# Update File
def file_update(token: str, password: str = None, previous_password: str = None, custom_expiry: str = None, hide_filename:bool = False):
    url = f"{__base_url__}/{token}"
    fields = {'hideFilename': "true" if hide_filename else "false"}
    if password is not None:
        fields['password'] = password
    if previous_password is not None:
        fields['previousPassword'] = previous_password
    if custom_expiry is not None:
        fields['customExpiry'] = custom_expiry

    response = requests.patch(
        url,
        data=fields
    )
    __check_error(response, False)
    return __dict_to_obj(json.loads(response.text))


# Get File Info
def file_info(token: str, formatted: bool):
    url = f"{__base_url__}/{token}"
    response = requests.get(
        url,
        params={'formatted': 'true' if formatted else 'false'}
    )
    __check_error(response, False)
    return __dict_to_obj(json.loads(response.text))


# Delete File
def delete_file(token: str):
    url = f"{__base_url__}/{token}"
    response = requests.delete(url)
    __check_error(response, False)
    return True if response.text == "true" else False


# Get File
def get_file(file_obj: FileResponse, password: str = None):
    headers = {}
    if password:
        headers["x-password"] = password
    if not file_obj.url and file_obj.token:
        url = file_info(file_obj.token, False).url
    else:
        url = file_obj.url
    response = requests.get(url, headers=headers)
    __check_error(response, True)
    return BytesIO(response.content)


# Check Error
def __check_error(response: requests.models.Response, is_download: bool):
    if not response.ok:
        try:
            err = json.loads(response.text)
            status = err["status"]
            name = err["name"]
            message = err['message']
        except:
            status = response.status_code
            name = "Password is Incorrect" if response.status_code == 403 and is_download else response.status_code
            message = "Password is Incorrect" if response.status_code == 403 and is_download else response.text
        raise Exception(f"Error {status} ({name}): {message}")
    return


def __dict_to_obj(dict_obj: any):
    return FileResponse(
        dict_obj.get("token"),
        dict_obj.get("url"),
        dict_obj.get("retentionPeriod"),
        dict_obj.get("bucket"),
        FileOptions(
            dict_obj["options"]["hideFilename"],
            dict_obj["options"]["oneTimeDownload"],
            dict_obj["options"]["protected"]
        ))


def __bucket_to_obj(bucket_obj: any):
    actual_files = []
    for file in bucket_obj.get("files"):
        actual_files.append(__dict_to_obj(file))
    return BucketResponse(
        bucket_obj.get("token"),
        actual_files
    )
