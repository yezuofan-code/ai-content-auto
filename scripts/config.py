"""
内容日历配置
推广链接改为运行时从 API 获取（scripts/fetch_affiliates.py）
"""

import datetime
import os

# ============================================================
# 内容日历（每日更新，30天不重复）
# 混搭类型：选购指南、深度评测、AI教程、经验分享、技巧、对比
# ============================================================
CONTENT_CALENDAR = [
    {
        "type": "buying_guide",
        "topic": "2026年网络加速服务选购指南：教你找到最适合自己的",
        "style": "guide",
        "description": "框架性内容，教用户怎么判断好坏",
        "image_label": "guide",
    },
    {
        "type": "buying_guide",
        "topic": "月付10元 vs 月付50元：不同价位的网络加速差别有多大",
        "style": "comparison",
        "description": "价格分层对比，帮助用户找到预算内的最佳选择",
        "image_label": "budget",
    },
    {
        "type": "buying_guide",
        "topic": "学生党怎么选网络加速服务？预算有限也能用好",
        "style": "guide",
        "description": "针对学生群体的推荐",
        "image_label": "budget",
    },
    {
        "type": "buying_guide",
        "topic": "外贸打工人必备的网络加速工具推荐",
        "style": "guide",
        "description": "针对跨境电商/外贸从业者",
        "image_label": "guide",
    },
    {
        "type": "buying_guide",
        "topic": "2026年新手买网络加速服务防坑指南",
        "style": "guide",
        "description": "列出常见骗局和坑，帮新人避雷",
        "image_label": "guide",
    },
    {
        "type": "review",
        "topic": "自由猫 Freecat 深度测评：用了半年的真实体验",
        "style": "review",
        "description": "主推机场详细评测",
        "image_label": "review",
    },
    {
        "type": "review",
        "topic": "奈云 IEPL 专线体验：168元年付到底值不值",
        "style": "review",
        "description": "热门平价机场评测",
        "image_label": "review",
    },
    {
        "type": "review",
        "topic": "一枝红杏10年老牌机场评测：老品牌还值得信赖吗",
        "style": "review",
        "description": "老牌机场评测",
        "image_label": "review",
    },
    {
        "type": "review",
        "topic": "万达云 vs 龙猫云：两家同价位服务商对比实测",
        "style": "comparison",
        "description": "两家服务商横向对比",
        "image_label": "compare",
    },
    {
        "type": "review",
        "topic": "悠兔 YouTu 低调运营的优质机场开箱测评",
        "style": "review",
        "description": "新兴机场体验",
        "image_label": "review",
    },
    {
        "type": "ai_tutorial",
        "topic": "ChatGPT 国内使用完整教程 2026",
        "style": "tutorial",
        "description": "ChatGPT 注册到使用全流程",
        "image_label": "chatgpt",
    },
    {
        "type": "ai_tutorial",
        "topic": "Claude 3.5 中文使用指南：比ChatGPT强在哪",
        "style": "tutorial",
        "description": "Claude 使用教程+特点",
        "image_label": "claude",
    },
    {
        "type": "ai_tutorial",
        "topic": "Cursor AI 编程工具入门：不会代码也能写程序",
        "style": "tutorial",
        "description": "面向非程序员的Cursor教程",
        "image_label": "cursor",
    },
    {
        "type": "ai_tutorial",
        "topic": "Midjourney 2026 最新使用指南：从注册到出图",
        "style": "tutorial",
        "description": "Midjourney AI绘画教程",
        "image_label": "midjourney",
    },
    {
        "type": "ai_tutorial",
        "topic": "2026年必装的10个AI工具，提升工作效率200%",
        "style": "tutorial",
        "description": "AI工具合集推荐",
        "image_label": "chatgpt",
    },
    {
        "type": "ai_tutorial",
        "topic": "用 AI 写公众号文章的完整工作流",
        "style": "tutorial",
        "description": "AI写作实战教程",
        "image_label": "chatgpt",
    },
    {
        "type": "ai_tutorial",
        "topic": "Perplexity AI 搜索工具使用教程：比Google更好用",
        "style": "tutorial",
        "description": "AI搜索工具教程",
        "image_label": "chatgpt",
    },
    {
        "type": "guide",
        "topic": "我用了3年网络加速服务，总结出这5条经验",
        "style": "experience",
        "description": "长期使用经验总结",
        "image_label": "guide",
    },
    {
        "type": "guide",
        "topic": "Clash Verge 客户端配置教程：小白也能看懂",
        "style": "tutorial",
        "description": "客户端配置教程",
        "image_label": "clash",
    },
    {
        "type": "guide",
        "topic": "2026年主流客户端对比：Clash vs Sing-Box vs Surge",
        "style": "comparison",
        "description": "客户端横向对比",
        "image_label": "clash",
    },
    {
        "type": "guide",
        "topic": "iOS/iPad 上最好的网络加速工具推荐",
        "style": "guide",
        "description": "苹果设备专用教程",
        "image_label": "guide",
    },
    {
        "type": "guide",
        "topic": "Android 手机网络加速配置教程",
        "style": "tutorial",
        "description": "安卓设备专用教程",
        "image_label": "guide",
    },
    {
        "type": "guide",
        "topic": "Mac 上配置网络加速的几种方式对比",
        "style": "tutorial",
        "description": "Mac设备教程",
        "image_label": "guide",
    },
    {
        "type": "troubleshooting",
        "topic": "常见网络加速连接失败问题排查手册",
        "style": "guide",
        "description": "总结最常见的问题和解决方法",
        "image_label": "troubleshoot",
    },
    {
        "type": "troubleshooting",
        "topic": "晚高峰卡顿怎么办？5个技巧提升速度",
        "style": "tips",
        "description": "速度优化技巧",
        "image_label": "troubleshoot",
    },
    {
        "type": "troubleshooting",
        "topic": "网络加速服务突然用不了？先别急着重装",
        "style": "guide",
        "description": "故障排查指南",
        "image_label": "troubleshoot",
    },
    {
        "type": "guide",
        "topic": "如何测试你的网络加速服务速度",
        "style": "tips",
        "description": "测速方法教程",
        "image_label": "troubleshoot",
    },
    {
        "type": "comparison",
        "topic": "2026年十大主流网络加速服务横向评测",
        "style": "review",
        "description": "大型横向评测",
        "image_label": "compare",
    },
    {
        "type": "comparison",
        "topic": "IEPL专线 vs 普通中转：到底差在哪",
        "style": "comparison",
        "description": "线路类型科普+对比",
        "image_label": "compare",
    },
    {
        "type": "comparison",
        "topic": "年付套餐值不值？帮你算一笔账",
        "style": "comparison",
        "description": "价格计算对比",
        "image_label": "compare",
    },
    {
        "type": "guide",
        "topic": "2026年 AI 工具发展趋势：哪些值得关注",
        "style": "trend",
        "description": "AI行业趋势分析",
        "image_label": "chatgpt",
    },
    {
        "type": "guide",
        "topic": "DeepSeek 2026 使用指南：国产AI的进步",
        "style": "tutorial",
        "description": "DeepSeek使用教程",
        "image_label": "chatgpt",
    },
    {
        "type": "comparison",
        "topic": "2026年主流网络加速服务线路类型横向评测：专线、IEPL、中转、家宽全解析",
        "style": "comparison",
        "description": "全面对比专线、IEPL、中转和家宽四种线路在速度、稳定性和价格上的差异，帮你选择最适合的线路类型。",
        "image_label": "compare",
    },
    {
        "type": "guide",
        "topic": "从0到1搭建自己的网络加速工作流：客户端选择与配置最佳实践",
        "style": "guide",
        "description": "涵盖主流客户端（Clash Meta、Sing-Box、Surge）的连携配置与常用技巧，搭建高效稳定的多设备加速环境。",
        "image_label": "clash",
    },
    {
        "type": "ai_tutorial",
        "topic": "AI效率工具组合：用Perplexity搜索+ChatGPT写作+Claude润色的完整内容生产链",
        "style": "tutorial",
        "description": "手把手教你串联三大AI工具，实现从选题、写作到润色的全流程内容生产，大幅提升创作效率。",
        "image_label": "chatgpt",
    },
    {
        "type": "review",
        "topic": "专线服务商深度体验：连续使用三个月的网络延迟数据对比",
        "style": "review",
        "description": "记录多家专线服务商（如肥猫云、NXO Earth等）三个月内的延迟波动、稳定性与高峰表现，提供真实数据参考",
        "image_label": "review",
    },
    {
        "type": "ai_tutorial",
        "topic": "2026年使用Sora生成视频完整教程：从注册到出片",
        "style": "tutorial",
        "description": "一步步教你在国内通过加速服务注册OpenAI Sora，掌握从输入提示词到输出高清视频的全流程",
        "image_label": "chatgpt",
    },
    {
        "type": "guide",
        "topic": "家庭多设备共享网络加速的最佳方案：路由器端配置详解",
        "style": "tips",
        "description": "无需每台设备单独安装客户端，通过路由器实现全屋设备自动加速，附主流路由器固件配置步骤",
        "image_label": "guide",
    },
    {
        "type": "comparison",
        "topic": "三大入门级IEPL服务商横向对比：自由猫、奈云、MESL实测数据大公开",
        "style": "comparison",
        "description": "对三家主打IEPL线路的入门级服务商进行多维度速度、稳定性和性价比实测，帮你选出最适合的起步选择。",
        "image_label": "compare",
    },
    {
        "type": "ai_tutorial",
        "topic": "不会写代码也能制作Clash配置文件？ChatGPT帮你搞定",
        "style": "tutorial",
        "description": "手把手教你用ChatGPT生成Clash规则的配置文件，无需编程基础也能自定义节点分组和分流策略。",
        "image_label": "chatgpt",
    },
    {
        "type": "comparison",
        "topic": "2026年入门级专线服务商深度横评：便宜也有好货？实测六家百元级年付服务商",
        "style": "review",
        "description": "挑选六家主推入门专线的服务商（如龙猫云、光年梯、新华云等）进行实际速度、稳定性、客服对比，帮预算有限的用户找到最佳选择。",
        "image_label": "compare",
    },
    {
        "type": "guide",
        "topic": "外贸行业专用网络加速配置指南：如何同时访问多个海外AI工具且不卡顿？",
        "style": "tutorial",
        "description": "针对外贸从业者，讲解如何利用支持分流策略的服务商（如支持IEPL+专线的万达云）配置多线路，确保ChatGPT、Claude、Perplexity等AI工具稳定使用。",
        "image_label": "guide",
    },
    {
        "type": "review",
        "topic": "家宽线路真的比专线慢吗？悠兔家宽一个月深度体验报告",
        "style": "review",
        "description": "真实体验悠兔的家宽线路，对比专线和IEPL，看家宽是否适合日常使用。",
        "image_label": "review",
    },
    {
        "type": "review",
        "topic": "月付5元能买到什么样的网络加速？新华云NewHua99低价套餐实测",
        "style": "review",
        "description": "购买新华云最低价套餐，测试速度、稳定性、晚高峰表现，看看便宜是否没好货。",
        "image_label": "budget",
    },
    {
        "type": "comparison",
        "topic": "闪狐云 vs 贝贝云：两家热门中转线路服务商横向对比",
        "style": "comparison",
        "description": "同价位中转服务商，从延迟、速度、可用节点、客服响应等多维度对比，帮你选。",
        "image_label": "compare",
    },
    {
        "type": "comparison",
        "topic": "iOS端网络加速工具横评：Surge、Quantumult X、Stash三款付费工具实测",
        "style": "review",
        "description": "为iOS用户实测三款主流付费加速工具，从性能、功能、易用性等角度对比，帮你决定花哪个钱。",
        "image_label": "compare",
    },
    {
        "type": "troubleshooting",
        "topic": "网络加速后依然被屏蔽？DNS泄露自查与修复指南",
        "style": "guide",
        "description": "教你检查DNS泄露、WebRTC泄露等问题，并给出修复方案，确保真正安全访问。",
        "image_label": "troubleshoot",
    },
    {
        "type": "comparison",
        "topic": "手动搭建网络加速服务 vs 商业服务：成本与隐私的全面对比",
        "style": "comparison",
        "description": "从费用、性能、隐私控制三个维度，深入对比自行搭建VPN与订阅商业加速服务的优劣，适合技术爱好者与隐私敏感用户。",
        "image_label": "compare",
        "category": "VPN",
    },
    {
        "type": "guide",
        "topic": "零隐私泄露的网络加速方案：手动配置让你的数据完全自主可控",
        "style": "guide",
        "description": "详细教程教你如何利用自有服务器和开源工具，搭建一个不依赖任何第三方、无日志的专属网络加速通道。",
        "image_label": "guide",
        "category": "VPN",
    },
]

# ============================================================
# 内容生成策略配置
# ============================================================
WRITING_STRATEGY = {
    "tone": "像一个真实付费用户分享经验，而非营销号",
    "trust_builders": [
        "强调真实付费使用",
        "主动列出缺点（反直觉坦诚建立信任）",
        "分享踩坑经历（拉近距离）",
        "建议先月付试用（劝用户谨慎）",
    ],
    "banned_words": ["翻墙", "梯子", "VPN", "科学上网", "富强"],
    "safe_alternatives": {
        "翻墙": "访问外网",
        "梯子": "网络加速工具",
        "VPN": "网络加速服务",
        "科学上网": "访问国际网络",
        "节点": "接入点",
        "机场": "网络服务商",
    },
    "affiliate_placement": "在推荐具体服务商时使用推广链接，非推荐类内容不使用",
}

# ============================================================
# 话题分类：推广向 vs 干货向
# ============================================================
PROMOTIONAL_TYPES = {"buying_guide", "review", "comparison"}
EDUCATIONAL_TYPES = {"ai_tutorial", "guide", "troubleshooting", "guide"}


def is_promotional(topic):
    """判断话题是否为推广向"""
    return topic.get("type") in PROMOTIONAL_TYPES


def count_remaining_promotional():
    """统计内容日历中剩余的推广向话题数量"""
    return sum(1 for t in CONTENT_CALENDAR if is_promotional(t))


def count_remaining_educational():
    """统计内容日历中剩余的干货向话题数量"""
    return sum(1 for t in CONTENT_CALENDAR if not is_promotional(t))


def auto_generate_promotional_topics(affiliates):
    """
    当推广向话题不足 10 个时，根据现有推广链接自动生成新话题
    affiliates: 从 API 获取的推广数据 {名称: {url, note, ...}}
    返回新增的话题列表
    """
    new_topics = []
    # 排除 Test 等测试条目，只保留有效推广
    valid_affs = {k: v for k, v in affiliates.items()
                  if k not in ("Test",) and v.get("url", "")}

    # 获取已存在的推广话题，避免重复
    existing_names = set()
    for t in CONTENT_CALENDAR:
        if is_promotional(t):
            topic = t.get("topic", "")
            for aff_name in valid_affs:
                if aff_name in topic:
                    existing_names.add(aff_name)
                    break

    # 为还没有评测话题的推广商生成新话题
    for name, info in valid_affs.items():
        if name in existing_names:
            continue
        if len(new_topics) >= 15:
            break

        note = info.get("note", "")
        if "不推荐" in note or "一般般" in note:
            continue  # 不推荐的不生成话题

        # 从 note 推断线路类型
        line_type = "网络加速"
        if "IEPL" in note:
            line_type = "IEPL专线"
        elif "专线" in note:
            line_type = "专线"
        elif "中转" in note:
            line_type = "中转"

        new_topics.append({
            "type": "review",
            "topic": f"{name} {line_type}使用体验：真实评测分享",
            "style": "review",
            "description": f"推广评测：{name}的真实使用体验",
            "image_label": "review",
        })
        # 如果推广商信息充足，再加一个对比类话题
        if len(new_topics) < 15:
            new_topics.append({
                "type": "comparison",
                "topic": f"{name} vs 同类服务商对比：{line_type}哪家强",
                "style": "comparison",
                "description": f"对比评测：{name}与同类服务商的多维度对比",
                "image_label": "compare",
            })

    return new_topics


# ============================================================
# 时间计算
# ============================================================
PROJECT_START_DATE = datetime.date(2026, 5, 25)


def get_current_week():
    """计算从项目开始到现在的第几周"""
    today = datetime.date.today()
    delta = today - PROJECT_START_DATE
    week_num = delta.days // 7
    return max(week_num, 0)


def ensure_topic_balance(affiliates=None):
    """
    确保内容日历保持 40% 推广 / 60% 干货的比例
    如果推广话题不足 10 个，自动补新话题
    返回调整后的日历长度
    """
    promo_count = count_remaining_promotional()
    if promo_count >= 10:
        return len(CONTENT_CALENDAR)

    if not affiliates:
        return len(CONTENT_CALENDAR)

    new_topics = auto_generate_promotional_topics(affiliates)
    if new_topics:
        CONTENT_CALENDAR.extend(new_topics)
        total = len(CONTENT_CALENDAR)
        print(f"[Config] Added {len(new_topics)} promotional topics ({total} total)")
    return len(CONTENT_CALENDAR)


def get_current_topic(affiliates=None):
    """获取本周应该写的内容，必要时自动补话题"""
    # 检查并补充推广话题
    ensure_topic_balance(affiliates)

    week_num = get_current_week()
    index = week_num % len(CONTENT_CALENDAR)
    topic = CONTENT_CALENDAR[index]
    return {
        **topic,
        "week_num": week_num,
        "cycle_index": index + 1,
        "total_cycles": len(CONTENT_CALENDAR),
    }


def get_output_filename(topic_info):
    """生成输出文件名"""
    date_str = datetime.date.today().isoformat()
    safe_name = topic_info["topic"].replace(" ", "_").replace("?", "").replace("：", "_").replace(":", "_")
    # 截断过长文件名
    if len(safe_name) > 80:
        safe_name = safe_name[:80]
    return f"{date_str}_{safe_name}"
