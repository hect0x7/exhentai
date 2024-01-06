def default_logging(topic, msg):
    from common import format_ts
    print(f'{format_ts()}:【{topic}】{msg}')


class ExHentaiModule:
    DOMAIN_DNS = {
        "e-hentai.org": "104.20.135.21",
        "exhentai.org": "178.175.128.254",
        "ehgt.org": "37.48.89.44",
        "forums.e-hentai.org": "104.20.135.21",
        "gt0.ehgt.org": "37.48.89.44",
        "api.e-hentai.org": "104.20.135.21",
    }

    MSG_IP_WAS_BANNED = 'Your IP address has been temporarily banned'
    LOGGING_FUNC = default_logging
    LOGGING_ENABLE = True

    @classmethod
    def downloader(cls):
        from .downloader import ExhantaiDownloader
        return ExhantaiDownloader

    @classmethod
    def log(cls, topic, msg):
        if cls.LOGGING_ENABLE:
            cls.LOGGING_FUNC(topic, msg)


log = ExHentaiModule.log
