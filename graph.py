import matplotlib.pyplot as plt
import pandas as pd
import json
import sys
import os

from pathlib import Path


class Graph(object):

    def __init__(self, dynamic_id: int):
        # setup matplot
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['figure.figsize'] = (12.0, 6.0)
        self.FILE_PATH = Path("output") / str(dynamic_id)
        if not self.FILE_PATH.exists():
            raise FileNotFoundError("You have to load data for that dynamic id first")
        # read lottery info
        with open(self.FILE_PATH / "prize_info.json") as f:
            lottery_info = json.load(f)
        self.start_time = lottery_info.get("start_time")
        self.end_time = lottery_info.get("end_time")
        self.sender_uid = lottery_info.get("sender_uid")
        self.df_prize_users = self.read("prize_users.csv")
        self.df_all_users = self.read("all_users.csv")

    def read(self, file_name: str) -> pd.DataFrame:
        df = pd.read_csv(self.FILE_PATH / file_name)
        # 过滤所有再抽奖之后发送的, 以及up主自己发的
        df = df.loc[df["timestamp"] <= self.end_time].loc[df["uid"] != self.sender_uid]
        # 当用户大会员过期，大会员类型还有可能是之前的状态, 所以将其设置成0, 如果大会员过期
        df.loc[df["vip_status"] == 0, "vip_type"] = 0
        df["time"] = df["timestamp"] - self.start_time
        del df["timestamp"]
        return df

    def gen_user_level_graph(self):
        fig, axes = plt.subplots(nrows=1, ncols=2)
        self.df_prize_users.level.value_counts().plot(kind="pie", ax=axes[0], title="Prize user level")
        self.df_all_users.level.value_counts().plot(kind="pie", ax=axes[1], title="ALl user level")
        plt.savefig(self.FILE_PATH / "user_level.png")

    def gen_vip_graph(self):
        fig, axes = plt.subplots(nrows=1, ncols=2)
        vip_status_data = pd.DataFrame({
            "prize": self.df_prize_users.vip_status.value_counts(),
            "all": self.df_all_users.vip_status.value_counts()
        })

        vip_type_data = pd.DataFrame({
            "prize": self.df_prize_users.vip_type.value_counts(),
            "all": self.df_all_users.vip_type.value_counts()
        })
        vip_status_data.plot(kind="bar", ax=axes[0], title="Vip status", secondary_y="all")
        vip_type_data.plot(kind="bar", ax=axes[1], title="Vip Type", secondary_y="all")

        plt.savefig(self.FILE_PATH / "vip.png")

    def gen_time_series(self):
        time = pd.DataFrame({
            "all": self.df_all_users["time"],
            "prize": self.df_prize_users["time"]
        })
        time[time <= time["prize"].quantile()].plot(kind="hist", bins=200, alpha=0.5, secondary_y="all")
        plt.show()

    def gen_all_graphs(self):
        self.gen_user_level_graph()
        self.gen_vip_graph()


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print("Dynamic id needed")
        print("You may select from")
        for _p in filter(lambda x: not x.startswith("."), os.listdir("./output")):
            print(f" - {_p}")
        return
    try:
        dynamic_id = int(args[0].strip("output/"))
    except ValueError:
        print("Dynamic id must be integer")
    else:
        graph = Graph(dynamic_id)
        # graph.gen_all_graphs()
        graph.gen_time_series()
        print("Finished")


if __name__ == "__main__":
    main()
