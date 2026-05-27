"""
推广信息库管理
维护每个推广服务商的详细信息（线路、价格、特点等），供文章生成时使用
"""

import os
import json

INFO_FILE = os.path.join("content", "affiliate_info.json")


def load_info():
    """加载推广信息库"""
    if not os.path.exists(INFO_FILE):
        return {}
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_info(data):
    """保存推广信息库"""
    os.makedirs(os.path.dirname(INFO_FILE), exist_ok=True)
    with open(INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_affiliate_info(name):
    """获取单个推广商的详细信息"""
    db = load_info()
    return db.get(name, {})


def get_all_info():
    """获取所有推广商的详细信息"""
    return load_info()


def format_info_for_prompt(affiliates, db=None):
    """
    把推广信息库格式化成文本，供 LLM prompt 使用
    affiliates: 从 API 获取的基础数据（含 url）
    db: 推广信息库（含详细描述）
    """
    if db is None:
        db = load_info()

    lines = []
    for name, info in affiliates.items():
        url = info.get("url", "")
        detail = db.get(name, {})

        parts = [f"【{name}】"]
        if url:
            parts.append(f"官网：{url}")

        # 线路信息
        lines_list = detail.get("lines", [])
        if lines_list:
            parts.append(f"线路：{'/'.join(lines_list)}")

        # 地区
        locs = detail.get("locations", [])
        if locs:
            parts.append(f"地区：{'/'.join(locs)}")

        # 优化线路
        opt = detail.get("optimized", [])
        if opt:
            parts.append(f"优化：{'/'.join(opt)}")

        # 价格
        pricing = detail.get("pricing", [])
        if pricing:
            price_strs = [f"{p.get('plan','')} {p.get('price','')} ({p.get('traffic','')}, {p.get('devices','')})" for p in pricing]
            parts.append(f"价格：{' | '.join(price_strs)}")

        # 特点
        features = detail.get("features", [])
        if features:
            parts.append(f"特点：{'/'.join(features)}")

        # 优缺点
        pros = detail.get("pros", [])
        cons = detail.get("cons", [])
        if pros:
            parts.append(f"优点：{'/'.join(pros)}")
        if cons:
            parts.append(f"缺点：{'/'.join(cons)}")

        # API 附注
        note = info.get("note", "")
        if note:
            parts.append(f"备注：{note}")

        lines.append(" | ".join(parts))

    return "\n".join(lines)


def build_affiliate_descriptions(affiliates, db=None):
    """
    生成简洁的推广商描述（单行），供文章自然植入
    返回：{ "名称": "一句话描述", ... }
    """
    if db is None:
        db = load_info()

    result = {}
    for name, info in affiliates.items():
        detail = db.get(name, {})
        lines_list = detail.get("lines", [])
        locs = detail.get("locations", [])
        pricing = detail.get("pricing", [])
        features = detail.get("features", [])

        desc_parts = []
        if lines_list:
            desc_parts.append('/'.join(lines_list))
        if locs:
            desc_parts.append(f"{len(locs)}个地区节点")
        if pricing:
            cheapest = pricing[0]
            desc_parts.append(f"起价{cheapest.get('price', '?')}")
        if features:
            desc_parts.append(features[0])

        note = info.get("note", "")
        if note and not desc_parts:
            desc_parts.append(note)

        result[name] = "，".join(desc_parts) if desc_parts else "暂无详细信息"

    return result


if __name__ == "__main__":
    import sys
    db = load_info()
    print(f"推广信息库：{len(db)} 条记录")
    for name, info in db.items():
        lines_list = info.get("lines", [])
        locs = info.get("locations", [])
        pricing = info.get("pricing", [])
        print(f"\n{name}")
        if lines_list:
            print(f"  线路：{'/'.join(lines_list)}")
        if locs:
            print(f"  地区：{'/'.join(locs)}")
        if pricing:
            for p in pricing:
                print(f"  {p.get('plan','')}: {p.get('price','')} ({p.get('traffic','')}, {p.get('devices','')})")
