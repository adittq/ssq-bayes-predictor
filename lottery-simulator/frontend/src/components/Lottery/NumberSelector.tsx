import React, { useState } from 'react';
import { Card, Button, Space, Typography, message, Divider } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface NumberSelectorProps {
  onNumbersChange: (redBalls: number[], blueBall: number) => void;
  selectedRedBalls: number[];
  selectedBlueBall: number | null;
  disabled?: boolean;
}

const NumberSelector: React.FC<NumberSelectorProps> = ({
  onNumbersChange,
  selectedRedBalls,
  selectedBlueBall,
  disabled = false,
}) => {
  const [redBalls, setRedBalls] = useState<number[]>(selectedRedBalls);
  const [blueBall, setBlueBall] = useState<number | null>(selectedBlueBall);

  // 生成红球号码数组 (01-33)
  const redNumbers = Array.from({ length: 33 }, (_, i) => i + 1);
  // 生成蓝球号码数组 (01-16)
  const blueNumbers = Array.from({ length: 16 }, (_, i) => i + 1);

  const handleRedBallClick = (number: number) => {
    if (disabled) return;

    let newRedBalls: number[];
    if (redBalls.includes(number)) {
      // 取消选择
      newRedBalls = redBalls.filter(n => n !== number);
    } else {
      // 选择号码
      if (redBalls.length >= 6) {
        message.warning('最多只能选择6个红球号码');
        return;
      }
      newRedBalls = [...redBalls, number].sort((a, b) => a - b);
    }
    
    setRedBalls(newRedBalls);
    onNumbersChange(newRedBalls, blueBall || 0);
  };

  const handleBlueBallClick = (number: number) => {
    if (disabled) return;

    const newBlueBall = blueBall === number ? null : number;
    setBlueBall(newBlueBall);
    onNumbersChange(redBalls, newBlueBall || 0);
  };

  const handleQuickPick = () => {
    if (disabled) return;

    // 随机选择6个红球
    const shuffledRed = [...redNumbers].sort(() => Math.random() - 0.5);
    const randomRedBalls = shuffledRed.slice(0, 6).sort((a, b) => a - b);
    
    // 随机选择1个蓝球
    const randomBlueBall = blueNumbers[Math.floor(Math.random() * blueNumbers.length)];
    
    setRedBalls(randomRedBalls);
    setBlueBall(randomBlueBall);
    onNumbersChange(randomRedBalls, randomBlueBall);
    
    message.success('已为您随机选择号码');
  };

  const handleClear = () => {
    if (disabled) return;

    setRedBalls([]);
    setBlueBall(null);
    onNumbersChange([], 0);
  };

  const formatNumber = (num: number) => num.toString().padStart(2, '0');

  const isComplete = redBalls.length === 6 && blueBall !== null;

  return (
    <Card title="选择号码" style={{ marginBottom: 16 }}>
      {/* 红球选择区域 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          红球区 (选择6个号码)
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 14 }}>
            已选择 {redBalls.length}/6
          </Text>
        </Title>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(11, 1fr)', 
          gap: 8,
          marginBottom: 16 
        }}>
          {redNumbers.map(number => (
            <Button
              key={number}
              type={redBalls.includes(number) ? 'primary' : 'default'}
              size="small"
              style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                fontSize: 12,
                fontWeight: 'bold',
                backgroundColor: redBalls.includes(number) ? '#ff4d4f' : undefined,
                borderColor: redBalls.includes(number) ? '#ff4d4f' : undefined,
              }}
              onClick={() => handleRedBallClick(number)}
              disabled={disabled}
            >
              {formatNumber(number)}
            </Button>
          ))}
        </div>
      </div>

      <Divider />

      {/* 蓝球选择区域 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          蓝球区 (选择1个号码)
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 14 }}>
            {blueBall ? `已选择 ${formatNumber(blueBall)}` : '未选择'}
          </Text>
        </Title>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(8, 1fr)', 
          gap: 8,
          marginBottom: 16 
        }}>
          {blueNumbers.map(number => (
            <Button
              key={number}
              type={blueBall === number ? 'primary' : 'default'}
              size="small"
              style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                fontSize: 12,
                fontWeight: 'bold',
                backgroundColor: blueBall === number ? '#1890ff' : undefined,
                borderColor: blueBall === number ? '#1890ff' : undefined,
              }}
              onClick={() => handleBlueBallClick(number)}
              disabled={disabled}
            >
              {formatNumber(number)}
            </Button>
          ))}
        </div>
      </div>

      {/* 操作按钮 */}
      <Space>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={handleQuickPick}
          disabled={disabled}
        >
          机选
        </Button>
        <Button onClick={handleClear} disabled={disabled}>
          清空
        </Button>
        <div style={{ marginLeft: 16 }}>
          <Text strong style={{ color: isComplete ? '#52c41a' : '#ff4d4f' }}>
            {isComplete ? '✓ 号码选择完成' : '请完成号码选择'}
          </Text>
        </div>
      </Space>

      {/* 选中号码显示 */}
      {(redBalls.length > 0 || blueBall) && (
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          background: '#f5f5f5', 
          borderRadius: 6 
        }}>
          <Text strong>已选号码：</Text>
          <div style={{ marginTop: 8 }}>
            <Space>
              {redBalls.map(num => (
                <span
                  key={num}
                  style={{
                    display: 'inline-block',
                    width: 28,
                    height: 28,
                    lineHeight: '28px',
                    textAlign: 'center',
                    backgroundColor: '#ff4d4f',
                    color: 'white',
                    borderRadius: '50%',
                    fontSize: 12,
                    fontWeight: 'bold',
                  }}
                >
                  {formatNumber(num)}
                </span>
              ))}
              {blueBall && (
                <>
                  <span style={{ margin: '0 8px', color: '#666' }}>|</span>
                  <span
                    style={{
                      display: 'inline-block',
                      width: 28,
                      height: 28,
                      lineHeight: '28px',
                      textAlign: 'center',
                      backgroundColor: '#1890ff',
                      color: 'white',
                      borderRadius: '50%',
                      fontSize: 12,
                      fontWeight: 'bold',
                    }}
                  >
                    {formatNumber(blueBall)}
                  </span>
                </>
              )}
            </Space>
          </div>
        </div>
      )}
    </Card>
  );
};

export default NumberSelector;