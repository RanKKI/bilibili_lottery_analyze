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
        try:
            return cls(**{
                "uid": profile["info"]["uid"],
                "name": profile["info"]["uname"],
                "level": profile["level_info"]["current_level"],
                "vip_type": profile["vip"]["vipType"],
                "vip_status": profile["vip"]["vipStatus"]
            })
        except KeyError:
            return None

    @classmethod
    def from_space_history(cls, data: dict):
        if "info" not in data:
            profile = data.get("desc", {}).get("user_profile")
        else:
            profile = data
        if not profile:
            return None
        return cls(**{
            "uid": profile["info"]["uid"],
            "name": profile["info"]["uname"],
            "level": profile["level_info"]["current_level"],
            "vip_type": profile["vip"]["vipType"],
            "vip_status": profile["vip"]["vipStatus"]
        })

    @classmethod
    def from_space_histories(cls, data: List[dict]):
        return cls.from_space_history(data[0])

    @classmethod
    def from_repost(cls, data: dict):
        pass

    @classmethod
    def from_reply(cls, data: dict):
        return cls(**{
            "uid": data.get("mid"),
            "name": data.get("uname"),
            "level": data["level_info"]["current_level"],
            "vip_type": data["vip"]["vipType"],
            "vip_status": data["vip"]["vipStatus"]
        })


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

        self.id = id
        self.dynamic_id = dynamic_id  # 如果是转发
        self.rp_id = rp_id  # 如果是回复

        # 抽奖相关
        self.lott_id = lott_id

    @classmethod
    def from_json(cls, root: dict, is_origin: bool = False):
        if not root:
            return None

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

        content = item.get("content", item.get("description"))
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
        return cls(**{
            "content": data.get("content").get("message"),
            "timestamp": data.get("ctime"),
            "id": data.get("rpid"),
            "user": User.from_reply(data.get("member"))
        })


class Space(object):

    def __init__(self,
                 user: User,
                 cards: List[Card]):
        self.user = user
        self.cards = cards
        self.offset = 0
        if len(cards) > 0:
            self.offset = cards[-1].dynamic_id

    def __repr__(self):
        return f"<Space of {self.user.uid}>"

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            user=User.from_space_histories(data),
            cards=list(filter(lambda x: x, map(lambda x: Card.from_json(x), data)))
        )
