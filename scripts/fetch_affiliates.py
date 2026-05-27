"""
从短链管理 API 自动获取最新的推广链接
API: https://api.huanghaiwan.com/links/api/affiliates（公开接口，无需登录）

推广链接数据不提交到 GitHub（affiliate_cache.json 已加入 .gitignore）
运行时从 API 获取，缓存在本地
"""

import os
import json
import requests

API_URL = "https://api.huanghaiwan.com/links/api/affiliates"
CACHE_FILE = os.path.join("content", "affiliate_cache.json")


def fetch_from_api():
    """调用短链 API 获取推广链接"""
    try:
        resp = requests.get(API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success") and "items" in data:
            return data["items"]
        print(f"[Affiliate] API returned success=false or no items")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Affiliate] API fetch failed: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Affiliate] API response parse failed: {e}")
        return None


def parse_api_response(items):
    """
    将 API 返回的 items 转为内部标准格式
    API 字段 → 内部字段:
      alias       → dict key（名称）
      target_url  → url
      backup_url  → backup_url
      note        → note
      commission  → commission
      short_url   → short_url（推广用短链）
      click_count → click_count（用于排序，优先推广点击高的）
    """
    affiliates = {}
    for item in items:
        name = item.get("alias", "").strip()
        if not name:
            continue
        affiliates[name] = {
            "url": item.get("target_url", ""),
            "backup_url": item.get("backup_url", ""),
            "note": item.get("note", ""),
            "commission": item.get("commission", ""),
            "short_url": item.get("short_url", ""),
            "click_count": item.get("click_count", 0),
        }
    return affiliates


def save_cache(affiliates):
    """缓存到本地文件"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    data = {
        "fetched_at": __import__("datetime").datetime.now().isoformat(),
        "source": API_URL,
        "affiliates": affiliates,
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Affiliate] Cached {len(affiliates)} links to {CACHE_FILE}")


def load_cache():
    """从缓存读取"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("affiliates", {})
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def sort_by_click_count(affiliates):
    """按点击量排序，点击高的排在前面（优先推广）"""
    sorted_items = sorted(
        affiliates.items(),
        key=lambda x: x[1].get("click_count", 0),
        reverse=True,
    )
    return dict(sorted_items)


def get_affiliates(force_refresh=False):
    """
    获取推广链接（优先从 API 获取，失败时用缓存）
    返回: { "名称": {"url": "...", "backup_url": "...", "note": "...", "commission": "...", "short_url": "...", "click_count": N} }

    注意：返回的推广链接数据不提交到 GitHub，仅在运行时使用。
    """
    if force_refresh:
        items = fetch_from_api()
        if items:
            affiliates = parse_api_response(items)
            if affiliates:
                affiliates = sort_by_click_count(affiliates)
                save_cache(affiliates)
                return affiliates

    # 尝试从缓存读取
    cached = load_cache()
    if cached:
        print(f"[Affiliate] Using cached {len(cached)} links")
        return cached

    # 缓存也没有，远程抓取
    items = fetch_from_api()
    if items:
        affiliates = parse_api_response(items)
        if affiliates:
            affiliates = sort_by_click_count(affiliates)
            save_cache(affiliates)
            return affiliates

    print("[Affiliate] No links available")
    return {}


def extract_urls_to_text(affiliates):
    """把推广链接转成文本，供 prompt 使用"""
    lines = []
    for name, info in affiliates.items():
        url = info.get("url", "")
        note = info.get("note", "")
        commission = info.get("commission", "")
        short_url = info.get("short_url", "")
        click_count = info.get("click_count", 0)
        parts = [f"- {name}：{url}"]
        if note:
            parts.append(f"  ({note})")
        if commission:
            parts.append(f"  推广码：{commission}")
        if short_url:
            parts.append(f"  短链：{short_url}（点击{click_count}次）")
        lines.append("".join(parts))
    return "\n".join(lines)


if __name__ == "__main__":
    print("Fetching affiliates from API...")
    affiliates = get_affiliates(force_refresh=True)
    print(f"\nFound {len(affiliates)} affiliates (sorted by click count):")
    for name, info in affiliates.items():
        print(f"  {name}: clicks={info.get('click_count', 0)}")
        if info.get("url"):
            print(f"    url: {info['url']}")
        if info.get("commission"):
            print(f"    commission: {info['commission']}")
        if info.get("note"):
            print(f"    note: {info['note']}")
        if info.get("short_url"):
            print(f"    short: {info['short_url']}")
