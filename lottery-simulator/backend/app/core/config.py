"""
系统配置文件
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "双色球模拟购买系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./lottery_simulator.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # 用户配置
    INITIAL_BALANCE: float = 5000000.0  # 初始虚拟资金500万
    MIN_BET_AMOUNT: float = 2.0  # 最小投注金额2元
    MAX_BET_AMOUNT: float = 20000.0  # 最大投注金额2万元
    
    # 双色球配置
    RED_BALL_RANGE: tuple = (1, 33)  # 红球范围1-33
    BLUE_BALL_RANGE: tuple = (1, 16)  # 蓝球范围1-16
    RED_BALL_COUNT: int = 6  # 红球数量
    BLUE_BALL_COUNT: int = 1  # 蓝球数量
    
    # 奖金配置
    PRIZE_LEVELS: dict = {
        "first": 5000000,    # 一等奖：6+1
        "second": 200000,    # 二等奖：6+0
        "third": 3000,       # 三等奖：5+1
        "fourth": 200,       # 四等奖：5+0或4+1
        "fifth": 10,         # 五等奖：4+0或3+1
        "sixth": 5           # 六等奖：2+1或1+1或0+1
    }
    
    # 数据分析配置
    MARKOV_ORDER: int = 2  # 马尔可夫链阶数
    ANALYSIS_CACHE_EXPIRE: int = 3600  # 分析结果缓存时间（秒）
    
    # Redis配置（可选）
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()


# 数据库配置
class DatabaseConfig:
    """数据库相关配置"""
    
    @staticmethod
    def get_database_url() -> str:
        """获取数据库连接URL"""
        return settings.DATABASE_URL
    
    @staticmethod
    def get_engine_kwargs() -> dict:
        """获取数据库引擎参数"""
        if "sqlite" in settings.DATABASE_URL:
            return {
                "connect_args": {"check_same_thread": False},
                "echo": settings.DEBUG
            }
        else:
            return {
                "echo": settings.DEBUG,
                "pool_size": 10,
                "max_overflow": 20
            }


# JWT配置
class JWTConfig:
    """JWT相关配置"""
    
    @staticmethod
    def get_secret_key() -> str:
        """获取JWT密钥"""
        return settings.SECRET_KEY
    
    @staticmethod
    def get_algorithm() -> str:
        """获取JWT算法"""
        return settings.ALGORITHM
    
    @staticmethod
    def get_access_token_expire_minutes() -> int:
        """获取访问令牌过期时间（分钟）"""
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @staticmethod
    def get_refresh_token_expire_days() -> int:
        """获取刷新令牌过期时间（天）"""
        return settings.REFRESH_TOKEN_EXPIRE_DAYS


# 业务配置
class BusinessConfig:
    """业务相关配置"""
    
    @staticmethod
    def get_initial_balance() -> float:
        """获取初始账户余额"""
        return settings.INITIAL_BALANCE
    
    @staticmethod
    def get_bet_amount_range() -> tuple:
        """获取投注金额范围"""
        return (settings.MIN_BET_AMOUNT, settings.MAX_BET_AMOUNT)
    
    @staticmethod
    def get_lottery_config() -> dict:
        """获取双色球配置"""
        return {
            "red_ball_range": settings.RED_BALL_RANGE,
            "blue_ball_range": settings.BLUE_BALL_RANGE,
            "red_ball_count": settings.RED_BALL_COUNT,
            "blue_ball_count": settings.BLUE_BALL_COUNT
        }
    
    @staticmethod
    def get_prize_levels() -> dict:
        """获取奖金等级配置"""
        return settings.PRIZE_LEVELS