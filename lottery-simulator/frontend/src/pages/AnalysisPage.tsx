import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Tabs, Table, Tag, Space, Typography, Statistic, Progress } from 'antd';
import { BarChartOutlined, LineChartOutlined, PieChartOutlined, TrophyOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { 
  getFrequencyAnalysis, 
  getHotColdAnalysis,
  getRecommendations 
} from '../store/slices/analysisSlice';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface FrequencyData {
  number: number;
  count: number;
  percentage: number;
  last_appearance: string;
}

interface HotColdData {
  number: number;
  type: 'hot' | 'cold';
  frequency: number;
  trend: 'up' | 'down' | 'stable';
}

const AnalysisPage: React.FC = () => {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('frequency');

  const { 
    frequencyAnalysis, 
    hotColdAnalysis, 
    recommendations, 
    loading 
  } = useSelector((state: RootState) => state.analysis as any);

  useEffect(() => {
    // 加载分析数据
    dispatch(getFrequencyAnalysis({}) as any);
    dispatch(getHotColdAnalysis({}) as any);
    dispatch(getRecommendations({}) as any);
  }, [dispatch]);

  const frequencyColumns: ColumnsType<FrequencyData> = [
    {
      title: '号码',
      dataIndex: 'number',
      key: 'number',
      width: 80,
      align: 'center',
      render: (number: number) => (
        <Tag color="blue" style={{ fontSize: '14px', fontWeight: 'bold' }}>
          {number.toString().padStart(2, '0')}
        </Tag>
      ),
    },
    {
      title: '出现次数',
      dataIndex: 'count',
      key: 'count',
      width: 100,
      align: 'center',
      sorter: (a: FrequencyData, b: FrequencyData) => a.count - b.count,
    },
    {
      title: '出现频率',
      dataIndex: 'percentage',
      key: 'percentage',
      width: 120,
      align: 'center',
      render: (percentage: number) => (
        <Progress 
          percent={percentage} 
          size="small" 
          format={(percent) => `${percent?.toFixed(1)}%`}
        />
      ),
    },
    {
      title: '最后出现',
      dataIndex: 'last_appearance',
      key: 'last_appearance',
      width: 120,
      align: 'center',
    },
  ];

  const hotColdColumns: ColumnsType<HotColdData> = [
    {
      title: '号码',
      dataIndex: 'number',
      key: 'number',
      width: 80,
      align: 'center',
      render: (number: number) => (
        <Tag color="blue" style={{ fontSize: '14px', fontWeight: 'bold' }}>
          {number.toString().padStart(2, '0')}
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      align: 'center',
      render: (type: string) => (
        <Tag color={type === 'hot' ? 'red' : 'cyan'}>
          {type === 'hot' ? '热号' : '冷号'}
        </Tag>
      ),
    },
    {
      title: '频率',
      dataIndex: 'frequency',
      key: 'frequency',
      width: 100,
      align: 'center',
    },
    {
      title: '趋势',
      dataIndex: 'trend',
      key: 'trend',
      width: 100,
      align: 'center',
      render: (trend: string) => {
        const trendMap = {
          up: { color: 'green', text: '上升' },
          down: { color: 'red', text: '下降' },
          stable: { color: 'blue', text: '稳定' },
        };
        const config = trendMap[trend as keyof typeof trendMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
  ];

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <BarChartOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          数据分析
        </Title>
        <Text type="secondary">
          基于历史开奖数据的统计分析，帮助您了解号码规律
        </Text>
      </div>

      {/* 推荐号码 */}
      {recommendations && (
        <Card 
          title={
            <span>
              <TrophyOutlined style={{ marginRight: 8, color: '#faad14' }} />
              智能推荐
            </span>
          }
          style={{ marginBottom: 24 }}
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card size="small" title="推荐红球">
                <Space wrap>
                  {recommendations.red_balls?.map((num: number, index: number) => (
                    <Tag 
                      key={index} 
                      color="red" 
                      style={{ fontSize: '16px', padding: '4px 8px' }}
                    >
                      {num.toString().padStart(2, '0')}
                    </Tag>
                  ))}
                </Space>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card size="small" title="推荐蓝球">
                <Tag 
                  color="blue" 
                  style={{ fontSize: '16px', padding: '4px 8px' }}
                >
                  {recommendations.blue_ball?.toString().padStart(2, '0')}
                </Tag>
              </Card>
            </Col>
          </Row>
          <div style={{ marginTop: 16, color: '#666', fontSize: '12px' }}>
            * 推荐号码基于历史数据分析生成，仅供参考，不保证中奖
          </div>
        </Card>
      )}

      {/* 分析数据 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane 
            tab={
              <span>
                <BarChartOutlined />
                频率分析
              </span>
            } 
            key="frequency"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card size="small" title="红球频率分析" loading={loading}>
                  <Table
                    columns={frequencyColumns}
                    dataSource={frequencyAnalysis?.red_balls || []}
                    rowKey="number"
                    size="small"
                    pagination={{ pageSize: 10 }}
                    scroll={{ y: 400 }}
                  />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card size="small" title="蓝球频率分析" loading={loading}>
                  <Table
                    columns={frequencyColumns}
                    dataSource={frequencyAnalysis?.blue_balls || []}
                    rowKey="number"
                    size="small"
                    pagination={{ pageSize: 10 }}
                    scroll={{ y: 400 }}
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <LineChartOutlined />
                热冷分析
              </span>
            } 
            key="hotcold"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card size="small" title="红球热冷分析" loading={loading}>
                  <Table
                    columns={hotColdColumns}
                    dataSource={hotColdAnalysis?.red_balls || []}
                    rowKey="number"
                    size="small"
                    pagination={{ pageSize: 10 }}
                    scroll={{ y: 400 }}
                  />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card size="small" title="蓝球热冷分析" loading={loading}>
                  <Table
                    columns={hotColdColumns}
                    dataSource={hotColdAnalysis?.blue_balls || []}
                    rowKey="number"
                    size="small"
                    pagination={{ pageSize: 10 }}
                    scroll={{ y: 400 }}
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <PieChartOutlined />
                统计概览
              </span>
            } 
            key="overview"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={6}>
                <Card>
                  <Statistic
                    title="分析期数"
                    value={frequencyAnalysis?.total_periods || 0}
                    suffix="期"
                  />
                </Card>
              </Col>
              <Col xs={24} sm={6}>
                <Card>
                  <Statistic
                    title="最热红球"
                    value={hotColdAnalysis?.hottest_red || '-'}
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={6}>
                <Card>
                  <Statistic
                    title="最冷红球"
                    value={hotColdAnalysis?.coldest_red || '-'}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={6}>
                <Card>
                  <Statistic
                    title="最热蓝球"
                    value={hotColdAnalysis?.hottest_blue || '-'}
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Card>
              </Col>
            </Row>

            <Card style={{ marginTop: 16 }} title="分析说明">
              <Space direction="vertical">
                <Text>• <strong>频率分析</strong>：统计各号码在历史开奖中的出现次数和频率</Text>
                <Text>• <strong>热冷分析</strong>：根据近期出现频率判断号码的热冷状态</Text>
                <Text>• <strong>智能推荐</strong>：综合多种分析算法生成的推荐号码</Text>
                <Text type="secondary">* 所有分析结果仅供参考，彩票开奖具有随机性</Text>
              </Space>
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default AnalysisPage;