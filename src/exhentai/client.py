# noinspection PyUnresolvedReferences
from common import Postman

from .toolkit import *


class ExhentaiClient:

    def __init__(self,
                 postman: Postman,
                 cookies_list: list[dict],
                 ):
        self.postman = postman
        self.cookies_list = cookies_list

    def get_html(self,
                 url,
                 retry=5,
                 *args,
                 **kwargs,
                 ):
        log('html', url)

        i, cookies = self.choose_cookies()
        resp = self.postman.get(url,
                                cookies=cookies,
                                allow_redirects=True,
                                *args,
                                **kwargs,
                                )

        if ExHentaiModule.MSG_IP_WAS_BANNED in resp.text and retry > 0:
            return self.get_html(url, *args, retry=retry - 1, **kwargs)

        if resp.status_code != 200:
            raise AssertionError(resp.status_code, resp.text)

        cookies = dict(resp.cookies)
        self.cookies_list[i].update(cookies)

        return resp

    def download_image(self, img_url, path):
        resp = self.get_image(img_url)
        SaveTool.save_resp_img(
            resp,
            path,
            need_convert=common.suffix_not_equal(img_url, path)
        )

    def post_api(self,
                 url,
                 *args,
                 **kwargs,
                 ):
        i, cookies = self.choose_cookies()
        return self.postman.post(url,
                                 cookies=cookies,
                                 *args,
                                 **kwargs,
                                 )

    def fetch_gallery_page(self, gid, token, p=0) -> BookInfo:
        resp = self.get_html(f'https://exhentai.org/g/{gid}/{token}/?p={p}')
        html = resp.text

        from .toolkit import ExhentaiHtmlParser
        book: BookInfo = ExhentaiHtmlParser.parse_book_info(html)

        return book

    def fetch_pic_page(self, url):
        """

        :param url: https://exhentai.org/s/cc3cc8e071/2787407-36
        """
        resp = self.get_html(url)
        return resp

    def choose_cookies(self):
        import random
        index = random.randint(0, len(self.cookies_list) - 1)
        return index, self.cookies_list[index]

    def get_image(self, img_url):
        log('image', img_url)

        i, cookies = self.choose_cookies()

        return self.postman.get(img_url, cookies=cookies)
