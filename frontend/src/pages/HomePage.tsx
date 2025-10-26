import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Card, Row, Col, Modal, Checkbox, message, Spin } from 'antd';
import { RocketOutlined } from '@ant-design/icons';
import { learningPathAPI } from '../services/api';

const { TextArea } = Input;

const popularJobs = [
  '前端开发工程师', '后端开发工程师', '全栈工程师',
  'Python工程师', 'Java工程师', '数据分析师',
  'AI工程师', '产品经理', 'UI设计师'
];

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [position, setPosition] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [contentTypes, setContentTypes] = useState<string[]>([
    'mindmap', 'knowledge', 'interview'
  ]);
  
  const handleJobSelect = (job: string) => {
    setPosition(job);
  };
  
  const handleGenerate = () => {
    if (!position.trim()) {
      message.warning('请输入或选择目标职位');
      return;
    }
    setModalVisible(true);
  };
  
  const handleConfirmGenerate = async () => {
    setModalVisible(false);
    setLoading(true);
    
    try {
      const result = await learningPathAPI.generate({
        position,
        job_description: jobDescription,
        content_types: contentTypes
      });
      
      message.success('学习路线生成成功！');
      navigate(`/learning-path/${result.id}`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: 60 }}>
        <h1 style={{ fontSize: 48, marginBottom: 20 }}>
          <RocketOutlined /> 职途伴侣
        </h1>
        <p style={{ fontSize: 18, color: '#666' }}>
          AI驱动的个性化职业技能提升助手
        </p>
      </div>
      
      <Card style={{ marginBottom: 40 }}>
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 10, display: 'block' }}>
            目标职位
          </label>
          <Input
            size="large"
            placeholder="输入你的目标职位，如：前端开发工程师"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            style={{ marginBottom: 20 }}
          />
        </div>
        
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 10, display: 'block' }}>
            职位描述（可选）
          </label>
          <TextArea
            rows={4}
            placeholder="粘贴职位描述或JD，帮助AI更精准地生成学习路线"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>
        
        <Button
          type="primary"
          size="large"
          block
          onClick={handleGenerate}
          loading={loading}
          style={{ height: 50, fontSize: 18 }}
        >
          生成学习路线
        </Button>
      </Card>
      
      <div>
        <h2 style={{ marginBottom: 20 }}>热门职位</h2>
        <Row gutter={[16, 16]}>
          {popularJobs.map((job) => (
            <Col xs={24} sm={12} md={8} key={job}>
              <Card
                hoverable
                onClick={() => handleJobSelect(job)}
                style={{ textAlign: 'center', cursor: 'pointer' }}
              >
                {job}
              </Card>
            </Col>
          ))}
        </Row>
      </div>
      
      <Modal
        title="选择生成内容"
        open={modalVisible}
        onOk={handleConfirmGenerate}
        onCancel={() => setModalVisible(false)}
        okText="确认生成"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16, padding: 12, background: '#e6f4ff', borderRadius: 4 }}>
          <p style={{ margin: 0, fontSize: 14, color: '#0958d9' }}>
            提示：首次将快速生成技能分析和思维导图，其他内容可在详情页按需生成，节省时间！
          </p>
        </div>
        <Checkbox.Group
          value={contentTypes}
          onChange={(values) => setContentTypes(values as string[])}
          style={{ display: 'flex', flexDirection: 'column', gap: 10 }}
        >
          <Checkbox value="mindmap">技能思维导图</Checkbox>
          <Checkbox value="knowledge">知识点详解</Checkbox>
          <Checkbox value="interview">面试题库</Checkbox>
          <Checkbox value="courses">课程推荐</Checkbox>
          <Checkbox value="books">书籍推荐</Checkbox>
          <Checkbox value="certifications">证书推荐</Checkbox>
        </Checkbox.Group>
      </Modal>
      
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0,0,0,0.5)',
          zIndex: 9999
        }}>
          <Spin size="large" tip="AI正在生成学习路线，预计需要30-40秒..." />
        </div>
      )}
    </div>
  );
};

export default HomePage;

