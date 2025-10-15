"""
双色球彩票模拟器 - FastAPI 主应用
"""

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import DatabaseManager
from app.api import auth, lottery, account, analysis, backtest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    db_manager = DatabaseManager()
    db_manager.create_tables()
    
    yield
    
    # 关闭时清理资源
    pass


# 创建FastAPI应用实例
app = FastAPI(
    title="双色球彩票模拟器",
    description="一个基于FastAPI的双色球彩票购买和数据分析模拟器",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(lottery.router, prefix="/api/lottery", tags=["彩票"])
app.include_router(account.router, prefix="/api/account", tags=["账户"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["数据分析"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用双色球彩票模拟器",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 自定义 Swagger UI，使用 unpkg CDN 以规避 jsDelivr 阻断
@app.get("/docs", include_in_schema=False)
def overridden_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="双色球彩票模拟器 - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        oauth2_redirect_url="/docs/oauth2-redirect",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# 自定义 ReDoc，切换到 unpkg CDN
@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="双色球彩票模拟器 - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )