
import matplotlib.pyplot as plt
import pandas as pd

prize_users = pd.read_csv("./prize_users.csv")
all_users = pd.read_csv("./all_other_users.csv")


# fig, axes = plt.subplots(nrows=1, ncols=2)

t = 5*60*60
pd.DataFrame({
    "prize": prize_users.time_after[prize_users.time_after < t] / 60 / 60,
    "all": all_users.time_after[all_users.time_after  < t] / 60 / 60
}).plot(kind="hist", secondary_y="all", bins=200, alpha=0.5)
plt.show()
