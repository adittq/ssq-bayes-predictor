# 双色球模拟购买系统

一个完整的双色球模拟购买平台，支持用户登录、虚拟资金管理、智能推荐和数据分析。

## 功能特性

- 🔐 **用户认证**: 支持微信/支付宝登录模拟
- 💰 **虚拟资金**: 每个账户提供500万虚拟资金
- 🎯 **智能推荐**: 基于马尔可夫模型的购彩建议
- 📊 **数据分析**: 多种分析模型（频率、趋势、机器学习）
- 🎲 **模拟购买**: 完整的双色球购买流程
- 📈 **统计报表**: 详细的购买和中奖统计

## 技术栈

### 后端
- FastAPI + Python 3.9+
- SQLAlchemy + SQLite/PostgreSQL
- JWT认证
- NumPy, Pandas, Scikit-learn

### 前端
- React 18 + TypeScript
- Ant Design + Tailwind CSS
- Redux Toolkit
- Axios

## 项目结构

```
lottery-simulator/
├── backend/                 # 后端API服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试文件
│   └── alembic/            # 数据库迁移
├── frontend/               # 前端React应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API服务
│   │   ├── store/          # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── utils/          # 工具函数
│   └── public/             # 静态资源
├── data/                   # 数据文件
├── docs/                   # 文档
└── scripts/                # 脚本工具
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 数据初始化
```bash
# 复制双色球历史数据
cp ../ssq_data_*.csv data/lottery_history.csv

# 运行数据分析脚本
python scripts/analyze_data.py
```

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 主要功能模块

### 1. 用户认证
- 微信登录模拟
- 支付宝登录模拟
- JWT token管理

### 2. 购彩系统
- 双色球号码选择
- 投注金额设置
- 购买历史查询

### 3. 数据分析
- 马尔可夫链分析
- 号码频率统计
- 趋势预测分析

### 4. 推荐系统
- 基于历史数据的智能推荐
- 多模型综合分析
- 个性化推荐算法

## 开发指南

详细的开发文档请查看 `docs/` 目录。

## 许可证

MIT License