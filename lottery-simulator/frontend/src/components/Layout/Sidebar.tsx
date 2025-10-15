import React from 'react';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  TrophyOutlined,
  BarChartOutlined,
  HistoryOutlined,
  PieChartOutlined,
  WalletOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Sider } = Layout;

interface SidebarProps {
  collapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
      onClick: () => navigate('/'),
    },
    {
      key: '/lottery',
      icon: <TrophyOutlined />,
      label: '双色球',
      onClick: () => navigate('/lottery'),
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: '数据分析',
      onClick: () => navigate('/analysis'),
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '购买记录',
      onClick: () => navigate('/history'),
    },
    {
      key: '/statistics',
      icon: <PieChartOutlined />,
      label: '统计报告',
      onClick: () => navigate('/statistics'),
    },
    {
      key: '/wallet',
      icon: <WalletOutlined />,
      label: '我的钱包',
      onClick: () => navigate('/wallet'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
    {
      key: '/help',
      icon: <QuestionCircleOutlined />,
      label: '帮助',
      onClick: () => navigate('/help'),
    },
  ];

  return (
    <Sider 
      trigger={null} 
      collapsible 
      collapsed={collapsed}
      width={200}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 64, // Header height
        zIndex: 100,
      }}
    >
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{ borderRight: 0 }}
      />
    </Sider>
  );
};

export default Sidebar;