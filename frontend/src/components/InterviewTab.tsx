import React, { useState, useEffect } from 'react';
import { 
  Empty, 
  Button, 
  Space, 
  Segmented, 
  Select, 
  message, 
  Statistic, 
  Row, 
  Col, 
  Card,
  Spin
} from 'antd';
import {
  AppstoreOutlined,
  UnorderedListOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons';
import InterviewCardView from './InterviewCardView';
import InterviewListView from './InterviewListView';
import { interviewAPI } from '../services/interviewAPI';
import type { 
  InterviewQuestion, 
  InterviewStatistics,
  QuestionStatus 
} from '../types/interview';

interface InterviewTabProps {
  pathId: number;
}

const InterviewTab: React.FC<InterviewTabProps> = ({ pathId }) => {
  const [viewMode, setViewMode] = useState<'card' | 'list'>('card');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [statistics, setStatistics] = useState<InterviewStatistics | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // 加载题目
  const loadQuestions = async () => {
    setLoading(true);
    try {
      const response = await interviewAPI.getQuestions(pathId, statusFilter === 'all' ? undefined : statusFilter);
      setQuestions(response.questions);
      setStatistics(response.statistics);
      setCurrentIndex(0);
    } catch (error: any) {
      message.error('加载题目失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, [pathId, statusFilter]);

  // 生成题目
  const handleGenerate = async (count: number = 20, basedOnWeakPoints: boolean = false) => {
    setGenerating(true);
    try {
      let response;
      if (basedOnWeakPoints) {
        response = await interviewAPI.generateWeakPointsQuestions(pathId, count);
      } else {
        response = await interviewAPI.generateQuestions({
          learning_path_id: pathId,
          count
        });
      }
      
      message.success(response.message);
      await loadQuestions();
    } catch (error: any) {
      message.error('生成失败：' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setGenerating(false);
    }
  };

  // 更新题目状态
  const handleStatusChange = async (questionId: number, status: QuestionStatus) => {
    try {
      await interviewAPI.updateStatus({ question_id: questionId, status });
      
      // 更新本地状态
      setQuestions(prev => prev.map(q => 
        q.id === questionId 
          ? { ...q, user_status: status, review_count: q.review_count + 1 } 
          : q
      ));
      
      // 刷新统计
      const stats = await interviewAPI.getStatistics(pathId);
      setStatistics(stats);
      
      message.success(status === 'mastered' ? '标记为已掌握' : '标记为未掌握');
    } catch (error: any) {
      message.error('更新失败：' + (error.response?.data?.detail || '未知错误'));
    }
  };

  // 如果没有题目
  if (!loading && questions.length === 0 && statusFilter === 'all') {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <Empty
          description={
            <div>
              <p style={{ fontSize: 16, marginBottom: 20 }}>
                还没有面试题
              </p>
              <p style={{ color: '#666', marginBottom: 30 }}>
                点击下方按钮生成题目，开始刷题之旅
              </p>
            </div>
          }
        >
          <Space>
            <Button
              type="primary"
              size="large"
              icon={<ThunderboltOutlined />}
              onClick={() => handleGenerate(20, false)}
              loading={generating}
            >
              生成20道题目
            </Button>
          </Space>
        </Empty>
      </div>
    );
  }

  return (
    <div>
      {/* 统计面板 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总题数"
                value={statistics.total}
                prefix={<AppstoreOutlined />}
                valueStyle={{ color: '#1677ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="已掌握"
                value={statistics.mastered}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="未掌握"
                value={statistics.not_mastered}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="掌握率"
                value={statistics.mastery_rate}
                suffix="%"
                prefix={<BulbOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 工具栏 */}
      <div style={{ 
        marginBottom: 24, 
        padding: 16, 
        background: '#fafafa', 
        borderRadius: 8,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 12
      }}>
        <Space wrap>
          {/* 视图切换 */}
          <Segmented
            value={viewMode}
            onChange={(value) => setViewMode(value as 'card' | 'list')}
            options={[
              { label: '卡片模式', value: 'card', icon: <AppstoreOutlined /> },
              { label: '列表模式', value: 'list', icon: <UnorderedListOutlined /> },
            ]}
          />
          
          {/* 状态筛选 */}
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
            options={[
              { label: '全部', value: 'all' },
              { label: '未学习', value: 'not_seen', icon: <MinusCircleOutlined /> },
              { label: '已掌握', value: 'mastered', icon: <CheckCircleOutlined /> },
              { label: '未掌握', value: 'not_mastered', icon: <CloseCircleOutlined /> },
            ]}
          />
        </Space>

        <Space wrap>
          {/* 生成更多 */}
          <Button
            icon={<ThunderboltOutlined />}
            onClick={() => handleGenerate(20, false)}
            loading={generating}
          >
            生成更多题目
          </Button>
          
          {/* 根据薄弱点生成 */}
          <Button
            type="primary"
            icon={<BulbOutlined />}
            onClick={() => handleGenerate(20, true)}
            loading={generating}
            disabled={!statistics || statistics.not_mastered === 0}
          >
            根据薄弱点生成
          </Button>
        </Space>
      </div>

      {/* 题目展示 */}
      <Spin spinning={loading}>
        {questions.length === 0 ? (
          <Empty description={`暂无${statusFilter === 'all' ? '' : '符合条件的'}题目`} />
        ) : viewMode === 'card' ? (
          <InterviewCardView
            questions={questions}
            currentIndex={currentIndex}
            onNext={() => setCurrentIndex(prev => Math.min(prev + 1, questions.length - 1))}
            onPrevious={() => setCurrentIndex(prev => Math.max(prev - 1, 0))}
            onStatusChange={handleStatusChange}
            loading={loading}
          />
        ) : (
          <InterviewListView
            questions={questions}
            onStatusChange={handleStatusChange}
            loading={loading}
          />
        )}
      </Spin>
    </div>
  );
};

export default InterviewTab;
