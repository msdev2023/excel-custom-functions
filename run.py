import logging
import os
import traceback
from datetime import datetime

import requests

formatter = logging.Formatter(
    "[%(asctime)s] %(funcName)s:%(lineno)d %(levelname)s %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

WEIBO_UID = os.environ.get("WEIBO_UID")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

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
    logger.info(resp.status_code)
    data = resp.json()
    tweets = data["data"]["list"]

    latest_timestamp = None
    for tweet in tweets:
        try:
            content, created_at = parse_tweet(uid, tweet)
        except:
            logger.error(traceback.print_exc())
            continue

        if ts and created_at <= ts:
            break

        if not content:
            continue

        try:
            gh_create_issue(content[:16], content)
        except:
            logger.error(traceback.print_exc())
            continue

        if latest_timestamp is None or latest_timestamp < created_at:
            latest_timestamp = created_at

    return latest_timestamp


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
        except:
            logger.error(traceback.print_exc())

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
    logger.info(resp.status_code)
    data = resp.json()
    return data["data"]["longTextContent"]


def gh_create_issue(title, body):
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "title": title,
        "body": body,
    }
    resp = requests.post(url, data=data, headers=headers)
    logger.info(resp.status_code)


def gh_get_latest_timestamp():
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables/WEIBO_LATEST_TIMESTAMP"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(url, headers=headers)
    logger.info(resp.status_code)
    return resp.json()["value"]


def gh_update_latest_timestamp(ts):
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables/WEIBO_LATEST_TIMESTAMP"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "name": "WEIBO_LATEST_TIMESTAMP",
        "value": ts,
    }
    resp = requests.patch(url, data=data, headers=headers)
    logger.info(resp.status_code)


def main():
    ts = None
    try:
        ts = gh_get_latest_timestamp()
        ts = int(ts)
    except:
        logger.error(traceback.print_exc())

    latest_ts = start_request(WEIBO_UID, ts=ts)

    try:
        gh_update_latest_timestamp(latest_ts)
    except:
        logger.error(traceback.print_exc())


if __name__ == "__main__":
    main()
