"""
彩票工具模块
提供双色球相关的工具函数
"""
import random
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.lottery import LotteryDraw


def generate_random_numbers() -> Tuple[List[int], int]:
    """
    生成随机双色球号码
    
    Returns:
        Tuple[List[int], int]: (红球号码列表, 蓝球号码)
    """
    # 生成6个红球号码（1-33）
    red_balls = sorted(random.sample(range(1, 34), 6))
    # 生成1个蓝球号码（1-16）
    blue_ball = random.randint(1, 16)
    
    return red_balls, blue_ball


def validate_lottery_numbers(red_balls: List[int], blue_ball: int) -> bool:
    """
    验证双色球号码是否有效
    
    Args:
        red_balls: 红球号码列表
        blue_ball: 蓝球号码
    
    Returns:
        bool: 号码是否有效
    """
    # 检查红球数量
    if len(red_balls) != 6:
        return False
    
    # 检查红球范围和重复
    if not all(1 <= ball <= 33 for ball in red_balls):
        return False
    
    if len(set(red_balls)) != 6:
        return False
    
    # 检查蓝球范围
    if not (1 <= blue_ball <= 16):
        return False
    
    return True


def calculate_prize_level(
    user_red_balls: List[int],
    user_blue_ball: int,
    winning_red_balls: List[int],
    winning_blue_ball: int
) -> Tuple[int, str, float]:
    """
    计算中奖等级
    
    Args:
        user_red_balls: 用户红球号码
        user_blue_ball: 用户蓝球号码
        winning_red_balls: 中奖红球号码
        winning_blue_ball: 中奖蓝球号码
    
    Returns:
        Tuple[int, str, float]: (等级, 等级名称, 奖金金额)
    """
    # 计算红球命中数
    red_hits = len(set(user_red_balls) & set(winning_red_balls))
    # 计算蓝球是否命中
    blue_hit = user_blue_ball == winning_blue_ball
    
    # 奖级判定
    if red_hits == 6 and blue_hit:
        return 1, "一等奖", 5000000.0  # 500万
    elif red_hits == 6:
        return 2, "二等奖", 100000.0   # 10万
    elif red_hits == 5 and blue_hit:
        return 3, "三等奖", 3000.0     # 3000元
    elif red_hits == 5 or (red_hits == 4 and blue_hit):
        return 4, "四等奖", 200.0      # 200元
    elif red_hits == 4 or (red_hits == 3 and blue_hit):
        return 5, "五等奖", 10.0       # 10元
    elif blue_hit:
        return 6, "六等奖", 5.0        # 5元
    else:
        return 0, "未中奖", 0.0


def format_lottery_numbers(red_balls: List[int], blue_ball: int) -> str:
    """
    格式化彩票号码显示
    
    Args:
        red_balls: 红球号码列表
        blue_ball: 蓝球号码
    
    Returns:
        str: 格式化的号码字符串
    """
    red_str = " ".join([f"{ball:02d}" for ball in sorted(red_balls)])
    blue_str = f"{blue_ball:02d}"
    return f"{red_str} | {blue_str}"


def get_current_period() -> str:
    """
    获取当前期号
    
    Returns:
        str: 当前期号（格式：YYYYNNN）
    """
    now = datetime.now()
    year = now.year
    
    # 双色球每周二、四、日开奖，一年大约150期
    # 这里简化计算，实际应该根据开奖日历计算
    day_of_year = now.timetuple().tm_yday
    period_num = (day_of_year // 3) + 1  # 简化计算
    
    return f"{year}{period_num:03d}"


def get_next_draw_time() -> datetime:
    """
    获取下次开奖时间
    
    Returns:
        datetime: 下次开奖时间
    """
    now = datetime.now()
    
    # 双色球开奖时间：每周二、四、日 21:15
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # 计算下次开奖日
    if weekday == 1:  # Tuesday
        if now.hour < 21 or (now.hour == 21 and now.minute < 15):
            next_draw = now.replace(hour=21, minute=15, second=0, microsecond=0)
        else:
            next_draw = now + timedelta(days=2)  # Thursday
            next_draw = next_draw.replace(hour=21, minute=15, second=0, microsecond=0)
    elif weekday == 3:  # Thursday
        if now.hour < 21 or (now.hour == 21 and now.minute < 15):
            next_draw = now.replace(hour=21, minute=15, second=0, microsecond=0)
        else:
            next_draw = now + timedelta(days=3)  # Sunday
            next_draw = next_draw.replace(hour=21, minute=15, second=0, microsecond=0)
    elif weekday == 6:  # Sunday
        if now.hour < 21 or (now.hour == 21 and now.minute < 15):
            next_draw = now.replace(hour=21, minute=15, second=0, microsecond=0)
        else:
            next_draw = now + timedelta(days=2)  # Tuesday
            next_draw = next_draw.replace(hour=21, minute=15, second=0, microsecond=0)
    else:
        # 其他日期，计算到最近的开奖日
        days_until_tuesday = (1 - weekday) % 7
        days_until_thursday = (3 - weekday) % 7
        days_until_sunday = (6 - weekday) % 7
        
        next_days = min(days_until_tuesday, days_until_thursday, days_until_sunday)
        next_draw = now + timedelta(days=next_days)
        next_draw = next_draw.replace(hour=21, minute=15, second=0, microsecond=0)
    
    return next_draw


def get_lottery_statistics(db: Session, periods: int = 30) -> Dict[str, Any]:
    """
    获取彩票统计信息
    
    Args:
        db: 数据库会话
        periods: 统计期数
    
    Returns:
        Dict[str, Any]: 统计信息
    """
    # 获取最近N期的开奖数据
    recent_draws = db.query(LotteryDraw).order_by(
        LotteryDraw.period_number.desc()
    ).limit(periods).all()
    
    if not recent_draws:
        return {
            "total_periods": 0,
            "red_ball_frequency": {},
            "blue_ball_frequency": {},
            "hot_red_balls": [],
            "cold_red_balls": [],
            "hot_blue_balls": [],
            "cold_blue_balls": []
        }
    
    # 统计红球频率
    red_frequency = {}
    blue_frequency = {}
    
    for draw in recent_draws:
        red_balls = draw.red_balls
        blue_ball = draw.blue_ball
        
        for ball in red_balls:
            red_frequency[ball] = red_frequency.get(ball, 0) + 1
        
        blue_frequency[blue_ball] = blue_frequency.get(blue_ball, 0) + 1
    
    # 计算热号和冷号
    sorted_red = sorted(red_frequency.items(), key=lambda x: x[1], reverse=True)
    sorted_blue = sorted(blue_frequency.items(), key=lambda x: x[1], reverse=True)
    
    hot_red_balls = [ball for ball, freq in sorted_red[:10]]
    cold_red_balls = [ball for ball, freq in sorted_red[-10:]]
    hot_blue_balls = [ball for ball, freq in sorted_blue[:5]]
    cold_blue_balls = [ball for ball, freq in sorted_blue[-5:]]
    
    return {
        "total_periods": len(recent_draws),
        "red_ball_frequency": red_frequency,
        "blue_ball_frequency": blue_frequency,
        "hot_red_balls": hot_red_balls,
        "cold_red_balls": cold_red_balls,
        "hot_blue_balls": hot_blue_balls,
        "cold_blue_balls": cold_blue_balls
    }