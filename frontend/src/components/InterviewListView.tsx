import React, { useState } from 'react';
import { List, Card, Tag, Button, Space, Typography, Collapse } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { InterviewQuestion, QuestionStatus as QStatus } from '../types/interview';
import { DifficultyLevel, QuestionStatus } from '../types/interview';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface InterviewListViewProps {
  questions: InterviewQuestion[];
  onStatusChange: (questionId: number, status: QStatus) => void;
  loading?: boolean;
}

// 难度标签颜色
const difficultyColors: Record<DifficultyLevel, string> = {
  [DifficultyLevel.EASY]: 'success',
  [DifficultyLevel.MEDIUM]: 'warning',
  [DifficultyLevel.HARD]: 'error'
};

// 难度中文
const difficultyLabels: Record<DifficultyLevel, string> = {
  [DifficultyLevel.EASY]: '简单',
  [DifficultyLevel.MEDIUM]: '中等',
  [DifficultyLevel.HARD]: '困难'
};

// 状态标签
const getStatusTag = (status: QStatus | null) => {
  switch (status) {
    case QuestionStatus.MASTERED:
      return <Tag icon={<CheckCircleOutlined />} color="success">已掌握</Tag>;
    case QuestionStatus.NOT_MASTERED:
      return <Tag icon={<CloseCircleOutlined />} color="error">未掌握</Tag>;
    case QuestionStatus.NOT_SEEN:
    default:
      return <Tag icon={<MinusCircleOutlined />} color="default">未学习</Tag>;
  }
};

const InterviewListView: React.FC<InterviewListViewProps> = ({
  questions,
  onStatusChange,
  loading = false
}) => {
  const [expandedKeys, setExpandedKeys] = useState<string[]>([]);

  if (questions.length === 0) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Paragraph type="secondary">暂无题目</Paragraph>
        </div>
      </Card>
    );
  }

  return (
    <List
      itemLayout="vertical"
      dataSource={questions}
      renderItem={(question, index) => (
        <Card
          key={question.id}
          style={{ marginBottom: 16 }}
          styles={{
            body: { padding: 0 }
          }}
        >
          <Collapse
            activeKey={expandedKeys}
            onChange={(keys) => setExpandedKeys(keys as string[])}
            bordered={false}
            expandIconPosition="end"
          >
            <Panel
              key={question.id.toString()}
              header={
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0' }}>
                  {/* 序号 */}
                  <div style={{
                    minWidth: 40,
                    height: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#1677ff',
                    color: 'white',
                    borderRadius: '50%',
                    fontWeight: 'bold'
                  }}>
                    {index + 1}
                  </div>

                  {/* 题目信息 */}
                  <div style={{ flex: 1 }}>
                    <Space wrap style={{ marginBottom: 4 }}>
                      {question.category && (
                        <Tag color="blue">{question.category}</Tag>
                      )}
                      <Tag color={difficultyColors[question.difficulty]}>
                        {difficultyLabels[question.difficulty]}
                      </Tag>
                      {getStatusTag(question.user_status)}
                    </Space>
                    <div style={{ fontSize: 15, fontWeight: 500, lineHeight: 1.5 }}>
                      {question.question.length > 100 
                        ? question.question.substring(0, 100) + '...'
                        : question.question
                      }
                    </div>
                  </div>
                </div>
              }
            >
              <div style={{ padding: '0 24px 24px' }}>
                {/* 完整题目 */}
                <div style={{ marginBottom: 20 }}>
                  <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 12 }}>
                    题目：
                  </Text>
                  <div className="markdown-content" style={{ fontSize: 14, lineHeight: 1.8 }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {question.question}
                    </ReactMarkdown>
                  </div>
                </div>

                {/* 知识点 */}
                {question.knowledge_points && question.knowledge_points.length > 0 && (
                  <div style={{ marginBottom: 20 }}>
                    <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 8 }}>
                      知识点：
                    </Text>
                    <Space wrap>
                      {question.knowledge_points.map((point, idx) => (
                        <Tag key={idx} color="purple">{point}</Tag>
                      ))}
                    </Space>
                  </div>
                )}

                {/* 参考答案 */}
                <div style={{ marginBottom: 20 }}>
                  <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 12 }}>
                    参考答案：
                  </Text>
                  <div 
                    className="markdown-content"
                    style={{
                      background: '#fafafa',
                      padding: 16,
                      borderRadius: 8,
                      border: '1px solid #e8e8e8',
                      fontSize: 14,
                      lineHeight: 1.8
                    }}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {question.answer}
                    </ReactMarkdown>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                  <Button
                    danger
                    icon={<CloseCircleOutlined />}
                    onClick={() => onStatusChange(question.id, QuestionStatus.NOT_MASTERED)}
                    disabled={loading || question.user_status === QuestionStatus.NOT_MASTERED}
                  >
                    不会
                  </Button>
                  <Button
                    type="primary"
                    icon={<CheckCircleOutlined />}
                    onClick={() => onStatusChange(question.id, QuestionStatus.MASTERED)}
                    disabled={loading || question.user_status === QuestionStatus.MASTERED}
                    style={{ background: '#52c41a', borderColor: '#52c41a' }}
                  >
                    会了
                  </Button>
                </div>

                {/* 复习记录 */}
                {question.review_count > 0 && (
                  <div style={{ 
                    marginTop: 12, 
                    padding: 8, 
                    background: '#f0f0f0', 
                    borderRadius: 4,
                    fontSize: 12,
                    color: '#666'
                  }}>
                    已复习 {question.review_count} 次
                    {question.last_reviewed_at && (
                      <> · 最后复习：{new Date(question.last_reviewed_at).toLocaleString('zh-CN')}</>
                    )}
                  </div>
                )}
              </div>
            </Panel>
          </Collapse>
        </Card>
      )}
    />
  );
};

export default InterviewListView;

