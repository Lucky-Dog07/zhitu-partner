import React, { useState } from 'react';
import { Card, Button, Tag, Space, Progress, Typography, Divider } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  EyeInvisibleOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { InterviewQuestion, QuestionStatus as QStatus } from '../types/interview';
import { DifficultyLevel } from '../types/interview';

const { Title, Paragraph, Text } = Typography;

interface InterviewCardViewProps {
  questions: InterviewQuestion[];
  currentIndex: number;
  onNext: () => void;
  onPrevious: () => void;
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

const InterviewCardView: React.FC<InterviewCardViewProps> = ({
  questions,
  currentIndex,
  onNext,
  onPrevious,
  onStatusChange,
  loading = false
}) => {
  const [showAnswer, setShowAnswer] = useState(false);

  if (questions.length === 0) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Paragraph type="secondary">暂无题目</Paragraph>
        </div>
      </Card>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;

  const handleMastered = () => {
    onStatusChange(currentQuestion.id, 'mastered' as QStatus);
    setShowAnswer(false);
    if (currentIndex < questions.length - 1) {
      onNext();
    }
  };

  const handleNotMastered = () => {
    onStatusChange(currentQuestion.id, 'not_mastered' as QStatus);
    setShowAnswer(false);
    if (currentIndex < questions.length - 1) {
      onNext();
    }
  };

  return (
    <div>
      {/* 进度条 */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <Text strong>刷题进度</Text>
          <Text type="secondary">{currentIndex + 1} / {questions.length}</Text>
        </div>
        <Progress percent={progress} showInfo={false} strokeColor="#1677ff" />
      </div>

      {/* 题目卡片 */}
      <Card
        style={{ marginBottom: 24 }}
        styles={{
          body: { minHeight: 400 }
        }}
      >
        {/* 题目标签 */}
        <Space style={{ marginBottom: 16 }} wrap>
          {currentQuestion.category && (
            <Tag color="blue">{currentQuestion.category}</Tag>
          )}
          <Tag color={difficultyColors[currentQuestion.difficulty]}>
            {difficultyLabels[currentQuestion.difficulty]}
          </Tag>
          {currentQuestion.knowledge_points && currentQuestion.knowledge_points.length > 0 && (
            currentQuestion.knowledge_points.map((point, idx) => (
              <Tag key={idx} color="purple">{point}</Tag>
            ))
          )}
        </Space>

        {/* 题目内容 */}
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ marginBottom: 16 }}>题目：</Title>
          <div className="markdown-content" style={{ fontSize: 16, lineHeight: 1.8 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {currentQuestion.question}
            </ReactMarkdown>
          </div>
        </div>

        <Divider />

        {/* 答案区域 */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <Title level={4} style={{ margin: 0 }}>参考答案：</Title>
            <Button
              type="link"
              icon={showAnswer ? <EyeInvisibleOutlined /> : <EyeOutlined />}
              onClick={() => setShowAnswer(!showAnswer)}
            >
              {showAnswer ? '隐藏答案' : '查看答案'}
            </Button>
          </div>
          
          {showAnswer ? (
            <div 
              className="markdown-content"
              style={{
                background: '#fafafa',
                padding: 20,
                borderRadius: 8,
                border: '1px solid #e8e8e8',
                fontSize: 15,
                lineHeight: 1.8
              }}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentQuestion.answer}
              </ReactMarkdown>
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px',
              background: '#f5f5f5',
              borderRadius: 8,
              border: '1px dashed #d9d9d9'
            }}>
              <EyeInvisibleOutlined style={{ fontSize: 32, color: '#bfbfbf', marginBottom: 8 }} />
              <Paragraph type="secondary">点击上方按钮查看答案</Paragraph>
            </div>
          )}
        </div>
      </Card>

      {/* 操作按钮 */}
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
        <Button
          size="large"
          onClick={onPrevious}
          disabled={currentIndex === 0 || loading}
        >
          上一题
        </Button>
        
        <Button
          size="large"
          danger
          icon={<CloseCircleOutlined />}
          onClick={handleNotMastered}
          disabled={loading}
          style={{ minWidth: 120 }}
        >
          不会
        </Button>
        
        <Button
          type="primary"
          size="large"
          icon={<CheckCircleOutlined />}
          onClick={handleMastered}
          disabled={loading}
          style={{ minWidth: 120, background: '#52c41a', borderColor: '#52c41a' }}
        >
          会了
        </Button>
        
        <Button
          size="large"
          onClick={onNext}
          disabled={currentIndex === questions.length - 1 || loading}
        >
          下一题
        </Button>
      </div>

      {/* 已完成提示 */}
      {currentIndex === questions.length - 1 && (
        <div style={{ 
          marginTop: 16, 
          textAlign: 'center', 
          padding: 12, 
          background: '#e6f4ff', 
          borderRadius: 4 
        }}>
          <Text type="secondary">已到最后一题</Text>
        </div>
      )}
    </div>
  );
};

export default InterviewCardView;

