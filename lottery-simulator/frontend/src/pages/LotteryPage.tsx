import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Typography, Space, Button, Divider, Statistic } from 'antd';
import { TrophyOutlined, HistoryOutlined, BarChartOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { getCurrentPeriod, quickPick, clearQuickPick } from '../store/slices/lotterySlice';
import { getAccountBalance } from '../store/slices/accountSlice';
import NumberSelector from '../components/Lottery/NumberSelector';
import PurchasePanel from '../components/Lottery/PurchasePanel';
import { formatDate, formatCurrency } from '../utils/format';

const { Title, Text } = Typography;

const LotteryPage: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [selectedRedBalls, setSelectedRedBalls] = useState<number[]>([]);
  const [selectedBlueBall, setSelectedBlueBall] = useState<number>(0);

  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { currentPeriod, quickPickNumbers, loading } = useSelector((state: RootState) => state.lottery as any);
  const { balance } = useSelector((state: RootState) => state.account as any);

  useEffect(() => {
    dispatch(getCurrentPeriod() as any);
    if (isAuthenticated) {
      dispatch(getAccountBalance() as any);
    }
  }, [dispatch, isAuthenticated]);

  // 当机选号码更新时，自动填充到选择器
  useEffect(() => {
    if (quickPickNumbers) {
      setSelectedRedBalls(quickPickNumbers.red_balls);
      setSelectedBlueBall(quickPickNumbers.blue_ball);
    }
  }, [quickPickNumbers]);

  const handleNumbersChange = (redBalls: number[], blueBall: number) => {
    setSelectedRedBalls(redBalls);
    setSelectedBlueBall(blueBall);
    // 清除机选状态
    if (quickPickNumbers) {
      dispatch(clearQuickPick());
    }
  };

  const handleQuickPick = () => {
    dispatch(quickPick() as any);
  };

  const handlePurchaseSuccess = () => {
    // 购买成功后清空选择
    setSelectedRedBalls([]);
    setSelectedBlueBall(0);
    dispatch(clearQuickPick());
    // 刷新余额
    if (isAuthenticated) {
      dispatch(getAccountBalance() as any);
    }
  };

  const formatNumbers = (redBalls: number[], blueBall: number) => {
    if (redBalls.length === 0 && blueBall === 0) return '请选择号码';
    const redStr = redBalls.map(n => n.toString().padStart(2, '0')).join(' ');
    const blueStr = blueBall > 0 ? blueBall.toString().padStart(2, '0') : '--';
    return `${redStr} | ${blueStr}`;
  };

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <TrophyOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          双色球购买
        </Title>
        <Text type="secondary">
          选择您的幸运号码，开启中奖之旅
        </Text>
      </div>

      {/* 当前期信息 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={6}>
            <Statistic
              title="当前期号"
              value={currentPeriod?.period || '加载中...'}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic
              title="开奖时间"
              value={currentPeriod ? formatDate(currentPeriod.draw_date, 'YYYY-MM-DD HH:mm') : '加载中...'}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic
              title="销售状态"
              value={currentPeriod?.can_purchase ? '正在销售' : '已截止'}
              valueStyle={{ 
                color: currentPeriod?.can_purchase ? '#52c41a' : '#ff4d4f' 
              }}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic
              title="账户余额"
              value={isAuthenticated ? formatCurrency(balance?.available_balance || 0) : '请登录'}
              valueStyle={{ color: '#faad14' }}
            />
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]}>
        {/* 左侧：号码选择 */}
        <Col xs={24} lg={16}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* 快捷操作 */}
            <Card size="small">
              <Space>
                <Button 
                  type="primary" 
                  onClick={handleQuickPick}
                  loading={loading}
                  disabled={!currentPeriod?.can_purchase}
                >
                  机选一注
                </Button>
                <Button onClick={() => navigate('/analysis')}>
                  <BarChartOutlined /> 数据分析
                </Button>
                <Button onClick={() => navigate('/history')}>
                  <HistoryOutlined /> 购买记录
                </Button>
              </Space>
            </Card>

            {/* 号码选择器 */}
            <NumberSelector
              onNumbersChange={handleNumbersChange}
              selectedRedBalls={selectedRedBalls}
              selectedBlueBall={selectedBlueBall}
              disabled={!currentPeriod?.can_purchase}
            />

            {/* 当前选择显示 */}
            <Card title="当前选择" size="small">
              <div style={{
                padding: 16,
                background: '#f5f5f5',
                borderRadius: 6,
                textAlign: 'center',
                fontSize: 18,
                fontWeight: 'bold',
                fontFamily: 'monospace',
              }}>
                {formatNumbers(selectedRedBalls, selectedBlueBall)}
              </div>
            </Card>
          </Space>
        </Col>

        {/* 右侧：购买面板 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <PurchasePanel
              redBalls={selectedRedBalls}
              blueBall={selectedBlueBall}
              onPurchaseSuccess={handlePurchaseSuccess}
            />

            {/* 游戏规则 */}
            <Card title="游戏规则" size="small">
              <Space direction="vertical" size="small">
                <Text>• 红球：从01-33中选择6个号码</Text>
                <Text>• 蓝球：从01-16中选择1个号码</Text>
                <Text>• 单注金额：2元</Text>
                <Text>• 开奖时间：每周二、四、日</Text>
                <Divider style={{ margin: '8px 0' }} />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  本系统为模拟系统，仅供娱乐学习使用
                </Text>
              </Space>
            </Card>

            {/* 中奖说明 */}
            <Card title="中奖说明" size="small">
              <Space direction="vertical" size="small">
                <Text>一等奖：6+1 (浮动奖金)</Text>
                <Text>二等奖：6+0 (浮动奖金)</Text>
                <Text>三等奖：5+1 (3000元)</Text>
                <Text>四等奖：5+0/4+1 (200元)</Text>
                <Text>五等奖：4+0/3+1 (10元)</Text>
                <Text>六等奖：2+1/1+1/0+1 (5元)</Text>
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default LotteryPage;