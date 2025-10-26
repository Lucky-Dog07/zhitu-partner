import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, List, Button, Typography, Space, Tag, Spin, Empty, Modal, message } from 'antd';
import { BookOutlined, CalendarOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { learningPathAPI } from '../services/api';
import type { LearningPath } from '../types';

const { Title, Paragraph } = Typography;

const LearningPathsListPage: React.FC = () => {
  const navigate = useNavigate();
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 加载学习路线列表
  useEffect(() => {
    loadLearningPaths();
  }, []);
  
  const loadLearningPaths = async () => {
    setLoading(true);
    try {
      const result = await learningPathAPI.list(0, 100);
      setLearningPaths(result.items);
    } catch (error: any) {
      message.error('加载失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeletePath = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个学习路线吗？删除后不可恢复。',
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await learningPathAPI.delete(id);
          message.success('删除成功');
          loadLearningPaths();
        } catch (error: any) {
          message.error('删除失败：' + (error.response?.data?.detail || '未知错误'));
        }
      }
    });
  };
  
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 20px' }}>
      <Card 
        title={
          <Space>
            <BookOutlined />
            <Title level={2} style={{ margin: 0 }}>我的学习路线</Title>
          </Space>
        }
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/')}
          >
            生成新路线
          </Button>
        }
      >
        <Spin spinning={loading}>
          {learningPaths.length === 0 ? (
            <Empty
              description="还没有学习路线"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button type="primary" onClick={() => navigate('/')}>
                立即生成
              </Button>
            </Empty>
          ) : (
            <List
              dataSource={learningPaths}
              renderItem={(path) => (
                <List.Item
                  key={path.id}
                  style={{ 
                    cursor: 'pointer',
                    padding: '16px',
                    borderRadius: '8px',
                    transition: 'background 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f5f5f5';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                  }}
                  onClick={() => navigate(`/learning-path/${path.id}`)}
                  actions={[
                    <Button
                      key="delete"
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => handleDeletePath(path.id, e)}
                    >
                      删除
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <div
                        style={{
                          width: 48,
                          height: 48,
                          borderRadius: '8px',
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <BookOutlined style={{ fontSize: 24, color: 'white' }} />
                      </div>
                    }
                    title={
                      <Space>
                        <span style={{ fontSize: 18, fontWeight: 'bold' }}>
                          {path.position}
                        </span>
                        {path.generated_content?.skills && (
                          <Tag color="blue">
                            {path.generated_content.skills.length} 个技能点
                          </Tag>
                        )}
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        {path.generated_content?.description && (
                          <Paragraph 
                            ellipsis={{ rows: 2 }} 
                            style={{ margin: 0, color: '#666', fontSize: 14 }}
                          >
                            {path.generated_content.description}
                          </Paragraph>
                        )}
                        <Space>
                          <CalendarOutlined style={{ color: '#999' }} />
                          <span style={{ fontSize: 12, color: '#999' }}>
                            创建于 {new Date(path.created_at).toLocaleDateString('zh-CN', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </span>
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default LearningPathsListPage;

