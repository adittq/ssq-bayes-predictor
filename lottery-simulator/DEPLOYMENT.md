# 部署指南 (Deployment Guide)

本文档详细说明如何在不同环境中部署彩票模拟器应用。

## 目录
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [云服务部署](#云服务部署)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)

## 开发环境部署

### 前置要求
- Python 3.8+
- Node.js 16+
- Git

### 步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd lottery-simulator
```

#### 2. 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置

# 初始化数据库
python init_db.py

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 验证部署
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 生产环境部署

### 系统要求
- Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- 4GB+ RAM
- 20GB+ 存储空间
- Python 3.8+
- Node.js 16+
- Nginx
- PostgreSQL (推荐) 或 SQLite

### 后端生产部署

#### 1. 系统准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

#### 2. 数据库设置
```bash
# 创建数据库用户和数据库
sudo -u postgres psql
CREATE USER lottery_user WITH PASSWORD 'your_password';
CREATE DATABASE lottery_db OWNER lottery_user;
GRANT ALL PRIVILEGES ON DATABASE lottery_db TO lottery_user;
\q
```

#### 3. 应用部署
```bash
# 创建应用目录
sudo mkdir -p /opt/lottery-simulator
sudo chown $USER:$USER /opt/lottery-simulator
cd /opt/lottery-simulator

# 克隆代码
git clone <repository-url> .

# 后端设置
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置生产环境配置
```

#### 4. 环境变量配置 (.env)
```bash
# 数据库配置
DATABASE_URL=postgresql://lottery_user:your_password@localhost/lottery_db

# JWT 配置
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### 5. 数据库迁移
```bash
# 初始化数据库
python init_db.py
```

#### 6. 创建系统服务
```bash
sudo tee /etc/systemd/system/lottery-backend.service > /dev/null <<EOF
[Unit]
Description=Lottery Simulator Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/lottery-simulator/backend
Environment=PATH=/opt/lottery-simulator/backend/venv/bin
ExecStart=/opt/lottery-simulator/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable lottery-backend
sudo systemctl start lottery-backend
```

### 前端生产部署

#### 1. 构建前端
```bash
cd /opt/lottery-simulator/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 2. Nginx 配置
```bash
sudo tee /etc/nginx/sites-available/lottery-simulator > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 前端静态文件
    location / {
        root /opt/lottery-simulator/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/lottery-simulator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 3. SSL 证书 (Let's Encrypt)
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Docker 部署

### 1. 创建 Dockerfile (后端)
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建 Dockerfile (前端)
```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: lottery_db
      POSTGRES_USER: lottery_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://lottery_user:your_password@db/lottery_db
      SECRET_KEY: your-super-secret-key
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 4. 运行 Docker 部署
```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 云服务部署

### AWS 部署

#### 1. EC2 实例设置
- 选择 Ubuntu 20.04 LTS
- 实例类型: t3.medium (生产环境推荐 t3.large+)
- 安全组: 开放 80, 443, 22 端口

#### 2. RDS 数据库
- 创建 PostgreSQL RDS 实例
- 配置安全组允许 EC2 访问

#### 3. S3 静态资源 (可选)
```bash
# 上传前端构建文件到 S3
aws s3 sync frontend/dist/ s3://your-bucket-name/
```

### 阿里云部署

#### 1. ECS 实例
- 选择 Ubuntu 20.04
- 配置安全组规则

#### 2. RDS 数据库
- 创建 PostgreSQL 实例
- 配置白名单

## 性能优化

### 后端优化
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 启用 Gzip 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 数据库连接池优化
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### 前端优化
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          router: ['react-router-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### Nginx 优化
```nginx
# 启用 Gzip
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

# 缓存配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 监控和日志

### 1. 应用监控
```python
# 添加健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### 2. 日志配置
```python
# app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 3. 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 设置日志轮转
sudo tee /etc/logrotate.d/lottery-simulator > /dev/null <<EOF
/opt/lottery-simulator/backend/app.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库状态
sudo systemctl status postgresql

# 检查连接
psql -h localhost -U lottery_user -d lottery_db
```

#### 2. 前端构建失败
```bash
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 3. 服务无法启动
```bash
# 检查服务状态
sudo systemctl status lottery-backend

# 查看日志
sudo journalctl -u lottery-backend -f
```

### 备份和恢复

#### 数据库备份
```bash
# 备份
pg_dump -h localhost -U lottery_user lottery_db > backup.sql

# 恢复
psql -h localhost -U lottery_user lottery_db < backup.sql
```

#### 应用备份
```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/lottery-simulator-$DATE.tar.gz /opt/lottery-simulator
```

## 安全建议

1. **定期更新系统和依赖**
2. **使用强密码和 SSH 密钥**
3. **配置防火墙规则**
4. **启用 SSL/TLS**
5. **定期备份数据**
6. **监控异常访问**

---

如有部署问题，请查看日志文件或联系技术支持。