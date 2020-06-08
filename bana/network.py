import requests
import os
import hashlib

from unittest.mock import MagicMock

_req_get = requests.get


def get(url, *args, **kwargs):
    ext = kwargs.get("ext", ".html")
    cache_dir = kwargs.get("cache_dir", "./cache/")
    logging = kwargs.get("log", True)
    no_cache = kwargs.get("no_cache", False)

    if cache_dir[-1] != "/":
        cache_dir += "/"
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    file_name = cache_dir + hashlib.md5(url.encode("latin-1")).hexdigest() + ext

    if os.path.exists(file_name) and not no_cache:
        res = MagicMock(status_code=200, url=url)  # Mock Response
        if logging:
            print("loading from ", file_name)
        with open(file_name, "r", encoding="utf8") as f:
            res.text = f.read()
        return res

    if logging:
        print("requesting ", url)
        print("saving to", file_name)
    try:
        res = _req_get(url)
    except Exception:
        res = get(url)
    else:
        res.encoding = "utf8"
        with open(file_name, "w", encoding="utf8") as f:
            f.write(res.text)
    finally:
        return res
