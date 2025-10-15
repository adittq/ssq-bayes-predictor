"""
账户管理相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from decimal import Decimal

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.account_service import AccountService
from app.models.user import User
from app.utils.response import success_response, error_response

router = APIRouter()


@router.get("/balance", summary="获取账户余额")
async def get_balance(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户账户余额
    """
    try:
        account_service = AccountService(db)
        account = account_service.get_user_account(current_user.id)
        
        return success_response(
            data={
                "balance": float(account.balance),
                "frozen_amount": float(account.frozen_amount),
                "available_balance": float(account.balance - account.frozen_amount),
                "total_recharge": float(account.total_recharge),
                "total_consumption": float(account.total_consumption),
                "total_winnings": float(account.total_winnings)
            },
            message="获取余额成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取余额失败: {str(e)}")


@router.post("/recharge", summary="账户充值")
async def recharge(
    amount: float,
    payment_method: str = "wechat",
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    账户充值（模拟）
    """
    try:
        account_service = AccountService(db)
        
        # 验证充值金额
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="充值金额必须大于0"
            )
        
        if amount > 100000:  # 单次充值限额10万
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单次充值金额不能超过100,000元"
            )
        
        # 验证支付方式
        valid_methods = ["wechat", "alipay", "bank_card"]
        if payment_method not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的支付方式，支持的方式: {', '.join(valid_methods)}"
            )
        
        # 执行充值
        transaction = account_service.recharge(
            user_id=current_user.id,
            amount=Decimal(str(amount)),
            payment_method=payment_method
        )
        
        return success_response(
            data={
                "transaction_id": transaction.id,
                "amount": float(transaction.amount),
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat()
            },
            message="充值成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"充值失败: {str(e)}")


@router.post("/withdraw", summary="账户提现")
async def withdraw(
    amount: float,
    withdraw_method: str = "bank_card",
    account_info: str = "",
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    账户提现（模拟）
    """
    try:
        account_service = AccountService(db)
        
        # 验证提现金额
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提现金额必须大于0"
            )
        
        # 检查账户余额
        account = account_service.get_user_account(current_user.id)
        available_balance = account.balance - account.frozen_amount
        
        if amount > available_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提现金额超过可用余额"
            )
        
        # 验证提现方式
        valid_methods = ["bank_card", "alipay", "wechat"]
        if withdraw_method not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的提现方式，支持的方式: {', '.join(valid_methods)}"
            )
        
        # 执行提现
        transaction = account_service.withdraw(
            user_id=current_user.id,
            amount=Decimal(str(amount)),
            withdraw_method=withdraw_method,
            account_info=account_info
        )
        
        return success_response(
            data={
                "transaction_id": transaction.id,
                "amount": float(transaction.amount),
                "withdraw_method": transaction.withdraw_method,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat()
            },
            message="提现申请提交成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"提现失败: {str(e)}")


@router.get("/transactions", summary="交易记录")
async def get_transactions(
    transaction_type: str = Query(None, description="交易类型: recharge, withdraw, purchase, winning"),
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(20, description="每页数量", ge=1, le=100),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取交易记录
    """
    try:
        account_service = AccountService(db)
        transactions = account_service.get_user_transactions(
            user_id=current_user.id,
            transaction_type=transaction_type,
            page=page,
            size=size
        )
        
        return success_response(
            data=transactions,
            message="获取交易记录成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取交易记录失败: {str(e)}")


@router.get("/transaction/{transaction_id}", summary="交易详情")
async def get_transaction_detail(
    transaction_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取交易详情
    """
    try:
        account_service = AccountService(db)
        transaction = account_service.get_transaction_detail(transaction_id, current_user.id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="交易记录不存在"
            )
        
        return success_response(
            data=transaction,
            message="获取交易详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取交易详情失败: {str(e)}")


@router.get("/statistics", summary="账户统计")
async def get_account_statistics(
    period: str = Query("month", description="统计周期: week, month, quarter, year"),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取账户统计信息
    """
    try:
        account_service = AccountService(db)
        
        valid_periods = ["week", "month", "quarter", "year"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的统计周期，支持的周期: {', '.join(valid_periods)}"
            )
        
        statistics = account_service.get_account_statistics(current_user.id, period)
        
        return success_response(
            data=statistics,
            message="获取账户统计成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取账户统计失败: {str(e)}")


@router.post("/freeze", summary="冻结资金")
async def freeze_amount(
    amount: float,
    reason: str = "",
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    冻结账户资金（用于购买等场景）
    """
    try:
        account_service = AccountService(db)
        
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="冻结金额必须大于0"
            )
        
        result = account_service.freeze_amount(
            user_id=current_user.id,
            amount=Decimal(str(amount)),
            reason=reason
        )
        
        return success_response(
            data=result,
            message="资金冻结成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"资金冻结失败: {str(e)}")


@router.post("/unfreeze", summary="解冻资金")
async def unfreeze_amount(
    amount: float,
    reason: str = "",
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    解冻账户资金
    """
    try:
        account_service = AccountService(db)
        
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="解冻金额必须大于0"
            )
        
        result = account_service.unfreeze_amount(
            user_id=current_user.id,
            amount=Decimal(str(amount)),
            reason=reason
        )
        
        return success_response(
            data=result,
            message="资金解冻成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"资金解冻失败: {str(e)}")


@router.get("/limits", summary="账户限额")
async def get_account_limits(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取账户限额信息
    """
    try:
        account_service = AccountService(db)
        limits = account_service.get_account_limits(current_user.id)
        
        return success_response(
            data=limits,
            message="获取账户限额成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取账户限额失败: {str(e)}")


@router.post("/set-limits", summary="设置账户限额")
async def set_account_limits(
    daily_limit: float = None,
    monthly_limit: float = None,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    设置账户限额
    """
    try:
        account_service = AccountService(db)
        
        limits_data = {}
        if daily_limit is not None:
            if daily_limit < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="日限额不能为负数"
                )
            limits_data["daily_limit"] = daily_limit
        
        if monthly_limit is not None:
            if monthly_limit < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="月限额不能为负数"
                )
            limits_data["monthly_limit"] = monthly_limit
        
        if not limits_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要设置一个限额"
            )
        
        result = account_service.set_account_limits(current_user.id, limits_data)
        
        return success_response(
            data=result,
            message="账户限额设置成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"设置账户限额失败: {str(e)}")


@router.get("/balance-history", summary="余额变动历史")
async def get_balance_history(
    days: int = Query(30, description="查询天数", ge=1, le=365),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取余额变动历史
    """
    try:
        account_service = AccountService(db)
        history = account_service.get_balance_history(current_user.id, days)
        
        return success_response(
            data=history,
            message="获取余额历史成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取余额历史失败: {str(e)}")