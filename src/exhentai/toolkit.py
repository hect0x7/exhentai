import os
import re
from typing import Callable

from bs4 import BeautifulSoup
import common

from .entity import *


class ExhentaiHtmlParser:
    pattern_hashimg_url = re.compile('<img id="img" src="(.*hath.network[^"]*)"')
    pattern_fullimg_url = re.compile('(https://exhentai.org/fullimg/[^"]*)')

    @classmethod
    def parse_hash_full_img_url(cls, html: str) -> tuple[str, str]:
        hashimg_url = ExceptionTool.require_match(html, cls.pattern_hashimg_url)
        fullimg_url = ExceptionTool.require_match(html, cls.pattern_fullimg_url)

        return hashimg_url, fullimg_url

    # noinspection DuplicatedCode
    # code are base on https://github.com/tonquer/ehentai-qt
    @classmethod
    def parse_book_info(cls, html: str) -> BookInfo:
        soup = BeautifulSoup(html, features="lxml")
        tag = soup.find("div", id="gdd")

        ExceptionTool.require_true(tag, html)

        table = tag.find("table")
        book = BookInfo()
        info = book.pageInfo
        for tr in table.find_all("tr"):
            key = tr.find("td", class_="gdt1").text.replace(":", "")
            value = tr.find("td", class_="gdt2").text
            info.kv[key] = value
        info.posted = info.kv.get("Posted")
        info.language = info.kv.get("Language")
        info.fileSize = info.kv.get("File Size")
        mo = re.search(r'\d+', info.kv.get("Length"))
        if mo:
            info.pages = int(mo.group())
        mo = re.search(r"\d+", info.kv.get("Favorited", ""))
        if mo:
            info.favorites = int(mo.group())

        for tag in soup.find_all("div", class_=re.compile(r"gdt\w")):
            url = tag.a.attrs.get('href')
            index = int(tag.a.img.attrs.get('alt'))
            info.picUrl[index] = url
            preUrl = tag.a.img.attrs.get("src")
            if preUrl and "ehgt.org/g/blank.gif" not in preUrl:
                info.preUrl[index] = preUrl

        # table = soup.find("table", class_="ptt")
        # maxPage = 1
        # for td in table.tr.children:
        #     if getattr(td, "a", None):
        #         pages = td.a.text
        #         datas = re.findall(r"\d+", pages)
        #         if not datas:
        #             continue
        #         maxPage = max(maxPage, int(datas[0]))

        comment = soup.find("div", id="cdiv")
        for tag in comment.find_all("div", class_="c1"):
            times = tag.find("div", class_="c3").text
            script = tag.find("div", class_="c6").get_text(separator="\n")
            info.comment.append([times, script])
        base = book.baseInfo
        script = soup.find_all("script", {'type': "text/javascript"})
        mo = re.search(r"(?<=var gid =\s)\d+", script[1].next)
        base.id = mo.group()
        mo = re.search("(?<=var token = \")\\w+", script[1].next)
        base.token = mo.group()
        mo = re.search(r"(?<=var apiuid = )\S*(?=;)", script[1].next)
        base.apiUid = mo.group()
        mo = re.search("(?<=var apikey = \")\\w+", script[1].next)
        base.apiKey = mo.group()
        mo = re.search(r"(?<=var average_rating =\s)\d+(.\d+)", script[1].next)
        base.average_rating = mo.group()
        mo = re.search(r"(?<=var display_rating =\s)\d+(.\d+)", script[1].next)
        base.display_rating = mo.group()
        tag = soup.find("div", id="gdc")
        base.category = tag.text.replace("\n", "")
        tag = soup.find("h1", id="gn")
        base.title = tag.text
        tag = soup.find("div", id="gd1")
        base.imgUrl = re.search(r"(?<=url\()\S*(?=\))", tag.div.attrs.get("style")).group()
        table = soup.find("div", id="taglist")
        for tc in table.find_all("td", class_="tc"):
            td = tc.find_next_sibling()
            if td:
                for div in td.find_all("div"):
                    base.tags.append(tc.text + div.text)

        # tag = soup.find("p", class_="br")
        # commentError = ""
        # if tag:
        #     commentError = tag.text
        # tags = soup.find_all("div", class_="gdtl")
        return book


class ExceptionTool:
    @classmethod
    def require_true(cls, case, msg):
        if case:
            return

        raise AssertionError(msg)

    @classmethod
    def match_or_default(cls, html: str, pattern: re.Pattern, default):
        match = pattern.search(html)
        return default if match is None else match[1]

    @classmethod
    def require_match(cls, html: str, pattern: re.Pattern, rindex=1):
        match = pattern.search(html)
        ExceptionTool.require_true(match is not None, f'pattern {pattern} not match: [{html}]')

        if match is not None:
            return match[rindex] if rindex is not None else match


class DirRule:
    RuleFunc = Callable[[BookInfo], str]
    RuleSolver = tuple[int, RuleFunc, str]
    RuleSolverList = list[RuleSolver]

    rule_solver_cache: dict[str, RuleSolver] = {}

    def __init__(self, rule: str, base_dir):
        base_dir = TextTool.parse_to_abspath(base_dir)
        self.base_dir = base_dir
        self.rule_dsl = rule
        self.solver_list = self.get_role_solver_list(rule, base_dir)

    def decide_image_save_dir(self,
                              base_info: BookBaseInfo,
                              page_info: BookPageInfo,
                              ) -> str:
        path_ls = []
        for solver in self.solver_list:
            ret = self.apply_rule_solver(base_info, page_info, solver)
            path_ls.append(str(ret))

        return os.path.abspath('/'.join(path_ls))

    def get_role_solver_list(self, rule_dsl: str, base_dir: str) -> RuleSolverList:
        ExceptionTool.require_true('_' in rule_dsl or rule_dsl == 'Bd',
                                   f'dsl is unsupported: "{rule_dsl}"')

        rule_list = rule_dsl.split('_')
        solver_ls: list[DirRule.RuleSolver] = []

        for rule in rule_list:
            if rule == 'Bd':
                solver_ls.append((0, lambda _: base_dir, 'Bd'))
                continue

            rule_solver = self.get_rule_solver(rule)
            ExceptionTool.require_true(rule_solver is not None, f'dsl is unsupported: "{rule}" in "{rule_dsl}"')

            solver_ls.append(rule_solver)

        return solver_ls

    @classmethod
    def get_rule_solver(cls, rule: str) -> RuleSolver | None:
        if not rule.startswith(('B', 'P')):
            return None

        # Axxx or Pyyy
        key = 1 if rule[0] == 'B' else 2
        solve_func = lambda detail, ref=rule[1:]: common.fix_windir_name(str(Entity.get_dirname(detail, ref)))

        # 保存缓存
        rule_solver = (key, solve_func, rule)
        return rule_solver

    @classmethod
    def apply_rule_solver(cls, base_info, page_info, rule_solver: RuleSolver) -> str:
        def choose_detail(key):
            if key == 0:
                return None
            if key == 1:
                return base_info
            if key == 2:
                return page_info

        key, func, _ = rule_solver
        detail = choose_detail(key)
        return func(detail)


class TextTool:
    class DSLReplacer:

        def __init__(self):
            self.dsl_dict: dict[re.Pattern, Callable[[re.Match], str]] = {}

        def parse_dsl_text(self, text) -> str:
            for pattern, replacer in self.dsl_dict.items():
                text = pattern.sub(replacer, text)
            return text

        def add_dsl_and_replacer(self, dsl: str, replacer: Callable[[re.Match], str]):
            pattern = re.compile(dsl)
            self.dsl_dict[pattern] = replacer

    @classmethod
    def match_os_env(cls, match: re.Match) -> str:
        name = match[1]
        value = os.getenv(name, None)
        ExceptionTool.require_true(value is not None, f'env not found: {name}')
        return value

    dsl_replacer = DSLReplacer()

    @classmethod
    def parse_to_abspath(cls, dsl_text: str) -> str:
        return os.path.abspath(cls.parse_dsl_text(dsl_text))

    @classmethod
    def parse_dsl_text(cls, dsl_text: str) -> str:
        return cls.dsl_replacer.parse_dsl_text(dsl_text)


TextTool.dsl_replacer.add_dsl_and_replacer(r'\$\{(.*?)\}', TextTool.match_os_env)


class SaveTool:

    @classmethod
    def save_resp_img(cls, resp, filepath: str, need_convert=True):
        if need_convert is False:
            cls.save_directly(resp, filepath)
        else:
            cls.save_image(cls.open_Image(resp.content), filepath)

    @classmethod
    def save_image(cls, image, filepath: str):
        image.save(filepath)

    @classmethod
    def save_directly(cls, resp, filepath):
        from common import save_resp_content
        save_resp_content(resp, filepath)

    @classmethod
    def open_Image(cls, fp):
        from io import BytesIO
        from PIL import Image
        return Image.open(BytesIO(fp))
