"""
彩票服务
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from fastapi import HTTPException, status

from app.models.lottery import LotteryDraw, Purchase, WinningRecord
from app.models.user import User
from app.core.config import settings


class LotteryService:
    """彩票服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_current_period(self) -> Dict[str, Any]:
        """获取当前期号信息"""
        # 双色球每周二、四、日开奖
        now = datetime.utcnow()
        
        # 计算下一期开奖时间
        next_draw_date = self._calculate_next_draw_date(now)
        
        # 生成期号（格式：YYYYNNN，如2024001）
        year = next_draw_date.year
        # 计算是当年第几期（每周3期）
        start_of_year = datetime(year, 1, 1)
        days_passed = (next_draw_date - start_of_year).days
        period_number = (days_passed // 7) * 3 + self._get_weekday_period(next_draw_date.weekday())
        
        period_str = f"{year}{period_number:03d}"
        
        # 检查是否已存在该期
        existing_draw = self.db.query(LotteryDraw).filter(LotteryDraw.period_number == period_str).first()
        
        return {
            "period": period_str,
            "draw_date": next_draw_date.isoformat(),
            "is_drawn": existing_draw is not None,
            "sales_deadline": (next_draw_date - timedelta(hours=2)).isoformat(),
            "can_purchase": datetime.utcnow() < (next_draw_date - timedelta(hours=2))
        }
    
    def _calculate_next_draw_date(self, current_date: datetime) -> datetime:
        """计算下一期开奖日期"""
        # 双色球开奖时间：每周二(1)、四(3)、日(6) 21:15
        draw_weekdays = [1, 3, 6]  # 周二、周四、周日
        current_weekday = current_date.weekday()
        
        # 找到下一个开奖日
        for days_ahead in range(8):  # 最多查找一周
            check_date = current_date + timedelta(days=days_ahead)
            if check_date.weekday() in draw_weekdays:
                # 如果是当天且还没到开奖时间，就是今天
                if days_ahead == 0 and current_date.hour < 21:
                    return check_date.replace(hour=21, minute=15, second=0, microsecond=0)
                # 否则是下一个开奖日
                elif days_ahead > 0:
                    return check_date.replace(hour=21, minute=15, second=0, microsecond=0)
        
        # 默认返回下周二
        days_until_tuesday = (1 - current_weekday) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        next_tuesday = current_date + timedelta(days=days_until_tuesday)
        return next_tuesday.replace(hour=21, minute=15, second=0, microsecond=0)
    
    def _get_weekday_period(self, weekday: int) -> int:
        """根据星期几获取当周期号"""
        if weekday == 1:  # 周二
            return 1
        elif weekday == 3:  # 周四
            return 2
        elif weekday == 6:  # 周日
            return 3
        else:
            return 1
    
    def get_historical_draws(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取历史开奖记录"""
        draws = self.db.query(LotteryDraw).order_by(desc(LotteryDraw.draw_date)).limit(limit).all()
        return [draw.to_dict() for draw in draws]
    
    def get_lottery_history(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取历史开奖记录（分页）"""
        offset = (page - 1) * size
        
        # 查询总数
        total = self.db.query(LotteryDraw).count()
        
        # 查询数据
        draws = (self.db.query(LotteryDraw)
                .order_by(desc(LotteryDraw.draw_date))
                .offset(offset)
                .limit(size)
                .all())
        
        items = []
        for draw in draws:
            items.append({
                "id": draw.id,
                "period": draw.period,
                "red_balls": draw.red_balls,
                "blue_ball": draw.blue_ball,
                "draw_date": draw.draw_date.isoformat() if draw.draw_date else None,
                "sales_amount": float(draw.sales_amount) if draw.sales_amount else 0,
                "pool_amount": float(draw.pool_amount) if draw.pool_amount else 0
            })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    def quick_pick_numbers(self) -> Dict[str, List[int]]:
        """机选号码"""
        # 红球：从1-33中选择6个不重复的数字
        red_balls = sorted(random.sample(range(1, 34), 6))
        
        # 蓝球：从1-16中选择1个数字
        blue_ball = [random.randint(1, 16)]
        
        return {
            "red_balls": red_balls,
            "blue_ball": blue_ball
        }
    
    def validate_numbers(self, red_balls: List[int], blue_ball: int) -> bool:
        """验证号码有效性"""
        # 检查红球
        if len(red_balls) != 6:
            return False
        
        if len(set(red_balls)) != 6:  # 检查是否有重复
            return False
        
        if not all(1 <= ball <= 33 for ball in red_balls):
            return False
        
        # 检查蓝球
        if not (1 <= blue_ball <= 16):
            return False
        
        return True
    
    def purchase_lottery(
        self,
        user_id: int,
        red_balls: List[int],
        blue_ball: int,
        multiple: int = 1,
        period: Optional[str] = None
    ) -> Purchase:
        """购买彩票"""
        # 验证号码
        if not self.validate_numbers(red_balls, blue_ball):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="号码格式不正确"
            )
        
        # 验证倍数
        if not (1 <= multiple <= 99):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="倍数必须在1-99之间"
            )
        
        # 获取期号
        if not period:
            current_period_info = self.get_current_period()
            period = current_period_info["period"]
            
            if not current_period_info["can_purchase"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前期号已停止销售"
                )
        
        # 计算金额
        single_bet_amount = Decimal(str(settings.SINGLE_BET_AMOUNT))
        total_amount = single_bet_amount * multiple
        
        # 创建购买记录
        purchase = Purchase(
            user_id=user_id,
            period=period,
            red_balls=red_balls,
            blue_ball=blue_ball,
            bet_amount=single_bet_amount,
            multiple=multiple,
            total_amount=total_amount,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    def batch_purchase_lottery(
        self,
        user_id: int,
        purchases: List[Dict[str, Any]],
        period: Optional[str] = None
    ) -> List[Purchase]:
        """批量购买彩票"""
        if len(purchases) > 100:  # 限制批量购买数量
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单次最多购买100注"
            )
        
        # 获取期号
        if not period:
            current_period_info = self.get_current_period()
            period = current_period_info["period"]
            
            if not current_period_info["can_purchase"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前期号已停止销售"
                )
        
        purchase_records = []
        total_cost = Decimal('0')
        
        for purchase_data in purchases:
            red_balls = purchase_data.get("red_balls", [])
            blue_ball = purchase_data.get("blue_ball", 1)
            multiple = purchase_data.get("multiple", 1)
            
            # 验证每注号码
            if not self.validate_numbers(red_balls, blue_ball):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"号码格式不正确: 红球{red_balls}, 蓝球{blue_ball}"
                )
            
            if not (1 <= multiple <= 99):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="倍数必须在1-99之间"
                )
            
            # 计算金额
            single_bet_amount = Decimal(str(settings.SINGLE_BET_AMOUNT))
            amount = single_bet_amount * multiple
            total_cost += amount
            
            # 创建购买记录
            purchase = Purchase(
                user_id=user_id,
                period=period,
                red_balls=red_balls,
                blue_ball=blue_ball,
                bet_amount=single_bet_amount,
                multiple=multiple,
                total_amount=amount,
                status="pending",
                created_at=datetime.utcnow()
            )
            
            purchase_records.append(purchase)
        
        # 批量添加到数据库
        self.db.add_all(purchase_records)
        self.db.commit()
        
        # 刷新所有记录
        for purchase in purchase_records:
            self.db.refresh(purchase)
        
        return purchase_records
    
    def get_user_purchases(
        self,
        user_id: int,
        period: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取用户购买记录"""
        query = self.db.query(Purchase).filter(Purchase.user_id == user_id)
        
        if period:
            query = query.filter(Purchase.period == period)
        
        total = query.count()
        purchases = query.order_by(desc(Purchase.created_at)).offset((page - 1) * size).limit(size).all()
        
        return {
            "purchases": [purchase.to_dict() for purchase in purchases],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    def get_purchase_detail(self, purchase_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取购买详情"""
        purchase = self.db.query(Purchase).filter(
            and_(Purchase.id == purchase_id, Purchase.user_id == user_id)
        ).first()
        
        if not purchase:
            return None
        
        # 获取开奖信息
        draw = self.db.query(LotteryDraw).filter(LotteryDraw.period_number == purchase.period_number).first()
        
        # 获取中奖记录
        winning_record = self.db.query(WinningRecord).filter(
            WinningRecord.purchase_id == purchase_id
        ).first()
        
        result = purchase.to_dict()
        result["draw_info"] = draw.to_dict() if draw else None
        result["winning_info"] = winning_record.to_dict() if winning_record else None
        
        return result
    
    def check_winning(self, purchase_id: int) -> Optional[WinningRecord]:
        """检查中奖情况"""
        purchase = self.db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not purchase:
            return None
        
        # 获取开奖结果
        draw = self.db.query(LotteryDraw).filter(LotteryDraw.period_number == purchase.period_number).first()
        if not draw:
            return None
        
        # 检查是否已经有中奖记录
        existing_record = self.db.query(WinningRecord).filter(
            WinningRecord.purchase_id == purchase_id
        ).first()
        if existing_record:
            return existing_record
        
        # 计算中奖情况
        red_matches = len(set(purchase.red_balls) & set(draw.red_balls))
        blue_matches = 1 if purchase.blue_ball == draw.blue_ball else 0
        
        # 判断奖级
        prize_level = self._determine_prize_level(red_matches, blue_matches)
        
        if prize_level:
            # 计算奖金
            single_prize_amount = self._calculate_prize_amount(prize_level, draw)
            total_prize_amount = single_prize_amount * purchase.multiple
            
            # 创建中奖记录
            winning_record = WinningRecord(
                user_id=purchase.user_id,
                purchase_id=purchase_id,
                lottery_draw_id=draw.id,
                prize_level=prize_level,
                red_ball_matches=red_matches,
                blue_ball_matches=blue_matches,
                single_prize_amount=single_prize_amount,
                total_prize_amount=total_prize_amount,
                claim_status="unclaimed",
                created_at=datetime.utcnow()
            )
            
            self.db.add(winning_record)
            self.db.commit()
            self.db.refresh(winning_record)
            
            return winning_record
        
        return None
    
    def _determine_prize_level(self, red_matches: int, blue_matches: int) -> Optional[int]:
        """判断奖级"""
        if red_matches == 6 and blue_matches == 1:
            return 1  # 一等奖
        elif red_matches == 6 and blue_matches == 0:
            return 2  # 二等奖
        elif red_matches == 5 and blue_matches == 1:
            return 3  # 三等奖
        elif (red_matches == 5 and blue_matches == 0) or (red_matches == 4 and blue_matches == 1):
            return 4  # 四等奖
        elif (red_matches == 4 and blue_matches == 0) or (red_matches == 3 and blue_matches == 1):
            return 5  # 五等奖
        elif (red_matches == 2 and blue_matches == 1) or (red_matches == 1 and blue_matches == 1) or (red_matches == 0 and blue_matches == 1):
            return 6  # 六等奖
        else:
            return None  # 未中奖
    
    def _calculate_prize_amount(self, prize_level: int, draw: LotteryDraw) -> Decimal:
        """计算奖金金额"""
        # 这里使用固定奖金，实际应该根据奖池和中奖注数计算
        prize_amounts = {
            1: Decimal('5000000'),    # 一等奖 500万
            2: Decimal('1000000'),    # 二等奖 100万
            3: Decimal('3000'),       # 三等奖 3000元
            4: Decimal('200'),        # 四等奖 200元
            5: Decimal('10'),         # 五等奖 10元
            6: Decimal('5')           # 六等奖 5元
        }
        
        return prize_amounts.get(prize_level, Decimal('0'))
    
    def get_purchase_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取购买统计"""
        # 总购买次数和金额
        total_purchases = self.db.query(func.count(Purchase.id)).filter(Purchase.user_id == user_id).scalar()
        total_amount = self.db.query(func.sum(Purchase.total_amount)).filter(Purchase.user_id == user_id).scalar() or Decimal('0')
        
        # 中奖统计
        total_winnings = self.db.query(func.count(WinningRecord.id)).filter(WinningRecord.user_id == user_id).scalar()
        total_prize_amount = self.db.query(func.sum(WinningRecord.total_prize_amount)).filter(WinningRecord.user_id == user_id).scalar() or Decimal('0')
        
        # 各奖级中奖次数
        prize_stats = {}
        for level in range(1, 7):
            count = self.db.query(func.count(WinningRecord.id)).filter(
                and_(WinningRecord.user_id == user_id, WinningRecord.prize_level == level)
            ).scalar()
            prize_stats[f"level_{level}"] = count
        
        return {
            "total_purchases": total_purchases,
            "total_amount": float(total_amount),
            "total_winnings": total_winnings,
            "total_prize_amount": float(total_prize_amount),
            "win_rate": float(total_winnings / total_purchases) if total_purchases > 0 else 0,
            "return_rate": float(total_prize_amount / total_amount) if total_amount > 0 else 0,
            "prize_level_stats": prize_stats
        }
    
    def get_prize_levels(self) -> List[Dict[str, Any]]:
        """获取奖级信息"""
        return [
            {"level": 1, "name": "一等奖", "condition": "6+1", "amount": "5,000,000元"},
            {"level": 2, "name": "二等奖", "condition": "6+0", "amount": "1,000,000元"},
            {"level": 3, "name": "三等奖", "condition": "5+1", "amount": "3,000元"},
            {"level": 4, "name": "四等奖", "condition": "5+0或4+1", "amount": "200元"},
            {"level": 5, "name": "五等奖", "condition": "4+0或3+1", "amount": "10元"},
            {"level": 6, "name": "六等奖", "condition": "2+1或1+1或0+1", "amount": "5元"}
        ]
    
    def simulate_draw(self, period: str) -> LotteryDraw:
        """模拟开奖（用于测试）"""
        # 检查是否已经开奖
        existing_draw = self.db.query(LotteryDraw).filter(LotteryDraw.period_number == period).first()
        if existing_draw:
            return existing_draw
        
        # 生成开奖号码
        red_balls = sorted(random.sample(range(1, 34), 6))
        blue_ball = random.randint(1, 16)
        
        # 模拟销售额和奖池
        sales_amount = Decimal(str(random.randint(200000000, 500000000)))  # 2-5亿
        prize_pool = sales_amount * Decimal('0.5')  # 50%进入奖池
        
        # 创建开奖记录
        draw = LotteryDraw(
            period=period,
            draw_date=datetime.utcnow(),
            red_balls=red_balls,
            blue_ball=blue_ball,
            sales_amount=sales_amount,
            prize_pool=prize_pool,
            first_prize_amount=Decimal('5000000'),
            first_prize_winners=random.randint(0, 10),
            second_prize_amount=Decimal('1000000'),
            second_prize_winners=random.randint(5, 50),
            created_at=datetime.utcnow()
        )
        
        self.db.add(draw)
        self.db.commit()
        self.db.refresh(draw)
        
        return draw