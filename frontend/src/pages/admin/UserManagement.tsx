import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Tag, Space, Modal, Form, message, Popconfirm } from 'antd';
import { SearchOutlined, EditOutlined, DeleteOutlined, StopOutlined, CheckOutlined } from '@ant-design/icons';
import { userManagementAPI, UserListItem } from '../../services/adminAPI';
import type { ColumnsType } from 'antd/es/table';

const UserManagement: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>();
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<UserListItem | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadUsers();
  }, [currentPage, pageSize, search, roleFilter, statusFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await userManagementAPI.list({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        role: roleFilter,
        is_active: statusFilter
      });
      setUsers(response.items);
      setTotal(response.total);
    } catch (error) {
      message.error('加载用户列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user: UserListItem) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      role: user.role
    });
    setEditModalVisible(true);
  };

  const handleUpdate = async () => {
    try {
      const values = await form.validateFields();
      if (editingUser) {
        await userManagementAPI.update(editingUser.id, values);
        message.success('用户更新成功');
        setEditModalVisible(false);
        loadUsers();
      }
    } catch (error) {
      message.error('用户更新失败');
      console.error(error);
    }
  };

  const handleToggleStatus = async (user: UserListItem) => {
    try {
      await userManagementAPI.updateStatus(user.id, !user.is_active);
      message.success(`用户已${user.is_active ? '禁用' : '启用'}`);
      loadUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
      console.error(error);
    }
  };

  const handleDelete = async (userId: number) => {
    try {
      await userManagementAPI.delete(userId);
      message.success('用户删除成功');
      loadUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
      console.error(error);
    }
  };

  const columns: ColumnsType<UserListItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email'
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'}>
          {role === 'admin' ? '管理员' : '普通用户'}
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? '正常' : '已禁用'}
        </Tag>
      )
    },
    {
      title: '学习路线',
      dataIndex: 'learning_paths_count',
      key: 'learning_paths_count',
      width: 100
    },
    {
      title: '笔记数',
      dataIndex: 'notes_count',
      key: 'notes_count',
      width: 100
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN')
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      render: (date: string | null) => date ? new Date(date).toLocaleString('zh-CN') : '从未登录'
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            icon={record.is_active ? <StopOutlined /> : <CheckOutlined />}
            onClick={() => handleToggleStatus(record)}
          >
            {record.is_active ? '禁用' : '启用'}
          </Button>
          <Popconfirm
            title="确定删除此用户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <h2>用户管理</h2>
      {/* 调试信息 */}
      <div style={{ marginBottom: 16, padding: 10, background: '#f0f0f0', borderRadius: 4 }}>
        <p>加载状态: {loading ? '加载中...' : '已加载'}</p>
        <p>用户总数: {total}</p>
        <p>当前显示: {users.length} 个用户</p>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索用户名或邮箱"
          prefix={<SearchOutlined />}
          style={{ width: 200 }}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
        />
        <Select
          placeholder="角色筛选"
          style={{ width: 120 }}
          value={roleFilter}
          onChange={setRoleFilter}
          allowClear
        >
          <Select.Option value="user">普通用户</Select.Option>
          <Select.Option value="admin">管理员</Select.Option>
        </Select>
        <Select
          placeholder="状态筛选"
          style={{ width: 120 }}
          value={statusFilter}
          onChange={setStatusFilter}
          allowClear
        >
          <Select.Option value={true}>正常</Select.Option>
          <Select.Option value={false}>已禁用</Select.Option>
        </Select>
        <Button onClick={loadUsers}>刷新</Button>
      </Space>

      <Table
        columns={columns}
        dataSource={users}
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
        scroll={{ x: 1400 }}
      />

      <Modal
        title="编辑用户"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => setEditModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="角色"
            name="role"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select>
              <Select.Option value="user">普通用户</Select.Option>
              <Select.Option value="admin">管理员</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;

