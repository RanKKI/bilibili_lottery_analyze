import logging

from .model import Space, Card, Lottery
from .api import BilibiliApi


class Bilibili(object):

    def __init__(self, dynamic_id: int = None):
        """
         post_id 抽奖动态的id
         user_id 抽奖up主的uid
         dynamic_id 抽奖动态的dynamic_id
        """
        self.dynamic_id = dynamic_id
        self.api = BilibiliApi()
        self.logger = logging.getLogger("Bilibili")

    def get_all_prize_user_ids(self) -> Lottery:
        self.logger.info(f"getting lottery infomation of {self.dynamic_id}")
        resp = self.api.get_lottery_notice(self.dynamic_id)
        data = resp.get("data")
        self.logger.info(f" ┗ lottery_time: {data.get('lottery_time')}")
        for key in ["first_prize", "second_prize", "third_prize"]:
            if data[key] == 0:
                continue
            self.logger.info(f" ┗ {key} #{data[key+'_cmt']}: {data[key]} users")
        return Lottery.from_lottery_notice(data)

    def get_dynamic_detail(self) -> Card:
        data = self.api.get_dynamic_detail(self.dynamic_id)
        return Card.from_json(data.get("data").get("card"))

    def get_user_space(self, uid: int, offset: int = 0) -> Space:
        self.logger.info(f"getting user's space infomation of {uid}")
        resp = self.api.get_user_space(self.dynamic_id, uid, offset)
        data = resp.get("data")
        if "cards" not in data:
            return None
        return Space.from_json(data)

    def find_user_dynamic(self, uid: int, origin: Card) -> Card:
        """
            找到所有和抽奖动态相关的动态, 并且返回发布最早的动态
        """
        space = self.get_user_space(uid)
        posts = []  # 所有origin一样的动态
        while space:
            posts += list(filter(lambda card: card.origin == origin, space.cards))
            if space.cards and space.cards[-1].timestamp < origin.timestamp:
                # 如果最后一个动态早于抽奖动态发送的时间
                break
            if not space.has_more:
                break
            space = self.get_user_space(uid, offset=space.offset)
        if not posts:
            self.logger.error(f"user {uid} doesn't have matched posts")
            return None
        return min(posts, key=lambda x: x.timestamp)

    def get_all_repost_user(self, offset: str = ""):
        self.logger.info(f"getting repost of dynamic {self.dynamic_id}")
        resp = self.api.get_repost_of_dynamic(self.dynamic_id, offset)
        data = resp.get("data")
        yield from map(Card.from_json, data.get("items", []))
        if data.get("has_more"):
            yield from self.get_all_repost_user(data.get("offset"))

    def get_all_reply_user(self, pn: int = 1):
        self.logger.info(f"getting replies of dynamic {self.dynamic_id}")

        resp = self.api.get_replies_of_dynamic(self.dynamic_id, pn)
        data = resp.get("data")
        page = data.get("page")

        yield from map(Card.from_reply_json, data.get("replies"))
        if page.get("num") * page.get("size") < page.get("count") and pn < 600:
            yield from self.get_all_reply_user(pn + 1)
