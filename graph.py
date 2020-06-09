
import matplotlib.pyplot as plt
import pandas as pd

PRIZE_USERS = pd.read_csv("./output/prize_users.csv")
ALL_USERS = pd.read_csv("./output/all_other_users.csv")


def draw_user_level():
    fig, axes = plt.subplots(nrows=1, ncols=2)
    PRIZE_USERS.level.value_counts().plot(kind="pie", ax=axes[0], title="Prize user level")
    ALL_USERS.level.value_counts().plot(kind="pie", ax=axes[1], title="ALl user level")
    plt.show()


def draw_vip():
    fig, axes = plt.subplots(nrows=1, ncols=2)
    vip_status_data = pd.DataFrame({
        "prize": PRIZE_USERS.vip_status.value_counts(),
        "all": ALL_USERS.vip_status.value_counts()
    })

    vip_type_data = pd.DataFrame({
        "prize": PRIZE_USERS.vip_type.value_counts(),
        "all": ALL_USERS.vip_type.value_counts()
    })
    vip_status_data.plot(kind="bar", ax=axes[0], title="Vip status", secondary_y="all")
    vip_type_data.plot(kind="bar", ax=axes[1], title="Vip Type", secondary_y="all")

    plt.show()


if __name__ == "__main__":
    draw_vip()
