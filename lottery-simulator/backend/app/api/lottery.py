"""
双色球彩票相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.lottery_service import LotteryService
from app.services.account_service import AccountService
from app.models.user import User
from app.utils.response import success_response, error_response

router = APIRouter()


@router.get("/current-period", summary="获取当前期号信息")
async def get_current_period(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取当前期号和开奖信息
    """
    try:
        lottery_service = LotteryService(db)
        current_period = lottery_service.get_current_period()
        
        return success_response(
            data=current_period,
            message="获取当前期号成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取当前期号失败: {str(e)}")


@router.get("/history", summary="获取历史开奖记录")
async def get_lottery_history(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取历史开奖记录
    """
    try:
        lottery_service = LotteryService(db)
        history = lottery_service.get_lottery_history(page=page, size=size)
        
        return success_response(
            data=history,
            message="获取历史记录成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取历史记录失败: {str(e)}")


@router.post("/purchase", summary="购买彩票")
async def purchase_lottery(
    red_balls: List[int],
    blue_ball: int,
    bet_amount: int = 2,
    multiple: int = 1,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    购买双色球彩票
    """
    try:
        lottery_service = LotteryService(db)
        account_service = AccountService(db)
        
        # 验证投注参数
        if not lottery_service.validate_bet_numbers(red_balls, blue_ball):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="投注号码不符合规则"
            )
        
        # 计算总金额
        total_amount = bet_amount * multiple
        
        # 检查账户余额
        account = account_service.get_user_account(current_user.id)
        if account.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户余额不足"
            )
        
        # 创建购买记录
        purchase = lottery_service.create_purchase(
            user_id=current_user.id,
            red_balls=red_balls,
            blue_ball=blue_ball,
            bet_amount=bet_amount,
            multiple=multiple
        )
        
        # 扣除账户余额
        account_service.deduct_balance(current_user.id, total_amount)
        
        return success_response(
            data={
                "purchase_id": purchase.id,
                "period_number": purchase.period_number,
                "red_balls": purchase.red_balls,
                "blue_ball": purchase.blue_ball,
                "bet_amount": purchase.bet_amount,
                "multiple": purchase.multiple,
                "total_amount": total_amount,
                "purchase_time": purchase.created_at.isoformat()
            },
            message="购买成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"购买失败: {str(e)}")


@router.post("/quick-pick", summary="机选号码")
async def quick_pick(
    count: int = 1,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    机选号码
    """
    try:
        lottery_service = LotteryService(db)
        
        if count < 1 or count > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="机选数量必须在1-10之间"
            )
        
        picks = []
        for _ in range(count):
            pick_result = lottery_service.quick_pick_numbers()
            picks.append({
                "red_balls": pick_result["red_balls"],
                "blue_ball": pick_result["blue_ball"][0]  # 蓝球是列表，取第一个元素
            })
        
        return success_response(
            data={"picks": picks},
            message="机选成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"机选失败: {str(e)}")


@router.get("/my-purchases", summary="我的购买记录")
async def get_my_purchases(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户购买记录
    """
    try:
        lottery_service = LotteryService(db)
        purchases = lottery_service.get_user_purchases(
            user_id=current_user.id,
            page=page,
            size=size
        )
        
        return success_response(
            data=purchases,
            message="获取购买记录成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取购买记录失败: {str(e)}")


@router.get("/purchase/{purchase_id}", summary="获取购买详情")
async def get_purchase_detail(
    purchase_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取购买详情
    """
    try:
        lottery_service = LotteryService(db)
        purchase = lottery_service.get_purchase_detail(purchase_id, current_user.id)
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="购买记录不存在"
            )
        
        return success_response(
            data=purchase,
            message="获取购买详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取购买详情失败: {str(e)}")


@router.post("/check-winning", summary="检查中奖情况")
async def check_winning(
    purchase_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    检查指定购买记录的中奖情况
    """
    try:
        lottery_service = LotteryService(db)
        winning_result = lottery_service.check_winning(purchase_id, current_user.id)
        
        return success_response(
            data=winning_result,
            message="中奖检查完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"中奖检查失败: {str(e)}")


@router.get("/statistics", summary="获取购买统计")
async def get_purchase_statistics(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户购买统计信息
    """
    try:
        lottery_service = LotteryService(db)
        stats = lottery_service.get_user_statistics(current_user.id)
        
        return success_response(
            data=stats,
            message="获取统计信息成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取统计信息失败: {str(e)}")


@router.get("/prize-levels", summary="获取奖级信息")
async def get_prize_levels(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取双色球奖级和奖金信息
    """
    try:
        lottery_service = LotteryService(db)
        prize_levels = lottery_service.get_prize_levels()
        
        return success_response(
            data={"prize_levels": prize_levels},
            message="获取奖级信息成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取奖级信息失败: {str(e)}")


@router.post("/batch-purchase", summary="批量购买")
async def batch_purchase(
    purchases: List[Dict[str, Any]],
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    批量购买彩票
    """
    try:
        lottery_service = LotteryService(db)
        account_service = AccountService(db)
        
        # 验证批量购买参数
        if len(purchases) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单次批量购买不能超过50注"
            )
        
        # 计算总金额
        total_amount = 0
        for purchase in purchases:
            red_balls = purchase.get("red_balls", [])
            blue_ball = purchase.get("blue_ball", 0)
            bet_amount = purchase.get("bet_amount", 2)
            multiple = purchase.get("multiple", 1)
            
            if not lottery_service.validate_bet_numbers(red_balls, blue_ball):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="存在不符合规则的投注号码"
                )
            
            total_amount += bet_amount * multiple
        
        # 检查账户余额
        account = account_service.get_user_account(current_user.id)
        if account.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户余额不足"
            )
        
        # 批量创建购买记录
        purchase_results = lottery_service.batch_purchase(current_user.id, purchases)
        
        # 扣除账户余额
        account_service.deduct_balance(current_user.id, total_amount)
        
        return success_response(
            data={
                "purchases": purchase_results,
                "total_amount": total_amount,
                "count": len(purchase_results)
            },
            message="批量购买成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"批量购买失败: {str(e)}")