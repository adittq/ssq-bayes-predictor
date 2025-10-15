"""
彩票相关数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class LotteryDraw(Base):
    """双色球开奖记录模型"""
    __tablename__ = "lottery_draws"
    
    id = Column(Integer, primary_key=True, index=True)
    period_number = Column(String(20), unique=True, nullable=False, index=True, comment="期号")
    draw_date = Column(DateTime, nullable=False, index=True, comment="开奖日期")
    
    # 开奖号码
    red_ball_1 = Column(Integer, nullable=False, comment="红球1")
    red_ball_2 = Column(Integer, nullable=False, comment="红球2")
    red_ball_3 = Column(Integer, nullable=False, comment="红球3")
    red_ball_4 = Column(Integer, nullable=False, comment="红球4")
    red_ball_5 = Column(Integer, nullable=False, comment="红球5")
    red_ball_6 = Column(Integer, nullable=False, comment="红球6")
    blue_ball = Column(Integer, nullable=False, comment="蓝球")
    
    # 销售和奖金信息
    total_sales = Column(Numeric(15, 2), nullable=True, comment="总销售额")
    prize_pool = Column(Numeric(15, 2), nullable=True, comment="奖池金额")
    
    # 各奖级中奖信息 (JSON格式存储)
    prize_details = Column(JSON, nullable=True, comment="各奖级详情")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    purchases = relationship("Purchase", back_populates="lottery_draw")
    winning_records = relationship("WinningRecord", back_populates="lottery_draw")
    
    def __repr__(self):
        return f"<LotteryDraw(period={self.period_number}, date={self.draw_date})>"
    
    @property
    def red_balls(self):
        """获取红球列表"""
        return [
            self.red_ball_1, self.red_ball_2, self.red_ball_3,
            self.red_ball_4, self.red_ball_5, self.red_ball_6
        ]
    
    @red_balls.setter
    def red_balls(self, balls):
        """设置红球"""
        if len(balls) != 6:
            raise ValueError("红球必须是6个数字")
        self.red_ball_1, self.red_ball_2, self.red_ball_3, \
        self.red_ball_4, self.red_ball_5, self.red_ball_6 = balls
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "period_number": self.period_number,
            "draw_date": self.draw_date.isoformat() if self.draw_date else None,
            "red_balls": self.red_balls,
            "blue_ball": self.blue_ball,
            "total_sales": float(self.total_sales) if self.total_sales else None,
            "prize_pool": float(self.prize_pool) if self.prize_pool else None,
            "prize_details": self.prize_details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Purchase(Base):
    """购买记录模型"""
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    period_number = Column(String(20), nullable=False, index=True, comment="期号")
    lottery_draw_id = Column(Integer, ForeignKey("lottery_draws.id"), nullable=True, comment="开奖记录ID")
    
    # 投注号码
    red_ball_1 = Column(Integer, nullable=False, comment="红球1")
    red_ball_2 = Column(Integer, nullable=False, comment="红球2")
    red_ball_3 = Column(Integer, nullable=False, comment="红球3")
    red_ball_4 = Column(Integer, nullable=False, comment="红球4")
    red_ball_5 = Column(Integer, nullable=False, comment="红球5")
    red_ball_6 = Column(Integer, nullable=False, comment="红球6")
    blue_ball = Column(Integer, nullable=False, comment="蓝球")
    
    # 投注信息
    bet_amount = Column(Numeric(10, 2), nullable=False, default=2.00, comment="单注金额")
    multiple = Column(Integer, nullable=False, default=1, comment="倍数")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="总金额")
    
    # 状态信息
    is_checked = Column(Boolean, default=False, comment="是否已检查中奖")
    is_winning = Column(Boolean, default=False, comment="是否中奖")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="购买时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="purchases")
    lottery_draw = relationship("LotteryDraw", back_populates="purchases")
    winning_records = relationship("WinningRecord", back_populates="purchase")
    
    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, period={self.period_number})>"
    
    @property
    def red_balls(self):
        """获取红球列表"""
        return [
            self.red_ball_1, self.red_ball_2, self.red_ball_3,
            self.red_ball_4, self.red_ball_5, self.red_ball_6
        ]
    
    @red_balls.setter
    def red_balls(self, balls):
        """设置红球"""
        if len(balls) != 6:
            raise ValueError("红球必须是6个数字")
        balls_sorted = sorted(balls)
        self.red_ball_1, self.red_ball_2, self.red_ball_3, \
        self.red_ball_4, self.red_ball_5, self.red_ball_6 = balls_sorted
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "period_number": self.period_number,
            "lottery_draw_id": self.lottery_draw_id,
            "red_balls": self.red_balls,
            "blue_ball": self.blue_ball,
            "bet_amount": float(self.bet_amount),
            "multiple": self.multiple,
            "total_amount": float(self.total_amount),
            "is_checked": self.is_checked,
            "is_winning": self.is_winning,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class WinningRecord(Base):
    """中奖记录模型"""
    __tablename__ = "winning_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False, comment="购买记录ID")
    lottery_draw_id = Column(Integer, ForeignKey("lottery_draws.id"), nullable=False, comment="开奖记录ID")
    
    # 中奖信息
    prize_level = Column(Integer, nullable=False, comment="奖级 (1-6)")
    red_match_count = Column(Integer, nullable=False, comment="红球命中数")
    blue_match = Column(Boolean, nullable=False, comment="蓝球是否命中")
    
    # 奖金信息
    single_prize_amount = Column(Numeric(15, 2), nullable=False, comment="单注奖金")
    multiple = Column(Integer, nullable=False, default=1, comment="倍数")
    total_prize_amount = Column(Numeric(15, 2), nullable=False, comment="总奖金")
    
    # 状态信息
    is_claimed = Column(Boolean, default=False, comment="是否已领奖")
    claimed_at = Column(DateTime, nullable=True, comment="领奖时间")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User")
    purchase = relationship("Purchase", back_populates="winning_records")
    lottery_draw = relationship("LotteryDraw", back_populates="winning_records")
    
    def __repr__(self):
        return f"<WinningRecord(id={self.id}, prize_level={self.prize_level}, amount={self.total_prize_amount})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "purchase_id": self.purchase_id,
            "lottery_draw_id": self.lottery_draw_id,
            "prize_level": self.prize_level,
            "red_match_count": self.red_match_count,
            "blue_match": self.blue_match,
            "single_prize_amount": float(self.single_prize_amount),
            "multiple": self.multiple,
            "total_prize_amount": float(self.total_prize_amount),
            "is_claimed": self.is_claimed,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }