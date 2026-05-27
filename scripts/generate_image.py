"""
图片生成脚本
调用 AI 绘图 API (gpt-image-2) 生成带中文文字的完整信息图
"""

import os
import re
import json
import time
import requests

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024

# AI 绘图 API 配置
IMAGE_API_URL = "https://ai.t8star.org/v1/images/generations"
IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "")
IMAGE_MODEL = "gpt-image-2"

# ============================================================
# 获取文章结构化数据
# ============================================================

def get_article_metadata(topic_info):
    """从 topic_info 中获取结构化数据，并提供默认降级"""
    metadata = topic_info.get("article_metadata", {})

    # 如果结构化数据为空，根据内容类型生成默认值
    if not metadata or not any(metadata.values()):
        return _default_metadata(topic_info)

    return metadata


def _default_metadata(topic_info):
    """根据内容类型生成默认的结构化数据"""
    content_type = topic_info["type"]
    topic = topic_info["topic"]

    defaults = {
        "buying_guide": {
            "key_points": ["明确自己的使用需求", "按预算筛选合适方案", "重点看稳定性和速度"],
            "steps": ["确定预算和使用场景", "对比不同价位的服务", "试用1-2家做决策"],
            "tips": ["不要只看价格要看综合体验", "先月付试用再考虑年付", "晚高峰测试最能看出水平"],
            "summary_items": ["需求决定选择", "性价比要算总账", "先试后买最稳妥"],
        },
        "review": {
            "key_points": ["长期使用后的真实感受", "与其他服务的对比分析", "优缺点都如实说明"],
            "steps": ["选择测试服务商", "在不同场景下测试", "记录使用体验和数据"],
            "tips": ["测试至少用一周", "记录具体数据更有说服力", "注意不同时段的表现差异"],
            "summary_items": ["如实分享优缺点", "给读者参考价值", "建议读者根据自己需求判断"],
        },
        "ai_tutorial": {
            "key_points": ["零基础也能上手", "每一步都有具体操作", "常见问题一并解决"],
            "steps": ["注册和准备工作", "基本设置和配置", "上手使用和调试"],
            "tips": ["先确认前提条件", "按步骤操作不要跳", "遇到问题看常见问题部分"],
            "summary_items": ["从零到一学会使用", "掌握核心功能", "能独立解决问题"],
        },
        "comparison": {
            "key_points": ["多维度横向对比", "价格、速度、稳定性", "不同需求不同推荐"],
            "steps": ["明确对比维度", "收集各方案数据", "按需求给出推荐"],
            "tips": ["对比维度要有实际意义", "不要只看价格", "适合的才是最好的"],
            "summary_items": ["综合对比见表格", "按需求选择最合适的", "性价比要综合考虑"],
        },
        "guide": {
            "key_points": ["手把手教学", "每一步都可操作", "避开常见坑"],
            "steps": ["准备工作要做好", "按步骤执行配置", "验证配置是否正确"],
            "tips": ["按顺序操作不要跳步", "注意版本差异", "备份原有配置"],
            "summary_items": ["按步骤操作就能完成", "遇到问题检查每一步", "配置完成记得验证"],
        },
        "troubleshooting": {
            "key_points": ["常见问题一览", "从简到繁排查", "预防措施同样重要"],
            "steps": ["确定问题类型", "按排查顺序检查", "执行解决方案"],
            "tips": ["先检查最简单的原因", "记录问题方便以后", "定期维护预防"],
            "summary_items": ["大部分问题可以自己解决", "排查要有顺序", "预防胜于修复"],
        },
    }

    return defaults.get(content_type, {
        "key_points": [topic[:20]],
        "steps": ["了解基本情况", "按需求选择方案", "上手使用"],
        "tips": ["多了解再决策", "先试用再付款", "有问题及时反馈"],
        "summary_items": ["做好功课再决策", "选择适合自己的", "有用的话收藏分享"],
    })


# ============================================================
# AI 生图（带文字）
# ============================================================

def generate_image_with_text(prompt, output_path, timeout=300):
    """
    调用 AI 绘图 API（异步模式）生成带文字的图片
    流程：提交任务 → 轮询结果 → 下载图片
    最多等待 timeout 秒（默认 5 分钟），超时或失败则放弃出图
    返回 True 表示成功
    """
    if not IMAGE_API_KEY:
        return False

    headers = {
        "Authorization": f"Bearer {IMAGE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}",
    }
    deadline = time.time() + timeout

    try:
        # 1) 提交异步任务
        async_url = f"{IMAGE_API_URL}?async=true"
        resp = requests.post(async_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        task_id = body.get("data")
        if not task_id:
            print(f"  [AI] No task_id in response: {body}")
            return False
        print(f"  [AI] Task submitted: {task_id}")

        # 2) 轮询任务结果
        poll_url = f"{IMAGE_API_URL.replace('/generations', '')}/tasks/{task_id}"
        while time.time() < deadline:
            time.sleep(5)
            poll_resp = requests.get(poll_url, headers=headers, timeout=15)
            poll_resp.raise_for_status()
            result = poll_resp.json()
            status = result.get("data", {}).get("status", "")
            if status == "SUCCESS":
                img_url = result["data"]["data"]["data"][0]["url"]
                remaining = max(int(deadline - time.time()), 10)
                with open(output_path, "wb") as f:
                    f.write(requests.get(img_url, timeout=remaining).content)
                print(f"  [AI] Image saved: {output_path}")
                return True
            elif status == "FAILURE":
                reason = result.get("data", {}).get("fail_reason", "unknown")
                print(f"  [AI] Task failed: {reason}")
                return False
            # else IN_PROGRESS → continue polling
            print(f"  [AI] Polling... status={status}")

        print(f"  [AI] Timeout after {timeout}s, task still processing")
        return False

    except Exception as e:
        print(f"  [AI] Image generation failed: {e}")
        return False


# ============================================================
# 构建各页面的 AI prompt
# ============================================================

def load_category_config_for_images(category_name="网络加速"):
    """通过环境变量加载品类配置"""
    config_json = os.environ.get(f"CATEGORY_CONFIG_{category_name}")
    if config_json:
        try:
            return json.loads(config_json)
        except json.JSONDecodeError:
            pass
    return {
        "image_style": "科技感、现代、网络拓扑示意图风格",
        "image_colors": "深蓝+紫色为主色调，搭配青色/金色点缀",
    }


def build_image_prompt(topic_info, metadata):
    """
    构建单张信息图 prompt
    利用 gpt-image-2 的强大能力，生成一张内容丰富、设计精美的信息图
    """
    topic = topic_info["topic"]
    content_type = topic_info["type"]
    desc = topic_info.get("description", "")
    key_points = metadata.get("key_points", [])
    steps = metadata.get("steps", [])
    tips = metadata.get("tips", [])
    summary_items = metadata.get("summary_items", [])

    type_labels = {
        "buying_guide": "选购指南",
        "review": "深度评测",
        "ai_tutorial": "AI教程",
        "comparison": "对比评测",
        "guide": "实用指南",
        "tutorial": "操作教程",
        "troubleshooting": "故障排查",
    }
    label = type_labels.get(content_type, "实用内容")

    # 提取文章关键元素用于 prompt
    kp_text = "、".join(key_points[:3])
    steps_text = " → ".join(steps[:3])
    tip_text = tips[0] if tips else ""

    # 加载品类配置（用于视觉风格）
    category_name = topic_info.get("category", "网络加速")
    cat_config = load_category_config_for_images(category_name)
    image_style = cat_config.get("image_style", "科技感、现代、网络拓扑示意图风格")
    image_colors = cat_config.get("image_colors", "深蓝+紫色为主色调，搭配青色/金色点缀")

    prompt = f"""请生成一张信息图，1024x1024，作为文章「{topic}」的头图。

这是一篇{label}类文章，{desc or f'主题是：{topic}'}。

设计要求：充分利用 gpt-image-2 的绘图能力，生成一张视觉丰富、内容充实的专业信息图。
需要包含以下元素：

1. **主标题**：醒目展示文章标题「{topic}」
2. **类型标签**：标记为「{label}」
3. **核心要点**：{kp_text}
4. **流程示意**：{steps_text}
5. **实用建议**：{tip_text}

视觉设计规范：
- 整体风格：{image_style}
- 布局：采用信息图/海报式布局，不同内容区域用卡片、圆角框或分隔线区分
- 配色：{image_colors}，渐变背景
- 图形元素：根据主题内容设计相关的信息图元素，如数据对比、流程图、示意图等
- 字体：中文文字用清晰的黑体风格，标题粗大醒目，正文纤细清晰
- 装饰：适当使用装饰元素增加视觉层次感
- 一定要充分利用画面空间，信息密度要高，不要留太多空白
- 所有中文文字必须清晰可读，文字和背景对比度要充足

这张图将放在文章最顶部作为头图，需要能吸引读者继续阅读。"""

    return prompt



# ============================================================
# 主入口
# ============================================================

def generate_images(topic_info, output_dir):
    """
    生成一张配图（AI 方案）
    利用 gpt-image-2 生成内容丰富的信息图
    返回图片文件路径列表
    """
    metadata = get_article_metadata(topic_info)
    os.makedirs(output_dir, exist_ok=True)

    image_files = []

    # AI 方案：生成一张丰富的头图
    prompt = build_image_prompt(topic_info, metadata)
    output_path = os.path.join(output_dir, "01_cover.png")

    if generate_image_with_text(prompt, output_path):
        image_files.append(output_path)
        print(f"  [Image] {output_path}")
    else:
        print(f"[Image] Failed to generate image for {topic_info['topic']}")

    print(f"[Image] Done! {len(image_files)} image(s)")
    return image_files
