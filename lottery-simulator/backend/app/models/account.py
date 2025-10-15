"""
账户相关数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class TransactionType(enum.Enum):
    """交易类型枚举"""
    RECHARGE = "recharge"      # 充值
    WITHDRAW = "withdraw"      # 提现
    PURCHASE = "purchase"      # 购买彩票
    WINNING = "winning"        # 中奖奖金
    REFUND = "refund"         # 退款
    FREEZE = "freeze"         # 冻结
    UNFREEZE = "unfreeze"     # 解冻


class TransactionStatus(enum.Enum):
    """交易状态枚举"""
    PENDING = "pending"        # 待处理
    SUCCESS = "success"        # 成功
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"    # 已取消
    PROCESSING = "processing"  # 处理中


class Account(Base):
    """用户账户模型"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    
    # 余额相关
    balance = Column(Numeric(10, 2), default=0.00, nullable=False, comment="账户余额")
    frozen_amount = Column(Numeric(10, 2), default=0.00, nullable=False, comment="冻结金额")
    
    # 统计字段
    total_recharge = Column(Numeric(10, 2), default=0.00, nullable=False, comment="总充值金额")
    total_consumption = Column(Numeric(10, 2), default=0.00, nullable=False, comment="总消费金额")
    total_winnings = Column(Numeric(10, 2), default=0.00, nullable=False, comment="总中奖金额")
    
    # 限额设置
    daily_limit = Column(Numeric(10, 2), default=10000.00, nullable=True, comment="日限额")
    monthly_limit = Column(Numeric(10, 2), default=100000.00, nullable=True, comment="月限额")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": float(self.balance),
            "frozen_amount": float(self.frozen_amount),
            "available_balance": float(self.balance - self.frozen_amount),
            "total_recharge": float(self.total_recharge),
            "total_consumption": float(self.total_consumption),
            "total_winnings": float(self.total_winnings),
            "daily_limit": float(self.daily_limit) if self.daily_limit else None,
            "monthly_limit": float(self.monthly_limit) if self.monthly_limit else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def available_balance(self):
        """可用余额"""
        return self.balance - self.frozen_amount


class Transaction(Base):
    """交易记录模型"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, comment="账户ID")
    
    # 交易信息
    transaction_type = Column(Enum(TransactionType), nullable=False, comment="交易类型")
    amount = Column(Numeric(10, 2), nullable=False, comment="交易金额")
    balance_before = Column(Numeric(10, 2), nullable=False, comment="交易前余额")
    balance_after = Column(Numeric(10, 2), nullable=False, comment="交易后余额")
    
    # 状态和描述
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, comment="交易状态")
    description = Column(String(255), nullable=True, comment="交易描述")
    remark = Column(Text, nullable=True, comment="备注")
    
    # 第三方信息
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    withdraw_method = Column(String(50), nullable=True, comment="提现方式")
    account_info = Column(String(255), nullable=True, comment="账户信息")
    external_transaction_id = Column(String(100), nullable=True, comment="外部交易ID")
    
    # 关联信息
    related_purchase_id = Column(Integer, nullable=True, comment="关联的购买记录ID")
    related_winning_id = Column(Integer, nullable=True, comment="关联的中奖记录ID")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关联关系
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type.value}, amount={self.amount})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type.value,
            "amount": float(self.amount),
            "balance_before": float(self.balance_before),
            "balance_after": float(self.balance_after),
            "status": self.status.value,
            "description": self.description,
            "remark": self.remark,
            "payment_method": self.payment_method,
            "withdraw_method": self.withdraw_method,
            "account_info": self.account_info,
            "external_transaction_id": self.external_transaction_id,
            "related_purchase_id": self.related_purchase_id,
            "related_winning_id": self.related_winning_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }