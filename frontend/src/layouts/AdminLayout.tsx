import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown, Space } from 'antd';
import {
  UserOutlined,
  BarChartOutlined,
  SettingOutlined,
  FileTextOutlined,
  LogoutOutlined,
  HomeOutlined,
  DashboardOutlined,
  AuditOutlined,
  LoginOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;

const AdminLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  // 根据当前路径设置选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/admin/dashboard') || path === '/admin' || path === '/admin/') return 'dashboard';
    if (path.includes('/admin/users')) return 'users';
    if (path.includes('/admin/config')) return 'config';
    if (path.includes('/admin/operation-logs')) return 'operation-logs';
    if (path.includes('/admin/login-logs')) return 'login-logs';
    return 'dashboard';
  };

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      onClick: () => navigate('/admin/dashboard')
    },
    {
      key: 'users',
      icon: <UserOutlined />,
      label: '用户管理',
      onClick: () => navigate('/admin/users')
    },
    {
      key: 'config',
      icon: <SettingOutlined />,
      label: '系统配置',
      onClick: () => navigate('/admin/config')
    },
    {
      key: 'operation-logs',
      icon: <AuditOutlined />,
      label: '操作日志',
      onClick: () => navigate('/admin/operation-logs')
    },
    {
      key: 'login-logs',
      icon: <LoginOutlined />,
      label: '登录日志',
      onClick: () => navigate('/admin/login-logs')
    }
  ];

  const userMenuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: '返回首页',
      onClick: () => navigate('/')
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#001529',
        padding: '0 24px'
      }}>
        <h2 style={{ margin: 0, color: '#fff' }}>职途伴侣 - 管理后台</h2>
        <Dropdown menu={{ items: userMenuItems }}>
          <Button type="text" style={{ color: '#fff' }}>
            <Space>
              <Avatar icon={<UserOutlined />} size="small" />
              {user?.username}
            </Space>
          </Button>
        </Dropdown>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[getSelectedKey()]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: 8
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;

