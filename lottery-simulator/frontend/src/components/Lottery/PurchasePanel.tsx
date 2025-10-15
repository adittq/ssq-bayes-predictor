import React, { useState } from 'react';
import { Card, InputNumber, Button, Space, Typography, Divider, message, Modal } from 'antd';
import { ShoppingCartOutlined, WalletOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import { purchaseLottery } from '../../store/slices/lotterySlice';
import { formatCurrency } from '../../utils/format';

const { Title, Text } = Typography;

interface PurchasePanelProps {
  redBalls: number[];
  blueBall: number;
  onPurchaseSuccess?: () => void;
}

const PurchasePanel: React.FC<PurchasePanelProps> = ({
  redBalls,
  blueBall,
  onPurchaseSuccess,
}) => {
  const dispatch = useDispatch();
  const [multiple, setMultiple] = useState(1);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [purchasing, setPurchasing] = useState(false);

  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { balance } = useSelector((state: RootState) => state.account as any);
  const { loading } = useSelector((state: RootState) => state.lottery as any);

  const TICKET_PRICE = 2; // 每注2元
  const totalCost = multiple * TICKET_PRICE;
  const isComplete = redBalls.length === 6 && blueBall > 0;
  const hasEnoughBalance = balance?.available_balance >= totalCost;

  const handlePurchase = () => {
    if (!isAuthenticated) {
      message.warning('请先登录');
      return;
    }

    if (!isComplete) {
      message.warning('请先完成号码选择');
      return;
    }

    if (!hasEnoughBalance) {
      message.error('余额不足，请先充值');
      return;
    }

    setIsModalVisible(true);
  };

  const confirmPurchase = async () => {
    try {
      setPurchasing(true);
      const purchaseData = {
        red_balls: redBalls,
        blue_ball: blueBall,
        multiple: multiple,
      };

      const result = await dispatch(purchaseLottery(purchaseData) as any);
      
      if (purchaseLottery.fulfilled.match(result)) {
        message.success('购买成功！');
        setIsModalVisible(false);
        onPurchaseSuccess?.();
      } else {
        message.error(result.payload as string || '购买失败');
      }
    } catch (error) {
      message.error('购买失败，请重试');
    } finally {
      setPurchasing(false);
    }
  };

  const formatNumbers = () => {
    const redStr = redBalls.map(n => n.toString().padStart(2, '0')).join(' ');
    const blueStr = blueBall.toString().padStart(2, '0');
    return `${redStr} | ${blueStr}`;
  };

  return (
    <>
      <Card title="购买设置" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 倍数设置 */}
          <div>
            <Title level={5} style={{ marginBottom: 8 }}>
              购买倍数
            </Title>
            <Space align="center">
              <InputNumber
                min={1}
                max={99}
                value={multiple}
                onChange={(value) => setMultiple(value || 1)}
                style={{ width: 100 }}
                disabled={!isComplete}
              />
              <Text>倍</Text>
              <Text type="secondary">
                (单注 {formatCurrency(TICKET_PRICE)})
              </Text>
            </Space>
          </div>

          <Divider style={{ margin: '16px 0' }} />

          {/* 费用计算 */}
          <div>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>单注金额:</Text>
                <Text strong>{formatCurrency(TICKET_PRICE)}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>购买倍数:</Text>
                <Text strong>{multiple} 倍</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>总计金额:</Text>
                <Text strong style={{ fontSize: 16, color: '#ff4d4f' }}>
                  {formatCurrency(totalCost)}
                </Text>
              </div>
            </Space>
          </div>

          <Divider style={{ margin: '16px 0' }} />

          {/* 余额信息 */}
          {isAuthenticated && (
            <div>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text>
                    <WalletOutlined /> 账户余额:
                  </Text>
                  <Text strong style={{ color: '#52c41a' }}>
                    {formatCurrency(balance?.available_balance || 0)}
                  </Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text>购买后余额:</Text>
                  <Text 
                    strong 
                    style={{ 
                      color: hasEnoughBalance ? '#52c41a' : '#ff4d4f' 
                    }}
                  >
                    {formatCurrency((balance?.available_balance || 0) - totalCost)}
                  </Text>
                </div>
              </Space>
            </div>
          )}

          {/* 购买按钮 */}
          <Button
            type="primary"
            size="large"
            icon={<ShoppingCartOutlined />}
            onClick={handlePurchase}
            disabled={!isComplete || !hasEnoughBalance || loading}
            loading={loading}
            block
            style={{ marginTop: 16 }}
          >
            {!isAuthenticated 
              ? '请先登录' 
              : !isComplete 
                ? '请完成号码选择' 
                : !hasEnoughBalance 
                  ? '余额不足' 
                  : `购买 ${formatCurrency(totalCost)}`
            }
          </Button>

          {!isAuthenticated && (
            <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
              登录后即可购买彩票
            </Text>
          )}
        </Space>
      </Card>

      {/* 购买确认弹窗 */}
      <Modal
        title="确认购买"
        open={isModalVisible}
        onOk={confirmPurchase}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={purchasing}
        okText="确认购买"
        cancelText="取消"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>选择号码:</Text>
            <div style={{ 
              marginTop: 8, 
              padding: 12, 
              background: '#f5f5f5', 
              borderRadius: 6,
              textAlign: 'center',
              fontSize: 16,
              fontWeight: 'bold',
            }}>
              {formatNumbers()}
            </div>
          </div>
          
          <Divider style={{ margin: '16px 0' }} />
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text>购买倍数:</Text>
            <Text strong>{multiple} 倍</Text>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text>总计金额:</Text>
            <Text strong style={{ fontSize: 16, color: '#ff4d4f' }}>
              {formatCurrency(totalCost)}
            </Text>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text>账户余额:</Text>
            <Text strong>{formatCurrency(balance?.available_balance || 0)}</Text>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text>购买后余额:</Text>
            <Text strong style={{ color: '#52c41a' }}>
              {formatCurrency((balance?.available_balance || 0) - totalCost)}
            </Text>
          </div>
        </Space>
      </Modal>
    </>
  );
};

export default PurchasePanel;