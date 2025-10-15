"""
回测服务
"""
import random
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.models import BacktestSession, User
from app.utils.lottery import generate_random_numbers


class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    def _judge_prize(self, bet_reds: List[int], bet_blue: int, result_reds: List[int], result_blue: int) -> Optional[str]:
        red_hits = len(set(bet_reds) & set(result_reds))
        blue_hit = (bet_blue == result_blue)

        if red_hits == 6 and blue_hit:
            return "first"
        if red_hits == 6:
            return "second"
        if red_hits == 5 and blue_hit:
            return "third"
        if red_hits == 5 or (red_hits == 4 and blue_hit):
            return "fourth"
        if red_hits == 4 or (red_hits == 3 and blue_hit):
            return "fifth"
        if blue_hit:
            return "sixth"
        return None

    def _random_strategy(self) -> (List[int], int):
        reds, blue = generate_random_numbers()
        return sorted(reds), blue

    def _odd_even_balance_strategy(self) -> (List[int], int):
        # 简化：与随机等价但尝试平衡奇偶（演示用途）
        reds, blue = generate_random_numbers()
        return sorted(reds), blue

    def _avoid_popular_strategy(self) -> (List[int], int):
        # 简化：与随机等价（真正避开模式需接入历史组合库）
        reds, blue = generate_random_numbers()
        return sorted(reds), blue

    def _strategy_picker(self, name: str):
        mapping = {
            "random": self._random_strategy,
            "odd_even": self._odd_even_balance_strategy,
            "avoid_popular": self._avoid_popular_strategy,
        }
        return mapping.get(name, self._random_strategy)

    def run_simulation(self, user: User, name: Optional[str], strategies: List[str], periods: int, tickets_per_period: int = 1, seed: Optional[int] = None) -> BacktestSession:
        if seed is not None:
            random.seed(seed)

        session = BacktestSession(
            user_id=user.id,
            name=name or f"回测-{datetime.utcnow().isoformat()}",
            mode="simulation",
            strategies=strategies,
            tickets_per_period=tickets_per_period,
            periods=periods,
            seed=seed,
            starting_balance=settings.INITIAL_BALANCE,
            created_at=datetime.utcnow(),
        )

        prize_counter = defaultdict(lambda: Counter())

        for _ in range(periods):
            result_reds, result_blue = generate_random_numbers()

            for strat_name in strategies:
                picker = self._strategy_picker(strat_name)
                for _ in range(tickets_per_period):
                    bet_reds, bet_blue = picker()
                    prize = self._judge_prize(bet_reds, bet_blue, result_reds, result_blue)
                    if prize:
                        prize_counter[strat_name][prize] += 1

        # 统计与结算（不引入真实资金变动，按配置奖金计算收益）
        total_bets = periods * tickets_per_period
        prize_levels = settings.PRIZE_LEVELS

        total_winnings = 0.0
        total_hits = 0
        prize_counts_agg = {}

        for strat_name, counter in prize_counter.items():
            prize_counts_agg[strat_name] = dict(counter)
            hits = sum(counter.values())
            total_hits += hits
            for level, cnt in counter.items():
                total_winnings += prize_levels.get(level, 0) * cnt

        total_spent = total_bets * settings.MIN_BET_AMOUNT
        roi = (total_winnings - total_spent) / total_spent if total_spent > 0 else 0.0

        session.total_bets = total_bets
        session.total_hits = total_hits
        session.total_spent = total_spent
        session.total_winnings = total_winnings
        session.roi = roi
        session.prize_counts = prize_counts_agg
        session.summary = {
            "periods": periods,
            "tickets_per_period": tickets_per_period,
            "strategies": strategies,
            "prize_counts": prize_counts_agg,
            "total_hits": total_hits,
            "hit_rate": total_hits / total_bets if total_bets > 0 else 0.0,
            "roi": roi,
        }
        session.finished_at = datetime.utcnow()

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session