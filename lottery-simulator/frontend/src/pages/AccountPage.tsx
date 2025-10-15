import React, { useEffect, useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Form, 
  Input, 
  Button, 
  Avatar, 
  Upload, 
  message, 
  Tabs, 
  Descriptions,
  Modal,
  Space,
  Typography,
  Divider,
  Switch,
  Select
} from 'antd';
import { 
  UserOutlined, 
  EditOutlined, 
  LockOutlined, 
  CameraOutlined,
  PhoneOutlined,
  MailOutlined,
  IdcardOutlined,
  BellOutlined,
  SecurityScanOutlined
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { authAPI } from '../services/api';
import type { UploadProps } from 'antd';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const AccountPage: React.FC = () => {
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [settingsForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('profile');
  const [editMode, setEditMode] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);

  const { user, loading } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        phone: user.phone,
      });
      
      settingsForm.setFieldsValue({
        email_notifications: false,
        sms_notifications: false,
        push_notifications: true,
        privacy_level: 'normal',
        auto_logout: 30,
      });
    }
  }, [user, form, settingsForm]);

  const handleProfileUpdate = async (values: any) => {
    try {
      const response = await authAPI.updateProfile({
        nickname: values.nickname,
        phone: values.phone,
        email: values.email
      });
      
      if (response.data.success) {
        message.success('个人信息更新成功');
        setEditMode(false);
        // 可以考虑更新Redux store中的用户信息
      } else {
        message.error(response.data.message || '更新失败');
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || error.message || '更新失败');
    }
  };

  const handlePasswordChange = async (values: any) => {
    try {
      const response = await authAPI.changePassword({
        old_password: values.oldPassword,
        new_password: values.newPassword
      });
      
      if (response.data.success) {
        message.success('密码修改成功');
        setPasswordModalVisible(false);
        passwordForm.resetFields();
      } else {
        message.error(response.data.message || '密码修改失败');
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || error.message || '密码修改失败');
    }
  };

  const handleSettingsUpdate = async (values: any) => {
    try {
      // 将设置保存到用户偏好中
      const preferences = JSON.stringify(values);
      
      // 注意：这里需要后端支持preferences字段的更新
      // 暂时使用本地存储作为临时方案
      localStorage.setItem('userPreferences', preferences);
      message.success('设置已保存');
      
      // 如果后端支持preferences字段，可以使用以下代码：
      // const response = await authAPI.updateProfile({ preferences });
      // if (response.data.success) {
      //   message.success('设置更新成功');
      // }
    } catch (error: any) {
      message.error(error.response?.data?.message || error.message || '设置更新失败');
    }
  };

  const uploadProps: UploadProps = {
    name: 'avatar',
    showUploadList: false,
    beforeUpload: (file) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
      if (!isJpgOrPng) {
        message.error('只能上传 JPG/PNG 格式的图片!');
        return false;
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB!');
        return false;
      }
      return true;
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        // 将图片转换为base64
        const reader = new FileReader();
        reader.onload = async () => {
          try {
            const base64 = reader.result as string;
            
            // 调用API更新头像
            const response = await authAPI.updateProfile({
              avatar: base64
            });
            
            if (response.data.success) {
              message.success('头像上传成功');
              onSuccess?.(file);
              // 可以考虑更新Redux store中的用户信息
            } else {
              message.error(response.data.message || '头像上传失败');
              onError?.(new Error('上传失败'));
            }
          } catch (error: any) {
            message.error(error.response?.data?.message || error.message || '头像上传失败');
            onError?.(error);
          }
        };
        reader.readAsDataURL(file as File);
      } catch (error: any) {
        message.error(error.message || '头像上传失败');
        onError?.(error);
      }
    },
  };

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <UserOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          账户管理
        </Title>
        <Text type="secondary">
          管理您的个人信息、安全设置和偏好配置
        </Text>
      </div>

      <Row gutter={[24, 24]}>
        {/* 左侧用户信息卡片 */}
        <Col xs={24} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Upload {...uploadProps}>
                <div style={{ position: 'relative', display: 'inline-block' }}>
                  <Avatar 
                    size={100} 
                    icon={<UserOutlined />}
                    style={{ cursor: 'pointer' }}
                  />
                  <div 
                    style={{
                      position: 'absolute',
                      bottom: 0,
                      right: 0,
                      background: '#1890ff',
                      borderRadius: '50%',
                      width: 28,
                      height: 28,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      border: '2px solid white'
                    }}
                  >
                    <CameraOutlined style={{ color: 'white', fontSize: 12 }} />
                  </div>
                </div>
              </Upload>
              
              <div style={{ marginTop: 16 }}>
                <Title level={4}>{user?.username}</Title>
                <Text type="secondary">{user?.email}</Text>
              </div>
              
              <Divider />
              
              <Descriptions column={1} size="small">
                <Descriptions.Item label="用户ID">
                  {user?.id}
                </Descriptions.Item>
                <Descriptions.Item label="注册时间">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最后登录">
                  -
                </Descriptions.Item>
                <Descriptions.Item label="账户状态">
                  <span style={{ color: '#52c41a' }}>
                    正常
                  </span>
                </Descriptions.Item>
              </Descriptions>
            </div>
          </Card>
        </Col>

        {/* 右侧详细信息 */}
        <Col xs={24} lg={16}>
          <Card>
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {/* 个人信息 */}
              <TabPane 
                tab={
                  <span>
                    <IdcardOutlined />
                    个人信息
                  </span>
                } 
                key="profile"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                  <Title level={4}>个人信息</Title>
                  <Button 
                    type={editMode ? 'default' : 'primary'}
                    icon={<EditOutlined />}
                    onClick={() => setEditMode(!editMode)}
                  >
                    {editMode ? '取消编辑' : '编辑信息'}
                  </Button>
                </div>

                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleProfileUpdate}
                  disabled={!editMode}
                >
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="用户名"
                        name="username"
                        rules={[{ required: true, message: '请输入用户名' }]}
                      >
                        <Input prefix={<UserOutlined />} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="邮箱"
                        name="email"
                        rules={[
                          { required: true, message: '请输入邮箱' },
                          { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                      >
                        <Input prefix={<MailOutlined />} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="手机号"
                        name="phone"
                        rules={[
                          { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                        ]}
                      >
                        <Input prefix={<PhoneOutlined />} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="真实姓名"
                        name="real_name"
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    label="身份证号"
                    name="id_card"
                    rules={[
                      { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '请输入有效的身份证号' }
                    ]}
                  >
                    <Input />
                  </Form.Item>

                  {editMode && (
                    <Form.Item>
                      <Space>
                        <Button type="primary" htmlType="submit" loading={loading}>
                          保存修改
                        </Button>
                        <Button onClick={() => setEditMode(false)}>
                          取消
                        </Button>
                      </Space>
                    </Form.Item>
                  )}
                </Form>
              </TabPane>

              {/* 安全设置 */}
              <TabPane 
                tab={
                  <span>
                    <SecurityScanOutlined />
                    安全设置
                  </span>
                } 
                key="security"
              >
                <Title level={4}>安全设置</Title>
                
                <Card size="small" style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div><strong>登录密码</strong></div>
                      <Text type="secondary">定期更换密码可以提高账户安全性</Text>
                    </div>
                    <Button 
                      icon={<LockOutlined />}
                      onClick={() => setPasswordModalVisible(true)}
                    >
                      修改密码
                    </Button>
                  </div>
                </Card>

                <Card size="small" style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div><strong>手机绑定</strong></div>
                      <Text type="secondary">
                        {user?.phone ? `已绑定：${user.phone}` : '未绑定手机号'}
                      </Text>
                    </div>
                    <Button>
                      {user?.phone ? '更换手机' : '绑定手机'}
                    </Button>
                  </div>
                </Card>

                <Card size="small">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div><strong>邮箱验证</strong></div>
                      <Text type="secondary">
                        {user?.email_verified ? '邮箱已验证' : '邮箱未验证'}
                      </Text>
                    </div>
                    {!user?.email_verified && (
                      <Button type="primary">
                        验证邮箱
                      </Button>
                    )}
                  </div>
                </Card>
              </TabPane>

              {/* 通知设置 */}
              <TabPane 
                tab={
                  <span>
                    <BellOutlined />
                    通知设置
                  </span>
                } 
                key="notifications"
              >
                <Title level={4}>通知设置</Title>
                
                <Form
                  form={settingsForm}
                  layout="vertical"
                  onValuesChange={(_, allValues) => {
                    handleSettingsUpdate(allValues);
                  }}
                >
                  <Card size="small" style={{ marginBottom: 16 }}>
                    <Form.Item
                      name="email_notifications"
                      valuePropName="checked"
                      style={{ marginBottom: 8 }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div><strong>邮件通知</strong></div>
                          <Text type="secondary">接收重要活动和中奖通知邮件</Text>
                        </div>
                        <Switch />
                      </div>
                    </Form.Item>
                  </Card>

                  <Card size="small" style={{ marginBottom: 16 }}>
                    <Form.Item
                      name="sms_notifications"
                      valuePropName="checked"
                      style={{ marginBottom: 8 }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div><strong>短信通知</strong></div>
                          <Text type="secondary">接收中奖和账户变动短信</Text>
                        </div>
                        <Switch />
                      </div>
                    </Form.Item>
                  </Card>

                  <Card size="small" style={{ marginBottom: 16 }}>
                    <Form.Item
                      name="push_notifications"
                      valuePropName="checked"
                      style={{ marginBottom: 8 }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div><strong>推送通知</strong></div>
                          <Text type="secondary">接收浏览器推送通知</Text>
                        </div>
                        <Switch />
                      </div>
                    </Form.Item>
                  </Card>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="隐私级别"
                        name="privacy_level"
                      >
                        <Select>
                          <Option value="low">低</Option>
                          <Option value="normal">普通</Option>
                          <Option value="high">高</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="自动登出时间（分钟）"
                        name="auto_logout"
                      >
                        <Select>
                          <Option value={15}>15分钟</Option>
                          <Option value={30}>30分钟</Option>
                          <Option value={60}>1小时</Option>
                          <Option value={120}>2小时</Option>
                          <Option value={0}>永不登出</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>
                </Form>
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onCancel={() => {
          setPasswordModalVisible(false);
          passwordForm.resetFields();
        }}
        footer={null}
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handlePasswordChange}
        >
          <Form.Item
            label="当前密码"
            name="old_password"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password />
          </Form.Item>

          <Form.Item
            label="新密码"
            name="new_password"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6位' }
            ]}
          >
            <Input.Password />
          </Form.Item>

          <Form.Item
            label="确认新密码"
            name="confirm_password"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                确认修改
              </Button>
              <Button onClick={() => {
                setPasswordModalVisible(false);
                passwordForm.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AccountPage;