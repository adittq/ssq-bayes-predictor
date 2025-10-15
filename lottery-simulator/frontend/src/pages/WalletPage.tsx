import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Button, Modal, Form, Input, Table, Tag, Space, Typography, Divider } from 'antd';
import { WalletOutlined, PlusOutlined, MinusOutlined, HistoryOutlined, DollarOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { getAccountBalance, recharge, withdraw, getTransactionHistory } from '../store/slices/accountSlice';
import { formatCurrency, formatDate } from '../utils/format';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;

interface Transaction {
  id: string;
  type: 'recharge' | 'withdraw' | 'purchase' | 'prize';
  amount: number;
  balance_after: number;
  description: string;
  created_at: string;
  status: 'pending' | 'completed' | 'failed';
}

const WalletPage: React.FC = () => {
  const dispatch = useDispatch();
  const [rechargeModalVisible, setRechargeModalVisible] = useState(false);
  const [withdrawModalVisible, setWithdrawModalVisible] = useState(false);
  const [rechargeForm] = Form.useForm();
  const [withdrawForm] = Form.useForm();

  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { balance, transactions, loading } = useSelector((state: RootState) => state.account as any);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(getAccountBalance() as any);
      dispatch(getTransactionHistory({}) as any);
    }
  }, [dispatch, isAuthenticated]);

  const handleRecharge = async (values: { amount: number }) => {
    try {
      await dispatch(recharge({ ...values, payment_method: 'alipay' }) as any);
      setRechargeModalVisible(false);
      rechargeForm.resetFields();
      dispatch(getAccountBalance() as any);
      dispatch(getTransactionHistory({}) as any);
    } catch (error) {
      console.error('充值失败:', error);
    }
  };

  const handleWithdraw = async (values: { amount: number }) => {
    try {
      await dispatch(withdraw({ ...values, payment_method: 'bank_card' }) as any);
      setWithdrawModalVisible(false);
      withdrawForm.resetFields();
      dispatch(getAccountBalance() as any);
      dispatch(getTransactionHistory({}) as any);
    } catch (error) {
      console.error('提现失败:', error);
    }
  };

  const transactionColumns: ColumnsType<Transaction> = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const typeMap = {
          recharge: { color: 'green', text: '充值' },
          withdraw: { color: 'orange', text: '提现' },
          purchase: { color: 'blue', text: '购买' },
          prize: { color: 'gold', text: '中奖' },
        };
        const config = typeMap[type as keyof typeof typeMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (amount: number, record: Transaction) => {
        const isIncome = record.type === 'recharge' || record.type === 'prize';
        return (
          <span style={{ color: isIncome ? '#52c41a' : '#ff4d4f' }}>
            {isIncome ? '+' : '-'}{formatCurrency(Math.abs(amount))}
          </span>
        );
      },
    },
    {
      title: '余额',
      dataIndex: 'balance_after',
      key: 'balance_after',
      width: 120,
      render: (balance: number) => formatCurrency(balance),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap = {
          pending: { color: 'processing', text: '处理中' },
          completed: { color: 'success', text: '已完成' },
          failed: { color: 'error', text: '失败' },
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time: string) => formatDate(time, 'YYYY-MM-DD HH:mm'),
    },
  ];

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录查看钱包信息</Title>
        <Button type="primary" href="/login">
          去登录
        </Button>
      </div>
    );
  }

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <WalletOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          我的钱包
        </Title>
      </div>

      {/* 余额信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="可用余额"
              value={balance?.available_balance || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="冻结余额"
              value={balance?.frozen_balance || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总余额"
              value={(balance?.available_balance || 0) + (balance?.frozen_balance || 0)}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => setRechargeModalVisible(true)}
          >
            充值
          </Button>
          <Button
            icon={<MinusOutlined />}
            size="large"
            onClick={() => setWithdrawModalVisible(true)}
            disabled={(balance?.available_balance || 0) <= 0}
          >
            提现
          </Button>
        </Space>
        <Divider />
        <div style={{ color: '#666', fontSize: '14px' }}>
          <p>• 充值金额将立即到账</p>
          <p>• 提现申请将在1-3个工作日内处理</p>
          <p>• 最低充值金额：10元，最低提现金额：50元</p>
        </div>
      </Card>

      {/* 交易记录 */}
      <Card
        title={
          <span>
            <HistoryOutlined style={{ marginRight: 8 }} />
            交易记录
          </span>
        }
      >
        <Table
          columns={transactionColumns}
          dataSource={transactions || []}
          loading={loading}
          rowKey="id"
          pagination={{
            total: transactions?.length || 0,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 充值弹窗 */}
      <Modal
        title="账户充值"
        open={rechargeModalVisible}
        onCancel={() => setRechargeModalVisible(false)}
        footer={null}
      >
        <Form
          form={rechargeForm}
          layout="vertical"
          onFinish={handleRecharge}
        >
          <Form.Item
            label="充值金额"
            name="amount"
            rules={[
              { required: true, message: '请输入充值金额' },
              { type: 'number', min: 10, message: '最低充值金额为10元' },
              { type: 'number', max: 10000, message: '单次最高充值金额为10000元' },
            ]}
          >
            <Input
              type="number"
              placeholder="请输入充值金额"
              suffix="元"
              min={10}
              max={10000}
            />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                确认充值
              </Button>
              <Button onClick={() => setRechargeModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 提现弹窗 */}
      <Modal
        title="账户提现"
        open={withdrawModalVisible}
        onCancel={() => setWithdrawModalVisible(false)}
        footer={null}
      >
        <Form
          form={withdrawForm}
          layout="vertical"
          onFinish={handleWithdraw}
        >
          <Form.Item
            label="提现金额"
            name="amount"
            rules={[
              { required: true, message: '请输入提现金额' },
              { type: 'number', min: 50, message: '最低提现金额为50元' },
              { 
                type: 'number', 
                max: balance?.available_balance || 0, 
                message: '提现金额不能超过可用余额' 
              },
            ]}
          >
            <Input
              type="number"
              placeholder="请输入提现金额"
              suffix="元"
              min={50}
              max={balance?.available_balance || 0}
            />
          </Form.Item>
          <div style={{ marginBottom: 16, color: '#666' }}>
            可用余额：{formatCurrency(balance?.available_balance || 0)}
          </div>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                确认提现
              </Button>
              <Button onClick={() => setWithdrawModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WalletPage;