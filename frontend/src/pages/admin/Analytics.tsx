import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Spin } from 'antd';
import { UserOutlined, TeamOutlined, UserAddOutlined, BookOutlined, FileTextOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { Line, Column } from '@ant-design/charts';
import { analyticsAPI, OverviewData } from '../../services/adminAPI';

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [userGrowth, setUserGrowth] = useState<any[]>([]);
  const [featuresUsage, setFeaturesUsage] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 加载概览数据
      const overviewData = await analyticsAPI.getOverview();
      setOverview(overviewData);

      // 加载用户增长数据
      const growthData = await analyticsAPI.getUserGrowth(30);
      setUserGrowth(growthData);

      // 加载功能使用数据
      const usageData = await analyticsAPI.getFeaturesUsage();
      setFeaturesUsage([
        { feature: '学习路线', count: usageData.learning_paths },
        { feature: '笔记', count: usageData.notes },
        { feature: '面试题', count: usageData.interview_questions }
      ]);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const lineConfig = {
    data: userGrowth,
    xField: 'date',
    yField: 'count',
    point: {
      size: 5,
      shape: 'diamond'
    },
    label: {
      style: {
        fill: '#aaa'
      }
    }
  };

  const columnConfig = {
    data: featuresUsage,
    xField: 'feature',
    yField: 'count',
    label: {
      position: 'top' as const,
      style: {
        fill: '#000',
        opacity: 0.6
      }
    },
    xAxis: {
      label: {
        autoHide: true,
        autoRotate: false
      }
    },
    meta: {
      feature: {
        alias: '功能'
      },
      count: {
        alias: '数量'
      }
    }
  };

  if (loading && !overview) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h2>数据统计</h2>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={overview?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日活跃"
              value={overview?.today_active_users || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本周新增"
              value={overview?.week_new_users || 0}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="学习路线总数"
              value={overview?.total_learning_paths || 0}
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="笔记总数"
              value={overview?.total_notes || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="面试题总数"
              value={overview?.total_questions || 0}
              prefix={<QuestionCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="用户增长趋势（最近30天）" loading={loading}>
            <Line {...lineConfig} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="功能使用统计" loading={loading}>
            <Column {...columnConfig} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;

