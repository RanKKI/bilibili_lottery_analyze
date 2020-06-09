import csv

from itertools import chain
from typing import Iterator

from bana.bilibili import Bilibili
from bana.model import Card


class Outputer(object):

    def __init__(self, post_id, user_id, dynamic_id):
        self.bilibili = Bilibili(post_id, user_id, dynamic_id)
        self.header = ["uid", "level", "vip_type", "vip_status", "time_after"]
        # 中奖动态的信息
        self.prized_post: Card = next(self.bilibili.get_all_repost_user()).origin

    def write(self, file_name: str, cards: Iterator[Card]):
        with open(file_name, 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(self.header)
            for card in cards:
                user = card.user
                time_after = card.timestamp - self.prized_post.timestamp
                writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, time_after])

    def write_prize_users(self):
        ids = self.bilibili.get_all_prize_user_ids()
        self.write("./output/prize_users.csv", chain.from_iterable(
            [self.bilibili.find_user_dynamic(uid, self.prized_post) for uid in ids]
        ))

    def write_all_users(self):
        self.write("./output/all_other_users.csv",
                   chain(self.bilibili.get_all_repost_user(),
                         self.bilibili.get_all_reply_user())
                   )


if __name__ == "__main__":
    outputer = Outputer(75347916, 254463269, 394000250829625700)
    # outputer.write_all_users()
    outputer.write_prize_users()
