"""
彩票相关的 Pydantic 模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator


class CurrentPeriod(BaseModel):
    """当前期号信息"""
    period: str
    draw_date: str
    is_drawn: bool
    sales_deadline: str
    can_purchase: bool


class LotteryDrawInfo(BaseModel):
    """开奖信息"""
    id: int
    period: str
    draw_date: str
    red_balls: List[int]
    blue_ball: int
    sales_amount: float
    prize_pool: float
    first_prize_amount: float
    first_prize_winners: int
    second_prize_amount: float
    second_prize_winners: int
    
    class Config:
        from_attributes = True


class QuickPickResponse(BaseModel):
    """机选号码响应"""
    red_balls: List[int]
    blue_ball: List[int]


class PurchaseRequest(BaseModel):
    """购买彩票请求"""
    red_balls: List[int]
    blue_ball: int
    multiple: int = 1
    period: Optional[str] = None
    
    @validator('red_balls')
    def validate_red_balls(cls, v):
        if len(v) != 6:
            raise ValueError('红球必须选择6个号码')
        if len(set(v)) != 6:
            raise ValueError('红球号码不能重复')
        if not all(1 <= ball <= 33 for ball in v):
            raise ValueError('红球号码必须在1-33之间')
        return sorted(v)
    
    @validator('blue_ball')
    def validate_blue_ball(cls, v):
        if not (1 <= v <= 16):
            raise ValueError('蓝球号码必须在1-16之间')
        return v
    
    @validator('multiple')
    def validate_multiple(cls, v):
        if not (1 <= v <= 99):
            raise ValueError('倍数必须在1-99之间')
        return v


class BatchPurchaseRequest(BaseModel):
    """批量购买请求"""
    purchases: List[PurchaseRequest]
    period: Optional[str] = None
    
    @validator('purchases')
    def validate_purchases(cls, v):
        if len(v) == 0:
            raise ValueError('购买列表不能为空')
        if len(v) > 100:
            raise ValueError('单次最多购买100注')
        return v


class PurchaseRecord(BaseModel):
    """购买记录"""
    id: int
    period: str
    red_balls: List[int]
    blue_ball: int
    bet_amount: float
    multiple: int
    total_amount: float
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class PurchaseListResponse(BaseModel):
    """购买记录列表响应"""
    purchases: List[PurchaseRecord]
    total: int
    page: int
    size: int
    pages: int


class WinningRecord(BaseModel):
    """中奖记录"""
    id: int
    purchase_id: int
    lottery_draw_id: int
    prize_level: int
    red_ball_matches: int
    blue_ball_matches: int
    single_prize_amount: float
    total_prize_amount: float
    claim_status: str
    created_at: str
    
    class Config:
        from_attributes = True


class PurchaseDetail(BaseModel):
    """购买详情"""
    purchase: PurchaseRecord
    draw_info: Optional[LotteryDrawInfo] = None
    winning_info: Optional[WinningRecord] = None


class PurchaseStatistics(BaseModel):
    """购买统计"""
    total_purchases: int
    total_amount: float
    total_winnings: int
    total_prize_amount: float
    win_rate: float
    return_rate: float
    prize_level_stats: Dict[str, int]


class PrizeLevel(BaseModel):
    """奖级信息"""
    level: int
    name: str
    condition: str
    amount: str


class SimulateDrawRequest(BaseModel):
    """模拟开奖请求"""
    period: str
    
    @validator('period')
    def validate_period(cls, v):
        if not v or len(v) != 7:
            raise ValueError('期号格式不正确，应为YYYYNNN格式')
        return v