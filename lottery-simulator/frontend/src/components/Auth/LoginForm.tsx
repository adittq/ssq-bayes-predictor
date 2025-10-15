import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Divider, Space } from 'antd';
import { UserOutlined, LockOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { RootState } from '../../store';
import { login } from '../../store/slices/authSlice';

interface LoginFormData {
  username: string;
  password: string;
}

const LoginForm: React.FC = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state: RootState) => state.auth);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onFinish = async (values: LoginFormData) => {
    try {
      setIsSubmitting(true);
      const result = await dispatch(login(values) as any);
      
      if (login.fulfilled.match(result)) {
        message.success('登录成功！');
        navigate('/');
      } else {
        message.error(result.payload as string || '登录失败');
      }
    } catch (error) {
      message.error('登录失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
    message.error('请检查输入信息');
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          borderRadius: 8,
        }}
        bodyStyle={{ padding: '32px' }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
            双色球模拟器
          </h1>
          <p style={{ color: '#666', fontSize: 14 }}>
            登录您的账户
          </p>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名!' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码!' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              autoComplete="current-password"
              iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading || isSubmitting}
              block
              style={{ height: 40 }}
            >
              登录
            </Button>
          </Form.Item>

          <Divider plain>
            <span style={{ color: '#999', fontSize: 12 }}>其他选项</span>
          </Divider>

          <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
            <Link to="/register" style={{ color: '#1890ff' }}>
              还没有账户？立即注册
            </Link>
            <Link to="/forgot-password" style={{ color: '#999', fontSize: 12 }}>
              忘记密码？
            </Link>
          </Space>
        </Form>
      </Card>
    </div>
  );
};

export default LoginForm;