from typing import List
from datetime import datetime

# from bilibili import Bilibili
from bana.network import get
from bana.utils import convert_json
from bana.model import Space


# 动态在 X 天里发送的
POST_IN_DAYS = 5


def get_ranking() -> List[int]:
    """
        获取原创榜单的所有up主
        统计所有投稿在 xx年y月z日 - xx年y月z+3日 的数据综合得分，每日更新一次
    """
    url = "https://api.bilibili.com/x/web-interface/ranking?rid=0&day=3&type=2&arc_type=0"
    data = convert_json(get(url, ext=".json").text)
    items = data["data"]["list"]
    return list(map(lambda x: x["mid"], items))


def get_all_user_space(ids: List[int]):
    for i, uid in enumerate(ids):
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
        data = convert_json(get(url, cache_dir="./cache/temp/").text)["data"]
        space = Space.from_json(data["cards"])
        now_timestamp = int(datetime.now().timestamp())
        # 动态必须是抽奖, 或者原始动态是抽奖
        # 且, 动态发送的时间必须是 X 天内发送的
        for card in space.cards:
            if card.origin and card.origin.timestamp > now_timestamp - POST_IN_DAYS * 60 * 60 * 24:
                if card.origin.lott_id:
                    print(card.origin.dynamic_id, card.origin.timestamp)
            if card.lott_id:
                print(card.dynamic_id, card.timestamp, "up主自己发的!!")


if __name__ == "__main__":
    uids = get_ranking()
    get_all_user_space(uids)
