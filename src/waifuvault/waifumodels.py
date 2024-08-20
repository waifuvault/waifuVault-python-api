# Models for waifuVault
import io


class FileUpload:
    def __init__(self, target: any, target_name: str = "unknown", bucket_token: str = None,  expires: str = None, password: str = None, hidefilename: bool = False, oneTimeDownload: bool = False):
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


class FileOptions:
    def __init__(self, hide_filename: bool = False, one_time_download: bool = False, protected: bool = False):
        self.hideFilename = hide_filename
        self.oneTimeDownload = one_time_download
        self.protected = protected


class FileResponse:
    def __init__(self, token: str = None, url: str = None, retention_period: any = None, bucket: str = None, options: FileOptions = None):
        self.token = token
        self.url = url
        self.retentionPeriod = retention_period
        self.bucket = bucket
        self.options = options


class BucketResponse:
    def __init__(self, token: str = None, files: list[FileResponse] = None):
        self.token = token
        self.files = files
