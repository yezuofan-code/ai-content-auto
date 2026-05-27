#!/usr/bin/env python
"""
主入口脚本 - 智能内容生成
流程：
1. 从用户仓库自动拉取最新推广链接
2. 检查历史记录，避免内容重复
3. 生成本周内容（文章 + 结构化数据 + 配图）
4. 更新 README 索引
5. 记录历史
"""

import os
import sys
import json
import datetime

# 确保在项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ============================================================
# 步骤 0：环境准备
# ============================================================
GENERATE_DATE = datetime.date.today().isoformat()
os.environ["GENERATE_DATE"] = GENERATE_DATE

print("=" * 55)
print(f"  AI Content Auto Generator - {GENERATE_DATE}")
print("=" * 55)

# ============================================================
# 步骤 1：从源仓库获取最新推广链接
# ============================================================
print("\n[1/5] Fetching affiliate links from source repo...")
from scripts.fetch_affiliates import get_affiliates, extract_urls_to_text

affiliates = get_affiliates(force_refresh=True)
if affiliates:
    print(f"       ✓ {len(affiliates)} links loaded")
    os.environ["AFFILIATE_TEXT"] = extract_urls_to_text(affiliates)

    main_affiliate = list(affiliates.keys())[0] if affiliates else ""
    os.environ["MAIN_AFFILIATE"] = main_affiliate
else:
    print("       ⚠ No links available, will use built-in fallback")

# ============================================================
# 步骤 2：检查历史，确定本周内容
# ============================================================
print("\n[2/5] Checking content history...")
from scripts.config import get_current_topic, CONTENT_CALENDAR
from scripts.content_tracker import (
    is_duplicate,
    get_all_generated_topics,
    get_statistics,
    get_generation_count,
)

stats = get_statistics()
print(f"       Previous generations: {stats['total']}")
if stats["last_date"]:
    print(f"       Last generation: {stats['last_date']}")

topic_info = get_current_topic()
print(f"       Planned topic: {topic_info['topic']}")

# 检查是否和已有内容重复
duplicate_count = 0
max_attempts = len(CONTENT_CALENDAR)
for attempt in range(max_attempts):
    if is_duplicate(topic_info):
        duplicate_count += 1
        next_index = (topic_info["cycle_index"] + attempt) % topic_info["total_cycles"]
        topic_info = {
            **CONTENT_CALENDAR[next_index],
            "week_num": topic_info["week_num"],
            "cycle_index": next_index + 1,
            "total_cycles": topic_info["total_cycles"],
        }
        print(f"       ↻ Skipping duplicate, trying: {topic_info['topic']}")
    else:
        break

print(f"       ✓ Final topic: {topic_info['topic']}")

# ============================================================
# 步骤 3：生成文章（用最新的推广链接）
# ============================================================
print("\n[3/5] Generating article...")
from scripts.generate_content import main as gen_content, generate_content_fingerprint
from scripts.generate_image import generate_images

article_path = None
article_metadata = {}
fingerprint = ""

try:
    if affiliates:
        os.environ["AFFILIATE_LINKS_JSON"] = json.dumps(
            {k: {"url": v.get("url", ""), "backup_url": v.get("backup_url", ""),
                  "note": v.get("note", ""), "commission": v.get("commission", "")}
             for k, v in affiliates.items()}, ensure_ascii=False
        )

    result = gen_content(topic_info)
    if result:
        article_path, result_topic_info = result
        article_metadata = result_topic_info.get("article_metadata", {})
        topic_info = result_topic_info  # 包含结构化数据

        if article_path:
            print(f"       ✓ Article: {article_path}")
            # 从文章内容计算指纹（用于历史记录）
            try:
                with open(article_path, "r", encoding="utf-8") as f:
                    article_text = f.read()
                fingerprint = generate_content_fingerprint(article_text)
            except:
                pass
        else:
            print("       ⚠ Article generation returned empty")
    else:
        print("       ⚠ Article generation returned empty")
except Exception as e:
    print(f"       ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# 步骤 4：生成配图（使用结构化数据）
# ============================================================
print("\n[4/5] Generating images...")

image_dir = os.path.join("images", GENERATE_DATE)
image_files = []
try:
    image_files = generate_images(topic_info, image_dir)
    print(f"       ✓ {len(image_files)} images generated")
except Exception as e:
    print(f"       ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# 步骤 5：更新索引 + 记录历史
# ============================================================
print("\n[5/5] Updating index and recording history...")

from scripts.update_index import main as update_idx
try:
    update_idx()
    print("       ✓ README updated")
except Exception as e:
    print(f"       ✗ Failed: {e}")

from scripts.content_tracker import record_generation
if article_path:
    record_generation(topic_info, article_path, len(image_files), fingerprint=fingerprint)
    generated_topics = get_all_generated_topics()
    print(f"       ✓ History recorded ({len(generated_topics)} total)")

print("\n" + "=" * 55)
print("  ✅ COMPLETE")
if article_path:
    print(f"     Article: {article_path}")
print(f"     Images: {len(image_files)}")
print(f"     Total content pieces: {get_generation_count()}")
print("=" * 55)
