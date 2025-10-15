"""
数据分析相关的 Pydantic 模型
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator


class AnalysisRequest(BaseModel):
    """分析请求"""
    analysis_type: str
    periods: int = 100
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['frequency', 'markov', 'trend', 'pattern', 'comprehensive']
        if v not in valid_types:
            raise ValueError(f'分析类型必须是 {", ".join(valid_types)} 之一')
        return v
    
    @validator('periods')
    def validate_periods(cls, v):
        if not (10 <= v <= 500):
            raise ValueError('分析期数必须在10-500之间')
        return v


class RecommendedNumbers(BaseModel):
    """推荐号码"""
    red_balls: List[int]
    blue_ball: int
    confidence: float
    method: Optional[str] = None
    strategy: Optional[str] = None


class FrequencyAnalysisResult(BaseModel):
    """频率分析结果"""
    analysis_type: str
    periods_analyzed: int
    red_ball_frequency: Dict[int, float]
    blue_ball_frequency: Dict[int, float]
    hot_red_balls: List[tuple]
    cold_red_balls: List[tuple]
    hot_blue_balls: List[tuple]
    cold_blue_balls: List[tuple]
    recommended_numbers: RecommendedNumbers
    analysis_summary: str


class MarkovAnalysisResult(BaseModel):
    """马尔可夫分析结果"""
    analysis_type: str
    model_order: int
    periods_analyzed: int
    state_transitions_count: int
    predicted_numbers: RecommendedNumbers
    model_performance: Dict[str, Any]
    analysis_summary: str


class TrendAnalysisResult(BaseModel):
    """趋势分析结果"""
    analysis_type: str
    periods_analyzed: int
    trends: Dict[str, Any]
    recommended_numbers: RecommendedNumbers
    analysis_summary: str


class PatternAnalysisResult(BaseModel):
    """模式分析结果"""
    analysis_type: str
    periods_analyzed: int
    patterns: Dict[str, Any]
    analysis_summary: str


class ComprehensiveAnalysisResult(BaseModel):
    """综合分析结果"""
    analysis_type: str
    individual_analyses: Dict[str, Any]
    all_recommendations: List[Dict[str, Any]]
    final_recommendation: RecommendedNumbers
    analysis_summary: str


class AnalysisResultRecord(BaseModel):
    """分析结果记录"""
    id: int
    analysis_type: str
    model_name: str
    parameters: str
    result_data: str
    summary: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    execution_time: float
    data_size: int
    created_at: str
    
    class Config:
        from_attributes = True


class UserAnalysisRecord(BaseModel):
    """用户分析记录"""
    id: int
    analysis_result_id: int
    title: str
    description: str
    tags: List[str]
    user_rating: Optional[float] = None
    user_feedback: Optional[str] = None
    view_count: int
    is_favorite: bool
    is_shared: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UserAnalysisListResponse(BaseModel):
    """用户分析记录列表响应"""
    analyses: List[UserAnalysisRecord]
    total: int
    page: int
    size: int
    pages: int


class MarkovRequest(BaseModel):
    """马尔可夫分析请求"""
    order: int = 2
    periods: int = 150
    
    @validator('order')
    def validate_order(cls, v):
        if not (1 <= v <= 5):
            raise ValueError('马尔可夫阶数必须在1-5之间')
        return v


class TrendRequest(BaseModel):
    """趋势分析请求"""
    periods: int = 50
    
    @validator('periods')
    def validate_periods(cls, v):
        if not (20 <= v <= 200):
            raise ValueError('趋势分析期数必须在20-200之间')
        return v


class PatternRequest(BaseModel):
    """模式分析请求"""
    periods: int = 100
    
    @validator('periods')
    def validate_periods(cls, v):
        if not (30 <= v <= 300):
            raise ValueError('模式分析期数必须在30-300之间')
        return v