import json
import csv
import os
import random

from functools import reduce
from typing import List
from itertools import chain

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

    def get_user_space(self, uid: int = None, offset: int = 0) -> Space:
        if not uid or not self.user_id:
            raise ValueError("uid or self.user_id must be provided")
        # 如果没有提供uid, 则获取up主的id
        uid = uid or self.user_id
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id={offset}"
        data = convert_json(self.get(url, type="user_space"))["data"]
        if "cards" not in data:
            return None
        return Space.from_json(data["cards"])

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

    def find_origin_post(self, space: Space) -> Card:
        if not space:
            raise ValueError("history not exists")
        if not self.post_id:
            raise ValueError("post_id is required")
        for history in sorted(space.cards, key=lambda x: x.timestamp, reverse=True):
            if history.origin and history.origin.id == self.post_id:
                return history
        """
        如果没有找到抽奖动态, 转至下一页
        """
        return self.find_origin_post(self.get_user_space(space.user.uid, offset=space.offset))

    def write_prize_users(self, ids: List[int]):
        with open('./output/prize_users.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(self.header)
            for space in map(lambda uid: self.get_user_space(uid=uid), ids):
                prized_post = self.find_origin_post(space)
                user = space.user
                time_after = prized_post.timestamp - prized_post.origin.timestamp
                writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, time_after])

    def write_all_users(self):
        with open('./output/all_other_users.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(self.header)
            prized_post = next(self.get_all_repost_user()).origin
            for card in chain(self.get_all_repost_user(), self.get_all_reply_user()):
                user = card.user
                time_after = card.timestamp - prized_post.timestamp
                writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, time_after])

    def run(self):
        # ids = self.get_all_prize_user_ids()
        # self.write_prize_users(ids)
        self.write_all_users()


if __name__ == "__main__":
    bilibili = Bilibili(75347916, 254463269, 394000250829625700)
    bilibili.run()
