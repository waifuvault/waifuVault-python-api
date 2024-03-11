import json
import os
from io import BytesIO

import requests
from requests_toolbelt import MultipartEncoder

import waifumodels


# Upload File
def upload_file(file_obj: waifumodels.FileUpload):
    parameters = {}
    if file_obj.password:
        parameters['password'] = file_obj.password
    if file_obj.expires:
        parameters['expires'] = file_obj.expires
    if file_obj.hidefilename:
        parameters['hide_filename'] = file_obj.hidefilename

    if file_obj.is_url():
        response = requests.put(
            "https://waifuvault.moe/rest",
            params=parameters,
            data={'url': file_obj.target}
        )
    else:
        multipart_data = MultipartEncoder(
            fields={
                'file': (os.path.basename(file_obj.target), open(file_obj.target, 'rb'))
            }
        )
        response = requests.put(
            "https://waifuvault.moe/rest",
            params=parameters,
            data=multipart_data,
            headers={'Content-Type': multipart_data.content_type})
    return json.loads(response.text)


# Get File Info
def file_info(token: str, formatted: bool):
    response = requests.get(
        "https://waifuvault.moe/rest",
        params={'token': token, 'formatted': 'true' if formatted else 'false'}
    )
    check_error(response)
    return json.loads(response.text)


# Delete File
def delete_file(token: str):
    response = requests.delete(
        "https://waifuvault.moe/rest",
        params={'token': token}
    )
    check_error(response)
    return json.loads(response.text)


# Get File
def get_file(file_obj: waifumodels.FileResponse, password: str = None):
    headers = {}
    if password:
        headers["x-password"] = password
    if not file_obj.url and file_obj.token:
        url = file_info(file_obj.token, False).url
    else:
        url = file_obj.url
    response = requests.get(url, headers=headers)
    check_error(response)
    return BytesIO(response.content)


# Check Error
def check_error(response: requests.models.Response):
    if not response.ok:
        err = json.loads(response.text)
        raise Exception(f"Error {err.status} ({err.name}): {err.message}")
    return
