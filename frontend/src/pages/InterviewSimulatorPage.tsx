import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Input, Space, message, Modal, Progress, Tag, Spin, Select } from 'antd';
import { SendOutlined, StopOutlined, HistoryOutlined, ClockCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { interviewSimulatorAPI, Message, Evaluation } from '../services/interviewSimulatorAPI';
import { learningPathAPI } from '../services/learningPathAPI';
import './InterviewSimulatorPage.css';

const { TextArea } = Input;

interface LearningPath {
  id: number;
  position: string;
  description?: string;
}

const InterviewSimulatorPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [duration, setDuration] = useState(0);
  const [position, setPosition] = useState('');
  
  // 学习路径选择
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [selectedPathId, setSelectedPathId] = useState<number | null>(null);
  const [loadingPaths, setLoadingPaths] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  useEffect(() => {
    // 自动滚动到底部
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  useEffect(() => {
    // 加载学习路径
    loadLearningPaths();
  }, []);
  
  useEffect(() => {
    // 清理定时器
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);
  
  const loadLearningPaths = async () => {
    try {
      setLoadingPaths(true);
      const response = await learningPathAPI.list();
      const paths = response.items || [];
      setLearningPaths(paths);
      if (paths.length > 0) {
        setSelectedPathId(paths[0].id);
      }
    } catch (error) {
      message.error('加载学习路径失败');
      console.error(error);
    } finally {
      setLoadingPaths(false);
    }
  };
  
  const startInterview = async () => {
    if (!selectedPathId) {
      message.warning('请选择学习路径');
      return;
    }
    
    try {
      setLoading(true);
      const response = await interviewSimulatorAPI.start(selectedPathId);
      setSessionId(response.session_id);
      setPosition(response.position);
      setMessages([{
        role: 'interviewer',
        content: response.first_message,
        timestamp: new Date().toISOString()
      }]);
      
      // 开始计时
      setDuration(0);
      timerRef.current = setInterval(() => {
        setDuration(d => d + 1);
      }, 1000);
      
      message.success('面试开始！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '启动面试失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const sendAnswer = async () => {
    if (!userInput.trim() || !sessionId) return;
    
    const userMessage: Message = {
      role: 'candidate',
      content: userInput,
      timestamp: new Date().toISOString()
    };
    
    setMessages([...messages, userMessage]);
    setUserInput('');
    setLoading(true);
    
    try {
      const response = await interviewSimulatorAPI.continue(sessionId, userInput);
      
      setMessages(prev => [...prev, {
        role: 'interviewer',
        content: response.interviewer_message,
        timestamp: new Date().toISOString()
      }]);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '发送失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const endInterview = () => {
    Modal.confirm({
      title: '确定结束面试吗？',
      content: '结束后将生成面试评价报告',
      okText: '结束面试',
      cancelText: '继续面试',
      onOk: async () => {
        if (!sessionId) return;
        
        try {
          setLoading(true);
          
          // 停止计时
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
          
          const response = await interviewSimulatorAPI.end(sessionId);
          setEvaluation(response.evaluation);
          setShowEvaluation(true);
          message.success('面试已结束，评价报告已生成');
        } catch (error: any) {
          message.error(error.response?.data?.detail || '结束面试失败');
          console.error(error);
        } finally {
          setLoading(false);
        }
      }
    });
  };
  
  const getQualityTag = (hint?: string) => {
    if (!hint) return null;
    const config: { [key: string]: { color: string; text: string } } = {
      excellent: { color: 'success', text: '优秀' },
      good: { color: 'processing', text: '良好' },
      needs_improvement: { color: 'warning', text: '需改进' }
    };
    const c = config[hint];
    return c ? <Tag color={c.color}>{c.text}</Tag> : null;
  };
  
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };
  
  const resetInterview = () => {
    setSessionId(null);
    setMessages([]);
    setUserInput('');
    setEvaluation(null);
    setShowEvaluation(false);
    setDuration(0);
    setPosition('');
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };
  
  return (
    <div className="interview-simulator-page">
      {!sessionId ? (
        <Card style={{ maxWidth: 600, margin: '50px auto', textAlign: 'center' }}>
          <h2>面试模拟系统</h2>
          <p>AI 面试官将根据您的回答进行深度追问</p>
          <Space direction="vertical" style={{ width: '100%', marginTop: 24 }}>
            <div style={{ textAlign: 'left' }}>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>选择学习路径：</div>
              <Select
                style={{ width: '100%' }}
                placeholder="请选择学习路径"
                value={selectedPathId}
                onChange={setSelectedPathId}
                loading={loadingPaths}
              >
                {learningPaths.map(path => (
                  <Select.Option key={path.id} value={path.id}>
                    {path.position}
                  </Select.Option>
                ))}
              </Select>
            </div>
            <Button
              type="primary"
              size="large"
              onClick={startInterview}
              loading={loading}
              disabled={!selectedPathId}
            >
              开始模拟面试
            </Button>
          </Space>
        </Card>
      ) : (
        <div className="interview-container">
          {/* 顶部状态栏 */}
          <Card className="status-bar" size="small">
            <Space split={<span>|</span>}>
              <span>{position}</span>
              <span><ClockCircleOutlined /> {formatTime(duration)}</span>
              <span>已回答：{messages.filter(m => m.role === 'candidate').length} 题</span>
            </Space>
            <Button danger icon={<StopOutlined />} onClick={endInterview} disabled={loading}>
              结束面试
            </Button>
          </Card>
          
          {/* 对话区域 */}
          <Card className="chat-area">
            {messages.map((msg, idx) => (
              msg.role !== 'system' && (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-header">
                    {msg.role === 'interviewer' ? '面试官' : '我'}
                  </div>
                  <div className="message-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              )
            ))}
            {loading && (
              <div className="message interviewer">
                <Spin />
                <span style={{ marginLeft: 8 }}>面试官正在思考...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </Card>
          
          {/* 输入区域 */}
          <Card className="input-area" size="small">
            <Space.Compact style={{ width: '100%' }}>
              <TextArea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="输入您的回答（按 Ctrl+Enter 发送）"
                autoSize={{ minRows: 2, maxRows: 6 }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    sendAnswer();
                  }
                }}
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={sendAnswer}
                loading={loading}
                disabled={!userInput.trim()}
                style={{ height: 'auto' }}
              >
                发送
              </Button>
            </Space.Compact>
          </Card>
        </div>
      )}
      
      {/* 评价报告弹窗 */}
      <Modal
        title="面试评价报告"
        open={showEvaluation}
        onCancel={() => setShowEvaluation(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setShowEvaluation(false)}>
            关闭
          </Button>,
          <Button key="restart" type="primary" onClick={() => {
            setShowEvaluation(false);
            resetInterview();
          }}>
            再来一次
          </Button>
        ]}
      >
        {evaluation && (
          <div className="evaluation-report">
            <h3>总体评分：{evaluation.overall_score} 分</h3>
            <Progress percent={evaluation.overall_score} status="active" />
            
            <h4>各维度得分：</h4>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>技术深度：<Progress percent={evaluation.dimension_scores.technical_depth} /></div>
              <div>表达能力：<Progress percent={evaluation.dimension_scores.expression} /></div>
              <div>问题解决：<Progress percent={evaluation.dimension_scores.problem_solving} /></div>
              <div>实践经验：<Progress percent={evaluation.dimension_scores.experience} /></div>
            </Space>
            
            <h4>优点：</h4>
            <ul>
              {evaluation.strengths.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
            
            <h4>需要改进：</h4>
            <ul>
              {evaluation.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
            
            <h4>改进建议：</h4>
            <ul>
              {evaluation.suggestions.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
            
            <h4>总结：</h4>
            <p>{evaluation.summary}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default InterviewSimulatorPage;

