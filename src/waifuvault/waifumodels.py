# Models for waifuVault
import io
import mimetypes
import os
from datetime import datetime, timedelta


class FileUpload:
    def __init__(self, target: str | io.BytesIO, target_name: str = "unknown", bucket_token: str = None,  expires: str = None, password: str = None, hidefilename: bool = False, oneTimeDownload: bool = False):
        self.target = target
        self.target_name = target_name
        self.bucket_token = bucket_token
        self.hidefilename = hidefilename
        self.one_time_download = oneTimeDownload
        self.expires = expires
        self.password = password

    def is_url(self):
        if isinstance(self.target, io.BytesIO):
            return False
        return self.target.lower().startswith("http://") or self.target.lower().startswith("https://")

    def is_buffer(self):
        return isinstance(self.target, io.BytesIO)

    def build_parameters(self):
        parameters = {}
        if self.expires:
            parameters['expires'] = self.expires
        if self.hidefilename:
            parameters['hide_filename'] = str(self.hidefilename).lower()
        if self.one_time_download:
            parameters['one_time_download'] = str(self.one_time_download).lower()
        return parameters


class FilesInfo:
    def __init__(self, record_count: int = None, record_size: int = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.record_count = dict_obj.get("recordCount")
            self.record_size = dict_obj.get("recordSize")
        else:
            self.record_count = record_count
            self.record_size = record_size


class FileOptions:
    def __init__(self, hide_filename: bool = False, one_time_download: bool = False, protected: bool = False, dict_obj: {} = None):
        if dict_obj is not None:
            self.hideFilename = dict_obj.get("hideFilename")
            self.oneTimeDownload = dict_obj.get("oneTimeDownload")
            self.protected = dict_obj.get("protected")
        else:
            self.hideFilename = hide_filename
            self.oneTimeDownload = one_time_download
            self.protected = protected


class FileResponse:
    def __init__(self, token: str = None, url: str = None, retention_period: str | int = None, bucket: str = None, views: int = None, album: str = None,  options: FileOptions = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.token = dict_obj.get("token")
            self.url = dict_obj.get("url")
            self.retentionPeriod = dict_obj.get("retentionPeriod")
            self.bucket = dict_obj.get("bucket")
            self.views = dict_obj.get("views")
            self.album = AlbumInfo(dict_obj=dict_obj.get("album"))
            self.options = FileOptions(dict_obj=dict_obj["options"])
        else:
            self.token = token
            self.url = url
            self.retentionPeriod = retention_period
            self.bucket = bucket
            self.views = views
            self.album = album
            self.options = options


class AlbumInfo:
    def __init__(self, token: str = None, public_token: str = None, name: str = None, bucket: str = None, date_created: int = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.token = dict_obj.get("token")
            self.public_token = dict_obj.get("publicToken")
            self.name = dict_obj.get("name")
            self.bucket = dict_obj.get("bucket")
            self.date_created = dict_obj.get("dateCreated")
        else:
            self.token = token
            self.public_token = public_token
            self.name = name
            self.bucket = bucket
            self.date_created =date_created


class AlbumResponse:
    def __init__(self, token: str = None, bucket_token: str = None, public_token: str = None, name: str = None, files: list[FileResponse] = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.files = []
            self.token = dict_obj.get("token")
            self.bucket_token = dict_obj.get("bucketToken")
            self.public_token = dict_obj.get("publicToken")
            self.name = dict_obj.get("name")
            files = dict_obj.get("files")
            if files is not None:
                for file in files:
                    self.files.append(FileResponse(dict_obj=file))
        else:
            self.token = token
            self.bucket_token = bucket_token
            self.public_token = public_token
            self.name = name
            self.files = files


class BucketResponse:
    def __init__(self, token: str = None, files: list[FileResponse] = None, albums: list[AlbumResponse] = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.files = []
            self.albums = []
            self.token = dict_obj.get("token")
            for file in dict_obj.get("files"):
                self.files.append(FileResponse(dict_obj=file))
            for album in dict_obj.get("albums"):
                self.albums.append(AlbumResponse(dict_obj=album))
        else:
            self.token = token
            self.files = files
            self.albums = albums


class Restriction:
    def __init__(self, type: str = None, value: str | int | list[str] = None, dict_obj: {} = None):
        if dict_obj is not None:
            self.type = dict_obj.get("type")
            self.value = dict_obj.get("value")
        else:
            self.type = type
            self.value = value

    def passes(self, file: FileUpload):
        if file.is_url():
            return
        match self.type:
            case "MAX_FILE_SIZE":
                if file.is_buffer():
                    if file.target.getbuffer().nbytes > self.value:
                        raise ValueError(f'File size {file.target.getbuffer().nbytes} is larger than max allowed {self.value}')
                elif os.path.getsize(file.target) > self.value:
                    raise ValueError(f'File size {os.path.getsize(file.target)} is larger than max allowed {self.value}')
                return
            case "BANNED_MIME_TYPE":
                if file.is_buffer():
                    mime_type, encoding = mimetypes.guess_type(file.target_name)
                else:
                    mime_type, encoding = mimetypes.guess_type(file.target)
                if mime_type in self.value.split(','):
                    raise ValueError(f'File MIME type {mime_type} is not allowed for upload')
                return
            case _:
                raise NotImplementedError(f'Restriction type {self.type} is not implemented')


class RestrictionResponse:
    def __init__(self, restrictions: list[Restriction] = None, rest_obj: [] = None):
        if rest_obj is not None:
            self.Restrictions = []
            for rest in rest_obj:
                self.Restrictions.append(Restriction(dict_obj=rest))
            self.Expires = datetime.now() + timedelta(minutes=10)
        else:
            self.Restrictions = restrictions
            self.Expires = datetime.now() + timedelta(minutes=10)
