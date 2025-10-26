import React, { useState, useEffect } from 'react';
import { Card, Table, Input, Select, DatePicker, Button, Space, Tag, Row, Col, Statistic, Alert, message } from 'antd';
import { SearchOutlined, UserOutlined, CheckCircleOutlined, CloseCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { loginLogsAPI, LoginLog, LoginLogStatistics } from '../../services/adminAPI';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const LoginLogs: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<LoginLog[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statistics, setStatistics] = useState<LoginLogStatistics | null>(null);

  // 筛选条件
  const [username, setUsername] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [ipAddress, setIpAddress] = useState<string>('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([null, null]);

  useEffect(() => {
    loadLogs();
    loadStatistics();
  }, [currentPage, pageSize, username, status, ipAddress, dateRange]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      };

      if (username) params.username = username;
      if (status) params.status = status;
      if (ipAddress) params.ip_address = ipAddress;
      if (dateRange[0]) params.start_date = dateRange[0].toISOString();
      if (dateRange[1]) params.end_date = dateRange[1].toISOString();

      const response = await loginLogsAPI.list(params);
      setLogs(response.logs);
      setTotal(response.total);
    } catch (error) {
      message.error('加载登录日志失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await loginLogsAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        if (status === 'success') {
          return <Tag color="success" icon={<CheckCircleOutlined />}>成功</Tag>;
        }
        return <Tag color="error" icon={<CloseCircleOutlined />}>失败</Tag>;
      }
    },
    {
      title: '失败原因',
      dataIndex: 'fail_reason',
      key: 'fail_reason',
      render: (text: string | null) => text || '-'
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
      render: (text: string | null) => text || '-'
    },
    {
      title: '浏览器',
      dataIndex: 'user_agent',
      key: 'user_agent',
      ellipsis: true,
      render: (text: string | null) => {
        if (!text) return '-';
        // 简化显示
        const match = text.match(/(Chrome|Safari|Firefox|Edge|Opera)\/[\d.]+/);
        return match ? match[0] : text.substring(0, 50);
      }
    },
    {
      title: '登录时间',
      dataIndex: 'login_time',
      key: 'login_time',
      width: 180,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      {statistics && (
        <>
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="今日登录"
                  value={statistics.today_logins}
                  prefix={<UserOutlined />}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="今日成功"
                  value={statistics.today_success}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="今日失败"
                  value={statistics.today_failed}
                  prefix={<CloseCircleOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="成功率"
                  value={statistics.success_rate}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 可疑IP警告 */}
          {statistics.suspicious_ips && statistics.suspicious_ips.length > 0 && (
            <Alert
              message="检测到可疑IP"
              description={
                <div>
                  以下IP今日登录失败次数异常：
                  {statistics.suspicious_ips.map(item => (
                    <div key={item.ip_address}>
                      <WarningOutlined /> {item.ip_address}: {item.fail_count}次
                    </div>
                  ))}
                </div>
              }
              type="warning"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}
        </>
      )}

      <Card title="登录日志">
        {/* 筛选器 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="用户名"
            value={username}
            onChange={e => setUsername(e.target.value)}
            style={{ width: 150 }}
            allowClear
          />
          <Select
            placeholder="状态"
            value={status || undefined}
            onChange={setStatus}
            style={{ width: 120 }}
            allowClear
          >
            <Select.Option value="success">成功</Select.Option>
            <Select.Option value="failed">失败</Select.Option>
          </Select>
          <Input
            placeholder="IP地址"
            value={ipAddress}
            onChange={e => setIpAddress(e.target.value)}
            style={{ width: 150 }}
            allowClear
          />
          <RangePicker
            value={dateRange}
            onChange={(dates) => setDateRange(dates as any)}
          />
          <Button icon={<SearchOutlined />} onClick={loadLogs} type="primary">
            搜索
          </Button>
        </Space>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 20);
            },
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </Card>
    </div>
  );
};

export default LoginLogs;

