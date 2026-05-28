"""
自动发帖到 X (Twitter)
每次生成文章后自动发布一条推文
需要安装 tweepy：pip install tweepy
"""

import os
import re

# Twitter API 配置（从环境变量读取）
API_KEY = os.environ.get("TWITTER_API_KEY", "")
API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

# 文章 GitHub 地址前缀
GITHUB_BASE = "https://github.com/yezuofan-code/weekly-digest/blob/main"


def post_tweet(text):
    """发推主入口"""
    if not API_KEY:
        print("  [X] TWITTER_API_KEY not set, skipping")
        return False

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
        )
        resp = client.create_tweet(text=text)
        if resp.data:
            tweet_id = resp.data["id"]
            print(f"  [X] Tweet posted: https://x.com/user/status/{tweet_id}")
            return True
    except ImportError:
        print("  [X] tweepy not installed, falling back to direct API")
        return _post_tweet_direct(text)
    except Exception as e:
        print(f"  [X] Tweet failed: {e}")
        return False

    return False


def _post_tweet_direct(text):
    """备用方案：直接用 requests 调用 API（不依赖 tweepy）"""
    try:
        from requests_oauthlib import OAuth1Session
        oauth = OAuth1Session(
            client_key=API_KEY,
            client_secret=API_SECRET,
            resource_owner_key=ACCESS_TOKEN,
            resource_owner_secret=ACCESS_SECRET,
        )
        resp = oauth.post(
            "https://api.twitter.com/2/tweets",
            json={"text": text},
        )
        if resp.status_code in (200, 201):
            print(f"  [X] Tweet posted successfully")
            return True
        else:
            print(f"  [X] Tweet failed: {resp.status_code} {resp.text[:200]}")
            return False
    except ImportError:
        print("  [X] requests_oauthlib not installed, cannot post")
        return False
    except Exception as e:
        print(f"  [X] Tweet failed: {e}")
        return False


def build_tweet_text(topic, article_path):
    """根据文章信息生成推文文案"""
    repo_path = article_path.replace("\\", "/")
    full_url = f"{GITHUB_BASE}/{repo_path}"

    # 根据内容类型生成不同提示
    type_hints = {
        "review": "长期用下来的一些真实感受，好坏都说了",
        "comparison": "几家放一起对比了一下，区别还挺明显的",
        "buying_guide": "总结了一些选购经验，怎么选、怎么避坑都写了",
        "ai_tutorial": "上手试了试，把完整过程记录了一下",
        "guide": "把配置过程整理了一下，一步步来的",
        "troubleshooting": "踩坑后整理的解决方案，遇到类似问题可以参考",
    }

    content_type = "guide"
    for t, hint in type_hints.items():
        if t in article_path.lower():
            content_type = t
            break

    hint = type_hints.get(content_type, "整理了一些经验")

    tweet = f"刚更新了一篇内容：{topic}\n\n自己{hint}，该踩的坑基本都踩了一遍，干脆写成文章了。\n有需要的可以看看，希望对你有帮助。\n\n{full_url}\n\n#网络加速 #经验分享"

    # 如果太长，缩短
    if len(tweet) > 280:
        tweet = f"{topic}\n\n自己{hint}，踩过的坑都写进文章了。\n\n{full_url}"

    # 还是太长，只保留核心
    if len(tweet) > 280:
        tweet = f"{topic}\n\n{full_url}"

    return tweet


if __name__ == "__main__":
    # 测试模式
    import json
    try:
        with open("content/generation_history.json", "r", encoding="utf-8") as f:
            hist = json.load(f)
        if hist:
            last = hist[-1]
            topic = last.get("topic", "?")
            fpath = last.get("file", "content/reviews/test.md")
            text = build_tweet_text(topic, fpath)
            print("=== Tweet Preview ===")
            print(text)
            print(f"\nLength: {len(text)} chars")
    except:
        print("No history found, using test text")
        text = build_tweet_text("测试文章", "content/guides/test.md")
        print(text)
