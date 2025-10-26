"""
证书搜索服务 - 搜索职业认证证书
"""
from typing import List, Dict, Any
from functools import lru_cache
import openai
import json
from ..core.config import settings


class CertSearchService:
    """证书搜索服务"""
    
    def __init__(self):
        # 初始化OpenAI客户端（用于AI智能匹配）
        self.openai_client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def _ai_match_categories(self, keywords: str) -> List[str]:
        """
        使用AI智能分析关键词应该匹配哪些证书分类
        
        Args:
            keywords: 搜索关键词（如"AI工程师"、"Java工程师"等）
            
        Returns:
            匹配的证书分类列表
        """
        available_categories = ['ai', 'java', 'python', 'aws', '数据库', '项目管理']
        
        prompt = f"""你是一个职业认证分析专家。根据给定的职位/关键词，分析它需要哪些技术方向的职业认证证书。

可用的证书分类：{', '.join(available_categories)}

职位/关键词：{keywords}

请分析这个职位/关键词最需要哪些技术方向的证书。按重要性排序，返回最相关的2-3个分类。

要求：
1. 只返回JSON格式：{{"categories": ["分类1", "分类2", ...]}}
2. 分类必须从可用列表中选择
3. 按重要性排序（最重要的放前面）

示例：
- "AI工程师" → {{"categories": ["ai", "python", "aws"]}}
- "Java工程师" → {{"categories": ["java", "数据库"]}}
- "项目经理" → {{"categories": ["项目管理"]}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个职业认证分析专家。只返回JSON格式，不要有其他内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_output = response.choices[0].message.content.strip()
            print(f"[DEBUG] AI匹配证书分类结果: {ai_output}")
            
            result = json.loads(ai_output)
            categories = result.get('categories', [])
            valid_categories = [cat for cat in categories if cat in available_categories]
            
            print(f"[DEBUG] AI推荐的证书分类: {valid_categories}")
            return valid_categories
            
        except Exception as e:
            print(f"[ERROR] AI匹配证书分类失败: {e}")
            keywords_lower = keywords.lower()
            matched = []
            for cat in available_categories:
                if cat in keywords_lower:
                    matched.append(cat)
            return matched if matched else ['python']
    
    def _ai_generate_certifications(self, keywords: str) -> List[Dict[str, Any]]:
        """
        使用AI生成证书推荐（当数据库没有匹配时）
        
        Args:
            keywords: 搜索关键词
            
        Returns:
            AI生成的证书列表
        """
        import time
        
        diversity_seed = int(time.time()) % 100
        print(f"[DEBUG] AI证书生成 (种子={diversity_seed})")
        
        prompt = f"""你是一个职业认证专家。请为"{keywords}"相关的职位/技能推荐3个真实存在的职业认证证书。

要求：
1. 推荐真实存在的、权威的职业认证
2. 包含国际认证和国内认证
3. 返回JSON格式：

{{
  "certifications": [
    {{
      "title": "证书全称",
      "issuer": "颁发机构",
      "description": "一句话简介（20字以内）",
      "level": "级别（如：专业级、助理级）",
      "validity": "有效期（如：3年、永久有效）",
      "url": "官方链接"
    }}
  ]
}}

职位/技能：{keywords}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个职业认证专家。只返回JSON格式，不要有其他内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_output = response.choices[0].message.content.strip()
            print(f"[DEBUG] AI生成证书推荐: {ai_output[:150]}...")
            
            # 清理markdown代码块
            if ai_output.startswith('```'):
                lines = ai_output.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                ai_output = '\n'.join(lines).strip()
            
            result = json.loads(ai_output)
            certs = result.get('certifications', [])
            
            print(f"[DEBUG] AI生成了 {len(certs)} 个证书")
            return certs
            
        except Exception as e:
            print(f"[ERROR] AI生成证书失败: {e}")
            return [
                {
                    'title': f'{keywords}相关职业认证',
                    'url': f'https://www.google.com/search?q={keywords}+职业认证+证书',
                    'issuer': '各认证机构',
                    'description': f'搜索 "{keywords}" 相关的职业认证证书',
                    'level': '各级别',
                    'validity': '查看详情',
                }
            ]
    
    def search_certifications(
        self, 
        keywords: str, 
        limit: int = 3,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索职业认证证书
        
        Args:
            keywords: 搜索关键词
            limit: 返回数量限制
            page: 页码（从1开始）
            
        Returns:
            证书列表
        """
        print(f"[DEBUG] 搜索职业证书: {keywords}, 页码: {page}")
        
        # 证书数据库（根据关键词匹配） - 扩展为每个技术多个证书
        cert_database = {
            'ai': [
                {
                    'title': 'TensorFlow Developer Certificate',
                    'url': 'https://www.tensorflow.org/certificate',
                    'issuer': 'Google/TensorFlow',
                    'description': 'Google官方TensorFlow开发者认证',
                    'level': '专业级',
                    'validity': '3年',
                },
                {
                    'title': 'AWS Certified Machine Learning - Specialty',
                    'url': 'https://aws.amazon.com/certification/certified-machine-learning-specialty/',
                    'issuer': 'Amazon Web Services',
                    'description': 'AWS机器学习专业认证',
                    'level': '专业级',
                    'validity': '3年',
                },
                {
                    'title': 'Microsoft Certified: Azure AI Engineer Associate',
                    'url': 'https://learn.microsoft.com/en-us/certifications/azure-ai-engineer/',
                    'issuer': 'Microsoft',
                    'description': 'Azure AI工程师认证',
                    'level': '助理级',
                    'validity': '2年',
                },
                {
                    'title': 'Google Cloud Professional Machine Learning Engineer',
                    'url': 'https://cloud.google.com/certification/machine-learning-engineer',
                    'issuer': 'Google Cloud',
                    'description': 'GCP专业机器学习工程师认证',
                    'level': '专业级',
                    'validity': '2年',
                },
            ],
            'java': [
                {
                    'title': 'Oracle Certified Professional: Java SE Programmer',
                    'url': 'https://education.oracle.com/java-se-11-developer/pexam_1Z0-819',
                    'issuer': 'Oracle',
                    'description': 'Oracle官方Java SE认证',
                    'level': '专业级',
                    'validity': '永久有效',
                },
                {
                    'title': 'Oracle Certified Master: Java EE Enterprise Architect',
                    'url': 'https://education.oracle.com/oracle-certified-master-java-ee-6-enterprise-architect/trackp_900',
                    'issuer': 'Oracle',
                    'description': 'Java EE企业架构师认证',
                    'level': '专家级',
                    'validity': '永久有效',
                },
                {
                    'title': 'Spring Professional Certification',
                    'url': 'https://spring.io/certifications',
                    'issuer': 'VMware/Spring',
                    'description': 'Spring框架专业认证',
                    'level': '专业级',
                    'validity': '2年',
                },
            ],
            'python': [
                {
                    'title': 'Python Institute认证',
                    'url': 'https://pythoninstitute.org/pcap',
                    'cover': 'https://via.placeholder.com/200x150?text=Python+Institute',
                    'issuer': 'Python Institute',
                    'description': 'Python编程认证',
                    'level': '专业级',
                    'validity': '永久有效',
                },
            ],
            'aws': [
                {
                    'title': 'AWS Certified Solutions Architect',
                    'url': 'https://aws.amazon.com/cn/certification/certified-solutions-architect-associate/',
                    'cover': 'https://via.placeholder.com/200x150?text=AWS',
                    'issuer': 'Amazon Web Services',
                    'description': 'AWS解决方案架构师认证',
                    'level': '助理级',
                    'validity': '3年',
                },
            ],
            '数据库': [
                {
                    'title': 'MySQL Database Administrator认证',
                    'url': 'https://www.mysql.com/certification/',
                    'cover': 'https://via.placeholder.com/200x150?text=MySQL',
                    'issuer': 'Oracle',
                    'description': 'MySQL数据库管理员认证',
                    'level': '专业级',
                    'validity': '永久有效',
                },
            ],
            '项目管理': [
                {
                    'title': 'PMP项目管理专业人士认证',
                    'url': 'https://www.pmi.org/certifications/project-management-pmp',
                    'cover': 'https://via.placeholder.com/200x150?text=PMP',
                    'issuer': 'PMI',
                    'description': '项目管理专业人士资格认证',
                    'level': '专业级',
                    'validity': '3年',
                },
            ],
        }
        
        # 使用AI智能匹配证书分类
        print(f"[DEBUG] 调用AI智能匹配证书分类: {keywords}")
        matched_categories = self._ai_match_categories(keywords)
        
        # 根据AI推荐的分类查找证书
        all_matched_certs = []
        if matched_categories:
            for category in matched_categories:
                if category in cert_database:
                    all_matched_certs.extend(cert_database[category])
                    print(f"[DEBUG] 从分类 '{category}' 找到 {len(cert_database[category])} 个证书")
        
        # 如果AI匹配失败或没有找到证书，尝试关键词直接匹配
        if not all_matched_certs:
            print(f"[DEBUG] AI匹配无结果，尝试关键词直接匹配")
            keywords_lower = keywords.lower()
            for key, certs in cert_database.items():
                if key in keywords_lower:
                    all_matched_certs.extend(certs)
                    print(f"[DEBUG] 关键词匹配到分类 '{key}'，找到 {len(certs)} 个证书")
        
        # 如果还是没有匹配到，使用AI生成证书推荐
        if not all_matched_certs:
            print(f"[DEBUG] 数据库无匹配，调用AI生成证书推荐")
            all_matched_certs = self._ai_generate_certifications(keywords)
        
        # 根据页码返回不同的证书子集
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # 如果数据库证书已经用完，调用AI生成新证书
        if start_idx >= len(all_matched_certs):
            print(f"[DEBUG] 数据库证书已耗尽（共{len(all_matched_certs)}个，请求索引{start_idx}），调用AI生成新证书")
            ai_certs = self._ai_generate_certifications(keywords)
            print(f"[DEBUG] AI生成了 {len(ai_certs)} 个新证书")
            return ai_certs
        
        matched_certs = all_matched_certs[start_idx:end_idx]
        
        # 如果不够，先尝试从数据库补充，还不够就AI生成
        if len(matched_certs) < limit and len(all_matched_certs) > 0:
            remaining_from_db = limit - len(matched_certs)
            if end_idx < len(all_matched_certs):
                matched_certs.extend(all_matched_certs[end_idx:end_idx + remaining_from_db])
            else:
                print(f"[DEBUG] 数据库剩余证书不足，调用AI生成 {remaining_from_db} 个补充")
                ai_certs = self._ai_generate_certifications(keywords)
                matched_certs.extend(ai_certs[:remaining_from_db])
        
        print(f"[DEBUG] 证书库共 {len(all_matched_certs)} 个，返回索引 {start_idx}-{end_idx}，实际 {len(matched_certs)} 个")
        
        return matched_certs


# 单例实例
cert_search_service = CertSearchService()

