__base_url__ = "https://waifuvault.moe/rest"

import json
import os
from io import BytesIO

import requests
from requests_toolbelt import MultipartEncoder

from .waifumodels import FileResponse, FileUpload


# Upload File
def upload_file(file_obj: FileUpload):
    parameters = __build_parameters(file_obj)

    if file_obj.is_buffer():
        multipart_data = MultipartEncoder(
            fields={'file': (file_obj.target_name, file_obj.target)}
        )
        header_data = {'Content-Type': multipart_data.content_type}
    elif file_obj.is_url():
        multipart_data = {'url': file_obj.target}
        header_data = None
    else:
        multipart_data = MultipartEncoder(
            fields={
                'file': (os.path.basename(file_obj.target), open(file_obj.target, 'rb'))
            }
        )
        header_data = {'Content-Type': multipart_data.content_type}

    response = requests.put(
        __base_url__,
        params=parameters,
        data=multipart_data,
        headers=header_data)
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
            message = response.text
        raise Exception(f"Error {status} ({name}): {message}")
    return


def __build_parameters(file_obj: FileUpload):
    parameters = {}
    if file_obj.password:
        parameters['password'] = file_obj.password
    if file_obj.expires:
        parameters['expires'] = file_obj.expires
    if file_obj.hidefilename:
        parameters['hide_filename'] = file_obj.hidefilename
    return parameters


def __dict_to_obj(dict_obj: any):
    return FileResponse(
        dict_obj["token"],
        dict_obj["url"],
        dict_obj["protected"] == "true",
        dict_obj["retentionPeriod"])
