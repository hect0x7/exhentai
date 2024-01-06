import math

# noinspection PyUnresolvedReferences
from .module import *


class Entity:
    @classmethod
    def get_dirname(cls, obj, ref: str):
        return getattr(obj, ref)


# code is copied from https://github.com/tonquer/ehentai-qt
class BookBaseInfo(Entity):
    def __init__(self):
        self.id = 0
        self.title = ""
        self.bookUrl = ""
        self.token = ""
        self.apiUid = ""
        self.apiKey = ""
        self.category = ""
        self.timeStr = ""
        self.imgData = None
        self.imgUrl = ""
        self.tags = []


# code is copied from https://github.com/tonquer/ehentai-qt
class BookPageInfo(Entity):
    def __init__(self):
        self.kv = {}
        self.posted = ""
        self.language = ""
        self.fileSize = ""
        self.pages = 0
        self.favorites = 0
        self.picUrl = {}  # index: url
        self.preUrl = {}  # index: url
        self.picRealUrl = {}
        self.showKey = ""
        self.comment = []

    def GetImgKey(self, index):
        if index not in self.picUrl:
            return None

        import re
        mo = re.search(r"(?<=/s/)\w+", self.picUrl.get(index))
        return mo.group()


# code is base on https://github.com/tonquer/ehentai-qt
class BookInfo(Entity):
    def __init__(self):
        self.baseInfo = BookBaseInfo()
        self.pageInfo = BookPageInfo()

    @property
    def pic_url_list(self) -> list[str]:
        return list(self.pageInfo.picUrl.values())

    @property
    def pic_url_set(self) -> set[str]:
        return set(self.pic_url_list)

    @property
    def total(self):
        return self.pageInfo.pages

    @property
    def page_count(self):
        return math.ceil(self.total / len(self.pageInfo.picUrl))
