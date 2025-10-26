import React, { useState, useEffect } from 'react';
import { Card, Table, Input, Select, DatePicker, Button, Space, Tag, Drawer, message, Descriptions } from 'antd';
import { SearchOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons';
import { operationLogsAPI, OperationLog } from '../../services/adminAPI';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const OperationLogs: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<OperationLog[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedLog, setSelectedLog] = useState<OperationLog | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);

  // 筛选条件
  const [action, setAction] = useState<string>('');
  const [targetType, setTargetType] = useState<string>('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([null, null]);

  useEffect(() => {
    loadLogs();
  }, [currentPage, pageSize, action, targetType, dateRange]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      };

      if (action) params.action = action;
      if (targetType) params.target_type = targetType;
      if (dateRange[0]) params.start_date = dateRange[0].toISOString();
      if (dateRange[1]) params.end_date = dateRange[1].toISOString();

      const response = await operationLogsAPI.list(params);
      setLogs(response.logs);
      setTotal(response.total);
    } catch (error) {
      message.error('加载日志失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const params: any = {};
      if (action) params.action = action;
      if (targetType) params.target_type = targetType;
      if (dateRange[0]) params.start_date = dateRange[0].toISOString();
      if (dateRange[1]) params.end_date = dateRange[1].toISOString();

      const blob = await operationLogsAPI.exportCSV(params);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `operation_logs_${Date.now()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const handleViewDetails = (record: OperationLog) => {
    setSelectedLog(record);
    setDrawerVisible(true);
  };

  const getActionTag = (action: string) => {
    if (action.includes('create')) return <Tag color="green">{action}</Tag>;
    if (action.includes('update')) return <Tag color="blue">{action}</Tag>;
    if (action.includes('delete')) return <Tag color="red">{action}</Tag>;
    return <Tag>{action}</Tag>;
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '操作人',
      dataIndex: 'username',
      key: 'username',
      width: 120
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (text: string) => getActionTag(text)
    },
    {
      title: '目标类型',
      dataIndex: 'target_type',
      key: 'target_type',
      render: (text: string | null) => text || '-'
    },
    {
      title: '目标ID',
      dataIndex: 'target_id',
      key: 'target_id',
      width: 100,
      render: (text: number | null) => text || '-'
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
      render: (text: string | null) => text || '-'
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_: any, record: OperationLog) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          详情
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="操作日志" extra={
        <Button icon={<DownloadOutlined />} onClick={handleExport}>
          导出CSV
        </Button>
      }>
        {/* 筛选器 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="操作类型"
            value={action}
            onChange={e => setAction(e.target.value)}
            style={{ width: 150 }}
            allowClear
          />
          <Select
            placeholder="目标类型"
            value={targetType || undefined}
            onChange={setTargetType}
            style={{ width: 150 }}
            allowClear
          >
            <Select.Option value="User">用户</Select.Option>
            <Select.Option value="SystemConfig">系统配置</Select.Option>
            <Select.Option value="LearningPath">学习路线</Select.Option>
            <Select.Option value="Note">笔记</Select.Option>
          </Select>
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

      {/* 详情抽屉 */}
      <Drawer
        title="操作日志详情"
        placement="right"
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        width={600}
      >
        {selectedLog && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="操作人">{selectedLog.username}</Descriptions.Item>
            <Descriptions.Item label="管理员ID">{selectedLog.admin_id}</Descriptions.Item>
            <Descriptions.Item label="操作">{getActionTag(selectedLog.action)}</Descriptions.Item>
            <Descriptions.Item label="目标类型">{selectedLog.target_type || '-'}</Descriptions.Item>
            <Descriptions.Item label="目标ID">{selectedLog.target_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="IP地址">{selectedLog.ip_address || '-'}</Descriptions.Item>
            <Descriptions.Item label="时间">
              {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="详情">
              <pre style={{ maxHeight: 300, overflow: 'auto' }}>
                {selectedLog.details || '无详情'}
              </pre>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
};

export default OperationLogs;
