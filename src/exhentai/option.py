import os.path

from common import Postmans, PackerUtil, AdvancedEasyAccessDict

from .client import *


class ExhentaiOption:
    constructor_fields = [
        'client',
        'cookies',
        'download',
    ]

    def __init__(self,
                 client: dict,
                 cookies: dict[str, dict],
                 download: dict,
                 ):
        self.client: dict = client
        self.cookies: dict[str, dict] = self.fix_cookies_value_type(cookies)
        self.download = AdvancedEasyAccessDict(download)  # read only
        self.dir_rule = DirRule(rule=self.download.rule, base_dir=self.download.base_dir)

    def new_client(self, group=None):
        postman = Postmans.create(data=self.client['postman'])

        if group is None:
            return ExhentaiClient(postman, list(self.cookies.values()))
        else:
            return ExhentaiClient(postman, [self.cookies[group]])

    def copy_cookies(self, group):
        cookies: dict = self.cookies[group]
        import_cookies = []
        for k, v in cookies.items():
            import_cookies.append({
                "name": k,
                "value": v,
            })
        from common import json_dumps, copy_to_clip

        imports = json_dumps(import_cookies, indent=2)
        copy_to_clip(imports)

    @classmethod
    def from_dir(cls,
                 dirpath: str,
                 suffix='.yml',
                 ) -> 'ExhentaiOption':
        dirpath = os.path.abspath(dirpath)

        data = {}
        for filename in cls.constructor_fields:
            part = PackerUtil.unpack(dirpath + f'/{filename}{suffix}')[0]
            data[filename] = part

        return cls(**data)

    @classmethod
    def from_file(cls, filepath: str) -> 'ExhentaiOption':
        option: dict = PackerUtil.unpack(filepath)[0]
        return cls(**option)

    def download_gallery(self, gid: str, token: str, group=None):
        """
        download gallery by gid and token using specific group cookies

        :param group: cookies group
        :param token: gallery token
        :param gid: gallery id
        """

        client = self.new_client(group=group)
        from .downloader import ExhantaiDownloader
        downloader: ExhantaiDownloader = ExHentaiModule.downloader()(self, client)
        downloader.download_gallery(gid, token)

    def download_gallery_by_url(self, url, group=None):
        match = re.compile(r'/g/(\d+)/(\w+)/').search(url)
        if not match:
            raise AssertionError(url)

        gid, token = match[1], match[2]
        return self.download_gallery(gid, token, group)

    @classmethod
    def fix_cookies_value_type(cls, cookies_groups: dict[str, dict]):
        """
        ensure cookies (key-value-pair) all values are string
        """
        for group, cookies in cookies_groups.items():
            for k, v in cookies.items():
                if not isinstance(v, str):
                    cookies[k] = str(v)

        return cookies_groups

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def decide_img_download_plan(self,
                                 book: BookInfo,
                                 index: int,
                                 hurl: str,
                                 furl: str,
                                 client: ExhentaiClient,
                                 ) -> tuple[str | None, str | None]:
        save_dir = self.dir_rule.decide_image_save_dir(book.baseInfo, book.pageInfo)
        url = furl
        save_path = os.path.join(save_dir,
                                 str(index) +
                                 (self.download.image.suffix or common.of_file_suffix(url)),
                                 )
        if self.download.image.check_exist and common.file_exists(save_path):
            return None, None

        return hurl, os.path.abspath(save_path)

    def decide_download_image_workers(self) -> int:
        return self.download.threading.workers
