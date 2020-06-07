from bilibili import Bilibili


if __name__ == "__main__":
    bilibili = Bilibili(75347916, 254463269, 394000250829625700)
    bilibili.get_all_repost_user(_rand=True)
