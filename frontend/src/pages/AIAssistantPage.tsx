import React, { useState, useEffect, useRef } from 'react';
import { Layout, Input, Button, Card, Row, Col, message, Modal, Spin, Empty } from 'antd';
import {
  SendOutlined,
  DeleteOutlined,
  BarChartOutlined,
  MessageOutlined,
  BulbOutlined,
  CalendarOutlined,
  BookOutlined,
  DashboardOutlined,
  RobotOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import * as aiAssistantAPI from '../api/aiAssistantAPI';
import type { ChatMessage, QuickAction } from '../api/aiAssistantAPI';

const { Content } = Layout;
const { TextArea } = Input;

// Icon映射
const iconMap: Record<string, React.ReactNode> = {
  'BarChartOutlined': <BarChartOutlined />,
  'MessageOutlined': <MessageOutlined />,
  'BulbOutlined': <BulbOutlined />,
  'CalendarOutlined': <CalendarOutlined />,
  'BookOutlined': <BookOutlined />,
  'DashboardOutlined': <DashboardOutlined />,
};

const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 加载对话历史和快捷功能
  useEffect(() => {
    loadHistory();
    loadQuickActions();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadHistory = async () => {
    try {
      const history = await aiAssistantAPI.getHistory();
      setMessages(history);
    } catch (error) {
      console.error('加载历史失败:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadQuickActions = async () => {
    try {
      const actions = await aiAssistantAPI.getQuickActions();
      setQuickActions(actions);
    } catch (error) {
      console.error('加载快捷功能失败:', error);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const messageText = textToSend || inputText.trim();
    if (!messageText) {
      message.warning('请输入消息');
      return;
    }

    setLoading(true);
    setInputText(''); // 清空输入框

    // 立即显示用户消息
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      message: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await aiAssistantAPI.sendMessage(messageText);
      
      if (response.success) {
        // 显示AI回复
        const aiMessage: ChatMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          message: response.message,
          created_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        message.error(response.error || 'AI助手暂时无法响应');
      }
    } catch (error: any) {
      message.error('发送失败，请稍后重试');
      console.error('发送消息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    Modal.confirm({
      title: '确认清空',
      content: '确定要清空所有对话历史吗？此操作不可恢复。',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await aiAssistantAPI.clearHistory();
          setMessages([]);
          message.success('对话历史已清空');
        } catch (error) {
          message.error('清空失败');
        }
      },
    });
  };

  const handleQuickAction = (action: QuickAction) => {
    handleSend(action.prompt);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        {/* 标题 */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
            <RobotOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
            AI学习助手
          </h1>
          <p style={{ color: '#666', marginTop: '8px' }}>
            专业的职业导师，随时为您解答技术问题、分析错题、模拟面试
          </p>
        </div>

        {/* 快捷功能按钮 */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]}>
            {quickActions.map((action) => (
              <Col xs={24} sm={12} md={8} key={action.id}>
                <Card
                  hoverable
                  onClick={() => handleQuickAction(action)}
                  style={{ height: '100%', cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                    <div style={{ fontSize: '24px', color: '#1890ff' }}>
                      {iconMap[action.icon] || <BulbOutlined />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{action.title}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>{action.description}</div>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>

        {/* 对话区域 */}
        <Card 
          style={{ marginBottom: '16px', height: '500px', display: 'flex', flexDirection: 'column' }}
          bodyStyle={{ flex: 1, overflow: 'auto', padding: '16px' }}
        >
          {loadingHistory ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Spin tip="加载对话历史..." />
            </div>
          ) : messages.length === 0 ? (
            <Empty
              description="还没有对话记录，点击上方快捷功能开始吧！"
              style={{ margin: 'auto' }}
            />
          ) : (
            <div>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: '16px',
                  }}
                >
                  <div
                    style={{
                      maxWidth: '70%',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                      color: msg.role === 'user' ? '#fff' : '#000',
                    }}
                  >
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          },
                        }}
                      >
                        {msg.message}
                      </ReactMarkdown>
                    ) : (
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.message}</div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
                  <div style={{ padding: '12px 16px', borderRadius: '8px', background: '#f0f0f0' }}>
                    <Spin size="small" /> AI正在思考...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </Card>

        {/* 输入区域 */}
        <Card>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
            <TextArea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题... (按Enter发送，Shift+Enter换行)"
              autoSize={{ minRows: 2, maxRows: 6 }}
              disabled={loading}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => handleSend()}
              loading={loading}
              size="large"
            >
              发送
            </Button>
            <Button
              icon={<DeleteOutlined />}
              onClick={handleClearHistory}
              disabled={loading || messages.length === 0}
              size="large"
            >
              清空历史
            </Button>
          </div>
        </Card>
      </Content>
    </Layout>
  );
};

export default AIAssistantPage;

