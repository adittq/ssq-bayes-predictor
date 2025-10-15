"""
账户管理服务
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status

from app.models.account import Account, Transaction, TransactionType, TransactionStatus
from app.models.user import User


class AccountService:
    """账户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_account(self, user_id: int) -> Account:
        """获取用户账户"""
        account = self.db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户账户不存在"
            )
        return account
    
    def create_transaction(
        self,
        user_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str = "",
        **kwargs
    ) -> Transaction:
        """创建交易记录"""
        account = self.get_user_account(user_id)
        
        # 记录交易前余额
        balance_before = account.balance
        
        # 计算交易后余额
        if transaction_type in [TransactionType.RECHARGE, TransactionType.WINNING, TransactionType.REFUND]:
            balance_after = balance_before + amount
        elif transaction_type in [TransactionType.WITHDRAW, TransactionType.PURCHASE]:
            balance_after = balance_before - amount
        else:
            balance_after = balance_before
        
        # 创建交易记录
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            status=TransactionStatus.SUCCESS,
            created_at=datetime.utcnow(),
            **kwargs
        )
        
        self.db.add(transaction)
        return transaction
    
    def recharge(
        self,
        user_id: int,
        amount: Decimal,
        payment_method: str = "wechat"
    ) -> Transaction:
        """账户充值"""
        account = self.get_user_account(user_id)
        
        # 创建充值交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.RECHARGE,
            amount=amount,
            description=f"账户充值 - {payment_method}",
            payment_method=payment_method,
            external_transaction_id=f"recharge_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}"
        )
        
        # 更新账户余额
        account.balance += amount
        account.total_recharge += amount
        account.updated_at = datetime.utcnow()
        
        # 更新交易状态
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def withdraw(
        self,
        user_id: int,
        amount: Decimal,
        withdraw_method: str = "bank_card",
        account_info: str = ""
    ) -> Transaction:
        """账户提现"""
        account = self.get_user_account(user_id)
        
        # 检查可用余额
        available_balance = account.balance - account.frozen_amount
        if amount > available_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提现金额超过可用余额"
            )
        
        # 创建提现交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            description=f"账户提现 - {withdraw_method}",
            withdraw_method=withdraw_method,
            account_info=account_info,
            external_transaction_id=f"withdraw_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}"
        )
        
        # 更新账户余额
        account.balance -= amount
        account.updated_at = datetime.utcnow()
        
        # 提现通常需要审核，这里模拟为立即成功
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def deduct_balance(self, user_id: int, amount: Decimal, description: str = "购买彩票") -> Transaction:
        """扣除余额（用于购买彩票）"""
        account = self.get_user_account(user_id)
        
        # 检查余额
        if account.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户余额不足"
            )
        
        # 创建消费交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.PURCHASE,
            amount=amount,
            description=description
        )
        
        # 更新账户余额
        account.balance -= amount
        account.total_consumption += amount
        account.updated_at = datetime.utcnow()
        
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def add_winnings(self, user_id: int, amount: Decimal, description: str = "中奖奖金") -> Transaction:
        """添加中奖奖金"""
        account = self.get_user_account(user_id)
        
        # 创建中奖交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.WINNING,
            amount=amount,
            description=description
        )
        
        # 更新账户余额
        account.balance += amount
        account.total_winnings += amount
        account.updated_at = datetime.utcnow()
        
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def freeze_amount(self, user_id: int, amount: Decimal, reason: str = "") -> Dict[str, Any]:
        """冻结资金"""
        account = self.get_user_account(user_id)
        
        # 检查可用余额
        available_balance = account.balance - account.frozen_amount
        if amount > available_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="冻结金额超过可用余额"
            )
        
        # 创建冻结交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.FREEZE,
            amount=amount,
            description=f"资金冻结 - {reason}"
        )
        
        # 更新冻结金额
        account.frozen_amount += amount
        account.updated_at = datetime.utcnow()
        
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "frozen_amount": float(amount),
            "total_frozen": float(account.frozen_amount),
            "available_balance": float(account.balance - account.frozen_amount)
        }
    
    def unfreeze_amount(self, user_id: int, amount: Decimal, reason: str = "") -> Dict[str, Any]:
        """解冻资金"""
        account = self.get_user_account(user_id)
        
        # 检查冻结金额
        if amount > account.frozen_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="解冻金额超过冻结金额"
            )
        
        # 创建解冻交易记录
        transaction = self.create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.UNFREEZE,
            amount=amount,
            description=f"资金解冻 - {reason}"
        )
        
        # 更新冻结金额
        account.frozen_amount -= amount
        account.updated_at = datetime.utcnow()
        
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "unfrozen_amount": float(amount),
            "total_frozen": float(account.frozen_amount),
            "available_balance": float(account.balance - account.frozen_amount)
        }
    
    def get_user_transactions(
        self,
        user_id: int,
        transaction_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取用户交易记录"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        # 按类型筛选
        if transaction_type:
            try:
                trans_type = TransactionType(transaction_type)
                query = query.filter(Transaction.transaction_type == trans_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的交易类型"
                )
        
        # 分页
        total = query.count()
        transactions = query.order_by(desc(Transaction.created_at)).offset((page - 1) * size).limit(size).all()
        
        return {
            "transactions": [trans.to_dict() for trans in transactions],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    def get_transaction_detail(self, transaction_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取交易详情"""
        transaction = self.db.query(Transaction).filter(
            and_(Transaction.id == transaction_id, Transaction.user_id == user_id)
        ).first()
        
        if not transaction:
            return None
        
        return transaction.to_dict()
    
    def get_account_statistics(self, user_id: int, period: str = "month") -> Dict[str, Any]:
        """获取账户统计信息"""
        account = self.get_user_account(user_id)
        
        # 计算时间范围
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # 查询期间内的交易统计
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.created_at >= start_date,
                Transaction.status == TransactionStatus.SUCCESS
            )
        ).all()
        
        # 统计各类型交易
        stats = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "account_info": account.to_dict(),
            "period_stats": {
                "total_recharge": 0,
                "total_withdraw": 0,
                "total_purchase": 0,
                "total_winnings": 0,
                "transaction_count": len(transactions)
            },
            "daily_stats": []
        }
        
        # 按交易类型统计
        for trans in transactions:
            if trans.transaction_type == TransactionType.RECHARGE:
                stats["period_stats"]["total_recharge"] += float(trans.amount)
            elif trans.transaction_type == TransactionType.WITHDRAW:
                stats["period_stats"]["total_withdraw"] += float(trans.amount)
            elif trans.transaction_type == TransactionType.PURCHASE:
                stats["period_stats"]["total_purchase"] += float(trans.amount)
            elif trans.transaction_type == TransactionType.WINNING:
                stats["period_stats"]["total_winnings"] += float(trans.amount)
        
        return stats
    
    def get_account_limits(self, user_id: int) -> Dict[str, Any]:
        """获取账户限额信息"""
        account = self.get_user_account(user_id)
        
        # 计算今日和本月消费
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 今日消费
        daily_consumption = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.PURCHASE,
                Transaction.created_at >= today_start,
                Transaction.status == TransactionStatus.SUCCESS
            )
        ).scalar() or Decimal('0')
        
        # 本月消费
        monthly_consumption = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.PURCHASE,
                Transaction.created_at >= month_start,
                Transaction.status == TransactionStatus.SUCCESS
            )
        ).scalar() or Decimal('0')
        
        return {
            "daily_limit": float(account.daily_limit) if account.daily_limit else None,
            "monthly_limit": float(account.monthly_limit) if account.monthly_limit else None,
            "daily_used": float(daily_consumption),
            "monthly_used": float(monthly_consumption),
            "daily_remaining": float(account.daily_limit - daily_consumption) if account.daily_limit else None,
            "monthly_remaining": float(account.monthly_limit - monthly_consumption) if account.monthly_limit else None
        }
    
    def set_account_limits(self, user_id: int, limits_data: Dict[str, float]) -> Dict[str, Any]:
        """设置账户限额"""
        account = self.get_user_account(user_id)
        
        if "daily_limit" in limits_data:
            account.daily_limit = Decimal(str(limits_data["daily_limit"]))
        
        if "monthly_limit" in limits_data:
            account.monthly_limit = Decimal(str(limits_data["monthly_limit"]))
        
        account.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(account)
        
        return self.get_account_limits(user_id)
    
    def get_balance_history(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取余额变动历史"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.created_at >= start_date,
                Transaction.status == TransactionStatus.SUCCESS
            )
        ).order_by(Transaction.created_at).all()
        
        history = []
        for trans in transactions:
            history.append({
                "date": trans.created_at.isoformat(),
                "transaction_type": trans.transaction_type.value,
                "amount": float(trans.amount),
                "balance_before": float(trans.balance_before),
                "balance_after": float(trans.balance_after),
                "description": trans.description
            })
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "history": history,
            "count": len(history)
        }