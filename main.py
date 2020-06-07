import csv

from itertools import chain

from bilibili import Bilibili
from model import Space, Card


class CleanOutput(object):

    def __init__(self, post_id, user_id, dynamic_id):
        self.bilibili = Bilibili(post_id, user_id, dynamic_id)
        self.header = ["uid", "level", "vip_type", "vip_status", "time_after"]

    def find_origin_post(self, space: Space) -> Card:
        if not space:
            raise ValueError("history not exists")
        for history in sorted(space.cards, key=lambda x: x.timestamp, reverse=True):
            if history.origin and history.origin.id == self.bilibili.post_id:
                return history
        """
        如果没有找到抽奖动态, 转至下一页
        """
        space = self.bilibili.get_user_space(space.user.uid, offset=history.dynamic_id)
        return self.find_origin_post(space)

    def write_prize_users(self):
        ids = self.bilibili.get_all_prize_user_ids()
        with open('./output/prize_users.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(self.header)
            for space in map(lambda uid: self.bilibili.get_user_space(uid), ids):
                prized_post = self.find_origin_post(space)
                user = space.user
                time_after = prized_post.timestamp - prized_post.origin.timestamp
                writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, time_after])

    def write_all_users(self):
        with open('./output/all_other_users.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(self.header)
            prized_post = next(self.bilibili.get_all_repost_user()).origin
            for card in chain(self.bilibili.get_all_repost_user(), self.bilibili.get_all_reply_user()):
                user = card.user
                time_after = card.timestamp - prized_post.timestamp
                writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, time_after])


if __name__ == "__main__":
    output = CleanOutput(75347916, 254463269, 394000250829625700)
    # output.write_all_users()
    output.write_prize_users()
