"""
回测相关数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class BacktestSession(Base):
    """回测会话模型"""
    __tablename__ = "backtest_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    name = Column(String(100), nullable=True, comment="会话名称")
    mode = Column(String(20), nullable=False, comment="回测模式: history/simulation")
    strategies = Column(JSON, nullable=False, comment="策略列表")

    # 数据与执行参数
    use_history_weight = Column(Boolean, default=False, comment="是否使用历史频率权重")
    data_source = Column(String(255), nullable=True, comment="历史数据来源(文件路径或说明)")
    periods = Column(Integer, nullable=True, comment="模拟期数(仅simulation模式)")
    tickets_per_period = Column(Integer, nullable=False, default=1, comment="每期投注注数")
    seed = Column(Integer, nullable=True, comment="随机种子")

    # 资金与统计
    starting_balance = Column(Numeric(15, 2), default=0.00, nullable=False, comment="起始虚拟资金")
    total_spent = Column(Numeric(15, 2), default=0.00, nullable=False, comment="总花费")
    total_winnings = Column(Numeric(15, 2), default=0.00, nullable=False, comment="总中奖金额")
    roi = Column(Float, nullable=True, comment="收益率")
    total_bets = Column(Integer, nullable=False, default=0, comment="总投注数")
    total_hits = Column(Integer, nullable=False, default=0, comment="总命中次数")
    prize_counts = Column(JSON, nullable=True, comment="各奖级命中次数")
    summary = Column(JSON, nullable=True, comment="结果摘要与明细")

    # 时间字段
    started_at = Column(DateTime, default=datetime.utcnow, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="结束时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联
    user = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "mode": self.mode,
            "strategies": self.strategies,
            "use_history_weight": self.use_history_weight,
            "data_source": self.data_source,
            "periods": self.periods,
            "tickets_per_period": self.tickets_per_period,
            "seed": self.seed,
            "starting_balance": float(self.starting_balance),
            "total_spent": float(self.total_spent),
            "total_winnings": float(self.total_winnings),
            "roi": self.roi,
            "total_bets": self.total_bets,
            "total_hits": self.total_hits,
            "prize_counts": self.prize_counts,
            "summary": self.summary,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }