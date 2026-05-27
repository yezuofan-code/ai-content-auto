"""
更新 README 内容索引
每次生成新内容后自动更新目录
升级：按分类展示 + 标签导航 + SEO 关键词
"""

import os
import datetime
import re


def scan_content():
    """扫描所有已生成的内容"""
    articles = []
    content_dir = "content"
    if not os.path.exists(content_dir):
        return articles

    for root, dirs, files in os.walk(content_dir):
        for f in files:
            if f.endswith(".md"):
                filepath = os.path.join(root, f)
                rel_path = os.path.relpath(filepath, ".").replace("\\", "/")
                # 排除 generation_history.json 和 affiliate_cache.json
                if "generation_history" in rel_path or "affiliate_cache" in rel_path:
                    continue
                # 读取 front matter
                title = f.replace(".md", "")
                date = ""
                article_type = root.split(os.sep)[-1].rstrip("s") if os.sep in root else "other"
                tags = ""
                with open(filepath, "r", encoding="utf-8") as fh:
                    first_line = fh.readline().strip()
                    if first_line == "<!--":
                        for _ in range(10):
                            line = fh.readline().strip()
                            if line == "-->":
                                break
                            if line.startswith("title:"):
                                title = line.replace("title:", "").strip()
                            elif line.startswith("date:"):
                                date = line.replace("date:", "").strip()
                            elif line.startswith("tags:"):
                                tags = line.replace("tags:", "").strip()
                articles.append({
                    "title": title,
                    "filepath": rel_path,
                    "date": date,
                    "type": article_type,
                    "tags": tags,
                })
    return articles


def type_display_name(t):
    """类型展示名称"""
    names = {
        "buying_guide": "选购指南",
        "review": "深度评测",
        "ai_tutorial": "AI 教程",
        "comparison": "对比评测",
        "guide": "实用指南",
        "tutorial": "操作教程",
        "troubleshooting": "故障排查",
    }
    return names.get(t, t)


def generate_readme(articles):
    """生成 README 内容索引（按分类展示）"""
    today = datetime.date.today().isoformat()
    total = len(articles)

    # 按类型分组
    by_type = {}
    for a in articles:
        t = a["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(a)

    # 按日期降序排列（每组内）
    for t in by_type:
        by_type[t].sort(key=lambda x: x["date"], reverse=True)

    # 计算各类型的数量
    type_counts = {t: len(items) for t, items in by_type.items()}

    content = f"""# 网络加速服务选购与 AI 工具使用指南

📅 持续更新 · 已发布 {total} 篇内容

> 分享我真实使用过的网络加速服务评测和 AI 工具教程。
> 所有内容均为个人真实体验，优缺点都会如实说明。

---

## 📋 快速导航

"""

    if by_type:
        # 生成导航链接
        nav_items = []
        for t in sorted(by_type.keys()):
            name = type_display_name(t)
            anchor = f"分类-{name}"
            count = type_counts.get(t, 0)
            nav_items.append(f"[{name}（{count}篇）](#{anchor})")
        content += " | ".join(nav_items) + "\n\n---\n\n"
    else:
        content += "> 内容整理中，请稍后查看...\n\n"
        content += "---\n\n"

    if by_type:
        # 按分类展示
        for t in sorted(by_type.keys()):
            name = type_display_name(t)
            count = type_counts.get(t, 0)
            content += f"## 📂 {name} <a id=\"分类-{name}\"></a>\n\n"
            content += f"> 共 {count} 篇\n\n"

            for a in by_type[t]:
                date_str = a["date"] if a["date"] else ""
                tags_str = a.get("tags", "")
                title_link = f"- [{a['title']}]({a['filepath']})"

                if date_str:
                    title_link += f" — {date_str}"

                if tags_str:
                    # 添加标签作为小字
                    tag_list = [t.strip() for t in tags_str.split(",") if t.strip()]
                    if tag_list:
                        tags_html = " · ".join(tag_list)
                        title_link += f"  \n  <sub>{tags_html}</sub>"

                content += title_link + "\n"
            content += "\n"

    content += """---

## 📌 说明

- 所有内容均为个人真实使用体验分享
- 推荐的服务商均列明优缺点，不构成购买建议
- 建议先试用再决定是否付费

## ⭐ 收藏

如果内容对你有帮助，欢迎 **Star** 收藏，方便以后查找。
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ README 已更新，共 {len(articles)} 篇文章，{len(by_type)} 个分类")


def main():
    articles = scan_content()
    generate_readme(articles)


if __name__ == "__main__":
    main()
