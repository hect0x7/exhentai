from concurrent.futures import ThreadPoolExecutor

from .option import *


class ExhantaiDownloader:
    def __init__(self,
                 option: ExhentaiOption,
                 client: ExhentaiClient,
                 ):
        self.option = option
        self.client = client
        self.workers = ThreadPoolExecutor(max_workers=self.option.decide_download_image_workers())

    def download_gallery(self, gid: str, token: str, ):
        pic_url_set: set[str] = set()
        # fetch all pic_url (https://exhentai.org/s/xx/xx) of gallery

        # first page
        book = self.client.fetch_gallery_page(gid, token, p=0)
        pic_url_set.update(book.pic_url_list)

        # the rest page
        # for p in range(1, book.page_count):
        #     book = self.client.fetch_gallery_page(gid, token, p)
        #     pic_url_set.update(book.pic_url_set)

        self.run_all(
            iterables=range(1, book.page_count),
            apply=lambda p: pic_url_set.update(self.client.fetch_gallery_page(gid, token, p).pic_url_list),
        )

        # to sorted list
        # sorted(list(pic_url_set), key=lambda url: int(url[url.index('-'):]), reverse=True)

        # for pic_url in pic_url_set:
        #     self.download_pic(pic_url, book)

        self.run_all(
            iterables=pic_url_set,
            apply=lambda pic_url: self.download_pic(pic_url, book),
        )

    def download_pic(self, pic_url: str, book: BookInfo):
        resp = self.client.fetch_pic_page(pic_url)
        hurl, furl = ExhentaiHtmlParser.parse_hash_full_img_url(resp.text)
        durl, path = self.option.decide_img_download_plan(book, hurl, furl, self.client)
        if durl is None:
            return

        self.download_image(durl, path)

    def download_image(self, img_url: str, path: str):
        self.workers.submit(self.client.download_image, img_url, path)

    def run_all(self, iterables, apply, wait=True):
        future_list = []

        for obj in iterables:
            f = self.workers.submit(apply, obj)
            future_list.append(f)

        if wait is True:
            for f in future_list:
                f.result()
