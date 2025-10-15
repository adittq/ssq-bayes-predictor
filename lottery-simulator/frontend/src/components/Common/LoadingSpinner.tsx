import React from 'react';
import { Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  tip?: string;
  spinning?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  overlay?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip = '加载中...',
  spinning = true,
  children,
  style,
  overlay = false,
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: getSizeValue(size) }} spin />;

  function getSizeValue(size: 'small' | 'default' | 'large'): number {
    switch (size) {
      case 'small':
        return 16;
      case 'large':
        return 32;
      default:
        return 24;
    }
  }

  if (overlay && children) {
    return (
      <Spin 
        spinning={spinning} 
        indicator={antIcon} 
        tip={tip}
        style={style}
      >
        {children}
      </Spin>
    );
  }

  if (children) {
    return (
      <Spin 
        spinning={spinning} 
        indicator={antIcon} 
        tip={tip}
        style={style}
      >
        {children}
      </Spin>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '50px 20px',
        ...style,
      }}
    >
      <Spin indicator={antIcon} size={size} />
      {tip && (
        <Text 
          type="secondary" 
          style={{ 
            marginTop: 16, 
            fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 
          }}
        >
          {tip}
        </Text>
      )}
    </div>
  );
};

// 页面级加载组件
export const PageLoading: React.FC<{ tip?: string }> = ({ tip = '页面加载中...' }) => {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        zIndex: 9999,
      }}
    >
      <LoadingSpinner size="large" tip={tip} />
    </div>
  );
};

// 内容加载组件
export const ContentLoading: React.FC<{ 
  tip?: string; 
  height?: number | string;
}> = ({ 
  tip = '内容加载中...', 
  height = 200 
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: typeof height === 'number' ? `${height}px` : height,
        width: '100%',
      }}
    >
      <LoadingSpinner tip={tip} />
    </div>
  );
};

// 按钮加载组件
export const ButtonLoading: React.FC<{ 
  loading?: boolean; 
  children: React.ReactNode;
}> = ({ 
  loading = false, 
  children 
}) => {
  if (loading) {
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <LoadingOutlined />
        {children}
      </span>
    );
  }
  return <>{children}</>;
};

// 表格加载组件
export const TableLoading: React.FC<{ tip?: string }> = ({ tip = '数据加载中...' }) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: 300,
        width: '100%',
        backgroundColor: '#fafafa',
        border: '1px solid #f0f0f0',
        borderRadius: 6,
      }}
    >
      <LoadingSpinner tip={tip} />
    </div>
  );
};

export default LoadingSpinner;