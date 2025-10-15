"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import DatabaseConfig

# 创建数据库引擎
engine = create_engine(
    DatabaseConfig.get_database_url(),
    **DatabaseConfig.get_engine_kwargs()
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """数据库管理器"""
    
    @staticmethod
    def create_tables():
        """创建所有表"""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """删除所有表"""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def get_session() -> Session:
        """获取数据库会话"""
        return SessionLocal()
    
    @staticmethod
    def close_session(session: Session):
        """关闭数据库会话"""
        session.close()