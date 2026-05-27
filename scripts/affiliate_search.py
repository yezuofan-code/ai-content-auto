"""
自动搜索推广商信息
当检测到新的推广商时，自动搜索其信息并填入数据库
使用 duckduckgo_search（免费，无需 API Key）+ DeepSeek 提取结构化数据
"""

import os
import json
import re

INFO_FILE = os.path.join("content", "affiliate_info.json")
CACHE_FILE = os.path.join("content", "affiliate_cache.json")

# ============================================================
# 检测新推广商
# ============================================================

def load_info_db():
    """加载现有推广信息库"""
    if not os.path.exists(INFO_FILE):
        return {}
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_affiliates():
    """加载 API 获取的推广列表"""
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("affiliates", {})


def find_new_affiliates():
    """找出信息库中完全不存在的推广商（已有记录的不再搜索）"""
    affs = load_affiliates()
    db = load_info_db()
    new_ones = {}
    for name, info in affs.items():
        if name == "Test" or not info.get("url", ""):
            continue
        if name not in db:  # 只要在库里就不管了
            new_ones[name] = info
    return new_ones


# ============================================================
# 搜索信息
# ============================================================

def search_affiliate_info(name, deepseek_api_key):
    """
    使用 DuckDuckGo 搜索 + DeepSeek 提取，获取推广商的结构化信息
    返回: dict {lines, locations, optimized, pricing, features, pros, cons}
    """
    # 先用 duckduckgo_search 搜索
    search_results = _search_web(name)
    if not search_results:
        print(f"  [AutoSearch] No search results for {name}")
        return _generate_basic_info(name)

    # 让 DeepSeek 从搜索结果中提取结构化信息
    info = _parse_with_deepseek(name, search_results, deepseek_api_key)
    if info:
        print(f"  [AutoSearch] Extracted info for {name}")
        return info

    return _generate_basic_info(name)


def _search_web(query):
    """使用 DuckDuckGo 搜索（免费，无需 API Key）"""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(f"{query} 机场 套餐 价格 线路", max_results=5):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                })
        if results:
            return results

        # 第二次搜索，换关键词
        with DDGS() as ddgs:
            for r in ddgs.text(f"{query} 价格 流量 节点", max_results=5):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                })
        return results if results else None
    except ImportError:
        print("  [AutoSearch] duckduckgo_search not installed, skipping web search")
        return None
    except Exception as e:
        print(f"  [AutoSearch] Search failed: {e}")
        return None


def _parse_with_deepseek(name, search_results, api_key):
    """用 DeepSeek 从搜索结果中提取结构化信息"""
    if not api_key:
        return None

    context = "\n".join([
        f"标题：{r['title']}\n内容：{r['body']}" for r in search_results[:3]
    ])

    prompt = f"""根据以下搜索结果，提取「{name}」网络加速服务的详细信息。

搜索结果：
{context}

请提取以下信息（如果没有找到明确信息就留空）：
1. 线路类型（如：IEPL专线、IPLC专线、中转、BGP等）
2. 覆盖地区（如：日本、新加坡、香港、美国等）
3. 优化的线路或地区
4. 价格方案（如月付多少钱、多少流量、年付优惠）
5. 核心特点（如：支持ChatGPT、解锁流媒体、晚高峰不限速等）
6. 优点
7. 缺点

以JSON格式输出，不要加其他说明：
{{
  "lines": ["线路1", "线路2"],
  "locations": ["地区1", "地区2"],
  "optimized": ["优化线路说明"],
  "pricing": [{{"plan": "月付", "price": "xx元/月", "traffic": "", "devices": ""}}],
  "features": ["特点1", "特点2"],
  "pros": ["优点1"],
  "cons": ["缺点1"]
}}
"""

    try:
        import requests
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "你是一个信息提取助手，从搜索结果中提取结构化信息。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]

        # 提取 JSON
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"  [AutoSearch] DeepSeek parse failed: {e}")

    return None


def _generate_basic_info(name):
    """当搜索失败时，生成一个基础信息模板"""
    return {
        "lines": [""],
        "locations": ["日本", "新加坡", "香港", "美国"],
        "optimized": [""],
        "pricing": [{"plan": "月付", "price": "", "traffic": "", "devices": ""}],
        "features": [""],
        "pros": [""],
        "cons": [""],
    }


# ============================================================
# 自动补充信息库
# ============================================================

def auto_fill_affiliates(deepseek_api_key=None):
    """
    自动检测并补充新推广商的信息
    返回补充的数量
    """
    new_ones = find_new_affiliates()
    if not new_ones:
        print("[AutoSearch] No new affiliates to research")
        return 0

    print(f"[AutoSearch] Found {len(new_ones)} new affiliates to research")
    db = load_info_db()
    filled = 0

    for name, info in new_ones.items():
        print(f"  Researching: {name}...")
        details = search_affiliate_info(name, deepseek_api_key)
        if details:
            db[name] = details
            filled += 1
            print(f"    -> Saved")

    if filled > 0:
        os.makedirs(os.path.dirname(INFO_FILE), exist_ok=True)
        with open(INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"[AutoSearch] Info database updated: {filled} new entries")

    return filled


if __name__ == "__main__":
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    count = auto_fill_affiliates(api_key)
    print(f"Done. {count} affiliates researched.")
