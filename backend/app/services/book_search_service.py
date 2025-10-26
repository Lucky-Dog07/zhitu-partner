"""
书籍搜索服务 - 搜索技术书籍
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from functools import lru_cache
import openai
import json
from ..core.config import settings


class BookSearchService:
    """书籍搜索服务"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.timeout = 10
        
        # 初始化OpenAI客户端（用于AI智能匹配）
        self.openai_client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def _ai_match_categories(self, keywords: str) -> List[str]:
        """
        使用AI智能分析关键词应该匹配哪些书籍分类
        
        Args:
            keywords: 搜索关键词（如"AI工程师"、"数据分析师"等）
            
        Returns:
            匹配的书籍分类列表
        """
        # 获取所有可用的书籍分类
        available_categories = ['ai', 'nlp', '计算机视觉', '强化学习', 'java', 'python', 
                               'javascript', 'react', '算法']
        
        prompt = f"""你是一个职业技能分析专家。根据给定的职位/关键词，分析它需要学习哪些技术方向的书籍。

可用的书籍分类：{', '.join(available_categories)}

职位/关键词：{keywords}

请分析这个职位/关键词最需要哪些技术方向的书籍。按重要性排序，返回最相关的3-5个分类。

要求：
1. 只返回JSON格式：{{"categories": ["分类1", "分类2", ...]}}
2. 分类必须从可用列表中选择
3. 按重要性排序（最重要的放前面）
4. 要全面考虑职位需求

示例：
- "AI工程师" → {{"categories": ["ai", "python", "nlp", "计算机视觉"]}}
- "前端工程师" → {{"categories": ["javascript", "react"]}}
- "Java后端工程师" → {{"categories": ["java", "算法"]}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个职业技能分析专家。只返回JSON格式，不要有其他内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_output = response.choices[0].message.content.strip()
            print(f"[DEBUG] AI匹配分类结果: {ai_output}")
            
            # 解析JSON
            result = json.loads(ai_output)
            categories = result.get('categories', [])
            
            # 验证分类是否在可用列表中
            valid_categories = [cat for cat in categories if cat in available_categories]
            
            print(f"[DEBUG] AI推荐的书籍分类: {valid_categories}")
            return valid_categories
            
        except Exception as e:
            print(f"[ERROR] AI匹配分类失败: {e}")
            # 失败时使用关键词直接匹配
            keywords_lower = keywords.lower()
            matched = []
            for cat in available_categories:
                if cat in keywords_lower:
                    matched.append(cat)
            return matched if matched else ['python']  # 默认返回python
    
    def _ai_generate_books(self, keywords: str, diversity_seed: int = None) -> List[Dict[str, Any]]:
        """
        使用AI生成书籍推荐（当数据库没有匹配时）
        
        Args:
            keywords: 搜索关键词
            diversity_seed: 多样性种子（用于生成不同的书籍）
            
        Returns:
            AI生成的书籍列表
        """
        import random
        import time
        
        # 使用时间戳作为多样性种子，确保每次生成不同的书籍
        if diversity_seed is None:
            diversity_seed = int(time.time()) % 100
        
        # 定义不同的生成策略，增加多样性
        strategies = [
            "推荐5本经典必读书籍",
            "推荐5本适合入门的书籍",
            "推荐5本进阶和深度学习的书籍",
            "推荐5本实战项目类书籍",
            "推荐5本最新出版的书籍（2020年后）",
            "推荐3本中文书籍和2本英文原版书籍",
        ]
        
        strategy = strategies[diversity_seed % len(strategies)]
        print(f"[DEBUG] AI书籍生成策略: {strategy} (种子={diversity_seed})")
        
        prompt = f"""你是一个技术图书推荐专家。请为"{keywords}"相关的职位/技能{strategy}。

要求：
1. 推荐真实存在的、高质量的技术书籍
2. 书籍要多样化，包含不同类型（理论、实战、工具书等）
3. 每次推荐都要不同，避免重复常见书籍
4. 返回JSON格式，格式如下：

{{
  "books": [
    {{
      "title": "书名（含版本号）",
      "author": "作者姓名",
      "publisher": "出版社",
      "rating": "评分（如9.1）",
      "description": "一句话简介（20字以内）",
      "url": "豆瓣或购买链接"
    }}
  ]
}}

职位/技能：{keywords}
生成策略：{strategy}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个技术图书推荐专家。只返回JSON格式，不要有其他内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 提高温度，增加多样性
                max_tokens=2000
            )
            
            ai_output = response.choices[0].message.content.strip()
            print(f"[DEBUG] AI生成书籍推荐: {ai_output[:200]}...")
            
            # 清理可能的markdown代码块标记
            if ai_output.startswith('```'):
                # 移除开头的 ```json 或 ```
                lines = ai_output.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # 移除结尾的 ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                ai_output = '\n'.join(lines).strip()
                print(f"[DEBUG] 清理后的JSON: {ai_output[:200]}...")
            
            # 解析JSON
            result = json.loads(ai_output)
            books = result.get('books', [])
            
            # 标准化字段
            standardized_books = []
            for book in books:
                standardized_books.append({
                    'title': book.get('title', '未知书名'),
                    'author': book.get('author', '多位作者'),
                    'publisher': book.get('publisher', '各大出版社'),
                    'rating': book.get('rating', '待评分'),
                    'description': book.get('description', ''),
                    'url': book.get('url', f'https://search.douban.com/book/subject_search?search_text={keywords}'),
                    'cover': 'https://via.placeholder.com/200x280?text=Book'
                })
            
            print(f"[DEBUG] AI生成了 {len(standardized_books)} 本书籍")
            return standardized_books
            
        except Exception as e:
            print(f"[ERROR] AI生成书籍失败: {e}")
            # 失败时返回搜索链接
            return [
                {
                    'title': f'{keywords}相关技术书籍',
                    'url': f'https://search.douban.com/book/subject_search?search_text={keywords}',
                    'cover': 'https://via.placeholder.com/200x280?text=Book',
                    'author': '多位作者',
                    'publisher': '各大出版社',
                    'rating': '待评分',
                    'description': f'点击搜索 "{keywords}" 相关技术书籍'
                }
            ]
    
    def search_books(
        self, 
        keywords: str, 
        limit: int = 5,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索技术书籍
        
        Args:
            keywords: 搜索关键词
            limit: 返回数量限制
            page: 页码（从1开始）
            
        Returns:
            书籍列表
        """
        print(f"[DEBUG] 搜索技术书籍: {keywords}, 页码: {page}")
        
        # 由于豆瓣等网站可能有反爬虫限制，这里使用预设的优质书籍推荐
        return self._get_fallback_books(keywords, limit, page)
    
    def _get_fallback_books(self, keywords: str, limit: int, page: int = 1) -> List[Dict]:
        """
        根据关键词返回预设的优质书籍
        """
        # 技术书籍推荐库（根据关键词匹配） - 扩展为每个技术10+本书
        book_database = {
            'ai': [
                {
                    'title': '深度学习',
                    'url': 'https://book.douban.com/subject/27087503/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s29190338.jpg',
                    'author': 'Ian Goodfellow / Yoshua Bengio / Aaron Courville',
                    'publisher': '人民邮电出版社',
                    'rating': '9.1',
                    'description': '深度学习领域的圣经'
                },
                {
                    'title': '机器学习',
                    'url': 'https://book.douban.com/subject/26708119/',
                    'cover': 'https://img3.doubanio.com/view/subject/l/public/s28735609.jpg',
                    'author': '周志华',
                    'publisher': '清华大学出版社',
                    'rating': '9.2',
                    'description': '机器学习西瓜书，中文经典'
                },
                {
                    'title': 'Python机器学习实践指南',
                    'url': 'https://book.douban.com/subject/30317874/',
                    'author': 'Alexander T. Ihler / Michael Bowles',
                    'publisher': '机械工业出版社',
                    'rating': '8.5',
                    'description': '机器学习实战教程'
                },
                {
                    'title': 'Hands-On Machine Learning',
                    'url': 'https://book.douban.com/subject/35218199/',
                    'author': 'Aurélien Géron',
                    'publisher': "O'Reilly Media",
                    'rating': '9.3',
                    'description': '使用Scikit-Learn、Keras和TensorFlow进行机器学习'
                },
                {
                    'title': '统计学习方法（第2版）',
                    'url': 'https://book.douban.com/subject/33437381/',
                    'author': '李航',
                    'publisher': '清华大学出版社',
                    'rating': '9.0',
                    'description': '机器学习理论基础'
                },
                {
                    'title': 'Python深度学习',
                    'url': 'https://book.douban.com/subject/30293801/',
                    'author': 'François Chollet',
                    'publisher': '人民邮电出版社',
                    'rating': '8.9',
                    'description': 'Keras之父的深度学习实战'
                },
                {
                    'title': '动手学深度学习',
                    'url': 'https://book.douban.com/subject/33450010/',
                    'author': '阿斯顿·张 / 李沐等',
                    'publisher': '人民邮电出版社',
                    'rating': '9.1',
                    'description': 'PyTorch版深度学习教程'
                },
                {
                    'title': '神经网络与深度学习',
                    'url': 'https://book.douban.com/subject/35044046/',
                    'author': '邱锡鹏',
                    'publisher': '机械工业出版社',
                    'rating': '8.8',
                    'description': '深度学习理论与实践'
                },
                {
                    'title': 'AI算法工程师手册',
                    'url': 'http://www.huaxiaozhuan.com/',
                    'author': '华校专',
                    'publisher': '在线开源',
                    'rating': '9.4',
                    'description': '机器学习与深度学习知识手册'
                },
                {
                    'title': 'Pattern Recognition and Machine Learning',
                    'url': 'https://book.douban.com/subject/2061116/',
                    'author': 'Christopher Bishop',
                    'publisher': 'Springer',
                    'rating': '9.5',
                    'description': '模式识别与机器学习经典'
                },
            ],
            'nlp': [
                {
                    'title': '自然语言处理实战',
                    'url': 'https://book.douban.com/subject/35051608/',
                    'author': 'Hobson Lane / Cole Howard / Hannes Hapke',
                    'publisher': '人民邮电出版社',
                    'rating': '8.6',
                    'description': 'NLP从理论到实践'
                },
                {
                    'title': 'Speech and Language Processing',
                    'url': 'https://web.stanford.edu/~jurafsky/slp3/',
                    'author': 'Dan Jurafsky / James H. Martin',
                    'publisher': 'Stanford',
                    'rating': '9.3',
                    'description': 'NLP领域经典教材（在线免费）'
                },
                {
                    'title': '基于BERT的自然语言处理实战',
                    'url': 'https://book.douban.com/subject/35270439/',
                    'author': 'Sudharsan Ravichandiran',
                    'publisher': '机械工业出版社',
                    'rating': '8.4',
                    'description': 'BERT及Transformers实战'
                },
                {
                    'title': 'Transformers自然语言处理',
                    'url': 'https://book.douban.com/subject/36042716/',
                    'author': 'Lewis Tunstall等',
                    'publisher': '人民邮电出版社',
                    'rating': '8.7',
                    'description': '使用Hugging Face进行NLP'
                },
            ],
            '计算机视觉': [
                {
                    'title': '计算机视觉：算法与应用',
                    'url': 'https://book.douban.com/subject/26883297/',
                    'author': 'Richard Szeliski',
                    'publisher': '清华大学出版社',
                    'rating': '9.0',
                    'description': '计算机视觉领域权威教材'
                },
                {
                    'title': '深度学习与计算机视觉',
                    'url': 'https://book.douban.com/subject/27116026/',
                    'author': '叶韵 / 阳洪波',
                    'publisher': '机械工业出版社',
                    'rating': '8.5',
                    'description': 'CV深度学习实战'
                },
                {
                    'title': 'OpenCV计算机视觉编程攻略（第3版）',
                    'url': 'https://book.douban.com/subject/27034658/',
                    'author': 'Robert Laganiere',
                    'publisher': '人民邮电出版社',
                    'rating': '8.3',
                    'description': 'OpenCV实战指南'
                },
            ],
            '强化学习': [
                {
                    'title': 'Reinforcement Learning: An Introduction',
                    'url': 'https://book.douban.com/subject/30323890/',
                    'author': 'Richard S. Sutton / Andrew G. Barto',
                    'publisher': 'MIT Press',
                    'rating': '9.4',
                    'description': '强化学习圣经'
                },
                {
                    'title': '深度强化学习',
                    'url': 'https://book.douban.com/subject/35267702/',
                    'author': '王琦 / 杨毅远 / 江季',
                    'publisher': '人民邮电出版社',
                    'rating': '8.6',
                    'description': 'DRL理论与实践'
                },
            ],
            'java': [
                {
                    'title': 'Effective Java 中文版（原书第3版）',
                    'url': 'https://book.douban.com/subject/30412517/',
                    'cover': 'https://img2.doubanio.com/view/subject/l/public/s29733555.jpg',
                    'author': 'Joshua Bloch',
                    'publisher': '机械工业出版社',
                    'rating': '9.1',
                    'description': 'Java编程语言最佳实践指南'
                },
                {
                    'title': 'Java核心技术（原书第11版）',
                    'url': 'https://book.douban.com/subject/34898994/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s33478049.jpg',
                    'author': 'Cay S. Horstmann',
                    'publisher': '机械工业出版社',
                    'rating': '9.0',
                    'description': 'Java技术权威指南'
                },
                {
                    'title': 'Java并发编程实战',
                    'url': 'https://book.douban.com/subject/10484692/',
                    'author': 'Brian Goetz',
                    'publisher': '机械工业出版社',
                    'rating': '9.0',
                    'description': 'Java并发编程经典之作'
                },
                {
                    'title': 'Head First Java（第2版）',
                    'url': 'https://book.douban.com/subject/2000732/',
                    'author': 'Kathy Sierra / Bert Bates',
                    'publisher': '中国电力出版社',
                    'rating': '8.7',
                    'description': 'Java入门最有趣的教材'
                },
                {
                    'title': 'Java性能权威指南',
                    'url': 'https://book.douban.com/subject/26740520/',
                    'author': 'Scott Oaks',
                    'publisher': '人民邮电出版社',
                    'rating': '8.5',
                    'description': 'Java性能优化全面指南'
                },
                {
                    'title': 'Spring实战（第5版）',
                    'url': 'https://book.douban.com/subject/34949443/',
                    'author': 'Craig Walls',
                    'publisher': '人民邮电出版社',
                    'rating': '8.8',
                    'description': 'Spring框架实战教程'
                },
                {
                    'title': '深入理解Java虚拟机（第3版）',
                    'url': 'https://book.douban.com/subject/34907497/',
                    'author': '周志明',
                    'publisher': '机械工业出版社',
                    'rating': '9.4',
                    'description': 'JVM原理深度解析'
                },
                {
                    'title': 'Java编程思想（第4版）',
                    'url': 'https://book.douban.com/subject/2130190/',
                    'author': 'Bruce Eckel',
                    'publisher': '机械工业出版社',
                    'rating': '9.1',
                    'description': 'Java编程经典名著'
                },
            ],
            'python': [
                {
                    'title': '流畅的Python（第2版）',
                    'url': 'https://book.douban.com/subject/35545258/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s34128612.jpg',
                    'author': 'Luciano Ramalho',
                    'publisher': '人民邮电出版社',
                    'rating': '9.5',
                    'description': 'Python进阶必读经典'
                },
                {
                    'title': 'Python编程：从入门到实践（第2版）',
                    'url': 'https://book.douban.com/subject/35196328/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s33907206.jpg',
                    'author': 'Eric Matthes',
                    'publisher': '人民邮电出版社',
                    'rating': '9.2',
                    'description': 'Python入门经典教材'
                },
                {
                    'title': 'Effective Python（第2版）',
                    'url': 'https://book.douban.com/subject/35213963/',
                    'author': 'Brett Slatkin',
                    'publisher': '机械工业出版社',
                    'rating': '9.0',
                    'description': 'Python最佳实践指南'
                },
                {
                    'title': 'Python Cookbook（第3版）',
                    'url': 'https://book.douban.com/subject/26381341/',
                    'author': 'David Beazley / Brian K. Jones',
                    'publisher': '人民邮电出版社',
                    'rating': '8.5',
                    'description': 'Python编程技巧大全'
                },
                {
                    'title': 'Python数据分析实战',
                    'url': 'https://book.douban.com/subject/35382092/',
                    'author': 'Wes McKinney',
                    'publisher': '机械工业出版社',
                    'rating': '8.8',
                    'description': 'Pandas作者的数据分析教程'
                },
            ],
            'javascript': [
                {
                    'title': 'JavaScript高级程序设计（第4版）',
                    'url': 'https://book.douban.com/subject/35175321/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s33906838.jpg',
                    'author': 'Matt Frisbie',
                    'publisher': '人民邮电出版社',
                    'rating': '9.3',
                    'description': '前端开发红宝书'
                },
                {
                    'title': 'JavaScript权威指南（第7版）',
                    'url': 'https://book.douban.com/subject/35396470/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s34077374.jpg',
                    'author': 'David Flanagan',
                    'publisher': '机械工业出版社',
                    'rating': '9.1',
                    'description': 'JavaScript犀牛书'
                },
            ],
            'react': [
                {
                    'title': 'React学习手册（第2版）',
                    'url': 'https://book.douban.com/subject/35523124/',
                    'cover': 'https://img9.doubanio.com/view/subject/l/public/s34129103.jpg',
                    'author': 'Alex Banks / Eve Porcello',
                    'publisher': '人民邮电出版社',
                    'rating': '8.7',
                    'description': 'React实战指南'
                },
            ],
            '算法': [
                {
                    'title': '算法（第4版）',
                    'url': 'https://book.douban.com/subject/19952400/',
                    'cover': 'https://img3.doubanio.com/view/subject/l/public/s28322244.jpg',
                    'author': 'Robert Sedgewick / Kevin Wayne',
                    'publisher': '人民邮电出版社',
                    'rating': '9.4',
                    'description': '算法学习经典之作'
                },
                {
                    'title': '算法导论（原书第3版）',
                    'url': 'https://book.douban.com/subject/20432061/',
                    'cover': 'https://img3.doubanio.com/view/subject/l/public/s26348984.jpg',
                    'author': 'Thomas H.Cormen 等',
                    'publisher': '机械工业出版社',
                    'rating': '9.2',
                    'description': '算法领域的经典之作'
                },
            ],
        }
        
        # 查找匹配的书籍
        keywords_lower = keywords.lower()
        all_matched_books = []
        
        # 使用AI智能匹配书籍分类
        print(f"[DEBUG] 调用AI智能匹配: {keywords}")
        matched_categories = self._ai_match_categories(keywords)
        
        # 根据AI推荐的分类查找书籍
        if matched_categories:
            for category in matched_categories:
                if category in book_database:
                    all_matched_books.extend(book_database[category])
                    print(f"[DEBUG] 从分类 '{category}' 找到 {len(book_database[category])} 本书")
        
        # 如果AI匹配失败或没有找到书籍，尝试关键词直接匹配
        if not all_matched_books:
            print(f"[DEBUG] AI匹配无结果，尝试关键词直接匹配")
            for key, books in book_database.items():
                if key in keywords_lower:
                    all_matched_books.extend(books)
                    print(f"[DEBUG] 关键词匹配到分类 '{key}'，找到 {len(books)} 本书")
        
        # 如果还是没有匹配到，使用AI生成书籍推荐
        if not all_matched_books:
            print(f"[DEBUG] 数据库无匹配，调用AI生成书籍推荐")
            all_matched_books = self._ai_generate_books(keywords)
        
        # 根据页码返回不同的书籍子集
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # 如果数据库书籍已经用完（或快用完），调用AI生成新书籍
        if start_idx >= len(all_matched_books):
            print(f"[DEBUG] 数据库书籍已耗尽（共{len(all_matched_books)}本，请求索引{start_idx}），调用AI生成新书籍")
            ai_books = self._ai_generate_books(keywords)
            print(f"[DEBUG] AI生成了 {len(ai_books)} 本新书籍")
            return ai_books
        
        matched_books = all_matched_books[start_idx:end_idx]
        
        # 如果不够，先尝试从数据库补充，还不够就AI生成
        if len(matched_books) < limit and len(all_matched_books) > 0:
            remaining_from_db = limit - len(matched_books)
            # 检查数据库是否还有足够的书
            if end_idx < len(all_matched_books):
                # 从数据库补充
                matched_books.extend(all_matched_books[end_idx:end_idx + remaining_from_db])
            else:
                # 数据库不够，AI生成补充
                print(f"[DEBUG] 数据库剩余书籍不足，调用AI生成 {remaining_from_db} 本补充")
                ai_books = self._ai_generate_books(keywords)
                matched_books.extend(ai_books[:remaining_from_db])
        
        print(f"[DEBUG] 书籍库共 {len(all_matched_books)} 本，返回索引 {start_idx}-{end_idx}，实际 {len(matched_books)} 本")
        
        return matched_books


# 单例实例
book_search_service = BookSearchService()

