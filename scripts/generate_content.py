"""
内容生成脚本
调用 DeepSeek API 生成高质量、不重复的文章
推广链接从环境变量动态获取（由 run_all.py 从源仓库抓取）

升级：支持结构化数据输出，用于图片生成
"""

import os
import re
import json
import random
import datetime
import hashlib
import requests
from config import get_current_topic, get_output_filename, WRITING_STRATEGY

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

# ============================================================
# 内容类型标签映射（用于图片生成和 SEO）
# ============================================================
CONTENT_TYPE_TAGS = {
    "buying_guide": ["选购指南", "对比评测", "新手必看"],
    "review": ["深度评测", "真实体验", "长期使用"],
    "ai_tutorial": ["AI教程", "效率工具", "入门指南"],
    "comparison": ["横向对比", "性价比", "选购参考"],
    "guide": ["实用教程", "经验分享", "配置指南"],
    "tutorial": ["操作教程", "手把手", "入门"],
    "troubleshooting": ["故障排查", "常见问题", "实用技巧"],
}


def get_dynamic_affiliates():
    """从环境变量获取最新的推广链接（由 run_all.py 从源仓库抓取）"""
    json_str = os.environ.get("AFFILIATE_LINKS_JSON", "{}")
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def pick_style_variant(content_type):
    """
    根据内容类型和日期，选择不同的写作风格变体
    避免每周生成的模板感
    """
    week_seed = int(datetime.date.today().strftime("%Y%W"))
    rng = random.Random(week_seed * 7 + hash(content_type) % 1000)

    styles = {
        "buying_guide": [
            "分享式：以一个过来人的身份分享选购经验",
            "对比式：先分析不同需求的差异，再给建议",
            "踩坑式：从自己买错的经验出发，教你怎么避坑",
            "框架式：先给判断标准，再套用标准做推荐",
        ],
        "review": [
            "深度体验：详细描述使用几个月下来的真实感受",
            "对比评测：和同类竞品对比，分析各自的优劣势",
            "情景测试：在不同场景（晚高峰、看视频、下载等）测试表现",
        ],
        "ai_tutorial": [
            "新手友好：假设读者完全零基础，一步步教",
            "效率导向：聚焦怎么用 AI 工具提高工作效率",
            "问题驱动：从常见报错/问题出发，反向给出解决方案",
            "场景化：按使用场景（写作、编程、翻译）组织内容",
        ],
        "comparison": [
            "分层对比：按价格梯度分组对比",
            "需求匹配：按使用场景推荐最合适的",
            "数据驱动：用表格和参数说话",
        ],
        "guide": [
            "图文步骤：详细的操作步骤，带参数说明",
            "问题排查：从常见故障出发，反向教配置",
            "最佳实践：分享经过验证的最优配置方案",
        ],
        "troubleshooting": [
            "问题清单式：按问题分类，逐个给出解决方案",
            "流程图式：教用户怎么一步步排查",
            "经验总结式：从踩过的坑里提炼出通用解法",
        ],
    }

    variants = styles.get(content_type, ["常规写法"])
    return rng.choice(variants)


def load_category_config(category_name="网络加速"):
    """通过环境变量加载品类配置（子进程无法访问 Flask DB）"""
    config_json = os.environ.get(f"CATEGORY_CONFIG_{category_name}")
    if config_json:
        try:
            return json.loads(config_json)
        except json.JSONDecodeError:
            pass
    # 回退默认值
    return {
        "domain_description": "网络加速服务、外网访问、AI工具使用",
        "banned_words": ["翻墙", "梯子", "VPN", "科学上网", "富强"],
        "safe_alternatives": {
            "翻墙": "访问外网",
            "梯子": "网络加速工具",
            "VPN": "网络加速服务",
            "科学上网": "访问国际网络",
        },
        "image_style": "科技感、现代、网络拓扑示意图风格",
        "image_colors": "深蓝+紫色为主色调，搭配青色/金色点缀",
    }


def build_system_prompt(category_config=None):
    """构建系统提示词（每周微调，增加变化）"""
    week_seed = int(datetime.date.today().strftime("%Y%W"))
    rng = random.Random(week_seed)

    tone_options = [
        "像一个在 GitHub 上分享干货的技术博主",
        "像一个用了多年网络服务的资深用户",
        "像一个帮朋友挑选服务的耐心达人",
        "像一个踩过无数坑后总结经验的过来人",
        "像一个喜欢折腾工具的极客玩家",
    ]

    selected_tone = rng.choice(tone_options)

    if category_config is None:
        category_config = load_category_config()

    banned = "、".join(category_config.get("banned_words", ["翻墙", "梯子", "VPN", "科学上网"]))
    alt_map = category_config.get("safe_alternatives", {})
    alternatives = "；".join([f"{k}→{v}" for k, v in alt_map.items()]) if alt_map else "网络加速工具、网络服务商、国际网络环境、加速服务"

    return f"""你是一个中文技术内容作者。{selected_tone}。

你的写作核心原则：
1. 不说假话，不吹捧 — 每个推荐都同时列优缺点
2. 分享真实体验 — 用"我用了多久""我踩过什么坑"这种语气
3. 替读者省钱 — 主动劝先试用再付款，别冲动消费
4. 用表格展示结构化信息 — 价格、配置、对比都用表格
5. 口语化但不啰嗦 — 每段3-5句话，不要太长
6. 多用具体细节 — 具体数字、具体时间、具体场景，不要空泛的描述
7. 开头要抓人 — 用一个读者有共鸣的问题或场景引入

绝对禁止的词：{banned}
替代方案：{alternatives}"""


def build_type_specific_guide(content_type):
    """针对不同类型的内容，给出更具体的写作指引"""
    guides = {
        "buying_guide": """
【选购指南类特别要求】
- 先给出判断标准/框架，再推荐具体服务
- 每个推荐都要说明"适合什么样的人"和"不适合什么样的人"
- 列出价格、速度、稳定性等关键维度的对比
- 帮助读者根据自己的预算和需求做决策""",

        "review": """
【评测类特别要求】
- 说明使用时长（如"用了3个月"），增加可信度
- 具体说明测试环境（宽带类型、时间段、设备）
- 优缺点都要具体，不要笼统说"快"或"稳"
- 可以和其他用过的服务做对比""",

        "ai_tutorial": """
【AI教程类特别要求】
- 步骤要可操作：读者不需要额外搜索就能跟着做
- 包含具体的提示词示例或操作截图描述
- 说明需要什么前提条件（账号、网络等）
- 给出实际应用场景，不教条""",

        "comparison": """
【对比类特别要求】
- 对比维度要有实际参考价值（价格、速度、稳定性等）
- 用表格呈现对比数据
- 按不同需求给出推荐（"如果你……推荐……"）
- 给出性价比分析""",

        "guide": """
【指南类特别要求】
- 步骤清晰，可执行
- 包含具体的配置参数或设置
- 说明常见错误和注意事项
- 适合新手跟着操作""",

        "troubleshooting": """
【故障排查类特别要求】
- 按问题分类组织
- 每个问题给出从简到繁的排查步骤
- 说明问题产生的原因（不只会修还要懂原理）
- 包含预防措施""",
    }
    return guides.get(content_type, "")


def build_article_prompt(topic_info, category_config=None):
    """构建文章 prompt（根据内容类型、风格变体、推广信息、结构化数据要求）"""
    topic = topic_info["topic"]
    content_type = topic_info["type"]
    description = topic_info.get("description", "")
    style_variant = pick_style_variant(content_type)
    type_guide = build_type_specific_guide(content_type)

    # 加载品类配置
    if category_config is None:
        category_name = topic_info.get("category", "网络加速")
        category_config = load_category_config(category_name)

    # 获取推广链接（按品类过滤）
    affiliates = get_dynamic_affiliates()
    topic_category = topic_info.get("category", "")
    if topic_category:
        affiliates = {k: v for k, v in affiliates.items()
                      if v.get("category", "网络加速") == topic_category}
    aff_list = list(affiliates.items())
    rng = random.Random(hash(topic) % 10000)

    # 获取内容类型标签
    tags = CONTENT_TYPE_TAGS.get(content_type, ["教程"])
    tags_str = ", ".join(tags)

    prompt = f"""请写一篇中文文章。

【主题】{topic}
【内容类型】{content_type}
【重点】{description}
【写作风格】{style_variant}
【标签】{tags_str}

=== 写作要求 ===

【结构要求】
- 标题自拟（吸引人、含关键词，但不夸张不标题党）
- 开头：用一个问题或场景引入，让读者觉得"这说的就是我"
- 正文：3-5个小标题分段，每段有干货
- 结尾：总结核心观点 + 互动引导（收藏/评论）
- 全文 2000-3000 字

【质量要求】
- 每段都要有实际信息量，不要凑字数
- 如果是教程：步骤要清晰，读者能跟着做
- 如果是推荐：每个推荐都要有具体的优缺点
- 如果是对比：对比维度要有实际参考价值
- 多用具体数字和时间（"用了3个月""每天都会用""月付30元"）

【格式】
- Markdown 格式
- 对比/参数信息用表格
- 重要内容用 **加粗**
- 适量 emoji（每段1个左右，不要刷屏）
"""

    prompt += type_guide

    # 如果内容类型适合植入推广
    if content_type in ("review", "comparison", "buying_guide", "guide"):
        # 加载推广信息库
        aff_db = {}
        try:
            import json as _json
            with open("content/affiliate_info.json", "r", encoding="utf-8") as _f:
                aff_db = _json.load(_f)
        except:
            pass

        from scripts.affiliate_db import format_info_for_prompt, build_affiliate_descriptions
        info_text = format_info_for_prompt(affiliates, aff_db) if affiliates else ""
        descs = build_affiliate_descriptions(affiliates, aff_db) if affiliates else {}

        prompt += f"""
【推广信息库（以下服务商的详细信息，供写作参考）】

"""
        if info_text:
            prompt += info_text + "\n"

        if descs:
            prompt += "【一句话描述】\n"
            for name, desc in descs.items():
                prompt += f"- {name}：{desc}\n"

        prompt += """
【推广植入原则】
- 推荐类文章可以自然提及1-2家作为例子
- 用"我目前在用""朋友推荐"这种自然语气
- 不要硬广，不要大段宣传，不要全部列出来
- 如果是纯教程/技术类内容，不需要放任何推广
- 推广链接要真实，不要虚构不存在的服务商
"""

    # ============================================================
    # 要求输出结构化数据（用于图片生成）
    # ============================================================
    prompt += """

=== 重要：请在文章末尾输出结构化数据 ===

在文章写完后，在最后加上一个 HTML 注释块，包含以下信息（不要省略，这将用于配图生成）：

<!-- article-data
key_points: 文章的核心要点，用 | 分隔，3-5条
steps: 文章中的步骤或行动建议，用 | 分隔，3-5条
tips: 文章的实用技巧或提醒，用 | 分隔，3-5条
summary_items: 文章的总结点，用 | 分隔，3-5条
-->

示例格式（请替换为你文章的实际内容）：
<!-- article-data
key_points: 第1个核心要点|第2个核心要点|第3个核心要点
steps: 第一步做什么|第二步做什么|第三步做什么
tips: 第1个实用技巧|第2个实用技巧|第3个实用技巧
summary_items: 第1个总结点|第2个总结点|第3个总结点
-->

注意：这个数据块要在文章内容之后，图片引用之前。每条用 | 分隔，不要用其他符号。
"""

    prompt += "\n请直接输出文章。不要加额外说明。"

    return prompt


def parse_article_metadata(content):
    """
    从文章内容中解析结构化数据
    返回 dict，包含 key_points, steps, tips, summary_items
    """
    metadata = {
        "key_points": [],
        "steps": [],
        "tips": [],
        "summary_items": [],
    }

    # 匹配 <!-- article-data ... --> 块
    pattern = r"<!--\s*article-data\s*\n(.*?)-->"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        # 尝试匹配单行格式
        pattern2 = r"<!--\s*article-data\s+(.*?)-->"
        match = re.search(pattern2, content, re.DOTALL)

    if match:
        data_block = match.group(1).strip()
        # 解析每一行
        for line in data_block.split("\n"):
            line = line.strip()
            for key in metadata.keys():
                prefix = f"{key}:"
                if line.startswith(prefix):
                    value = line[len(prefix):].strip()
                    # 用 | 分割
                    items = [item.strip() for item in value.split("|") if item.strip()]
                    metadata[key] = items
                    break

    return metadata


def call_deepseek(prompt, system_prompt=None, category_config=None):
    """调用 DeepSeek API"""
    if system_prompt is None:
        system_prompt = build_system_prompt(category_config)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.75,
        "max_tokens": 6000,
    }

    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content
    except requests.exceptions.RequestException as e:
        print(f"[API Error] {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"  Response: {e.response.text[:500]}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"[Parse Error] {e}")
        return None


def check_and_replace_sensitive(text):
    """检查并替换敏感词"""
    for old, new in WRITING_STRATEGY["safe_alternatives"].items():
        text = text.replace(old, new)
    return text


def generate_content_fingerprint(text):
    """生成内容指纹，用于检测相似度"""
    normalized = re.sub(r'\s+', '', text[:500])
    return hashlib.md5(normalized.encode()).hexdigest()


def inject_affiliate_links(content, topic_info):
    """
    给文章中提到的服务商名加上推广链接
    只对推荐/对比类的文章注入，教程类不注入
    只注入与当前话题品类匹配的推广链接
    """
    content_type = topic_info["type"]
    if content_type not in ("review", "comparison", "buying_guide", "guide"):
        return content

    affiliates = get_dynamic_affiliates()
    if not affiliates:
        return content

    # 按品类过滤（如果话题指定了品类）
    topic_category = topic_info.get("category", "")
    if topic_category:
        affiliates = {k: v for k, v in affiliates.items()
                      if v.get("category", "网络加速") == topic_category}
    if not affiliates:
        return content

    # 按名称长度倒序排列（先匹配长的名字）
    sorted_affs = sorted(affiliates.items(), key=lambda x: len(x[0]), reverse=True)

    for name, info in sorted_affs:
        url = info.get("url", "")
        if not url:
            continue

        # 跳过已经在链接里的文本
        pattern = re.compile(
            r'(?<!\()'          # 不在已有链接的 ( 后面
            rf'(?<![\[\(\"/])'   # 不在已有链接、引号或 URL 路径后面
            rf'{re.escape(name)}'
            r'(?!\])'           # 不在链接文本 ] 前面
            r'(?!\s*\]\s*\()',  # 不在 [名称]( 结构中
            re.UNICODE
        )

        replacement = f'[{name}](https://api.huanghaiwan.com/go/{name})'
        content = pattern.sub(replacement, content)

    return content


def save_article(content, topic_info):
    """保存文章到文件，同时解析结构化数据"""
    filename = get_output_filename(topic_info)
    content_type = topic_info["type"]

    type_to_dir = {
        "buying_guide": "buying_guides",
        "review": "reviews",
        "ai_tutorial": "ai_tutorials",
        "comparison": "comparisons",
        "guide": "guides",
        "tutorial": "tutorials",
        "troubleshooting": "troubleshooting",
    }
    subdir = type_to_dir.get(content_type, "others")

    output_dir = os.path.join("content", subdir)
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"{filename}.md")

    # 计算指纹
    fingerprint = generate_content_fingerprint(content)

    # 获取标签
    tags = CONTENT_TYPE_TAGS.get(content_type, ["教程"])
    tags_str = ", ".join(tags)

    # 用 HTML 注释隐藏元信息（不会在页面显示）
    front_matter = f"""<!--
title: {topic_info['topic']}
date: {os.environ.get('GENERATE_DATE', '')}
type: {content_type}
week: {topic_info['week_num']}
style: {pick_style_variant(content_type)}
fingerprint: {fingerprint}
tags: {tags_str}
-->

"""
    # 注入推广链接
    content_with_links = inject_affiliate_links(content, topic_info)

    # 在文章顶部加上头图 + 元信息
    date_str = os.environ.get('GENERATE_DATE', '')
    image_header = f"""
<div align="center">
  <img src="../../images/{date_str}/01_cover.png" width="85%" />
  <br><sub>{date_str} · {tags_str}</sub>
</div>

<br>
"""
    full_content = front_matter + image_header + content_with_links

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"[Article] Saved: {filepath}")
    return filepath


def generate_sample(topic_info):
    """无 API Key 时的示例文章"""
    topic = topic_info["topic"]
    content_type = topic_info["type"]
    style = pick_style_variant(content_type)
    date_str = datetime.date.today().isoformat()

    # 为示例文章生成结构化数据
    tags = CONTENT_TYPE_TAGS.get(content_type, ["教程"])
    tags_str = ", ".join(tags)

    sample = f"""# {topic}

> 发布日期：{date_str} | 本文为示例内容（未配置 API Key）

## 为什么写这篇

最近总有朋友问我同样的问题：{topic_info.get('description', '')}

我刚开始也是一头雾水，花了些时间研究、试用，踩了不少坑。
这篇把我学到的东西整理出来，希望能帮你少走弯路。

## 我的判断标准

先说说我是怎么衡量一个服务好不好的：

### 1. 稳定性是第一位的

白天能用不算什么，**晚高峰才是试金石**。
我一般会选在工作日晚上 8-10 点测试，这个时段最能看出真实水平。

### 2. 性价比要算总账

不要只看月付价格，要看包含了什么：
- 多少流量
- 多少接入点
- 什么线路类型
- 支持几个设备同时用

### 3. 售后服务很重要

出问题的时候能找到人、能及时解决，这点很关键。
有 TG 群且响应快的，会比只能发工单的省心很多。

## 常见误区

### ❌ 越贵越好
不一定。贵的可能有更好的线路，但不一定适合你的使用场景。
如果你只是刷刷网页看看视频，中档的完全够用。

### ❌ 越便宜越划算
便宜的往往人多拥堵，体验很差。
而且便宜的容易跑路，售后也没保障。

### ❌ 一家就够了
建议至少准备 **主力 + 备用** 两家。
万一哪天主力出问题了，备用顶上，不影响使用。

## {style}

> 按照上面说的标准，结合我自己的使用经验：

**主力推荐方向：**
- 稳定性优先，宁可多花一点也要稳
- 接入点覆盖主流区域
- 有良好的售后支持

**备用推荐方向：**
- 价格实惠
- 做补充使用
- 和主力不同的线路，增加冗余

## 总结

选服务最重要的是**先搞清楚自己的需求**：

| 场景 | 关注重点 | 预算建议 |
|------|---------|---------|
| 日常网页浏览 | 稳定性 | 低-中 |
| 看视频/流媒体 | 速度 + 解锁能力 | 中 |
| 使用 AI 工具 | 稳定性 + 延迟 | 中-高 |
| 下载大文件 | 速度 + 流量 | 中 |

希望这篇对你有帮助。有用的话收藏一下，以后需要的时候方便找。

<!-- article-data
key_points: 先搞清楚需求再选|稳定性比速度更重要|不要只看价格要看综合性价比|建议主力+备用双保险|先试用再付款别冲动
steps: 明确自己的使用场景和预算|按五大维度筛选服务商|试用1-2家对比体验|确定主力并准备备用方案|定期评估是否需要调整
tips: 晚高峰测试最能看出真实水平|便宜的容易拥堵和跑路|先月付试用再考虑年付|至少准备两家防止断网
summary_items: 需求决定选择|稳定性优先|性价比要算总账|先试后买最稳妥|备用方案不可少
-->
"""
    sample = check_and_replace_sensitive(sample)
    return sample


def main(topic_info=None):
    """
    主函数
    返回: (filepath, metadata_dict) 或 None
    """
    if topic_info is None:
        topic_info = get_current_topic()
    print(f"\nTopic: {topic_info['topic']}")
    print(f"Type: {topic_info['type']} | Week: {topic_info['week_num']}")
    print(f"Style: {pick_style_variant(topic_info['type'])}")

    # 加载品类配置
    category_name = topic_info.get("category", "网络加速")
    category_config = load_category_config(category_name)
    if category_name != "网络加速":
        print(f"Category: {category_name}")

    article_metadata = {}

    if not DEEPSEEK_API_KEY:
        print("[Warning] No DEEPSEEK_API_KEY set, generating sample article")
        content = generate_sample(topic_info)
        article_metadata = parse_article_metadata(content)
    else:
        prompt = build_article_prompt(topic_info, category_config)
        print("[API] Calling DeepSeek...")
        content = call_deepseek(prompt, category_config=category_config)
        if content is None:
            print("[Error] API call failed, using fallback")
            content = generate_sample(topic_info)
        else:
            print(f"[API] Success! {len(content)} chars")
            # 解析结构化数据
            article_metadata = parse_article_metadata(content)
            print(f"      Metadata: {len(article_metadata.get('key_points', []))} key points, "
                  f"{len(article_metadata.get('steps', []))} steps, "
                  f"{len(article_metadata.get('tips', []))} tips, "
                  f"{len(article_metadata.get('summary_items', []))} summary items")

    content = check_and_replace_sensitive(content)
    filepath = save_article(content, topic_info)

    # 把结构化数据加到 topic_info 中返回
    result_topic_info = dict(topic_info)
    result_topic_info["article_metadata"] = article_metadata

    print(f"[Done] Output: {filepath}")
    return filepath, result_topic_info


if __name__ == "__main__":
    result = main()
    if result:
        filepath, info = result
        print(f"\nMetadata extracted:")
        for k, v in info.get("article_metadata", {}).items():
            print(f"  {k}: {v}")
