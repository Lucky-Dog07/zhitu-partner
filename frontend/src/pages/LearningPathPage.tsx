import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Spin, Typography, message, Divider, Tag, Tabs } from 'antd';
import { 
  ArrowLeftOutlined, 
  ApartmentOutlined, 
  FileTextOutlined,
  QuestionCircleOutlined,
  ShoppingOutlined,
  BookOutlined,
  LinkOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MindMap from '../components/MindMap';
import KnowledgeTab from '../components/KnowledgeTab';
import InterviewTab from '../components/InterviewTab';
import ResourcesTab from '../components/ResourcesTab';
import { learningPathAPI } from '../services/api';
import type { LearningPath } from '../types';
import { useTechLinkEnhancer } from '../hooks/useTechLinkEnhancer';

const { Title, Paragraph } = Typography;

const LearningPathPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadLearningPath();
  }, [id]);
  
  const loadLearningPath = async () => {
    if (!id) return;
    
    try {
      const data = await learningPathAPI.get(parseInt(id));
      console.log('[DEBUG] 加载的学习路线数据:', data);
      console.log('[DEBUG] generated_content:', data.generated_content);
      setLearningPath(data);
    } catch (error: any) {
      message.error('加载失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 处理内容生成完成的回调
  const handleContentGenerated = (newContent?: any) => {
    console.log('[DEBUG] handleContentGenerated 被调用，新内容:', newContent);
    // 直接重新加载学习路线数据
    loadLearningPath();
  };
  
  // 处理课程生成的回调
  const handleCoursesGenerated = (courses: any) => {
    console.log('[DEBUG] ========== 课程生成回调开始 ==========');
    console.log('[DEBUG] 接收到的课程数据:', courses);
    console.log('[DEBUG] 课程数量:', courses?.length);
    console.log('[DEBUG] 当前learningPath:', learningPath);
    console.log('[DEBUG] 当前课程数量:', learningPath?.generated_content?.courses?.length);
    
    if (learningPath && courses) {
      const newLearningPath = {
        ...learningPath,
        generated_content: {
          ...learningPath.generated_content,
          courses: courses
        }
      };
      console.log('[DEBUG] 更新后的learningPath:', newLearningPath);
      console.log('[DEBUG] 更新后的课程数量:', newLearningPath.generated_content.courses?.length);
      
      // 直接更新状态
      setLearningPath(newLearningPath);
      console.log('[DEBUG] ========== 课程生成回调结束 ==========');
    }
  };
  
  // 处理书籍生成的回调
  const handleBooksGenerated = (books: any) => {
    console.log('[DEBUG] 书籍生成回调，新书籍数量:', books?.length);
    if (learningPath && books) {
      setLearningPath({
        ...learningPath,
        generated_content: {
          ...learningPath.generated_content,
          books: books
        }
      });
    }
  };
  
  // 处理证书生成的回调
  const handleCertificationsGenerated = (certifications: any) => {
    console.log('[DEBUG] 证书生成回调，新证书数量:', certifications?.length);
    if (learningPath && certifications) {
      setLearningPath({
        ...learningPath,
        generated_content: {
          ...learningPath.generated_content,
          certifications: certifications
        }
      });
    }
  };
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }
  
  if (!learningPath) {
    return (
      <Card>
        <p>学习路线不存在</p>
        <Button onClick={() => navigate('/')}>返回首页</Button>
      </Card>
    );
  }
  
  // 解析生成的内容
  const content = learningPath.generated_content;
  const output = content?.data?.output || content?.output || '暂无内容';
  
  // 使用Hook增强Markdown内容，自动添加技术链接
  const { enhancedMarkdown: enhancedOutput, loading: linkLoading, error: linkError } = useTechLinkEnhancer(output);
  
  // 提取各类型内容
  const knowledgeContent = content?.knowledge;
  const interviewContent = content?.interview;
  const courses = content?.courses;
  const books = content?.books;
  const certifications = content?.certifications;
  
  console.log('[DEBUG] 提取的内容:');
  console.log('  - knowledge:', knowledgeContent ? '有内容' : '无内容');
  console.log('  - interview:', interviewContent ? '有内容' : '无内容');
  console.log('  - courses:', courses);
  console.log('  - books:', books);
  
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 20, display: 'flex', gap: 12 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
        >
          返回首页
        </Button>
        <Button
          type="primary"
          danger
          icon={<ExclamationCircleOutlined />}
          onClick={() => navigate(`/mistakes/${id}`)}
        >
          查看错题本
        </Button>
      </div>
      
      <Card>
        <Title level={2}>
          <BookOutlined /> {learningPath.position}
        </Title>
        
        <div style={{ marginBottom: 20 }}>
          <Tag color="blue">生成时间: {new Date(learningPath.created_at).toLocaleString('zh-CN')}</Tag>
        </div>
        
        {learningPath.job_description && (
          <>
            <Title level={4}>职位描述</Title>
            <Paragraph style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
              {learningPath.job_description}
            </Paragraph>
            <Divider />
          </>
        )}
        
        <Title level={4}>学习内容</Title>
        <Tabs
          defaultActiveKey="mindmap"
          items={[
            {
              key: 'mindmap',
              label: (
                <span>
                  <ApartmentOutlined />
                  思维导图
                </span>
              ),
              children: (
                <div style={{ padding: '20px 0' }}>
                  {linkLoading && (
                    <div style={{ 
                      padding: 12, 
                      marginBottom: 16,
                      background: '#fff7e6', 
                      borderRadius: 4,
                      fontSize: 14,
                      color: '#d46b08',
                      textAlign: 'center'
                    }}>
                      AI正在智能生成技术文档链接...
                    </div>
                  )}
                  {linkError && (
                    <div style={{ 
                      padding: 12, 
                      marginBottom: 16,
                      background: '#fff1f0', 
                      borderRadius: 4,
                      fontSize: 14,
                      color: '#cf1322',
                      textAlign: 'center'
                    }}>
                      链接生成失败，显示原始内容
                    </div>
                  )}
                  <MindMap markdown={enhancedOutput} height={700} />
                  <div style={{ 
                    marginTop: 16, 
                    padding: 12, 
                    background: '#e6f4ff', 
                    borderRadius: 4,
                    fontSize: 14,
                    color: '#1677ff'
                  }}>
                    提示：
                    <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
                      <li>单击节点：折叠/展开子节点</li>
                      <li>双击蓝色链接：跳转到技术文档（由AI智能生成）</li>
                      <li>拖拽：移动视图</li>
                      <li>滚轮：缩放</li>
                    </ul>
                  </div>
                </div>
              )
            },
            {
              key: 'markdown',
              label: (
                <span>
                  <FileTextOutlined />
                  文本视图
                </span>
              ),
              children: (
                <div>
                  {linkLoading && (
                    <div style={{ 
                      padding: 12, 
                      marginBottom: 16,
                      background: '#fff7e6', 
                      borderRadius: 4,
                      fontSize: 14,
                      color: '#d46b08',
                      textAlign: 'center'
                    }}>
                      AI正在智能生成技术文档链接...
                    </div>
                  )}
                  {linkError && (
                    <div style={{ 
                      padding: 12, 
                      marginBottom: 16,
                      background: '#fff1f0', 
                      borderRadius: 4,
                      fontSize: 14,
                      color: '#cf1322',
                      textAlign: 'center'
                    }}>
                      链接生成失败，显示原始内容
                    </div>
                  )}
                  <div 
                    style={{ 
                      background: '#fafafa',
                      padding: 20,
                      borderRadius: 8,
                      border: '1px solid #e8e8e8'
                    }}
                    className="markdown-content"
                  >
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        a: ({ node, href, children, ...props }) => (
                          <a 
                            {...props} 
                            href={href}
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{
                              color: '#1677ff',
                              textDecoration: 'underline',
                              cursor: 'pointer'
                            }}
                          >
                            {children}
                            <LinkOutlined style={{ marginLeft: 4, fontSize: 12 }} />
                          </a>
                        )
                      }}
                    >
                      {enhancedOutput}
                    </ReactMarkdown>
                  </div>
                </div>
              )
            },
            {
              key: 'knowledge',
              label: (
                <span>
                  <FileTextOutlined />
                  知识点详解
                </span>
              ),
              children: (
                <KnowledgeTab
                  pathId={parseInt(id!)}
                  content={knowledgeContent}
                  onContentGenerated={handleContentGenerated}
                />
              )
            },
            {
              key: 'interview',
              label: (
                <span>
                  <QuestionCircleOutlined />
                  面试题库
                </span>
              ),
              children: (
                <InterviewTab
                  pathId={parseInt(id!)}
                />
              )
            },
            {
              key: 'resources',
              label: (
                <span>
                  <ShoppingOutlined />
                  学习资源
                </span>
              ),
              children: (
                <ResourcesTab
                  pathId={parseInt(id!)}
                  courses={courses}
                  books={books}
                  certifications={certifications}
                  onCoursesGenerated={handleCoursesGenerated}
                  onBooksGenerated={handleBooksGenerated}
                  onCertificationsGenerated={handleCertificationsGenerated}
                />
              )
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default LearningPathPage;

