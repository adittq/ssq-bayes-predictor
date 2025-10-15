from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, BacktestSession
from app.services.backtest_service import BacktestService
from app.utils.response import success_response, error_response

router = APIRouter()


@router.post("/simulate")
def run_backtest(
    strategies: List[str],
    periods: int,
    tickets_per_period: int = 1,
    seed: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not strategies:
            raise HTTPException(status_code=400, detail="请至少提供一个策略")
        service = BacktestService(db)
        session = service.run_simulation(current_user, name, strategies, periods, tickets_per_period, seed)
        return success_response(
            data={"session": session.to_dict()},
            message="回测完成",
            code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"回测失败: {str(e)}")