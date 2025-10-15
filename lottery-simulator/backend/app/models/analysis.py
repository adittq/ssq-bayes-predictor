"""
数据分析相关模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AnalysisResult(Base):
    """分析结果模型"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    model_name = Column(String(50), nullable=False, comment="模型名称")
    
    # 分析参数
    parameters = Column(JSON, nullable=True, comment="分析参数")
    
    # 分析结果
    result_data = Column(JSON, nullable=False, comment="分析结果数据")
    summary = Column(Text, nullable=True, comment="结果摘要")
    
    # 性能指标
    accuracy_score = Column(Float, nullable=True, comment="准确率")
    precision_score = Column(Float, nullable=True, comment="精确率")
    recall_score = Column(Float, nullable=True, comment="召回率")
    f1_score = Column(Float, nullable=True, comment="F1分数")
    
    # 执行信息
    execution_time = Column(Float, nullable=True, comment="执行时间(秒)")
    data_size = Column(Integer, nullable=True, comment="数据量")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user_analyses = relationship("UserAnalysis", back_populates="analysis_result")
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, type={self.analysis_type}, model={self.model_name})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "analysis_type": self.analysis_type,
            "model_name": self.model_name,
            "parameters": self.parameters,
            "result_data": self.result_data,
            "summary": self.summary,
            "accuracy_score": self.accuracy_score,
            "precision_score": self.precision_score,
            "recall_score": self.recall_score,
            "f1_score": self.f1_score,
            "execution_time": self.execution_time,
            "data_size": self.data_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class UserAnalysis(Base):
    """用户分析记录模型"""
    __tablename__ = "user_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    analysis_result_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False, comment="分析结果ID")
    
    # 用户自定义信息
    title = Column(String(100), nullable=True, comment="分析标题")
    description = Column(Text, nullable=True, comment="分析描述")
    tags = Column(String(255), nullable=True, comment="标签")
    
    # 用户评价
    user_rating = Column(Integer, nullable=True, comment="用户评分(1-5)")
    user_feedback = Column(Text, nullable=True, comment="用户反馈")
    
    # 使用情况
    view_count = Column(Integer, default=0, comment="查看次数")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    is_shared = Column(Boolean, default=False, comment="是否分享")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_viewed_at = Column(DateTime, nullable=True, comment="最后查看时间")
    
    # 关联关系
    user = relationship("User", back_populates="user_analyses")
    analysis_result = relationship("AnalysisResult", back_populates="user_analyses")
    
    def __repr__(self):
        return f"<UserAnalysis(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_result_id": self.analysis_result_id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "view_count": self.view_count,
            "is_favorite": self.is_favorite,
            "is_shared": self.is_shared,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None
        }