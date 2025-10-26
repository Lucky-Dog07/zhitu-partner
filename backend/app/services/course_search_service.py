"""
课程搜索服务 - 搜索B站、慕课网、极客时间等平台的课程
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import time
from functools import lru_cache
import json


class CourseSearchService:
    """课程搜索服务"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.timeout = 10
    
    def search_bilibili_courses(
        self, 
        keywords: str, 
        limit: int = 10,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索B站课程
        
        Args:
            keywords: 搜索关键词
            limit: 返回数量限制
            page: 页码（从1开始）
            
        Returns:
            课程列表
        """
        print(f"[DEBUG] 搜索B站课程: {keywords}, 页码: {page}")
        
        try:
            # 根据页码使用不同的排序和筛选策略，增加结果多样性
            sort_orders = ['totalrank', 'click', 'pubdate', 'dm', 'stow']  # 综合、播放量、最新、弹幕、收藏
            durations = [0, 4, 3, 2]  # 全部时长、60分钟+、30-60分钟、10-30分钟
            
            order = sort_orders[(page - 1) % len(sort_orders)]
            duration = durations[(page - 1) % len(durations)]
            
            print(f"[DEBUG] B站搜索策略: 排序={order}, 时长筛选={duration}")
            
            # B站搜索API（视频搜索）
            search_url = "https://api.bilibili.com/x/web-interface/wbi/search/type"
            params = {
                'keyword': f'{keywords}',  # 不再固定加"教程"，让dynamic_resource_service控制
                'search_type': 'video',
                'page': 1,  # 总是第1页，但改变排序和筛选条件
                'page_size': limit,
                'order': order,
                'duration': duration,
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                print(f"[WARN] B站搜索请求失败: {response.status_code}")
                return self._get_bilibili_fallback_results(keywords, limit)
            
            data = response.json()
            
            if data.get('code') != 0:
                print(f"[WARN] B站API返回错误: {data.get('message')}")
                return self._get_bilibili_fallback_results(keywords, limit)
            
            results = data.get('data', {}).get('result', [])
            
            courses = []
            for item in results[:limit]:
                try:
                    # 提取课程信息
                    course = {
                        'title': self._clean_html(item.get('title', '')),
                        'url': item.get('arcurl', f"https://www.bilibili.com/video/{item.get('bvid', '')}"),
                        'cover': f"https:{item.get('pic', '')}" if item.get('pic', '').startswith('//') else item.get('pic', ''),
                        'platform': 'bilibili',
                        'author': item.get('author', ''),
                        'views': self._format_number(item.get('play', 0)),
                        'description': self._clean_html(item.get('description', '')),
                        'duration': self._format_duration(item.get('duration', 0)),
                        'rating': None,  # B站没有评分
                        'publish_time': item.get('pubdate', 0),
                    }
                    courses.append(course)
                except Exception as e:
                    print(f"[WARN] 解析B站课程失败: {e}")
                    continue
            
            print(f"[DEBUG] B站搜索成功，找到 {len(courses)} 个结果")
            return courses
            
        except Exception as e:
            print(f"[ERROR] B站搜索异常: {e}")
            return self._get_bilibili_fallback_results(keywords, limit)
    
    def _get_bilibili_fallback_results(self, keywords: str, limit: int) -> List[Dict]:
        """B站搜索失败时的备选结果（预设优质课程）"""
        fallback_courses = [
            {
                'title': f'{keywords}入门到精通教程',
                'url': f'https://search.bilibili.com/all?keyword={keywords}%20教程',
                'cover': 'https://via.placeholder.com/300x200?text=Bilibili',
                'platform': 'bilibili',
                'author': '优质UP主',
                'views': '点击搜索查看',
                'description': f'在B站搜索 "{keywords}" 相关优质教程',
                'duration': None,
                'rating': None,
            }
        ]
        return fallback_courses[:limit]
    
    def search_imooc_courses(
        self, 
        keywords: str, 
        limit: int = 5,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索慕课网课程
        
        Args:
            keywords: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            课程列表
        """
        print(f"[DEBUG] 搜索慕课网课程: {keywords}")
        
        try:
            # 慕课网搜索页面
            search_url = f"https://www.imooc.com/search/?words={keywords}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code != 200:
                return self._get_imooc_fallback_results(keywords, limit)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            courses = []
            # 查找课程卡片
            course_items = soup.select('.course-card-container')[:limit]
            
            for item in course_items:
                try:
                    title_elem = item.select_one('.course-card-name')
                    url_elem = item.select_one('a')
                    cover_elem = item.select_one('.course-card-top img')
                    price_elem = item.select_one('.course-card-price')
                    
                    if title_elem and url_elem:
                        course = {
                            'title': title_elem.text.strip(),
                            'url': 'https://www.imooc.com' + url_elem.get('href', ''),
                            'cover': cover_elem.get('src', '') if cover_elem else '',
                            'platform': 'imooc',
                            'author': '慕课网',
                            'views': price_elem.text.strip() if price_elem else '查看详情',
                            'description': f'{keywords}相关课程',
                            'duration': None,
                            'rating': None,
                        }
                        courses.append(course)
                except Exception as e:
                    print(f"[WARN] 解析慕课网课程失败: {e}")
                    continue
            
            if courses:
                print(f"[DEBUG] 慕课网搜索成功，找到 {len(courses)} 个结果")
                return courses
            else:
                return self._get_imooc_fallback_results(keywords, limit)
            
        except Exception as e:
            print(f"[ERROR] 慕课网搜索异常: {e}")
            return self._get_imooc_fallback_results(keywords, limit)
    
    def _get_imooc_fallback_results(self, keywords: str, limit: int) -> List[Dict]:
        """慕课网搜索失败时的备选结果"""
        fallback_courses = [
            {
                'title': f'{keywords}系统课程',
                'url': f'https://www.imooc.com/search/?words={keywords}',
                'cover': 'https://via.placeholder.com/300x200?text=imooc',
                'platform': 'imooc',
                'author': '慕课网',
                'views': '点击搜索查看',
                'description': f'在慕课网搜索 "{keywords}" 相关课程',
                'duration': None,
                'rating': None,
            }
        ]
        return fallback_courses[:limit]
    
    def search_geekbang_courses(
        self, 
        keywords: str, 
        limit: int = 3,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索极客时间课程
        
        Args:
            keywords: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            课程列表
        """
        print(f"[DEBUG] 搜索极客时间课程: {keywords}")
        
        # 极客时间需要登录，使用备选方案
        return self._get_geekbang_fallback_results(keywords, limit)
    
    def _get_geekbang_fallback_results(self, keywords: str, limit: int) -> List[Dict]:
        """极客时间备选结果"""
        fallback_courses = [
            {
                'title': f'{keywords}专栏课程',
                'url': f'https://time.geekbang.org/search?q={keywords}',
                'cover': 'https://via.placeholder.com/300x200?text=GeekBang',
                'platform': 'geekbang',
                'author': '极客时间',
                'views': '点击搜索查看',
                'description': f'在极客时间搜索 "{keywords}" 相关专栏',
                'duration': None,
                'rating': None,
            }
        ]
        return fallback_courses[:limit]
    
    def search_all_courses(
        self, 
        keywords: str,
        platforms: List[str] = ['bilibili', 'imooc', 'geekbang']
    ) -> List[Dict[str, Any]]:
        """
        搜索所有平台的课程
        
        Args:
            keywords: 搜索关键词
            platforms: 平台列表
            
        Returns:
            所有平台的课程列表
        """
        all_courses = []
        
        if 'bilibili' in platforms:
            bilibili_courses = self.search_bilibili_courses(keywords, limit=10)
            all_courses.extend(bilibili_courses)
            time.sleep(0.5)  # 避免请求过快
        
        if 'imooc' in platforms:
            imooc_courses = self.search_imooc_courses(keywords, limit=5)
            all_courses.extend(imooc_courses)
            time.sleep(0.5)
        
        if 'geekbang' in platforms:
            geekbang_courses = self.search_geekbang_courses(keywords, limit=3)
            all_courses.extend(geekbang_courses)
        
        return all_courses
    
    def _clean_html(self, html_text: str) -> str:
        """清理HTML标签"""
        if not html_text:
            return ''
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        # 解码HTML实体
        clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return clean_text.strip()
    
    def _format_number(self, num: int) -> str:
        """格式化播放量"""
        if num >= 10000:
            return f'{num / 10000:.1f}万'
        return str(num)
    
    def _format_duration(self, seconds: int) -> Optional[str]:
        """格式化时长"""
        if not seconds or seconds == 0:
            return None
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f'{hours}小时{minutes}分钟'
        return f'{minutes}分钟'


# 单例实例
course_search_service = CourseSearchService()

