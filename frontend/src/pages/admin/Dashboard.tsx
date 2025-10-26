import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Button, Select, Space, Empty, Spin, message, Progress, Tag, Timeline } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  UserAddOutlined,
  BookOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  GlobalOutlined,
  ReloadOutlined,
  DownloadOutlined,
  DatabaseOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { Area, Pie, Heatmap } from '@ant-design/charts';
import dayjs from 'dayjs';
import { useNavigate } from 'react-router-dom';
import {
  dashboardAPI,
  DashboardOverview,
  ActivityItem,
  SystemStatus,
  QuickStats,
  UserGrowthItem,
  FeatureUsageData,
  ActivityHeatmapItem
} from '../../services/adminAPI';

const { Option } = Select;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [quickStats, setQuickStats] = useState<QuickStats | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [userGrowth, setUserGrowth] = useState<UserGrowthItem[]>([]);
  const [featureUsage, setFeatureUsage] = useState<FeatureUsageData | null>(null);
  const [activityHeatmap, setActivityHeatmap] = useState<ActivityHeatmapItem[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [days, setDays] = useState(30);

  // 加载所有数据
  const loadAllData = useCallback(async () => {
    try {
      setLoading(true);
      const [
        overviewData,
        quickStatsData,
        systemStatusData,
        activitiesData,
        userGrowthData,
        featureUsageData,
        heatmapData
      ] = await Promise.all([
        dashboardAPI.getOverview(),
        dashboardAPI.getQuickStats(),
        dashboardAPI.getSystemStatus(),
        dashboardAPI.getRecentActivities(10),
        dashboardAPI.getUserGrowth(days),
        dashboardAPI.getFeatureUsage(),
        dashboardAPI.getActivityHeatmap()
      ]);

      setOverview(overviewData);
      setQuickStats(quickStatsData);
      setSystemStatus(systemStatusData);
      setActivities(activitiesData);
      setUserGrowth(userGrowthData);
      setFeatureUsage(featureUsageData);
      setActivityHeatmap(heatmapData);
    } catch (error) {
      console.error('加载仪表盘数据失败:', error);
      message.error('加载数据失败，请刷新重试');
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadAllData();
      }, 30000); // 30秒刷新一次
      return () => clearInterval(interval);
    }
  }, [autoRefresh, loadAllData]);

  // 导出数据
  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      message.loading('正在导出数据...');
      const blob = await dashboardAPI.export({ format });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `dashboard_export_${dayjs().format('YYYYMMDD')}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请重试');
    }
  };

  // 增长率显示
  const renderGrowthRate = (rate: number) => {
    if (rate === 0) return <span style={{ color: '#999' }}>0%</span>;
    const isPositive = rate > 0;
    return (
      <span style={{ color: isPositive ? '#52c41a' : '#ff4d4f' }}>
        {isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {Math.abs(rate).toFixed(2)}%
      </span>
    );
  };

  // 活动类型图标
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'register':
        return <UserAddOutlined style={{ color: '#1890ff' }} />;
      case 'create_path':
        return <BookOutlined style={{ color: '#52c41a' }} />;
      case 'login':
        return <CheckCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <GlobalOutlined />;
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载仪表盘数据..." />
      </div>
    );
  }

  // 用户增长趋势图配置
  const areaConfig = {
    data: userGrowth,
    xField: 'date',
    yField: 'total_users',
    smooth: true,
    areaStyle: {
      fill: 'l(270) 0:#ffffff 0.5:#7ec2f3 1:#1890ff',
    },
    line: {
      color: '#1890ff',
    },
    point: {
      size: 3,
      shape: 'circle',
    },
    tooltip: {
      formatter: (datum: UserGrowthItem) => {
        return {
          name: '总用户数',
          value: `${datum.total_users} (新增 ${datum.new_users})`,
        };
      },
    },
  };

  // 功能使用分布饼图配置
  const pieConfig = {
    data: featureUsage
      ? [
          { type: '学习路线', value: featureUsage.learning_paths },
          { type: '笔记', value: featureUsage.notes },
          { type: '面试题', value: featureUsage.interviews },
        ]
      : [],
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [
      {
        type: 'element-active',
      },
    ],
  };

  // 活跃度热力图配置
  const heatmapConfig = {
    data: activityHeatmap,
    xField: 'hour',
    yField: 'day',
    colorField: 'count',
    color: ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'],
    meta: {
      hour: {
        type: 'cat',
      },
    },
  };

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* 顶部工具栏 */}
      <Card style={{ marginBottom: 16 }} bordered={false}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space>
              <Select
                value={days}
                onChange={setDays}
                style={{ width: 150 }}
              >
                <Option value={7}>最近 7 天</Option>
                <Option value={30}>最近 30 天</Option>
                <Option value={90}>最近 90 天</Option>
              </Select>
              <Button
                icon={<ReloadOutlined spin={autoRefresh} />}
                onClick={() => loadAllData()}
              >
                刷新
              </Button>
              <Button
                type={autoRefresh ? 'primary' : 'default'}
                onClick={() => setAutoRefresh(!autoRefresh)}
              >
                {autoRefresh ? '停止自动刷新' : '自动刷新 (30秒)'}
              </Button>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<DownloadOutlined />} onClick={() => handleExport('csv')}>
                导出 CSV
              </Button>
              <Button icon={<DownloadOutlined />} onClick={() => handleExport('xlsx')}>
                导出 Excel
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="总用户数"
              value={overview?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="今日活跃"
              value={overview?.active_users_today || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="本周新增"
              value={overview?.new_users_this_week || 0}
              prefix={<UserAddOutlined />}
              suffix={quickStats && renderGrowthRate(quickStats.users_growth_rate)}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="学习路线"
              value={overview?.total_learning_paths || 0}
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="笔记数"
              value={overview?.total_notes || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="面试题"
              value={overview?.total_interview_questions || 0}
              prefix={<QuestionCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {/* 用户增长趋势 */}
        <Col xs={24} lg={16}>
          <Card title="用户增长趋势" bordered={false}>
            {userGrowth.length > 0 ? (
              <Area {...areaConfig} height={300} />
            ) : (
              <Empty description="暂无用户增长数据" />
            )}
          </Card>
        </Col>

        {/* 功能使用分布 */}
        <Col xs={24} lg={8}>
          <Card title="功能使用分布" bordered={false}>
            {featureUsage && (featureUsage.learning_paths > 0 || featureUsage.notes > 0 || featureUsage.interviews > 0) ? (
              <Pie {...pieConfig} height={300} />
            ) : (
              <Empty description="暂无功能使用数据" />
            )}
          </Card>
        </Col>
      </Row>

      {/* 热力图和登录趋势 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {/* 活跃度热力图 */}
        <Col xs={24} lg={12}>
          <Card title="用户活跃度热力图 (7天x24小时)" bordered={false}>
            {activityHeatmap.length > 0 ? (
              <Heatmap {...heatmapConfig} height={300} />
            ) : (
              <Empty description="暂无活跃度数据" />
            )}
          </Card>
        </Col>

        {/* 登录统计 */}
        <Col xs={24} lg={12}>
          <Card title="登录统计" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="成功登录"
                  value={featureUsage?.login_success || 0}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="失败登录"
                  value={featureUsage?.login_failed || 0}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 系统状态和最近活动 */}
      <Row gutter={[16, 16]}>
        {/* 系统状态 */}
        <Col xs={24} lg={12}>
          <Card title="系统状态" bordered={false}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ marginBottom: 8 }}>
                    <DatabaseOutlined style={{ marginRight: 8 }} />
                    数据库: <Tag color={systemStatus?.database_status === 'healthy' ? 'green' : 'red'}>
                      {systemStatus?.database_status === 'healthy' ? '正常' : '异常'}
                    </Tag>
                  </div>
                  <div>
                    <GlobalOutlined style={{ marginRight: 8 }} />
                    API: <Tag color="green">正常</Tag>
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ marginBottom: 4 }}>CPU 使用率</div>
                    <Progress percent={Math.round(systemStatus?.cpu_usage || 0)} size="small" />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ marginBottom: 4 }}>内存使用率</div>
                    <Progress percent={Math.round(systemStatus?.memory_usage || 0)} size="small" />
                  </div>
                  <div>
                    <div style={{ marginBottom: 4 }}>磁盘使用率</div>
                    <Progress percent={Math.round(systemStatus?.disk_usage || 0)} size="small" />
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 最近活动 */}
        <Col xs={24} lg={12}>
          <Card
            title="最近活动"
            bordered={false}
            extra={
              <Button type="link" onClick={() => navigate('/admin/operation-logs')}>
                查看全部
              </Button>
            }
          >
            {activities.length > 0 ? (
              <Timeline
                items={activities.map(activity => ({
                  dot: getActivityIcon(activity.type),
                  children: (
                    <div>
                      <div>{activity.description}</div>
                      <div style={{ fontSize: 12, color: '#999' }}>
                        {dayjs(activity.timestamp).format('YYYY-MM-DD HH:mm:ss')}
                      </div>
                    </div>
                  ),
                }))}
              />
            ) : (
              <Empty description="暂无活动记录" />
            )}
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Card title="快速操作" bordered={false} style={{ marginTop: 16 }}>
        <Space wrap>
          <Button type="primary" onClick={() => navigate('/admin/users')}>
            用户管理
          </Button>
          <Button onClick={() => navigate('/admin/operation-logs')}>
            操作日志
          </Button>
          <Button onClick={() => navigate('/admin/login-logs')}>
            登录日志
          </Button>
          <Button onClick={() => navigate('/admin/config')}>
            系统配置
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default Dashboard;
