"""
内容历史追踪器
记录每次生成的内容，避免重复，保证质量

升级：Jaccard 相似度 + 内容指纹比对
"""

import os
import json
import datetime
import hashlib
import re

HISTORY_FILE = os.path.join("content", "generation_history.json")


def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """保存历史记录"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def record_generation(topic_info, article_path, image_count, fingerprint=""):
    """记录一次内容生成"""
    history = load_history()

    record = {
        "date": datetime.date.today().isoformat(),
        "week_num": topic_info["week_num"],
        "topic": topic_info["topic"],
        "type": topic_info["type"],
        "article_path": article_path,
        "image_count": image_count,
        "cycle_index": topic_info["cycle_index"],
        "fingerprint": fingerprint,
    }

    history.append(record)
    save_history(history)
    print(f"[History] Recorded: {topic_info['topic']}")
    return record


def get_last_generation():
    """获取上次生成的内容"""
    history = load_history()
    if not history:
        return None
    return history[-1]


def get_recent_topics(weeks_back=8):
    """获取最近几周生成过的主题"""
    history = load_history()
    if not history:
        return []

    cutoff = datetime.date.today() - datetime.timedelta(weeks=weeks_back)
    recent = [r for r in history if r["date"] >= cutoff.isoformat()]
    return recent  # 返回完整记录，不止标题


def get_all_generated_topics():
    """获取所有已经生成过的主题"""
    history = load_history()
    return [r["topic"] for r in history]


def tokenize(text):
    """将中文文本分词（按非字母数字字符分割）"""
    # 对于中文，按字分割太细，按词分割太复杂
    # 这里用简单方法：提取所有中文字词（2-4字组合）和英文单词
    text = text.lower()
    # 提取英文单词
    eng_words = set(re.findall(r'[a-z]+', text))
    # 提取中文词组（连续的汉字）
    cjk_chars = re.findall(r'[一-鿿]+', text)
    cjk_words = set()
    for chunk in cjk_chars:
        # 对连续中文，按2字滑动窗口提取bigram作为特征词
        if len(chunk) >= 2:
            for i in range(len(chunk) - 1):
                cjk_words.add(chunk[i:i+2])
        # 也保留完整词组
        if len(chunk) <= 6:
            cjk_words.add(chunk)
        else:
            # 过长的词组截取前4字和后2字
            cjk_words.add(chunk[:4])
            cjk_words.add(chunk[-2:])
    return eng_words | cjk_words


def jaccard_similarity(set1, set2):
    """计算 Jaccard 相似度"""
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def is_duplicate(topic_info):
    """
    检查是否和近期内容重复
    使用 Jaccard 相似度 + 内容指纹比对
    """
    topic = topic_info["topic"]
    recent_records = get_recent_topics(weeks_back=8)
    recent_topics = [r["topic"] for r in recent_records]
    recent_fingerprints = [r.get("fingerprint", "") for r in recent_records if r.get("fingerprint")]

    # 精确匹配
    if topic in recent_topics:
        print(f"[Warning] Exact duplicate: {topic}")
        return True

    # Jaccard 相似度匹配
    topic_tokens = tokenize(topic)
    for recent in recent_topics:
        recent_tokens = tokenize(recent)
        similarity = jaccard_similarity(topic_tokens, recent_tokens)
        if similarity >= 0.35:
            print(f"[Warning] Similar topic ({similarity:.0%}): {recent}")
            print(f"          Overlap: {topic_tokens & recent_tokens}")
            return True

    return False


def check_fingerprint_duplicate(new_fingerprint, weeks_back=8):
    """检查内容指纹是否与近期内容重复"""
    if not new_fingerprint:
        return False

    recent_records = get_recent_topics(weeks_back=weeks_back)
    for r in recent_records:
        existing_fp = r.get("fingerprint", "")
        if existing_fp and existing_fp == new_fingerprint:
            print(f"[Warning] Duplicate fingerprint: {r['topic']}")
            return True
    return False


def get_generation_count():
    """获取已生成的总次数"""
    return len(load_history())


def get_statistics():
    """获取统计信息"""
    history = load_history()
    stats = {
        "total": len(history),
        "by_type": {},
        "last_date": None,
        "topics": [],
    }

    for r in history:
        t = r.get("type", "unknown")
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    if history:
        stats["last_date"] = history[-1]["date"]
        stats["topics"] = [r["topic"] for r in history[-4:]]

    return stats


if __name__ == "__main__":
    stats = get_statistics()
    print(f"Total generations: {stats['total']}")
    print(f"By type: {stats['by_type']}")
    if stats["last_date"]:
        print(f"Last: {stats['last_date']}")
