# 双色球模拟购买系统 - 项目架构

## 系统概述
一个完整的双色球模拟购买平台，支持用户注册登录、虚拟资金管理、智能推荐和数据分析。

## 技术栈

### 后端 (FastAPI)
- **框架**: FastAPI + Uvicorn
- **数据库**: SQLAlchemy + SQLite/PostgreSQL
- **认证**: JWT + OAuth2
- **数据分析**: NumPy, Pandas, Scikit-learn
- **任务队列**: Celery (可选)

### 前端 (React)
- **框架**: React 18 + TypeScript
- **状态管理**: Redux Toolkit
- **路由**: React Router
- **UI组件**: Ant Design
- **样式**: Tailwind CSS
- **HTTP客户端**: Axios

### 数据分析模块
- **马尔可夫模型**: 基于历史数据的状态转移分析
- **频率分析**: 号码出现频率统计
- **趋势分析**: 时间序列分析
- **机器学习**: 随机森林、神经网络等

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (React)   │────│  后端 (FastAPI)  │────│   数据库 (SQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │  数据分析模块    │
                       │  - 马尔可夫模型  │
                       │  - 频率分析     │
                       │  - 趋势分析     │
                       └─────────────────┘
```

## 核心功能模块

### 1. 用户认证模块
- 微信登录模拟
- 支付宝登录模拟
- JWT token管理
- 用户权限控制

### 2. 资金管理模块
- 虚拟账户系统
- 初始资金500万
- 交易记录追踪
- 余额实时更新

### 3. 购彩模块
- 双色球号码选择
- 投注金额设置
- 购买历史记录
- 中奖结果模拟

### 4. 数据分析模块
- 马尔可夫链分析
- 号码频率统计
- 冷热号分析
- 趋势预测

### 5. 推荐系统
- 基于历史数据的智能推荐
- 多种分析模型结合
- 个性化推荐算法
- 推荐结果评估

## 数据库设计

### 主要表结构
- `users` - 用户信息
- `accounts` - 账户资金
- `lottery_purchases` - 购彩记录
- `lottery_results` - 开奖结果
- `recommendations` - 推荐记录
- `analysis_cache` - 分析结果缓存

## API设计

### 认证相关
- POST /auth/login - 用户登录
- POST /auth/logout - 用户登出
- GET /auth/profile - 获取用户信息

### 购彩相关
- POST /lottery/purchase - 购买彩票
- GET /lottery/history - 购买历史
- GET /lottery/results - 开奖结果

### 分析相关
- GET /analysis/markov - 马尔可夫分析
- GET /analysis/frequency - 频率分析
- GET /analysis/trends - 趋势分析
- GET /recommendations - 获取推荐

### 账户相关
- GET /account/balance - 账户余额
- GET /account/transactions - 交易记录

## 部署架构

### 开发环境
- 前端: npm run dev (Vite)
- 后端: uvicorn main:app --reload
- 数据库: SQLite

### 生产环境
- 前端: Nginx + 静态文件
- 后端: Gunicorn + Uvicorn workers
- 数据库: PostgreSQL
- 缓存: Redis
- 负载均衡: Nginx

## 安全考虑

1. **认证安全**: JWT token + 刷新机制
2. **数据验证**: Pydantic模型验证
3. **SQL注入防护**: SQLAlchemy ORM
4. **CORS配置**: 跨域请求控制
5. **速率限制**: API调用频率限制

## 性能优化

1. **数据库优化**: 索引设计、查询优化
2. **缓存策略**: Redis缓存热点数据
3. **异步处理**: FastAPI异步特性
4. **前端优化**: 代码分割、懒加载
5. **CDN加速**: 静态资源分发