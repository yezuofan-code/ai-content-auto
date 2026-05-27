"""
更新 README 内容索引
每次生成新内容后自动更新目录
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
                # 排除 generation_history.json
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

    content = '<p align="center">\n'
    content += '  <img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:1a1a2e,50:16213e,100:0f3460&text=Weekly%20Digest&fontAlign=50&fontAlignY=40&fontColor=ffffff"/>\n'
    content += '</p>\n\n'
    content += '<p align="center">\n'
    content += f"  \U0001f4c5 持续更新 · 已发布 {total} 篇内容\n"
    content += '</p>\n\n'
    content += '<p align="center">\n'

    if by_type:
        for t in sorted(by_type.keys()):
            name = type_display_name(t)
            count = type_counts.get(t, 0)
            content += f'  <a href="#{name}"><img src="https://img.shields.io/badge/{name}-{count}-2d3436?style=for-the-badge&labelColor=0f3460"/></a>\n'

    content += '</p>\n\n<br>\n\n---\n\n'

    if by_type:
        for t in sorted(by_type.keys()):
            name = type_display_name(t)
            count = type_counts.get(t, 0)
            content += f"## {name}\n\n"

            for a in by_type[t]:
                date_str = a["date"] if a["date"] else ""
                tags_str = a.get("tags", "")
                title_link = f"- [{a['title']}]({a['filepath']})"

                if date_str:
                    title_link += f" — {date_str}"

                if tags_str:
                    tag_list = [t.strip() for t in tags_str.split(",") if t.strip()]
                    if tag_list:
                        tags_html = " · ".join(tag_list)
                        title_link += f"  \n  <sub>{tags_html}</sub>"

                content += title_link + "\n"
            content += "\n"

    content += '---\n\n'
    content += '<p align="center">\n'
    content += '  <sub>内容持续更新中 · 欢迎 Star 收藏</sub>\n'
    content += '</p>\n'

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"READ README updated: {len(articles)} articles, {len(by_type)} categories")


def main():
    articles = scan_content()
    generate_readme(articles)


if __name__ == "__main__":
    main()
