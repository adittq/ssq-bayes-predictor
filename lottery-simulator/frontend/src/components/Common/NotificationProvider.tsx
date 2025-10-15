import React, { createContext, useContext, ReactNode } from 'react';
import { notification } from 'antd';
import { 
  CheckCircleOutlined, 
  ExclamationCircleOutlined, 
  InfoCircleOutlined, 
  CloseCircleOutlined 
} from '@ant-design/icons';

type NotificationType = 'success' | 'info' | 'warning' | 'error';

interface NotificationConfig {
  message: string;
  description?: string;
  duration?: number;
  placement?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
}

interface NotificationContextType {
  showSuccess: (config: NotificationConfig) => void;
  showError: (config: NotificationConfig) => void;
  showWarning: (config: NotificationConfig) => void;
  showInfo: (config: NotificationConfig) => void;
  showNotification: (type: NotificationType, config: NotificationConfig) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  // 配置全局通知样式
  React.useEffect(() => {
    notification.config({
      placement: 'topRight',
      duration: 4.5,
      rtl: false,
    });
  }, []);

  const showNotification = (type: NotificationType, config: NotificationConfig) => {
    const icons = {
      success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      error: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      warning: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
      info: <InfoCircleOutlined style={{ color: '#1890ff' }} />,
    };

    notification[type]({
      message: config.message,
      description: config.description,
      duration: config.duration,
      placement: config.placement,
      icon: icons[type],
      style: {
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      },
    });
  };

  const showSuccess = (config: NotificationConfig) => {
    showNotification('success', config);
  };

  const showError = (config: NotificationConfig) => {
    showNotification('error', config);
  };

  const showWarning = (config: NotificationConfig) => {
    showNotification('warning', config);
  };

  const showInfo = (config: NotificationConfig) => {
    showNotification('info', config);
  };

  const value: NotificationContextType = {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

// 预定义的通知消息
export const NotificationMessages = {
  // 成功消息
  SUCCESS: {
    LOGIN: { message: '登录成功', description: '欢迎回来！' },
    REGISTER: { message: '注册成功', description: '账户创建成功，请登录' },
    PURCHASE: { message: '购买成功', description: '彩票购买成功，祝您好运！' },
    PROFILE_UPDATE: { message: '信息更新成功', description: '个人信息已成功更新' },
    PASSWORD_CHANGE: { message: '密码修改成功', description: '密码已成功修改' },
  },
  
  // 错误消息
  ERROR: {
    LOGIN_FAILED: { message: '登录失败', description: '用户名或密码错误' },
    REGISTER_FAILED: { message: '注册失败', description: '请检查输入信息' },
    NETWORK_ERROR: { message: '网络错误', description: '请检查网络连接后重试' },
    INSUFFICIENT_BALANCE: { message: '余额不足', description: '请先充值后再购买' },
    PURCHASE_FAILED: { message: '购买失败', description: '购买过程中出现错误' },
    UNAUTHORIZED: { message: '未授权访问', description: '请先登录后再操作' },
  },
  
  // 警告消息
  WARNING: {
    UNSAVED_CHANGES: { message: '有未保存的更改', description: '离开页面前请保存更改' },
    SESSION_EXPIRE: { message: '会话即将过期', description: '请及时保存数据' },
    HIGH_AMOUNT: { message: '购买金额较大', description: '请确认购买金额无误' },
  },
  
  // 信息消息
  INFO: {
    LOADING: { message: '正在加载', description: '请稍候...' },
    NO_DATA: { message: '暂无数据', description: '当前没有可显示的数据' },
    FEATURE_COMING: { message: '功能开发中', description: '该功能正在开发中，敬请期待' },
    MAINTENANCE: { message: '系统维护', description: '系统正在维护中，请稍后再试' },
  },
};

export default NotificationProvider;