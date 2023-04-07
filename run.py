import os
from datetime import datetime

import requests
from ghapi.all import GhApi

WEIBO_UID = os.environ.get("WEIBO_UID")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE")
LATEST_TIMESTAMP = os.environ.get("WEIBO_LATEST_TIMESTAMP")
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
GITHUB_OWNER, GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY").split("/")
api = GhApi(owner=GITHUB_OWNER, repo=GITHUB_REPO, token=GITHUB_TOKEN)

session = requests.Session()
session.headers.update(
    {
        "authority": "weibo.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "client-version": "v2.40.22",
        "referer": f"https://weibo.com/u/{WEIBO_UID}",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "server-version": "v2023.04.04.2",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
)
cookies = WEIBO_COOKIE.split("; ")
for cookie in WEIBO_COOKIE.split():
    k, v = cookie.split("=", 1)
    session.cookies.set(k, v)


def start_request(uid, ts=None):
    url = f"https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1"
    resp = session.get(url)
    data = resp.json()
    tweets = data["data"]["list"]

    for tweet in tweets:
        try:
            content, created_at = parse_tweet(uid, tweet)
        except Exception as e:
            print(e)
            continue

        if ts and created_at <= ts:
            break

        try:
            api.issues.create(GITHUB_OWNER, GITHUB_REPO, content[:16], content)
        except Exception as e:
            print(e)


def parse_time(s):
    """
    Thu Apr 06 12:31:14 +0800 2023 => 1680755474
    """
    return int(datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y").timestamp())


def parse_tweet(uid, tweet):
    created_at = parse_time(tweet["created_at"])

    if "repost_type" in tweet:
        return None, created_at

    mblogid = tweet["mblogid"]
    content = tweet["text_raw"]
    if "continue_tag" in tweet and tweet["isLongText"]:
        try:
            long_url = f"https://weibo.com/ajax/statuses/longtext?id={mblogid}"
            content = retrieve_long_tweet(long_url)
        except Exception as e:
            print(e)

    content = content.replace("\u200b", "")
    pic_urls = [
        f"![](https://wx1.sinaimg.cn/orj960/{pic_id})"
        for pic_id in tweet.get("pic_ids", [])
    ]
    tweet_url = f"https://weibo.com/{uid}/{mblogid}"
    content += "\n" + "\n".join(pic_urls) + "\n\n" + tweet_url
    return content, created_at


def retrieve_long_tweet(url):
    resp = session.get(url)
    data = resp.json()
    return data["data"]["longTextContent"]


if __name__ == "__main__":
    start_request(WEIBO_UID)
