import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import {
  HomeOutlined,
  BookOutlined,
  MessageOutlined,
  FileTextOutlined,
  UserOutlined,
  LogoutOutlined,
  ExclamationCircleOutlined,
  VideoCameraOutlined,
  ControlOutlined
} from '@ant-design/icons';
import { useAuthStore } from './store/authStore';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import LearningPathPage from './pages/LearningPathPage';
import LearningPathsListPage from './pages/LearningPathsListPage';
import MistakesPage from './pages/MistakesPage';
import AIAssistantPage from './pages/AIAssistantPage';
import NotesPage from './pages/NotesPage';
import InterviewSimulatorPage from './pages/InterviewSimulatorPage';
import AdminLayout from './layouts/AdminLayout';
import Dashboard from './pages/admin/Dashboard';
import UserManagement from './pages/admin/UserManagement';
import SystemConfig from './pages/admin/SystemConfig';
import OperationLogs from './pages/admin/OperationLogs';
import LoginLogs from './pages/admin/LoginLogs';

const { Header, Content } = Layout;

// 主布局组件（必须在Router内部）
const MainLayout: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  
  const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
  };
  
  // 根据当前路径设置选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/') return 'home';
    if (path.startsWith('/paths')) return 'paths';
    if (path.startsWith('/learning-path')) return 'paths';
    if (path.startsWith('/mistakes')) return 'mistakes';
    if (path.startsWith('/interview-simulator')) return 'interview';
    if (path.startsWith('/chat')) return 'chat';
    if (path.startsWith('/notes')) return 'notes';
    return 'home';
  };
  
  const handleMenuClick = (key: string) => {
    switch(key) {
      case 'home':
        navigate('/');
        break;
      case 'paths':
        navigate('/paths');
        break;
      case 'mistakes':
        // 跳转到统一的错题本页面
        navigate('/mistakes');
        break;
      case 'interview':
        navigate('/interview-simulator');
        break;
      case 'chat':
        navigate('/chat');
        break;
      case 'notes':
        navigate('/notes');
        break;
    }
  };
  
  // 构建用户菜单（管理员显示管理后台入口）
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心'
    },
    ...(user?.role === 'admin' ? [{
      key: 'admin',
      icon: <ControlOutlined />,
      label: '管理后台',
      onClick: () => navigate('/admin/dashboard')
    }] : []),
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout
    }
  ];
  
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      {/* 管理后台路由 */}
      <Route
        path="/admin"
        element={
          <PrivateRoute>
            {user?.role === 'admin' ? <AdminLayout /> : <Navigate to="/" replace />}
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="config" element={<SystemConfig />} />
        <Route path="operation-logs" element={<OperationLogs />} />
        <Route path="login-logs" element={<LoginLogs />} />
      </Route>
      
      {/* 主应用路由 */}
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout style={{ minHeight: '100vh' }}>
              <Header style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: '#fff',
                borderBottom: '1px solid #f0f0f0'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 40 }}>
                  <h2 style={{ margin: 0 }}>职途伴侣</h2>
                  <Menu
                    mode="horizontal"
                    selectedKeys={[getSelectedKey()]}
                    style={{ flex: 1, border: 'none' }}
                    onClick={({ key }) => handleMenuClick(key)}
                    items={[
                      { key: 'home', icon: <HomeOutlined />, label: '首页' },
                      { key: 'paths', icon: <BookOutlined />, label: '学习路线' },
                      { key: 'mistakes', icon: <ExclamationCircleOutlined />, label: '错题本' },
                      { key: 'interview', icon: <VideoCameraOutlined />, label: '模拟面试' },
                      { key: 'chat', icon: <MessageOutlined />, label: 'AI助手' },
                      { key: 'notes', icon: <FileTextOutlined />, label: '笔记' }
                    ]}
                  />
                </div>
                <Dropdown menu={{ items: userMenuItems }}>
                  <Button type="text" icon={<Avatar icon={<UserOutlined />} />}>
                    {user?.username}
                  </Button>
                </Dropdown>
              </Header>
              <Content style={{ padding: '24px', background: '#f0f2f5' }}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/paths" element={<LearningPathsListPage />} />
                  <Route path="/learning-path/:id" element={<LearningPathPage />} />
                  <Route path="/mistakes" element={<MistakesPage />} />
                  <Route path="/mistakes/:id" element={<MistakesPage />} />
                  <Route path="/interview-simulator" element={<InterviewSimulatorPage />} />
                  <Route path="/chat" element={<AIAssistantPage />} />
                  <Route path="/notes" element={<NotesPage />} />
                  <Route path="/profile" element={<div>个人中心（待实现）</div>} />
                </Routes>
              </Content>
            </Layout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
};

const App: React.FC = () => {
  const { loading, initAuth } = useAuthStore();
  
  useEffect(() => {
    initAuth();
  }, [initAuth]);
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );
};

export default App;

