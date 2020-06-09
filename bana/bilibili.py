import json
import os
import random

from functools import reduce
from typing import List

from bana.model import Space, Card
from bana.network import get as network_get
from bana.utils import convert_json


class Bilibili(object):

    def __init__(self,
                 post_id: int = None,
                 user_id: int = None,
                 dynamic_id: int = None):
        """
         post_id 抽奖动态的id
         user_id 抽奖up主的uid
         dynamic_id 抽奖动态的dynamic_id
        """
        self.post_id = post_id
        self.user_id = user_id
        self.dynamic_id = dynamic_id
        self.cache_dir = f"./cache/{self.user_id}/"
        if not os.path.exists("./cache/"):
            os.mkdir("./cache/")

    def get(self, url: str, **kwargs) -> str:
        cache_dir = self.cache_dir
        if kwargs.get("type"):
            cache_dir += f"{kwargs.get('type')}/"
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        return network_get(url, cache_dir=cache_dir, ext=".json", **kwargs).text

    def get_all_prize_user_ids(self) -> List[int]:
        if not self.dynamic_id:
            raise ValueError("dynamic_id is required")
        url = f"https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={self.dynamic_id}"
        data = json.loads(self.get(url, type="prize_users"))
        return list(map(lambda x: x["uid"], reduce(lambda x, y: x + y, data["data"]["lottery_result"].values())))

    def get_user_space(self, uid: int, offset: int = 0) -> Space:
        # 如果没有提供uid, 则获取up主的id
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id={offset}"
        data = convert_json(self.get(url, type="user_space"))
        if "cards" not in data["data"]:
            return None
        return Space.from_json(data["data"])

    def find_user_dynamic(self, uid: int, origin: Card = None) -> Card:
        """
            Find all of user's post
            if origin provided return the post with same origin
        """
        offset = 0
        while True:
            space = self.get_user_space(uid, offset)
            if not space:
                break
            for card in space.cards:
                if origin and card.origin == origin:
                    yield card
                    break
                else:
                    yield card
            if not space.has_more:
                break
            offset = space.offset

    def get_all_repost_user(self, offset: str = None, _rand: bool = False):
        if not self.dynamic_id:
            raise ValueError("dynamic_id is required")
        url = f"https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail?dynamic_id={self.dynamic_id}"
        no_cache = not bool(offset)
        if offset:
            url += "&offset=" + offset
            no_cache = int(offset.split(":")[1]) < 100
        if _rand:
            no_cache = random.random() < 0.5
        data = convert_json(self.get(url, no_cache=no_cache, type="repost"))["data"]
        for card in map(Card.from_json, data["items"]):
            if card.user.uid != self.user_id:  # 跳过up主本人
                yield card
        if data.get("has_more"):
            yield from self.get_all_repost_user(data["offset"], _rand=_rand)

    def get_all_reply_user(self, pn: int = 1):
        if not self.post_id:
            raise ValueError("post_id is required")
        url = f"https://api.bilibili.com/x/v2/reply?pn={pn}&type=11&oid={self.post_id}&sort=2"
        data = json.loads(self.get(url, type="reply"))["data"]
        for reply in map(Card.from_reply_json, data["replies"]):
            if reply.user.uid != self.user_id:
                yield reply
        page = data["page"]
        if page["num"] * page["size"] < page["count"] and pn < 600:
            yield from self.get_all_reply_user(pn + 1)
