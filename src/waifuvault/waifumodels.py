# Models for waifuVault
import io

class FileUpload:
    def __init__(self, target: any, target_name: str = "unknown", expires: str = None, password: str = None, hidefilename: bool = False):
        self.target = target
        self.target_name = target_name
        self.hidefilename = hidefilename
        self.expires = expires
        self.password = password

    def is_url(self):
        if isinstance(self.target, io.BytesIO):
            return False
        return self.target.lower().startswith("http://") or self.target.lower().startswith("https://")

    def is_buffer(self):
        return isinstance(self.target, io.BytesIO)


class FileResponse:
    def __init__(self, token: str = None, url: str = None, protected: bool = False, retention_period: any = None):
        self.token = token
        self.url = url
        self.protected = protected
        self.retentionPeriod = retention_period
