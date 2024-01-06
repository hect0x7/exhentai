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
        pic_url_dict: dict[str, str] = {}
        # fetch all pic_url (https://exhentai.org/s/xx/xx) of gallery

        # first page
        book = self.client.fetch_gallery_page(gid, token, p=0)
        pic_url_dict.update(book.pageInfo.picUrl)

        # the rest page
        # for p in range(1, book.page_count):
        #     book = self.client.fetch_gallery_page(gid, token, p)
        #     pic_url_dict.update(book.pic_url_dict)

        self.run_all(
            iterables=range(1, book.page_count),
            apply=lambda p: pic_url_dict.update(self.client.fetch_gallery_page(gid, token, p).pageInfo.picUrl),
        )

        # to sorted list
        # sorted(list(pic_url_dict), key=lambda url: int(url[url.index('-'):]), reverse=True)

        # for pic_url in pic_url_dict:
        #     self.download_pic(pic_url, book)

        self.run_all(
            iterables=pic_url_dict.items(),
            apply=lambda index, pic_url: self.download_pic(index, pic_url, book),
        )

    def download_pic(self, index: str, pic_url: str, book: BookInfo):
        resp = self.client.fetch_pic_page(pic_url)
        hurl, furl = ExhentaiHtmlParser.parse_hash_full_img_url(resp.text)
        durl, path = self.option.decide_img_download_plan(book, int(index), hurl, furl, self.client)
        if durl is None:
            return

        self.download_image(durl, path)

    def download_image(self, img_url: str, path: str):
        self.workers.submit(self.client.download_image, img_url, path)

    def run_all(self, iterables, apply, wait=True):
        future_list = []

        for obj in iterables:
            args, kwargs = common.process_single_arg_to_args_and_kwargs(obj)
            f = self.workers.submit(apply, *args, **kwargs)
            future_list.append(f)

        if wait is True:
            for f in future_list:
                f.result()
