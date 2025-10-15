import React, { useEffect } from 'react';
import { Row, Col, Card, Statistic, Button, Space, Typography } from 'antd';
import { TrophyOutlined, BarChartOutlined, WalletOutlined, HistoryOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { getCurrentPeriod } from '../store/slices/lotterySlice';
import { getAccountBalance } from '../store/slices/accountSlice';
import { formatCurrency, formatDate } from '../utils/format';

const { Title, Paragraph } = Typography;

const HomePage: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { currentPeriod } = useSelector((state: RootState) => state.lottery as any);
  const { balance } = useSelector((state: RootState) => state.account as any);

  useEffect(() => {
    dispatch(getCurrentPeriod() as any);
    if (isAuthenticated) {
      dispatch(getAccountBalance() as any);
    }
  }, [dispatch, isAuthenticated]);

  const quickActions = [
    {
      title: '购买双色球',
      description: '选择您的幸运号码',
      icon: <TrophyOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      action: () => navigate('/lottery'),
    },
    {
      title: '数据分析',
      description: '查看历史数据和趋势',
      icon: <BarChartOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      action: () => navigate('/analysis'),
    },
    {
      title: '我的钱包',
      description: '管理您的账户余额',
      icon: <WalletOutlined style={{ fontSize: 24, color: '#faad14' }} />,
      action: () => navigate('/wallet'),
    },
    {
      title: '购买记录',
      description: '查看历史购买记录',
      icon: <HistoryOutlined style={{ fontSize: 24, color: '#722ed1' }} />,
      action: () => navigate('/history'),
    },
  ];

  return (
    <div>
      {/* 欢迎区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[24, 24]} align="middle">
          <Col xs={24} md={16}>
            <Title level={2} style={{ marginBottom: 8 }}>
              欢迎来到双色球模拟器
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 16 }}>
              体验真实的双色球购买流程，分析历史数据，提升您的选号技巧
            </Paragraph>
            {!isAuthenticated && (
              <Space>
                <Button type="primary" size="large" onClick={() => navigate('/register')}>
                  立即注册
                </Button>
                <Button size="large" onClick={() => navigate('/login')}>
                  登录
                </Button>
              </Space>
            )}
          </Col>
          <Col xs={24} md={8}>
            <div style={{ textAlign: 'center' }}>
              <TrophyOutlined style={{ fontSize: 80, color: '#1890ff' }} />
            </div>
          </Col>
        </Row>
      </Card>

      {/* 统计信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="当前期号"
              value={currentPeriod?.period || '加载中...'}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="开奖时间"
              value={currentPeriod ? formatDate(currentPeriod.draw_date, 'MM-DD') : '加载中...'}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="账户余额"
              value={isAuthenticated ? formatCurrency(balance?.available_balance || 0) : '请登录'}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="今日购买"
              value="0"
              suffix="注"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 快捷操作 */}
      <Card title="快捷操作" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          {quickActions.map((action, index) => (
            <Col xs={12} sm={6} key={index}>
              <Card
                hoverable
                style={{ textAlign: 'center', height: '100%' }}
                onClick={action.action}
              >
                <div style={{ marginBottom: 16 }}>
                  {action.icon}
                </div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  {action.title}
                </Title>
                <Paragraph style={{ color: '#666', marginBottom: 0 }}>
                  {action.description}
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 功能介绍 */}
      <Card title="功能特色">
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <TrophyOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            </div>
            <Title level={4} style={{ textAlign: 'center' }}>真实模拟</Title>
            <Paragraph style={{ textAlign: 'center', color: '#666' }}>
              完全按照真实双色球规则进行模拟，包括开奖时间、奖金计算等
            </Paragraph>
          </Col>
          <Col xs={24} md={8}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <BarChartOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            </div>
            <Title level={4} style={{ textAlign: 'center' }}>数据分析</Title>
            <Paragraph style={{ textAlign: 'center', color: '#666' }}>
              提供丰富的历史数据分析，包括号码频率、趋势分析、智能推荐等
            </Paragraph>
          </Col>
          <Col xs={24} md={8}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <WalletOutlined style={{ fontSize: 48, color: '#faad14' }} />
            </div>
            <Title level={4} style={{ textAlign: 'center' }}>资金管理</Title>
            <Paragraph style={{ textAlign: 'center', color: '#666' }}>
              完善的虚拟资金管理系统，让您体验真实的资金流动
            </Paragraph>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default HomePage;