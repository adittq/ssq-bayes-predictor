"""
用户相关数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=True, comment="密码哈希")
    nickname = Column(String(50), nullable=False, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    login_type = Column(String(20), nullable=False, default="wechat", comment="登录类型: wechat, alipay, phone")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 扩展信息
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    id_card = Column(String(20), nullable=True, comment="身份证号")
    
    # 第三方登录信息
    wechat_openid = Column(String(100), nullable=True, comment="微信OpenID")
    alipay_user_id = Column(String(100), nullable=True, comment="支付宝用户ID")
    
    # 用户偏好设置
    preferences = Column(Text, nullable=True, comment="用户偏好设置(JSON)")
    
    # 关联关系
    account = relationship("Account", back_populates="user", uselist=False)
    purchases = relationship("Purchase", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    user_analyses = relationship("UserAnalysis", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "login_type": self.login_type,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "phone": self.phone,
            "email": self.email
        }
    
    @property
    def is_authenticated(self):
        """是否已认证"""
        return True
    
    @property
    def is_anonymous(self):
        """是否匿名用户"""
        return False