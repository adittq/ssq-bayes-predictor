"""
数据分析和推荐系统API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService
from app.models.user import User
from app.utils.response import success_response, error_response

router = APIRouter()


@router.get("/recommendations", summary="获取号码推荐")
async def get_recommendations(
    model_type: str = Query("markov", description="推荐模型类型: markov, frequency, trend, hot_cold"),
    count: int = Query(5, description="推荐数量", ge=1, le=10),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取基于不同模型的号码推荐
    """
    try:
        recommendation_service = RecommendationService(db)
        
        # 验证模型类型
        valid_models = ["markov", "frequency", "trend", "hot_cold", "neural", "ensemble"]
        if model_type not in valid_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的模型类型，支持的类型: {', '.join(valid_models)}"
            )
        
        # 获取推荐
        recommendations = recommendation_service.get_recommendations(
            model_type=model_type,
            count=count,
            user_id=current_user.id
        )
        
        return success_response(
            data={
                "model_type": model_type,
                "recommendations": recommendations,
                "count": len(recommendations)
            },
            message="获取推荐成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取推荐失败: {str(e)}")


@router.get("/markov-analysis", summary="马尔可夫链分析")
async def markov_analysis(
    order: int = Query(2, description="马尔可夫链阶数", ge=1, le=5),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    马尔可夫链分析
    """
    try:
        analysis_service = AnalysisService(db)
        markov_result = analysis_service.markov_chain_analysis(order=order)
        
        return success_response(
            data=markov_result,
            message="马尔可夫链分析完成"
        )
        
    except Exception as e:
        return error_response(message=f"马尔可夫链分析失败: {str(e)}")


@router.get("/frequency-analysis", summary="频率分析")
async def frequency_analysis(
    period_count: int = Query(100, description="分析期数", ge=10, le=1000),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    号码频率分析
    """
    try:
        analysis_service = AnalysisService(db)
        frequency_result = analysis_service.frequency_analysis(period_count=period_count)
        
        return success_response(
            data=frequency_result,
            message="频率分析完成"
        )
        
    except Exception as e:
        return error_response(message=f"频率分析失败: {str(e)}")


@router.get("/trend-analysis", summary="趋势分析")
async def trend_analysis(
    period_count: int = Query(50, description="分析期数", ge=10, le=500),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    号码趋势分析
    """
    try:
        analysis_service = AnalysisService(db)
        trend_result = analysis_service.trend_analysis(period_count=period_count)
        
        return success_response(
            data=trend_result,
            message="趋势分析完成"
        )
        
    except Exception as e:
        return error_response(message=f"趋势分析失败: {str(e)}")


@router.get("/hot-cold-analysis", summary="冷热号分析")
async def hot_cold_analysis(
    period_count: int = Query(30, description="分析期数", ge=10, le=200),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    冷热号分析
    """
    try:
        analysis_service = AnalysisService(db)
        hot_cold_result = analysis_service.hot_cold_analysis(period_count=period_count)
        
        return success_response(
            data=hot_cold_result,
            message="冷热号分析完成"
        )
        
    except Exception as e:
        return error_response(message=f"冷热号分析失败: {str(e)}")


@router.get("/pattern-analysis", summary="模式分析")
async def pattern_analysis(
    pattern_type: str = Query("consecutive", description="模式类型: consecutive, sum_range, odd_even"),
    period_count: int = Query(100, description="分析期数", ge=20, le=500),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    号码模式分析
    """
    try:
        analysis_service = AnalysisService(db)
        
        valid_patterns = ["consecutive", "sum_range", "odd_even", "ac_value", "span"]
        if pattern_type not in valid_patterns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的模式类型，支持的类型: {', '.join(valid_patterns)}"
            )
        
        pattern_result = analysis_service.pattern_analysis(
            pattern_type=pattern_type,
            period_count=period_count
        )
        
        return success_response(
            data=pattern_result,
            message="模式分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"模式分析失败: {str(e)}")


@router.get("/correlation-analysis", summary="相关性分析")
async def correlation_analysis(
    period_count: int = Query(200, description="分析期数", ge=50, le=1000),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    号码相关性分析
    """
    try:
        analysis_service = AnalysisService(db)
        correlation_result = analysis_service.correlation_analysis(period_count=period_count)
        
        return success_response(
            data=correlation_result,
            message="相关性分析完成"
        )
        
    except Exception as e:
        return error_response(message=f"相关性分析失败: {str(e)}")


@router.get("/prediction-accuracy", summary="预测准确率")
async def prediction_accuracy(
    model_type: str = Query("markov", description="模型类型"),
    test_periods: int = Query(10, description="测试期数", ge=5, le=50),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取模型预测准确率
    """
    try:
        analysis_service = AnalysisService(db)
        accuracy_result = analysis_service.calculate_prediction_accuracy(
            model_type=model_type,
            test_periods=test_periods
        )
        
        return success_response(
            data=accuracy_result,
            message="预测准确率计算完成"
        )
        
    except Exception as e:
        return error_response(message=f"预测准确率计算失败: {str(e)}")


@router.get("/model-comparison", summary="模型对比")
async def model_comparison(
    test_periods: int = Query(20, description="测试期数", ge=10, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    多个模型的对比分析
    """
    try:
        analysis_service = AnalysisService(db)
        comparison_result = analysis_service.compare_models(test_periods=test_periods)
        
        return success_response(
            data=comparison_result,
            message="模型对比完成"
        )
        
    except Exception as e:
        return error_response(message=f"模型对比失败: {str(e)}")


@router.post("/custom-analysis", summary="自定义分析")
async def custom_analysis(
    analysis_config: Dict[str, Any],
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    自定义分析配置
    """
    try:
        analysis_service = AnalysisService(db)
        
        # 验证分析配置
        required_fields = ["analysis_type", "parameters"]
        for field in required_fields:
            if field not in analysis_config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少必需字段: {field}"
                )
        
        custom_result = analysis_service.custom_analysis(
            config=analysis_config,
            user_id=current_user.id
        )
        
        return success_response(
            data=custom_result,
            message="自定义分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"自定义分析失败: {str(e)}")


@router.get("/statistics", summary="分析统计")
async def analysis_statistics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取分析统计信息
    """
    try:
        analysis_service = AnalysisService(db)
        stats = analysis_service.get_analysis_statistics()
        
        return success_response(
            data=stats,
            message="获取分析统计成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取分析统计失败: {str(e)}")


@router.post("/save-analysis", summary="保存分析结果")
async def save_analysis(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    保存用户的分析结果
    """
    try:
        analysis_service = AnalysisService(db)
        
        saved_analysis = analysis_service.save_user_analysis(
            user_id=current_user.id,
            analysis_data=analysis_data
        )
        
        return success_response(
            data={"analysis_id": saved_analysis.id},
            message="分析结果保存成功"
        )
        
    except Exception as e:
        return error_response(message=f"保存分析结果失败: {str(e)}")


@router.get("/my-analyses", summary="我的分析记录")
async def get_my_analyses(
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=50),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户的分析记录
    """
    try:
        analysis_service = AnalysisService(db)
        analyses = analysis_service.get_user_analyses(
            user_id=current_user.id,
            page=page,
            size=size
        )
        
        return success_response(
            data=analyses,
            message="获取分析记录成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取分析记录失败: {str(e)}")