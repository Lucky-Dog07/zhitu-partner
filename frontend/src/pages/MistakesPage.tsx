import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  Empty, 
  message, 
  Spin, 
  Typography, 
  Space,
  Tag,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  ArrowLeftOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import InterviewCardView from '../components/InterviewCardView';
import { interviewAPI } from '../services/interviewAPI';
import type { InterviewQuestion, QuestionStatus } from '../types/interview';

const { Title, Paragraph } = Typography;

const MistakesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // 加载错题
  const loadMistakes = async () => {
    setLoading(true);
    try {
      if (id) {
        // 如果有 ID，获取特定学习路线的错题
        const response = await interviewAPI.getQuestions(
          parseInt(id),
          'not_mastered',
          500
        );
        setQuestions(response.questions);
      } else {
        // 如果没有 ID，获取所有错题
        const response = await interviewAPI.getAllMistakes(500, 0);
        setQuestions(response.questions);
      }
      setCurrentIndex(0);
    } catch (error: any) {
      message.error('加载失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMistakes();
  }, [id]);

  // 更新题目状态
  const handleStatusChange = async (questionId: number, status: QuestionStatus) => {
    try {
      await interviewAPI.updateStatus({ question_id: questionId, status });
      
      // 如果标记为已掌握，从列表中移除
      if (status === 'mastered') {
        setQuestions(prev => prev.filter(q => q.id !== questionId));
        // 如果当前题目被移除，跳到下一题
        if (currentIndex >= questions.length - 1) {
          setCurrentIndex(Math.max(0, questions.length - 2));
        }
        message.success('已移出错题本');
      } else {
        // 更新状态
        setQuestions(prev => prev.map(q => 
          q.id === questionId 
            ? { ...q, user_status: status, review_count: q.review_count + 1 } 
            : q
        ));
        message.success('已更新状态');
      }
    } catch (error: any) {
      message.error('更新失败：' + (error.response?.data?.detail || '未知错误'));
    }
  };

  // 根据错题生成针对性题目
  const handleGenerateFromMistakes = async () => {
    if (!id) return;
    
    setGenerating(true);
    try {
      const response = await interviewAPI.generateWeakPointsQuestions(parseInt(id), 20);
      message.success(response.message + '，请返回面试题库查看');
      
      // 提示用户返回
      setTimeout(() => {
        navigate(`/learning-path/${id}`);
      }, 2000);
    } catch (error: any) {
      message.error('生成失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      {id && (
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/learning-path/${id}`)}
          style={{ marginBottom: 20 }}
        >
          返回学习路线
        </Button>
      )}

      <Card style={{ marginBottom: 24 }}>
        <Title level={2}>
          <CloseCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
          {id ? '错题本' : '全部错题'}
        </Title>
        <Paragraph type="secondary">
          {id ? '专注复习未掌握的题目，巩固薄弱知识点' : '复习所有学习路线中未掌握的题目'}
        </Paragraph>

        <Row gutter={16} style={{ marginTop: 24 }}>
          <Col span={12}>
            <Statistic
              title="待掌握题目"
              value={questions.length}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Col>
          {id && (
            <Col span={12}>
              <Space>
                <Button
                  type="primary"
                  icon={<BulbOutlined />}
                  onClick={handleGenerateFromMistakes}
                  loading={generating}
                  disabled={questions.length === 0}
                >
                  根据错题生成新题
                </Button>
              </Space>
            </Col>
          )}
        </Row>
      </Card>

      <Spin spinning={loading}>
        {questions.length === 0 ? (
          <Card>
            <Empty
              description={
                <div>
                  <p style={{ fontSize: 16, marginBottom: 10 }}>
                    恭喜！暂无错题
                  </p>
                  <p style={{ color: '#666' }}>
                    继续努力，保持好成绩
                  </p>
                </div>
              }
            >
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={() => navigate(`/learning-path/${id}`)}
              >
                返回刷题
              </Button>
            </Empty>
          </Card>
        ) : (
          <>
            <div style={{ marginBottom: 16, padding: 12, background: '#fff7e6', borderRadius: 4 }}>
              <Space>
                <BulbOutlined style={{ color: '#faad14' }} />
                <span style={{ color: '#d46b08' }}>
                  提示：标记"会了"后，题目将从错题本中移除
                </span>
              </Space>
            </div>
            
            <InterviewCardView
              questions={questions}
              currentIndex={currentIndex}
              onNext={() => setCurrentIndex(prev => Math.min(prev + 1, questions.length - 1))}
              onPrevious={() => setCurrentIndex(prev => Math.max(prev - 1, 0))}
              onStatusChange={handleStatusChange}
              loading={loading}
            />
          </>
        )}
      </Spin>
    </div>
  );
};

export default MistakesPage;

