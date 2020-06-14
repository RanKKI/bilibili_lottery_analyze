import csv
import os
import json

from itertools import chain
from typing import Iterator, TextIO
from pathlib import Path

from bana import Bilibili, Card
from conf import APP_DIR


class Outputer(object):

    def __init__(self, dynamic_id: int):
        self.bilibili = Bilibili(dynamic_id)
        self.header = ["uid", "level", "vip_type", "vip_status", "timestamp"]
        # 中奖动态的信息
        self.prized_post: Card = next(self.bilibili.get_all_repost_user()).origin
        self.output_path = Path(APP_DIR) / "output" / str(dynamic_id)
        if not self.output_path.exists():
            os.makedirs(self.output_path)

    def write_to_file(self, file_stream: TextIO, cards: Iterator[Card]):
        writer = csv.writer(file_stream, delimiter=",")
        writer.writerow(self.header)
        for card in filter(lambda x: x, cards):
            user = card.user
            writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, card.timestamp])

    def write_prize_users(self):
        file_path = self.output_path / "prize_users.csv"
        if file_path.exists():
            return
        lottery = self.bilibili.get_all_prize_user_ids()
        with open(file_path, "w", encoding="utf8") as f:
            cards = (self.bilibili.find_user_dynamic(user.uid, self.prized_post) for user in lottery.prize_users)
            self.write_to_file(f, cards)

    def write_prize_info(self):
        file_path = self.output_path / "prize_info.json"
        if file_path.exists():
            return
        lottery = self.bilibili.get_all_prize_user_ids()
        detail = self.bilibili.get_dynamic_detail()
        with open(file_path, "w", encoding="utf8") as f:
            json.dump({
                "start_time": detail.timestamp,
                "end_time": lottery.lottery_time,
                "sender_uid": lottery.sender_id
            }, f, indent=2)

    def write_all_users(self):
        file_path = self.output_path / "all_users.csv"
        if file_path.exists():
            return
        with open(file_path, "w", encoding="utf8") as f:
            self.write_to_file(f, chain(
                self.bilibili.get_all_repost_user(),
                self.bilibili.get_all_reply_user()
            ))

    def run(self):
        self.write_all_users()
        self.write_prize_users()
        self.write_prize_info()


if __name__ == "__main__":
    outputer = Outputer(399225516637381754)
    outputer.run()
