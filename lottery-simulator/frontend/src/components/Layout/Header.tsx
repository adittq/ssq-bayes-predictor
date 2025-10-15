import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Badge, Button } from 'antd';
import { UserOutlined, BellOutlined, LogoutOutlined, SettingOutlined, WalletOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { formatCurrency } from '../../utils/format';

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { balance } = useSelector((state: RootState) => state.account as any);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'wallet',
      icon: <WalletOutlined />,
      label: '我的钱包',
      onClick: () => navigate('/wallet'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  const mainMenuItems = [
    {
      key: 'home',
      label: '首页',
      onClick: () => navigate('/'),
    },
    {
      key: 'lottery',
      label: '双色球',
      onClick: () => navigate('/lottery'),
    },
    {
      key: 'analysis',
      label: '数据分析',
      onClick: () => navigate('/analysis'),
    },
    {
      key: 'history',
      label: '购买记录',
      onClick: () => navigate('/history'),
    },
    {
      key: 'statistics',
      label: '统计报告',
      onClick: () => navigate('/statistics'),
    },
  ];

  return (
    <AntHeader className="header">
      <div className="header-content">
        <div className="logo">
          <h2 style={{ color: '#fff', margin: 0 }}>双色球模拟器</h2>
        </div>
        
        <Menu
          theme="dark"
          mode="horizontal"
          items={mainMenuItems}
          style={{ flex: 1, minWidth: 0 }}
        />

        <div className="header-actions">
          {isAuthenticated ? (
            <Space size="large">
              {/* 余额显示 */}
              <div className="balance-display">
                <WalletOutlined style={{ color: '#52c41a' }} />
                <span style={{ color: '#fff', marginLeft: 8 }}>
                  余额: {formatCurrency(balance?.available_balance || 0)}
                </span>
              </div>

              {/* 通知 */}
              <Badge count={0} size="small">
                <BellOutlined 
                  style={{ fontSize: '18px', color: '#fff', cursor: 'pointer' }}
                  onClick={() => navigate('/notifications')}
                />
              </Badge>

              {/* 用户菜单 */}
              <Dropdown
                menu={{ items: userMenuItems }}
                placement="bottomRight"
                trigger={['click']}
              >
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar 
                    size="small" 
                    icon={<UserOutlined />}
                    src={(user as any)?.avatar}
                  />
                  <span style={{ color: '#fff' }}>{user?.username}</span>
                </Space>
              </Dropdown>
            </Space>
          ) : (
            <Space>
              <Button onClick={() => navigate('/login')}>
                登录
              </Button>
              <Button type="primary" onClick={() => navigate('/register')}>
                注册
              </Button>
            </Space>
          )}
        </div>
      </div>
    </AntHeader>
  );
};

export default Header;