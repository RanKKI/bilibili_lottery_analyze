import hashlib
import logging
import os
import requests
import urllib.parse as urlparse

from pathlib import Path
from urllib.parse import urlencode
from typing import Union

from conf import APP_DIR
from .utils import convert_json

URL_API = "https://api.bilibili.com"
URL_VC_API = "https://api.vc.bilibili.com"

URL_LOTTERY_NOTICE = URL_VC_API + "/lottery_svr/v1/lottery_svr/lottery_notice"
URL_SPACE_HISTORY = URL_VC_API + "/dynamic_svr/v1/dynamic_svr/space_history"
URL_REPOST_DETAILS = URL_VC_API + "/dynamic_repost/v1/dynamic_repost/repost_detail"
URL_DYNAMIC_DETAIL = URL_VC_API + "/dynamic_svr/v1/dynamic_svr/get_dynamic_detail"

URL_REPLY = URL_API + "/x/v2/reply"
URL_RANKING = URL_API + "/x/web-interface/ranking"


class BilibiliApi(object):

    def __init__(self):
        self.logger = logging.getLogger("Bilibili API")
        self.cache_dir = Path(APP_DIR) / "cache"
        self.request_get = requests.get

    def get(self, url: str, ext: str, cache_dir: Path = None, cache: bool = True, query: dict = None):
        if cache:
            if not cache_dir:
                raise ValueError("cache_dir must be provided, if cache needed")
            elif not cache_dir.exists():
                os.makedirs(cache_dir)

        if query:
            # 增加参数
            url_parts = list(urlparse.urlparse(url))
            query.update(dict(urlparse.parse_qsl(url_parts[4])))
            url_parts[4] = urlencode(query)
            url = urlparse.urlunparse(url_parts)

        if cache:
            _hash = hashlib.md5(url.encode("latin-1")).hexdigest()
            file_name = cache_dir / f"{_hash}.{ext}"
            if file_name.exists():
                self.logger.debug(f"loading from {file_name}")
                with open(file_name, "r", encoding="utf8") as f:
                    if ext == "json":
                        return convert_json(f.read())
                    return f.read()

        self.logger.debug(f"requesting {url}")
        res = self.request_get(url)
        res.encoding = "utf8"
        if cache:
            self.logger.debug(f"         - {file_name}")
            with open(file_name, "w", encoding="utf8") as f:
                f.write(res.text)
        if ext == "json":
            return convert_json(res.text)
        return res.text

    def get_lottery_notice(self, dynamic_id: int) -> dict:
        return self.get(
            url=URL_LOTTERY_NOTICE,
            cache_dir=self.cache_dir / str(dynamic_id) / "lottery",
            ext="json",
            query={
                "dynamic_id": dynamic_id
            }
        )

    def get_user_space(self, dynamic_id: Union[int, str], user_id: int, offset: int = 0, **kwargs) -> dict:
        """
            如果dynamic_id是int, 则dynamic_id是动态的id,
            如果是str, 那就是 sub cache dir
        """
        return self.get(
            url=URL_SPACE_HISTORY,
            cache_dir=self.cache_dir / str(dynamic_id) / "user",
            ext="json",
            query={
                "host_uid": user_id,
                "offset_dynamic_id": offset
            },
            **kwargs
        )

    def get_dynamic_detail(self, dynamic_id: int) -> dict:
        return self.get(
            url=URL_DYNAMIC_DETAIL,
            cache_dir=self.cache_dir / str(dynamic_id),
            ext="json",
            query={
                "dynamic_id": dynamic_id,
            }
        )

    def get_repost_of_dynamic(self, dynamic_id: int, offset: str = "") -> dict:
        # 缓存相关
        # 如果是最近几页, 不做缓存
        cache = ":" in offset and int(offset.split(":")[1]) < 100
        return self.get(
            url=URL_REPOST_DETAILS,
            cache_dir=self.cache_dir / str(dynamic_id) / "repost",
            ext="json",
            query={
                "dynamic_id": dynamic_id,
                "offset": offset
            },
            cache=cache
        )

    def get_replies_of_dynamic(self, dynamic_id: int, pn: int = 1) -> dict:
        return self.get(
            url=URL_REPLY,
            cache_dir=self.cache_dir / str(dynamic_id) / "reply",
            ext="json",
            query={
                "pn": pn,
                "type": 11,
                "oid": dynamic_id,
                "sort": 0  # 0是按时间, 2是热度
            }
        )

    def get_ranking(self, rid: int, day: int, _type: int, arc_type: int) -> dict:
        return self.get(
            url=URL_RANKING,
            cache=False,
            ext="json",
            query={
                "rid": rid,
                "day": day,
                "type": _type,
                "arc_type": arc_type
            },
        )
