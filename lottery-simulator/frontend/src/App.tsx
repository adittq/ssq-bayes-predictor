import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { useSelector, useDispatch } from 'react-redux';
import { store } from './store';
import { RootState } from './store';
import { getCurrentUser, logout } from './store/slices/authSlice';

// 布局组件
import MainLayout from './components/Layout/MainLayout';

// 页面组件
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import LotteryPage from './pages/LotteryPage';
import HistoryPage from './pages/HistoryPage';
import WalletPage from './pages/WalletPage';
import AnalysisPage from './pages/AnalysisPage';
import AccountPage from './pages/AccountPage';

// 通用组件
import ErrorBoundary from './components/Common/ErrorBoundary';
import NotificationProvider from './components/Common/NotificationProvider';

// 样式
import './index.css';

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// 应用内容组件
const AppContent: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, token } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // 应用启动时，如果有token则自动验证用户身份
    if (token) {
      dispatch(getCurrentUser() as any);
    }
  }, [dispatch, token]);

  useEffect(() => {
    // 监听401错误事件
    const handleAuthLogout = () => {
      dispatch(logout());
    };

    window.addEventListener('auth:logout', handleAuthLogout);
    
    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, [dispatch]);

  return (
    <Router>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* 需要布局的路由 */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="lottery" element={
            <ProtectedRoute>
              <LotteryPage />
            </ProtectedRoute>
          } />
          <Route path="history" element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          } />
          <Route path="wallet" element={
            <ProtectedRoute>
              <WalletPage />
            </ProtectedRoute>
          } />
          <Route path="analysis" element={
            <ProtectedRoute>
              <AnalysisPage />
            </ProtectedRoute>
          } />
          <Route path="account" element={
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          } />
          {/* 其他路由将在后续添加 */}
        </Route>
        
        {/* 默认重定向 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ConfigProvider locale={zhCN}>
        <ErrorBoundary>
          <NotificationProvider>
            <AppContent />
          </NotificationProvider>
        </ErrorBoundary>
      </ConfigProvider>
    </Provider>
  );
};

export default App;