// import { useMemo } from 'react';

/**
 * 资源类型定义
 */
interface TechResource {
  url: string;
  type: 'official' | 'tutorial' | 'video' | 'book' | 'course';
  title?: string;
  lang?: 'zh' | 'en';
}

/**
 * 多资源类型映射表
 * 每个技术可以有多种学习资源
 */
const TECH_RESOURCES_MAP: Record<string, TechResource[]> = {
  // 前端基础 - 多资源示例
  'html': [
    { url: 'https://developer.mozilla.org/zh-CN/docs/Web/HTML', type: 'official', title: 'MDN HTML文档', lang: 'zh' },
    { url: 'https://www.runoob.com/html/html-tutorial.html', type: 'tutorial', title: '菜鸟教程', lang: 'zh' },
  ],
  'css': [
    { url: 'https://developer.mozilla.org/zh-CN/docs/Web/CSS', type: 'official', lang: 'zh' },
    { url: 'https://css-tricks.com/', type: 'tutorial', lang: 'en' },
  ],
  'javascript': [
    { url: 'https://developer.mozilla.org/zh-CN/docs/Web/JavaScript', type: 'official', lang: 'zh' },
    { url: 'https://javascript.info/', type: 'tutorial', title: 'JavaScript.info', lang: 'en' },
  ],
  'typescript': [
    { url: 'https://www.typescriptlang.org/zh/docs/', type: 'official', lang: 'zh' },
    { url: 'https://typescript.tv/', type: 'video', lang: 'en' },
  ],
  
  // 前端框架
  'react': [
    { url: 'https://react.dev/', type: 'official', lang: 'en' },
    { url: 'https://zh-hans.react.dev/', type: 'official', lang: 'zh' },
  ],
  'vue': [
    { url: 'https://cn.vuejs.org/', type: 'official', lang: 'zh' },
  ],
  'angular': [
    { url: 'https://angular.io/docs', type: 'official', lang: 'en' },
  ],
  'svelte': [
    { url: 'https://svelte.dev/docs', type: 'official', lang: 'en' },
  ],
  'nextjs': [
    { url: 'https://nextjs.org/docs', type: 'official', lang: 'en' },
  ],
  'next.js': [
    { url: 'https://nextjs.org/docs', type: 'official', lang: 'en' },
  ],
  
  // 前端工具
  'webpack': [
    { url: 'https://webpack.js.org/concepts/', type: 'official', lang: 'en' },
  ],
  'vite': [
    { url: 'https://cn.vitejs.dev/', type: 'official', lang: 'zh' },
  ],
  'tailwind': [
    { url: 'https://tailwindcss.com/docs', type: 'official', lang: 'en' },
  ],
  'sass': [
    { url: 'https://sass-lang.com/documentation/', type: 'official', lang: 'en' },
  ],
  
  // 后端语言
  'python': [
    { url: 'https://docs.python.org/zh-cn/3/', type: 'official', lang: 'zh' },
    { url: 'https://www.liaoxuefeng.com/wiki/1016959663602400', type: 'tutorial', title: '廖雪峰Python教程', lang: 'zh' },
  ],
  'java': [
    { url: 'https://docs.oracle.com/en/java/', type: 'official', lang: 'en' },
  ],
  'go': [
    { url: 'https://go.dev/doc/', type: 'official', lang: 'en' },
    { url: 'https://tour.go-zh.org/', type: 'tutorial', title: 'Go语言之旅', lang: 'zh' },
  ],
  'golang': [
    { url: 'https://go.dev/doc/', type: 'official', lang: 'en' },
  ],
  'rust': [
    { url: 'https://www.rust-lang.org/learn', type: 'official', lang: 'en' },
    { url: 'https://course.rs/', type: 'tutorial', title: 'Rust语言圣经', lang: 'zh' },
  ],
  'php': [
    { url: 'https://www.php.net/manual/zh/', type: 'official', lang: 'zh' },
  ],
  
  // 后端框架
  'django': [
    { url: 'https://docs.djangoproject.com/zh-hans/', type: 'official', lang: 'zh' },
  ],
  'flask': [
    { url: 'https://flask.palletsprojects.com/', type: 'official', lang: 'en' },
  ],
  'fastapi': [
    { url: 'https://fastapi.tiangolo.com/zh/', type: 'official', lang: 'zh' },
  ],
  'spring': [
    { url: 'https://spring.io/guides', type: 'official', lang: 'en' },
  ],
  'express': [
    { url: 'https://expressjs.com/', type: 'official', lang: 'en' },
  ],
  'nestjs': [
    { url: 'https://nestjs.com/', type: 'official', lang: 'en' },
  ],
  
  // 数据库
  'mysql': [
    { url: 'https://dev.mysql.com/doc/', type: 'official', lang: 'en' },
  ],
  'postgresql': [
    { url: 'https://www.postgresql.org/docs/', type: 'official', lang: 'en' },
  ],
  'mongodb': [
    { url: 'https://www.mongodb.com/docs/', type: 'official', lang: 'en' },
  ],
  'redis': [
    { url: 'https://redis.io/docs/', type: 'official', lang: 'en' },
  ],
  'sqlite': [
    { url: 'https://www.sqlite.org/docs.html', type: 'official', lang: 'en' },
  ],
  
  // AI/ML
  'pytorch': [
    { url: 'https://pytorch.org/docs/stable/index.html', type: 'official', lang: 'en' },
  ],
  'tensorflow': [
    { url: 'https://www.tensorflow.org/api_docs', type: 'official', lang: 'en' },
  ],
  'langchain': [
    { url: 'https://python.langchain.com/docs/get_started/introduction', type: 'official', lang: 'en' },
  ],
  'openai': [
    { url: 'https://platform.openai.com/docs/introduction', type: 'official', lang: 'en' },
  ],
  
  // DevOps
  'docker': [
    { url: 'https://docs.docker.com/', type: 'official', lang: 'en' },
  ],
  'kubernetes': [
    { url: 'https://kubernetes.io/zh-cn/docs/', type: 'official', lang: 'zh' },
  ],
  'k8s': [
    { url: 'https://kubernetes.io/zh-cn/docs/', type: 'official', lang: 'zh' },
  ],
  'git': [
    { url: 'https://git-scm.com/doc', type: 'official', lang: 'en' },
    { url: 'https://www.liaoxuefeng.com/wiki/896043488029600', type: 'tutorial', title: '廖雪峰Git教程', lang: 'zh' },
  ],
  'github': [
    { url: 'https://docs.github.com/zh', type: 'official', lang: 'zh' },
  ],
  'nginx': [
    { url: 'https://nginx.org/en/docs/', type: 'official', lang: 'en' },
  ],
};

/**
 * 获取技术关键词的首选资源URL
 * 优先返回中文官方文档，其次英文官方文档
 * 
 * @deprecated 当前使用简化版本的techList，此函数暂时不用
 */
/* function getTechDocUrl(keyword: string): string | null {
  const lowerKeyword = keyword.toLowerCase().trim();
  const resources = TECH_RESOURCES_MAP[lowerKeyword];
  
  if (!resources || resources.length === 0) {
    return null;
  }
  
  // 优先级：中文官方文档 > 英文官方文档 > 中文教程 > 其他
  const zhOfficial = resources.find(r => r.type === 'official' && r.lang === 'zh');
  if (zhOfficial) return zhOfficial.url;
  
  const enOfficial = resources.find(r => r.type === 'official');
  if (enOfficial) return enOfficial.url;
  
  // 返回第一个可用资源
  return resources[0].url;
} */

/**
 * 获取技术关键词的所有资源
 * 用于后续扩展：显示资源选择菜单
 */
export function getTechResources(keyword: string): TechResource[] {
  const lowerKeyword = keyword.toLowerCase().trim();
  return TECH_RESOURCES_MAP[lowerKeyword] || [];
}

/**
 * 技术链接增强Hook - 极简版
 * 
 * 直接返回对象，不使用任何React Hook
 */
export const useTechLinkEnhancer = (markdown: string) => {
  return {
    enhancedMarkdown: markdown || '',
    loading: false,
    error: null
  };
};

/**
 * 扩展功能：动态获取资源（预留接口）
 * 
 * 未来可以接入：
 * - DevDocs API
 * - GitHub API（搜索相关仓库）
 * - YouTube Data API（搜索教程视频）
 * - 自建资源推荐服务
 */
export async function fetchDynamicResources(keyword: string): Promise<TechResource[]> {
  // TODO: 实现动态资源获取
  // 1. 调用搜索API
  // 2. 调用资源聚合服务
  // 3. 返回多种类型的资源
  
  return getTechResources(keyword);
}

export default useTechLinkEnhancer;
