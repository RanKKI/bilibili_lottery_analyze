import csv
import os
import sys

from typing import TextIO, Iterator
from pathlib import Path

from bana import Bilibili, Card
from conf import APP_DIR


class SaveRepost(object):

    def __init__(self, dynamic_id: int):
        self.dynamic_id = dynamic_id
        self.base_dir = Path(APP_DIR) / "output" / str(dynamic_id)
        self.bilibili = Bilibili(dynamic_id)
        if not self.base_dir.exists():
            os.makedirs(self.base_dir)

    def write_to_file(self, file_stream: TextIO, cards: Iterator[Card]):
        writer = csv.writer(file_stream, delimiter=",")
        if file_stream.tell() == 0:
            writer.writerow(["uid", "level", "vip_type", "vip_status", "timestamp"])
        for card in cards:
            user = card.user
            writer.writerow([user.uid, user.level, user.vip_type, user.vip_status, card.timestamp])

    def write(self):
        file_path = self.base_dir / "all_users.csv"
        with open(file_path, "a+", encoding="utf8") as f:
            self.write_to_file(f, self.bilibili.get_all_repost_user())


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print("Dynamic id needed")
        return
    try:
        dynamic_id = int(args[0])
    except ValueError:
        print("Dynamic id must be integer")
    else:
        SaveRepost(dynamic_id).write()
        print("Finished")


if __name__ == "__main__":
    main()
