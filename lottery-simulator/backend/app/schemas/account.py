"""
账户相关的 Pydantic 模型
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, validator


class AccountBalance(BaseModel):
    """账户余额响应"""
    balance: float
    frozen_amount: float
    available_balance: float
    total_recharge: float
    total_consumption: float
    total_winnings: float
    
    class Config:
        from_attributes = True


class RechargeRequest(BaseModel):
    """充值请求"""
    amount: float
    payment_method: str = "wechat"
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('充值金额必须大于0')
        if v > 50000:
            raise ValueError('单次充值金额不能超过50000元')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ['wechat', 'alipay', 'bank_card']:
            raise ValueError('支付方式必须是 wechat, alipay 或 bank_card')
        return v


class WithdrawRequest(BaseModel):
    """提现请求"""
    amount: float
    withdraw_method: str = "bank_card"
    account_info: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('提现金额必须大于0')
        if v < 10:
            raise ValueError('最小提现金额为10元')
        return v
    
    @validator('withdraw_method')
    def validate_withdraw_method(cls, v):
        if v not in ['bank_card', 'alipay', 'wechat']:
            raise ValueError('提现方式必须是 bank_card, alipay 或 wechat')
        return v


class TransactionRecord(BaseModel):
    """交易记录"""
    id: int
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    status: str
    description: str
    payment_method: Optional[str] = None
    withdraw_method: Optional[str] = None
    external_transaction_id: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """交易记录列表响应"""
    transactions: List[TransactionRecord]
    total: int
    page: int
    size: int
    pages: int


class FreezeRequest(BaseModel):
    """冻结资金请求"""
    amount: float
    reason: Optional[str] = ""
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('冻结金额必须大于0')
        return v


class UnfreezeRequest(BaseModel):
    """解冻资金请求"""
    amount: float
    reason: Optional[str] = ""
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('解冻金额必须大于0')
        return v


class AccountStatistics(BaseModel):
    """账户统计"""
    period: str
    start_date: str
    end_date: str
    account_info: AccountBalance
    period_stats: dict
    daily_stats: List[dict]


class AccountLimits(BaseModel):
    """账户限额"""
    daily_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    daily_used: float
    monthly_used: float
    daily_remaining: Optional[float] = None
    monthly_remaining: Optional[float] = None


class SetLimitsRequest(BaseModel):
    """设置限额请求"""
    daily_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    
    @validator('daily_limit')
    def validate_daily_limit(cls, v):
        if v is not None and v <= 0:
            raise ValueError('日限额必须大于0')
        return v
    
    @validator('monthly_limit')
    def validate_monthly_limit(cls, v):
        if v is not None and v <= 0:
            raise ValueError('月限额必须大于0')
        return v


class BalanceHistory(BaseModel):
    """余额变动历史"""
    period_days: int
    start_date: str
    history: List[dict]
    count: int