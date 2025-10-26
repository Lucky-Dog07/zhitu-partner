"""
AI 笔记生成的职业化 Prompt 模板
"""

# 程序员相关职业关键词
PROGRAMMER_KEYWORDS = [
    '程序员', '开发', '工程师', '前端', '后端', '全栈', 
    'Frontend', 'Backend', 'Developer', 'Engineer',
    'Java', 'Python', 'JavaScript', 'React', 'Vue', 'Angular',
    '移动端', 'iOS', 'Android', '算法'
]

# 教师相关职业关键词
TEACHER_KEYWORDS = [
    '教师', '老师', '讲师', '教授', '教学', '培训师',
    'Teacher', 'Instructor', 'Professor', 'Educator'
]

CAREER_PROMPTS = {
    "programmer": """你是一位资深编程导师。请根据以下数据，生成一份程序员专用的学习笔记：

职业：{position}

错题列表：
{mistakes}

薄弱知识点：
{weak_points}

学习进度概况：
{learning_progress}

请按以下结构生成 Markdown 格式笔记：

## 错题分析

（逐题分析错误原因、正确思路、代码示例）

## 知识点梳理

（提取涉及的技术栈、核心原理、最佳实践）

{optional_sections}

注意：
- 代码示例使用实际可运行的语法
- 提供具体的学习资源链接
- 关注工程实践而非纯理论
- 语言简洁专业，重点突出
""",

    "teacher": """你是一位教学专家。请根据以下数据，生成一份教师专用的教学笔记：

职业：{position}

学习记录：
{mistakes}

薄弱环节：
{weak_points}

学习进度：
{learning_progress}

请按以下结构生成笔记：

## 知识点掌握情况

（分析学习者的理解误区、知识盲区、认知水平）

## 教学反思

（如何更好地讲解这些内容、教学方法改进建议）

{optional_sections}

注意：
- 从教学角度分析问题
- 提供可操作的教学方案
- 关注学习者认知规律
- 包含实际教学案例
""",

    "general": """你是一位专业的学习顾问。请根据以下数据，生成一份个性化学习笔记：

职业方向：{position}

学习难点：
{mistakes}

薄弱知识点：
{weak_points}

学习进度：
{learning_progress}

请按以下结构生成 Markdown 格式笔记：

## 学习难点分析

（分析学习中遇到的问题、原因、解决思路）

## 知识点总结

（系统梳理相关知识点、重点难点）

{optional_sections}

注意：
- 内容贴合职业发展需求
- 提供实用的学习建议
- 包含可行的行动计划
- 语言通俗易懂
"""
}

# 可选章节模板
OPTIONAL_SECTIONS = {
    "study_plan": """
## 个性化学习计划

（根据薄弱点制定3-7天的学习计划，包括每日学习目标、练习任务、检验标准）
""",

    "interview_tips": """
## 面试技巧与策略

（针对这些知识点的面试常考题型、答题思路、注意事项、高频考点）
"""
}


def detect_career_type(position: str) -> str:
    """
    根据职业名称判断职业类型
    
    Args:
        position: 职业名称
        
    Returns:
        'programmer' | 'teacher' | 'general'
    """
    position_lower = position.lower()
    
    # 检查是否为程序员相关
    for keyword in PROGRAMMER_KEYWORDS:
        if keyword.lower() in position_lower:
            return 'programmer'
    
    # 检查是否为教师相关
    for keyword in TEACHER_KEYWORDS:
        if keyword.lower() in position_lower:
            return 'teacher'
    
    # 默认为通用模板
    return 'general'


def build_prompt(
    position: str,
    mistakes: list,
    weak_points: dict,
    learning_progress: str,
    include_study_plan: bool = True,
    include_interview_tips: bool = True,
    custom_requirements: str = None
) -> str:
    """
    构建职业化的 AI Prompt
    
    Args:
        position: 职业名称
        mistakes: 错题列表
        weak_points: 薄弱知识点字典
        learning_progress: 学习进度描述
        include_study_plan: 是否包含学习计划
        include_interview_tips: 是否包含面试技巧
        custom_requirements: 用户自定义要求
        
    Returns:
        完整的 Prompt 字符串
    """
    # 检测职业类型
    career_type = detect_career_type(position)
    
    # 获取基础模板
    base_template = CAREER_PROMPTS[career_type]
    
    # 构建可选章节
    optional_sections = []
    if include_study_plan:
        optional_sections.append(OPTIONAL_SECTIONS['study_plan'])
    if include_interview_tips:
        optional_sections.append(OPTIONAL_SECTIONS['interview_tips'])
    
    optional_sections_text = '\n'.join(optional_sections)
    
    # 格式化错题列表
    mistakes_text = "\n".join([
        f"{i+1}. 题目：{m['question']}\n   错误原因：{m.get('reason', '未分析')}\n   正确答案：{m.get('answer', '暂无')}"
        for i, m in enumerate(mistakes[:10])  # 最多10道题
    ]) if mistakes else "暂无错题记录"
    
    # 格式化薄弱知识点
    weak_points_text = "\n".join([
        f"- {category}：{', '.join(points)}"
        for category, points in weak_points.items()
    ]) if weak_points else "暂无薄弱知识点分析"
    
    # 填充模板
    prompt = base_template.format(
        position=position,
        mistakes=mistakes_text,
        weak_points=weak_points_text,
        learning_progress=learning_progress,
        optional_sections=optional_sections_text
    )
    
    # 添加自定义要求
    if custom_requirements:
        prompt += f"\n\n特别要求：\n{custom_requirements}"
    
    return prompt

