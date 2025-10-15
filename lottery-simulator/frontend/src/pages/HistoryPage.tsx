import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Button, DatePicker, Select, Statistic, Row, Col, Typography } from 'antd';
import { HistoryOutlined, TrophyOutlined, DollarOutlined, CalendarOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { getPurchaseHistory, getPurchaseStatistics } from '../store/slices/lotterySlice';
import { formatCurrency, formatDate } from '../utils/format';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface PurchaseRecord {
  id: string;
  period: string;
  numbers: string;
  multiple: number;
  amount: number;
  status: 'pending' | 'winning' | 'not_winning';
  prize_amount?: number;
  purchase_time: string;
}

const HistoryPage: React.FC = () => {
  const dispatch = useDispatch();
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { purchaseHistory, purchaseStats, loading } = useSelector((state: RootState) => state.lottery as any);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(getPurchaseHistory({}) as any);
      dispatch(getPurchaseStatistics() as any);
    }
  }, [dispatch, isAuthenticated]);

  const columns: ColumnsType<PurchaseRecord> = [
    {
      title: '期号',
      dataIndex: 'period',
      key: 'period',
      width: 120,
    },
    {
      title: '选号',
      dataIndex: 'numbers',
      key: 'numbers',
      width: 200,
      render: (numbers: string) => (
        <span style={{ fontFamily: 'monospace', fontSize: '14px' }}>
          {numbers}
        </span>
      ),
    },
    {
      title: '倍数',
      dataIndex: 'multiple',
      key: 'multiple',
      width: 80,
      align: 'center',
    },
    {
      title: '投注金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      render: (amount: number) => formatCurrency(amount),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap = {
          pending: { color: 'processing', text: '待开奖' },
          winning: { color: 'success', text: '中奖' },
          not_winning: { color: 'default', text: '未中奖' },
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '中奖金额',
      dataIndex: 'prize_amount',
      key: 'prize_amount',
      width: 120,
      render: (amount: number) => amount ? formatCurrency(amount) : '-',
    },
    {
      title: '购买时间',
      dataIndex: 'purchase_time',
      key: 'purchase_time',
      width: 160,
      render: (time: string) => formatDate(time, 'YYYY-MM-DD HH:mm'),
    },
  ];

  const handleDateRangeChange = (dates: any) => {
    setDateRange(dates);
    // 这里可以添加根据日期范围筛选的逻辑
  };

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    // 这里可以添加根据状态筛选的逻辑
  };

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录查看购买记录</Title>
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
          <HistoryOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          购买记录
        </Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总投注次数"
              value={purchaseStats?.total_purchases || 0}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总投注金额"
              value={purchaseStats?.total_amount || 0}
              prefix={<DollarOutlined />}
              formatter={(value) => formatCurrency(Number(value))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="中奖次数"
              value={purchaseStats?.winning_count || 0}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="中奖金额"
              value={purchaseStats?.total_prize || 0}
              prefix={<TrophyOutlined />}
              formatter={(value) => formatCurrency(Number(value))}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选条件 */}
      <Card style={{ marginBottom: 24 }}>
        <Space>
          <span>时间范围：</span>
          <RangePicker
            value={dateRange}
            onChange={handleDateRangeChange}
            placeholder={['开始日期', '结束日期']}
          />
          <span>状态：</span>
          <Select
            value={statusFilter}
            onChange={handleStatusFilterChange}
            style={{ width: 120 }}
          >
            <Option value="all">全部</Option>
            <Option value="pending">待开奖</Option>
            <Option value="winning">中奖</Option>
            <Option value="not_winning">未中奖</Option>
          </Select>
          <Button type="primary">查询</Button>
          <Button>重置</Button>
        </Space>
      </Card>

      {/* 购买记录表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={purchaseHistory || []}
          loading={loading}
          rowKey="id"
          pagination={{
            total: purchaseHistory?.length || 0,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default HistoryPage;