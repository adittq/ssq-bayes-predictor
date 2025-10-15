# API 文档 (API Documentation)

彩票模拟器 REST API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **认证方式**: JWT Bearer Token
- **Content-Type**: `application/json`

## 认证

### 获取访问令牌

所有需要认证的接口都需要在请求头中包含 JWT token：

```http
Authorization: Bearer <your-jwt-token>
```

## 接口列表

### 1. 认证相关 (Authentication)

#### 1.1 用户注册
```http
POST /auth/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "balance": 5000000.0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 1.2 用户登录
```http
POST /auth/login
```

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "balance": 5000000.0
  }
}
```

#### 1.3 获取当前用户信息
```http
GET /auth/me
```

**请求头**:
```http
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "balance": 4999998.0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. 彩票相关 (Lottery)

#### 2.1 购买彩票
```http
POST /lottery/purchase
```

**请求头**:
```http
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "red_balls": [1, 5, 12, 18, 25, 32],
  "blue_ball": 8,
  "amount": 2.0
}
```

**响应**:
```json
{
  "id": 1,
  "user_id": 1,
  "red_balls": [1, 5, 12, 18, 25, 32],
  "blue_ball": 8,
  "amount": 2.0,
  "purchase_time": "2024-01-01T10:00:00Z",
  "status": "pending"
}
```

#### 2.2 获取彩票购买历史
```http
GET /lottery/history
```

**请求头**:
```http
Authorization: Bearer <token>
```

**查询参数**:
- `page` (int, optional): 页码，默认 1
- `size` (int, optional): 每页数量，默认 20
- `status` (string, optional): 状态筛选 (pending, won, lost)

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "red_balls": [1, 5, 12, 18, 25, 32],
      "blue_ball": 8,
      "amount": 2.0,
      "purchase_time": "2024-01-01T10:00:00Z",
      "status": "pending",
      "prize_amount": null
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### 2.3 获取开奖结果
```http
GET /lottery/results
```

**查询参数**:
- `page` (int, optional): 页码，默认 1
- `size` (int, optional): 每页数量，默认 20

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "period": "2024001",
      "red_balls": [3, 8, 15, 22, 28, 33],
      "blue_ball": 12,
      "draw_time": "2024-01-01T21:00:00Z",
      "total_sales": 1500000000.0,
      "prize_pool": 800000000.0
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### 2.4 生成随机号码
```http
GET /lottery/random
```

**响应**:
```json
{
  "red_balls": [7, 14, 19, 26, 30, 33],
  "blue_ball": 5
}
```

### 3. 账户相关 (Account)

#### 3.1 获取账户余额
```http
GET /account/balance
```

**请求头**:
```http
Authorization: Bearer <token>
```

**响应**:
```json
{
  "balance": 4999998.0,
  "currency": "CNY"
}
```

#### 3.2 账户充值
```http
POST /account/recharge
```

**请求头**:
```http
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "amount": 1000.0,
  "payment_method": "alipay"
}
```

**响应**:
```json
{
  "transaction_id": "tx_123456789",
  "amount": 1000.0,
  "new_balance": 5000998.0,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 3.3 获取交易历史
```http
GET /account/transactions
```

**请求头**:
```http
Authorization: Bearer <token>
```

**查询参数**:
- `page` (int, optional): 页码，默认 1
- `size` (int, optional): 每页数量，默认 20
- `type` (string, optional): 交易类型 (recharge, purchase, prize)

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "type": "purchase",
      "amount": -2.0,
      "balance_after": 4999998.0,
      "description": "购买彩票",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### 4. 数据分析 (Analysis)

#### 4.1 获取统计数据
```http
GET /analysis/stats
```

**请求头**:
```http
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_purchases": 10,
  "total_spent": 20.0,
  "total_won": 0.0,
  "win_rate": 0.0,
  "favorite_numbers": {
    "red": [1, 5, 12, 18, 25, 32],
    "blue": [8, 12, 16]
  },
  "monthly_stats": [
    {
      "month": "2024-01",
      "purchases": 10,
      "spent": 20.0,
      "won": 0.0
    }
  ]
}
```

#### 4.2 获取号码频率分析
```http
GET /analysis/frequency
```

**查询参数**:
- `periods` (int, optional): 分析期数，默认 100

**响应**:
```json
{
  "red_balls": {
    "1": 15,
    "2": 12,
    "3": 18,
    // ... 其他号码
  },
  "blue_balls": {
    "1": 8,
    "2": 6,
    "3": 10,
    // ... 其他号码
  },
  "analysis_periods": 100,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### 4.3 获取趋势分析
```http
GET /analysis/trends
```

**查询参数**:
- `periods` (int, optional): 分析期数，默认 50

**响应**:
```json
{
  "hot_numbers": {
    "red": [1, 5, 12, 18, 25, 32],
    "blue": [8, 12, 16]
  },
  "cold_numbers": {
    "red": [2, 9, 17, 24, 29, 33],
    "blue": [3, 7, 11]
  },
  "trend_data": [
    {
      "period": "2024001",
      "red_sum": 131,
      "blue_value": 12,
      "odd_count": 3,
      "even_count": 3
    }
  ]
}
```

#### 4.4 获取智能推荐
```http
GET /analysis/recommendations
```

**请求头**:
```http
Authorization: Bearer <token>
```

**查询参数**:
- `count` (int, optional): 推荐组数，默认 5

**响应**:
```json
{
  "recommendations": [
    {
      "red_balls": [3, 8, 15, 22, 28, 33],
      "blue_ball": 12,
      "confidence": 0.75,
      "reason": "基于马尔可夫链分析"
    },
    {
      "red_balls": [1, 7, 14, 19, 26, 30],
      "blue_ball": 5,
      "confidence": 0.68,
      "reason": "基于频率分析"
    }
  ],
  "generated_at": "2024-01-01T15:00:00Z"
}
```

### 5. 系统相关 (System)

#### 5.1 健康检查
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

#### 5.2 获取系统信息
```http
GET /info
```

**响应**:
```json
{
  "name": "Lottery Simulator API",
  "version": "1.0.0",
  "description": "彩票模拟器后端API",
  "docs_url": "/docs",
  "redoc_url": "/redoc"
}
```

## 错误处理

### 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 常见错误码

| HTTP 状态码 | 错误码 | 描述 |
|------------|--------|------|
| 400 | INVALID_REQUEST | 请求参数无效 |
| 401 | UNAUTHORIZED | 未授权访问 |
| 403 | FORBIDDEN | 禁止访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

### 具体错误示例

#### 认证失败
```json
{
  "detail": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 余额不足
```json
{
  "detail": "Insufficient balance",
  "error_code": "INSUFFICIENT_BALANCE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 参数验证失败
```json
{
  "detail": [
    {
      "loc": ["body", "red_balls"],
      "msg": "Red balls must contain exactly 6 unique numbers",
      "type": "value_error"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 限流规则

为了保护系统稳定性，API 实施了以下限流规则：

- **认证接口**: 每分钟最多 10 次请求
- **购买接口**: 每分钟最多 30 次请求
- **查询接口**: 每分钟最多 100 次请求
- **分析接口**: 每分钟最多 20 次请求

超出限制时返回 429 状态码：

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## SDK 示例

### JavaScript/TypeScript

```typescript
class LotteryAPI {
  private baseURL = 'http://localhost:8000';
  private token: string | null = null;

  async login(username: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async purchaseLottery(redBalls: number[], blueBall: number, amount: number) {
    const response = await fetch(`${this.baseURL}/lottery/purchase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        red_balls: redBalls,
        blue_ball: blueBall,
        amount
      })
    });
    
    return response.json();
  }
}
```

### Python

```python
import requests

class LotteryAPI:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.token = None
    
    def login(self, username: str, password: str):
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'username': username, 'password': password}
        )
        data = response.json()
        self.token = data['access_token']
        return data
    
    def purchase_lottery(self, red_balls: list, blue_ball: int, amount: float):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f'{self.base_url}/lottery/purchase',
            json={
                'red_balls': red_balls,
                'blue_ball': blue_ball,
                'amount': amount
            },
            headers=headers
        )
        return response.json()
```

## 测试

### 使用 curl 测试

```bash
# 用户注册
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# 用户登录
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# 购买彩票 (需要替换 TOKEN)
curl -X POST "http://localhost:8000/lottery/purchase" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"red_balls": [1, 5, 12, 18, 25, 32], "blue_ball": 8, "amount": 2.0}'
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基础认证功能
- 实现彩票购买和查询功能
- 实现账户管理功能
- 实现数据分析功能

---

更多详细信息请访问 [Swagger UI](http://localhost:8000/docs) 或 [ReDoc](http://localhost:8000/redoc)。