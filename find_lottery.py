from typing import List
from datetime import datetime
from itertools import chain

from bana import BilibiliApi, Space


class FindLottery(object):

    def __init__(self):
        # 动态在 X 天里发送的
        self.POST_IN_DAYS = 10
        self.api = BilibiliApi()

    def get_ranking(self) -> List[int]:
        """
            获取原创榜单的所有up主
            统计所有投稿在 xx年y月z日 - xx年y月z+3日 的数据综合得分，每日更新一次
        """
        data = self.api.get_ranking(0, 3, 2, 0)
        return list(map(lambda x: x["mid"], data["data"]["list"]))

    def get_all_user_space(self, ids: List[int]):
        for uid in ids:
            data = self.api.get_user_space("ranking", uid, cache=False)
            yield Space.from_json(data["data"])

    def find(self, ids: List[int]):
        now_timestamp = int(datetime.now().timestamp())
        for card in chain.from_iterable(map(lambda x: x.cards, self.get_all_user_space(ids))):
            # 动态必须是抽奖, 或者原始动态是抽奖, 动态发送的时间必须是 X 天内发送的
            if card.origin and card.origin.timestamp > now_timestamp - self.POST_IN_DAYS * 60 * 60 * 24:
                if card.origin.lott:
                    print(card.origin.dynamic_id, card.origin.timestamp)
            if card.lott:
                print(card.dynamic_id, card.timestamp, "up主自己发的!!")


if __name__ == "__main__":
    finder = FindLottery()
    ids = finder.get_ranking()
    finder.find(ids)
