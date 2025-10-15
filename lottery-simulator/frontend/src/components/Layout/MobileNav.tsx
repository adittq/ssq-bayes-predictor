import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  HomeOutlined,
  TrophyOutlined,
  BarChartOutlined,
  HistoryOutlined,
  WalletOutlined
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

const MobileNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  // 如果未登录，不显示底部导航
  if (!isAuthenticated) {
    return null;
  }

  const navItems = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { key: '/lottery', icon: <TrophyOutlined />, label: '双色球' },
    { key: '/analysis', icon: <BarChartOutlined />, label: '分析' },
    { key: '/history', icon: <HistoryOutlined />, label: '记录' },
    { key: '/wallet', icon: <WalletOutlined />, label: '钱包' },
  ];

  const handleNavClick = (path: string) => {
    navigate(path);
  };

  return (
    <>
      <div 
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          backgroundColor: 'white',
          borderTop: '1px solid #f0f0f0',
          display: 'none',
          height: 60,
          boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.1)',
        }}
        className="mobile-nav"
      >
        <div
          style={{
            display: 'flex',
            height: '100%',
            alignItems: 'center',
            justifyContent: 'space-around',
          }}
        >
          {navItems.map((item) => {
            const isActive = location.pathname === item.key;
            return (
              <div
                key={item.key}
                onClick={() => handleNavClick(item.key)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '4px 8px',
                  cursor: 'pointer',
                  color: isActive ? '#1890ff' : '#8c8c8c',
                  transition: 'color 0.3s ease',
                  minWidth: 60,
                }}
              >
                <div
                  style={{
                    fontSize: 20,
                    marginBottom: 2,
                    transform: isActive ? 'scale(1.1)' : 'scale(1)',
                    transition: 'transform 0.3s ease',
                  }}
                >
                  {item.icon}
                </div>
                <div
                  style={{
                    fontSize: 12,
                    fontWeight: isActive ? 600 : 400,
                    lineHeight: 1,
                  }}
                >
                  {item.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <style>{`
        @media (max-width: 768px) {
          .mobile-nav {
            display: block !important;
          }
          
          .ant-layout-content {
            padding-bottom: 80px !important;
          }
          
          .ant-layout-sider {
            display: none !important;
          }
        }
      `}</style>
    </>
  );
};

export default MobileNav;