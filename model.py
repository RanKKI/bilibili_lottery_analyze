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
    def from_space_history(cls, data: dict):
        profile = data.get("desc", {}).get("user_profile")
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
                 id: int = None,
                 dynamic_id: int = None):
        self.content = content
        self.timestamp = timestamp
        self.user = user
        self.origin = origin
        self.id = id
        self.dynamic_id = dynamic_id

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return
        card = data.get("card", data)
        item = card.get("item")
        if not item:
            return
        content = item.get("content", item.get("description"))
        timestamp = item.get("timestamp", item.get("upload_time"))
        try:
            timestamp = int(timestamp)
        except ValueError:
            timestamp = int(datetime.strptime("2020-01-19 18:10:19", "%Y-%m-%d %H:%M:%S").timestamp())
        return cls(**{
            "content": content,
            "timestamp": timestamp,
            "origin": Card.from_json(card.get("origin")),
            "id": item.get("id"),
            "user": User.from_space_history(data),
            "dynamic_id": data.get("desc", {}).get("dynamic_id")
        })

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

    def __repr__(self):
        return f"<Space of {self.user.uid}>"

    @classmethod
    def from_json(cls, data: dict):
        return cls(**{
            "user": User.from_space_histories(data),
            "cards": list(filter(lambda x: x, map(lambda x: Card.from_json(x), data)))
        })
