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

        cookies = dict(resp.cookies)
        self.cookies_list[i].update(cookies)

        return resp

    def download_image(self, img_url, path):
        log('image.before', f'prepare [{img_url}] -> [{path}]')
        resp = self.get_image(img_url)
        SaveTool.save_resp_img(
            resp,
            path,
            need_convert=common.suffix_not_equal(img_url, path)
        )
        log('image.after', f'finish [{img_url}] -> [{path}]')

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


class RetryProxy(common.RetryPostman):
    def tip_retrying(self, time, _request, url, kwargs):
        log('request.retry', f'[{time + 1}/{self.retry_times}]: {url}')

    def retry_request(self, request, url, **kwargs):
        retry_times = self.retry_times
        if retry_times <= 0:
            return request(url, **kwargs)

        for i in range(retry_times):
            try:
                resp = request(url, **kwargs)
                resp = self.check_resp_should_retry(resp)
                return resp
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                self.excp_handle(e)
                self.tip_retrying(i, request, url, kwargs)

        return self.fallback(url, kwargs)

    # noinspection PyMethodMayBeStatic
    def check_resp_should_retry(self, resp):
        if resp.status_code != 200:
            raise AssertionError(resp.status_code, resp.text)

        if ExHentaiModule.MSG_IP_WAS_BANNED in resp.text:
            raise AssertionError(resp.text)

        return resp

    def excp_handle(self, e):
        log('request.fail', e)
