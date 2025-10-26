"""
动态资源搜索服务 - 统一资源搜索接口
"""
from typing import List, Dict, Any
from .course_search_service import course_search_service
from .book_search_service import book_search_service
from .cert_search_service import cert_search_service


class DynamicResourceService:
    """动态资源搜索服务 - 整合课程、书籍、证书搜索"""
    
    def __init__(self):
        self.course_searcher = course_search_service
        self.book_searcher = book_search_service
        self.cert_searcher = cert_search_service
    
    def search_courses(
        self, 
        keywords: List[str], 
        platforms: List[str] = ['bilibili', 'imooc', 'geekbang'],
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索课程
        
        Args:
            keywords: 关键词列表
            platforms: 平台列表
            page: 页码（从1开始）
            
        Returns:
            课程列表
        """
        # 根据页码使用不同的搜索策略，增加结果多样性
        search_strategies = [
            lambda kw: f"{kw[0]} 教程",  # 策略1: 主关键词 + 教程
            lambda kw: f"{' '.join(kw[:2])} 入门",  # 策略2: 前2个关键词 + 入门
            lambda kw: f"{kw[0]} 实战项目",  # 策略3: 主关键词 + 实战项目
            lambda kw: f"{' '.join(kw[:2])} 进阶",  # 策略4: 前2个关键词 + 进阶
            lambda kw: f"{kw[0]} 从零开始",  # 策略5: 主关键词 + 从零开始
            lambda kw: f"{' '.join(kw[:2])} 完整课程",  # 策略6: 前2个关键词 + 完整课程
            lambda kw: f"{kw[0]} 零基础",  # 策略7: 主关键词 + 零基础
            lambda kw: f"{' '.join(kw[:2])} 系统学习",  # 策略8: 前2个关键词 + 系统学习
            lambda kw: f"{kw[0]} 快速入门",  # 策略9: 主关键词 + 快速入门
            lambda kw: f"{' '.join(kw[:2])} 核心技术",  # 策略10: 前2个关键词 + 核心技术
        ]
        
        strategy_func = search_strategies[(page - 1) % len(search_strategies)]
        search_query = strategy_func(keywords)
        
        print(f"[DEBUG] DynamicResourceService 搜索课程: {search_query}, 页码: {page}, 策略: {(page - 1) % len(search_strategies) + 1}")
        
        # 搜索所有平台，并传递页码
        all_courses = []
        for platform in platforms:
            try:
                if platform == 'bilibili':
                    courses = self.course_searcher.search_bilibili_courses(
                        keywords=search_query,
                        limit=5,
                        page=page
                    )
                elif platform == 'imooc':
                    courses = self.course_searcher.search_imooc_courses(
                        keywords=search_query,
                        limit=3,
                        page=page
                    )
                elif platform == 'geekbang':
                    courses = self.course_searcher.search_geekbang_courses(
                        keywords=search_query,
                        limit=2,
                        page=page
                    )
                else:
                    courses = []
                
                all_courses.extend(courses)
            except Exception as e:
                print(f"[ERROR] {platform} 搜索失败: {e}")
        
        return all_courses
    
    def search_books(self, keywords: List[str], page: int = 1) -> List[Dict[str, Any]]:
        """
        搜索书籍
        
        Args:
            keywords: 关键词列表
            page: 页码（从1开始）
            
        Returns:
            书籍列表
        """
        # 合并关键词
        search_query = ' '.join(keywords[:2])  # 最多使用2个关键词
        
        print(f"[DEBUG] DynamicResourceService 搜索书籍: {search_query}, 页码: {page}")
        
        books = self.book_searcher.search_books(
            keywords=search_query,
            limit=5,
            page=page  # 传递页码参数
        )
        
        return books
    
    def search_certifications(self, keywords: List[str], page: int = 1) -> List[Dict[str, Any]]:
        """
        搜索证书
        
        Args:
            keywords: 关键词列表
            page: 页码（从1开始）
            
        Returns:
            证书列表
        """
        # 合并关键词
        search_query = ' '.join(keywords[:2])
        
        print(f"[DEBUG] DynamicResourceService 搜索证书: {search_query}, 页码: {page}")
        
        certs = self.cert_searcher.search_certifications(
            keywords=search_query,
            limit=3,
            page=page  # 传递页码参数
        )
        
        return certs
    
    def search_all_resources(
        self, 
        keywords: List[str],
        platforms: List[str] = ['bilibili', 'imooc', 'geekbang']
    ) -> Dict[str, List[Dict]]:
        """
        搜索所有类型的资源
        
        Args:
            keywords: 关键词列表
            platforms: 课程平台列表
            
        Returns:
            包含courses, books, certifications的字典
        """
        return {
            'courses': self.search_courses(keywords, platforms),
            'books': self.search_books(keywords),
            'certifications': self.search_certifications(keywords),
        }


# 单例实例
dynamic_resource_service = DynamicResourceService()

