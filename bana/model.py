from __future__ import annotations

from typing import List
from datetime import datetime


class User(object):

    def __init__(self,
                 uid: int,
                 name: str,
                 level: int,
                 vip_type: int,
                 vip_status: int):
        self.uid = uid
        self.name = name
        self.level = level
        self.vip_type = vip_type
        self.vip_status = vip_status

    def __repr__(self):
        return f"<User {self.uid}>"

    @classmethod
    def from_user_profile(cls, profile: dict):
        if not profile:
            raise ValueError("Profile is required")
        return cls(
            uid=profile["info"]["uid"],
            name=profile["info"]["uname"],
            level=profile["level_info"]["current_level"],
            vip_type=profile["vip"]["vipType"],
            vip_status=profile["vip"]["vipStatus"]
        )

    @classmethod
    def from_reply(cls, data: dict):
        data["info"] = {
            "uid": data.pop("mid"),
            "uname": data.pop("uname")
        }
        return cls.from_user_profile(data)


class Card(object):

    def __init__(self,
                 content: str,
                 timestamp: int,
                 user: User,
                 origin: Card = None,
                 dynamic_id: int = None,
                 lott_id: int = None,
                 rp_id: int = None,
                 id: int = None):
        self.content = content
        self.timestamp = timestamp
        self.user = user

        self.origin = origin

        self.id = id  # 动态 post id
        self.dynamic_id = dynamic_id  # 动态的dynamic_id
        self.rp_id = rp_id  # 回复

        # 抽奖相关
        self.lott_id = lott_id

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.dynamic_id == other.dynamic_id

    @classmethod
    def from_json(cls, root: dict, is_origin: bool = False):
        if not root:
            raise ValueError("root is not none")
        desc = root.get("desc")
        card = root.get("card")

        item = card.get("item")
        user_profile = desc.get("user_profile")
        dynamic_id = desc.get("dynamic_id")

        # 是否有抽奖
        lott_id = card.get("extension", {}).get("lott", {}).get("lottery_id")

        if is_origin:
            item = card.get("origin").get("item")
            user_profile = card.get("origin_user")
            dynamic_id = desc.get("origin").get("dynamic_id")
            lott_id = card.get("origin_extension", {}).get("lott", {}).get("lottery_id")

        if "aid" in card or not item:
            """
                是视频！
                或者, 没有item
            """
            return None

        origin_object = None
        if "origin" in card and not is_origin:
            origin_object = cls.from_json(root, is_origin=True)

        content = item.get("content", item.get("description", ""))
        timestamp = item.get("timestamp", item.get("upload_time"))

        try:
            timestamp = int(timestamp)
        except ValueError:
            timestamp = int(datetime.strptime("2020-01-19 18:10:19", "%Y-%m-%d %H:%M:%S").timestamp())

        return cls(
            content=content,
            timestamp=timestamp,
            origin=origin_object,
            user=User.from_user_profile(user_profile),
            dynamic_id=dynamic_id,
            lott_id=lott_id,
            id=card.get("id")
        )

    @classmethod
    def from_reply_json(cls, data: dict):
        return cls(
            content=data.get("content").get("message"),
            timestamp=data.get("ctime"),
            rp_id=data.get("rpid"),
            user=User.from_reply(data.get("member"))
        )


class Space(object):

    def __init__(self,
                 user: User,
                 cards: List[Card],
                 has_more: bool = False):
        self.user = user
        self.cards = cards
        self.offset = 0
        self.has_more = has_more
        if len(cards) > 0:
            self.offset = cards[-1].dynamic_id

    def __repr__(self):
        return f"<Space of {self.user.uid}>"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            user=User.from_user_profile(data["cards"][0].get("desc", {}).get("user_profile")),
            cards=list(filter(lambda x: x, map(lambda x: Card.from_json(x), data["cards"]))),
            has_more=bool(data["has_more"])
        )
