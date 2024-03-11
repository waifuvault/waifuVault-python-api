# Models for waifuVault

class FileUpload:
    def __init__(self, target: str, expires: str = None, password: str = None, hidefilename: bool = False):
        self.target = target
        self.hidefilename = hidefilename
        self.expires = expires
        self.password = password

    def is_url(self):
        return self.target.lower().startswith("http://") or self.target.lower().startswith("https://")


class FileResponse:
    def __init__(self, token: str, url: str, protected: bool, retention_period: any):
        self.token = token
        self.url = url
        self.protected = protected
        self.retentionPeriod = retention_period
