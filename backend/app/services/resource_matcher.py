"""
资源匹配服务 - 智能匹配学习资源
"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path


class ResourceMatcher:
    """资源匹配器 - 根据技能和职位推荐学习资源"""
    
    def __init__(self):
        """初始化资源库"""
        self.resources = self._load_resources()
    
    def _load_resources(self) -> Dict[str, Any]:
        """加载资源库数据"""
        # 获取resources.json的路径
        current_dir = Path(__file__).parent.parent
        resource_file = current_dir / "data" / "resources.json"
        
        try:
            with open(resource_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"courses": {}, "books": {}, "certifications": {}}
    
    def _calculate_relevance(self, resource: Dict[str, Any], skills: List[str]) -> float:
        """
        计算资源与技能的相关性分数
        
        Args:
            resource: 资源对象
            skills: 技能列表
            
        Returns:
            相关性分数 (0-1)
        """
        if not skills:
            return 0.0
        
        resource_tags = [tag.lower() for tag in resource.get('tags', [])]
        resource_title = resource.get('title', '').lower()
        resource_desc = resource.get('description', '').lower()
        
        score = 0.0
        matched_skills = 0
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # 技能在tags中匹配 (权重: 3)
            if skill_lower in resource_tags:
                score += 3.0
                matched_skills += 1
            
            # 技能在标题中匹配 (权重: 2)
            elif skill_lower in resource_title:
                score += 2.0
                matched_skills += 1
            
            # 技能在描述中匹配 (权重: 1)
            elif skill_lower in resource_desc:
                score += 1.0
                matched_skills += 1
        
        # 归一化分数
        max_score = len(skills) * 3.0
        return score / max_score if max_score > 0 else 0.0
    
    def _filter_by_level(self, resources: List[Dict], level: str = None) -> List[Dict]:
        """根据难度级别过滤资源"""
        if not level:
            return resources
        return [r for r in resources if r.get('level') == level]
    
    def _sort_by_rating(self, resources: List[Dict]) -> List[Dict]:
        """按评分排序"""
        return sorted(resources, key=lambda x: x.get('rating', 0), reverse=True)
    
    def match_courses(
        self, 
        skills: List[str], 
        level: str = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        匹配课程资源
        
        Args:
            skills: 技能列表
            level: 难度级别 (beginner/intermediate/advanced)
            limit: 返回数量限制
            
        Returns:
            匹配的课程列表
        """
        all_courses = []
        
        # 收集所有类别的课程
        for category, courses in self.resources.get('courses', {}).items():
            all_courses.extend(courses)
        
        # 计算每个课程的相关性分数
        scored_courses = []
        for course in all_courses:
            relevance = self._calculate_relevance(course, skills)
            if relevance > 0:  # 只保留有相关性的课程
                course_with_score = course.copy()
                course_with_score['relevance_score'] = relevance
                scored_courses.append(course_with_score)
        
        # 按相关性和评分排序
        scored_courses.sort(
            key=lambda x: (x['relevance_score'], x.get('rating', 0)), 
            reverse=True
        )
        
        # 过滤难度级别
        if level:
            scored_courses = self._filter_by_level(scored_courses, level)
        
        return scored_courses[:limit]
    
    def match_books(
        self, 
        skills: List[str], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        匹配书籍资源
        
        Args:
            skills: 技能列表
            limit: 返回数量限制
            
        Returns:
            匹配的书籍列表
        """
        all_books = []
        
        # 收集所有类别的书籍
        for category, books in self.resources.get('books', {}).items():
            all_books.extend(books)
        
        # 计算相关性并排序
        scored_books = []
        for book in all_books:
            relevance = self._calculate_relevance(book, skills)
            if relevance > 0:
                book_with_score = book.copy()
                book_with_score['relevance_score'] = relevance
                scored_books.append(book_with_score)
        
        scored_books.sort(
            key=lambda x: (x['relevance_score'], x.get('rating', 0)), 
            reverse=True
        )
        
        return scored_books[:limit]
    
    def match_certifications(
        self, 
        skills: List[str], 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        匹配职业证书
        
        Args:
            skills: 技能列表
            limit: 返回数量限制
            
        Returns:
            匹配的证书列表
        """
        all_certs = []
        
        # 收集所有类别的证书
        for category, certs in self.resources.get('certifications', {}).items():
            all_certs.extend(certs)
        
        # 计算相关性并排序
        scored_certs = []
        for cert in all_certs:
            relevance = self._calculate_relevance(cert, skills)
            if relevance > 0:
                cert_with_score = cert.copy()
                cert_with_score['relevance_score'] = relevance
                scored_certs.append(cert_with_score)
        
        scored_certs.sort(
            key=lambda x: (x['relevance_score'], x.get('rating', 0)), 
            reverse=True
        )
        
        return scored_certs[:limit]
    
    def get_all_resources(
        self, 
        skills: List[str], 
        level: str = None
    ) -> Dict[str, List[Dict]]:
        """
        获取所有类型的匹配资源
        
        Args:
            skills: 技能列表
            level: 难度级别
            
        Returns:
            包含courses, books, certifications的字典
        """
        return {
            "courses": self.match_courses(skills, level),
            "books": self.match_books(skills),
            "certifications": self.match_certifications(skills)
        }


# 单例实例
resource_matcher = ResourceMatcher()

