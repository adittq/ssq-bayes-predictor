"""
推荐服务模块
提供各种彩票号码推荐算法
"""
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import Counter, defaultdict

from app.models.lottery import LotteryDraw
from app.utils.lottery import generate_random_numbers, get_lottery_statistics


class RecommendationService:
    """推荐服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recommendations(self, model_type: str = "frequency", count: int = 5, user_id: int = None) -> List[Dict[str, Any]]:
        """
        获取推荐号码
        
        Args:
            model_type: 推荐模型类型
            count: 推荐数量
            user_id: 用户ID（可选）
        
        Returns:
            List[Dict[str, Any]]: 推荐结果列表
        """
        recommendations = []
        
        if model_type == "frequency":
            result = self.get_frequency_recommendations()
            recommendations = result.get("recommendations", [])
        elif model_type == "markov":
            result = self.get_markov_recommendations()
            recommendations = result.get("recommendations", [])
        elif model_type == "trend":
            result = self.get_trend_recommendations()
            recommendations = result.get("recommendations", [])
        elif model_type == "hot_cold":
            result = self.get_pattern_recommendations()
            recommendations = result.get("recommendations", [])
        elif model_type == "neural":
            # 暂时使用频率推荐作为替代
            result = self.get_frequency_recommendations()
            recommendations = result.get("recommendations", [])
        elif model_type == "ensemble":
            result = self.get_comprehensive_recommendations()
            recommendations = result.get("recommendations", [])
        else:
            # 默认使用频率推荐
            result = self.get_frequency_recommendations()
            recommendations = result.get("recommendations", [])
        
        # 限制返回数量
        return recommendations[:count]
    
    def get_frequency_recommendations(self, periods: int = 30) -> Dict[str, Any]:
        """
        基于频率分析的推荐
        
        Args:
            periods: 分析期数
        
        Returns:
            Dict[str, Any]: 推荐结果
        """
        stats = get_lottery_statistics(self.db, periods)
        
        # 获取热号和冷号
        hot_red = stats.get("hot_red_balls", [])[:6]
        cold_red = stats.get("cold_red_balls", [])[:6]
        hot_blue = stats.get("hot_blue_balls", [])[:3]
        cold_blue = stats.get("cold_blue_balls", [])[:3]
        
        # 生成推荐号码
        recommendations = []
        
        # 热号推荐
        if len(hot_red) >= 6:
            hot_recommendation = {
                "type": "热号推荐",
                "red_balls": hot_red[:6],
                "blue_ball": hot_blue[0] if hot_blue else random.randint(1, 16),
                "confidence": 0.7,
                "description": f"基于最近{periods}期的热门号码"
            }
            recommendations.append(hot_recommendation)
        
        # 冷号推荐
        if len(cold_red) >= 6:
            cold_recommendation = {
                "type": "冷号推荐", 
                "red_balls": cold_red[:6],
                "blue_ball": cold_blue[0] if cold_blue else random.randint(1, 16),
                "confidence": 0.6,
                "description": f"基于最近{periods}期的冷门号码"
            }
            recommendations.append(cold_recommendation)
        
        # 均衡推荐（热号+冷号）
        if len(hot_red) >= 3 and len(cold_red) >= 3:
            balanced_red = hot_red[:3] + cold_red[:3]
            balanced_recommendation = {
                "type": "均衡推荐",
                "red_balls": sorted(balanced_red),
                "blue_ball": hot_blue[0] if hot_blue else random.randint(1, 16),
                "confidence": 0.8,
                "description": "热号与冷号的均衡组合"
            }
            recommendations.append(balanced_recommendation)
        
        return {
            "recommendations": recommendations,
            "analysis_period": periods,
            "statistics": stats
        }
    
    def get_markov_recommendations(self, periods: int = 50) -> Dict[str, Any]:
        """
        基于马尔可夫链的推荐
        
        Args:
            periods: 分析期数
        
        Returns:
            Dict[str, Any]: 推荐结果
        """
        # 获取历史数据
        draws = self.db.query(LotteryDraw).order_by(
            LotteryDraw.period_number.desc()
        ).limit(periods).all()
        
        if len(draws) < 10:
            # 数据不足，返回随机推荐
            red_balls, blue_ball = generate_random_numbers()
            return {
                "recommendations": [{
                    "type": "随机推荐",
                    "red_balls": red_balls,
                    "blue_ball": blue_ball,
                    "confidence": 0.5,
                    "description": "历史数据不足，使用随机推荐"
                }],
                "analysis_period": len(draws)
            }
        
        # 构建转移矩阵
        red_transitions = defaultdict(lambda: defaultdict(int))
        blue_transitions = defaultdict(int)
        
        for i in range(len(draws) - 1):
            current_red = set(draws[i].red_balls)
            next_red = set(draws[i + 1].red_balls)
            current_blue = draws[i].blue_ball
            next_blue = draws[i + 1].blue_ball
            
            # 红球转移
            for ball in current_red:
                for next_ball in next_red:
                    red_transitions[ball][next_ball] += 1
            
            # 蓝球转移
            blue_transitions[next_blue] += 1
        
        # 生成推荐
        recommendations = []
        
        # 基于最近一期预测下一期
        if draws:
            last_draw = draws[0]
            predicted_red = []
            
            # 预测红球
            for ball in last_draw.red_balls:
                if ball in red_transitions:
                    transitions = red_transitions[ball]
                    if transitions:
                        # 选择转移概率最高的球
                        next_ball = max(transitions.items(), key=lambda x: x[1])[0]
                        if next_ball not in predicted_red and len(predicted_red) < 6:
                            predicted_red.append(next_ball)
            
            # 如果预测的红球不足6个，随机补充
            while len(predicted_red) < 6:
                ball = random.randint(1, 33)
                if ball not in predicted_red:
                    predicted_red.append(ball)
            
            # 预测蓝球
            if blue_transitions:
                predicted_blue = max(blue_transitions.items(), key=lambda x: x[1])[0]
            else:
                predicted_blue = random.randint(1, 16)
            
            markov_recommendation = {
                "type": "马尔可夫预测",
                "red_balls": sorted(predicted_red),
                "blue_ball": predicted_blue,
                "confidence": 0.75,
                "description": f"基于{periods}期历史数据的马尔可夫链预测"
            }
            recommendations.append(markov_recommendation)
        
        return {
            "recommendations": recommendations,
            "analysis_period": len(draws),
            "transition_matrix_size": len(red_transitions)
        }
    
    def get_trend_recommendations(self, periods: int = 20) -> Dict[str, Any]:
        """
        基于趋势分析的推荐
        
        Args:
            periods: 分析期数
        
        Returns:
            Dict[str, Any]: 推荐结果
        """
        # 获取历史数据
        draws = self.db.query(LotteryDraw).order_by(
            LotteryDraw.period_number.asc()
        ).limit(periods).all()
        
        if len(draws) < 5:
            red_balls, blue_ball = generate_random_numbers()
            return {
                "recommendations": [{
                    "type": "随机推荐",
                    "red_balls": red_balls,
                    "blue_ball": blue_ball,
                    "confidence": 0.5,
                    "description": "历史数据不足，使用随机推荐"
                }],
                "analysis_period": len(draws)
            }
        
        # 分析号码出现趋势
        ball_trends = {}
        
        for ball in range(1, 34):  # 红球1-33
            appearances = []
            for i, draw in enumerate(draws):
                if ball in draw.red_balls:
                    appearances.append(i)
            
            if len(appearances) >= 2:
                # 计算出现间隔的趋势
                intervals = [appearances[i] - appearances[i-1] for i in range(1, len(appearances))]
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    last_appearance = appearances[-1]
                    expected_next = last_appearance + avg_interval
                    
                    # 计算趋势分数
                    trend_score = max(0, 1 - abs(expected_next - len(draws)) / len(draws))
                    ball_trends[ball] = trend_score
        
        # 选择趋势分数最高的6个红球
        sorted_trends = sorted(ball_trends.items(), key=lambda x: x[1], reverse=True)
        trending_red = [ball for ball, score in sorted_trends[:6]]
        
        # 如果不足6个，随机补充
        while len(trending_red) < 6:
            ball = random.randint(1, 33)
            if ball not in trending_red:
                trending_red.append(ball)
        
        # 蓝球趋势分析
        blue_trends = {}
        for ball in range(1, 17):  # 蓝球1-16
            appearances = []
            for i, draw in enumerate(draws):
                if draw.blue_ball == ball:
                    appearances.append(i)
            
            if len(appearances) >= 1:
                last_appearance = appearances[-1]
                trend_score = max(0, 1 - (len(draws) - last_appearance) / len(draws))
                blue_trends[ball] = trend_score
        
        if blue_trends:
            trending_blue = max(blue_trends.items(), key=lambda x: x[1])[0]
        else:
            trending_blue = random.randint(1, 16)
        
        recommendations = [{
            "type": "趋势预测",
            "red_balls": sorted(trending_red),
            "blue_ball": trending_blue,
            "confidence": 0.7,
            "description": f"基于{periods}期数据的号码出现趋势分析"
        }]
        
        return {
            "recommendations": recommendations,
            "analysis_period": len(draws),
            "trend_scores": dict(sorted_trends[:10])
        }
    
    def get_pattern_recommendations(self, periods: int = 30) -> Dict[str, Any]:
        """
        基于模式分析的推荐
        
        Args:
            periods: 分析期数
        
        Returns:
            Dict[str, Any]: 推荐结果
        """
        # 获取历史数据
        draws = self.db.query(LotteryDraw).order_by(
            LotteryDraw.period_number.desc()
        ).limit(periods).all()
        
        if len(draws) < 10:
            red_balls, blue_ball = generate_random_numbers()
            return {
                "recommendations": [{
                    "type": "随机推荐",
                    "red_balls": red_balls,
                    "blue_ball": blue_ball,
                    "confidence": 0.5,
                    "description": "历史数据不足，使用随机推荐"
                }],
                "analysis_period": len(draws)
            }
        
        # 分析号码分布模式
        patterns = {
            "consecutive": [],  # 连号
            "same_tail": [],    # 同尾号
            "sum_range": [],    # 和值范围
            "odd_even": []      # 奇偶比例
        }
        
        for draw in draws:
            red_balls = sorted(draw.red_balls)
            
            # 连号分析
            consecutive_count = 0
            for i in range(len(red_balls) - 1):
                if red_balls[i + 1] - red_balls[i] == 1:
                    consecutive_count += 1
            patterns["consecutive"].append(consecutive_count)
            
            # 同尾号分析
            tail_groups = defaultdict(list)
            for ball in red_balls:
                tail_groups[ball % 10].append(ball)
            same_tail_count = sum(1 for group in tail_groups.values() if len(group) > 1)
            patterns["same_tail"].append(same_tail_count)
            
            # 和值分析
            total_sum = sum(red_balls)
            patterns["sum_range"].append(total_sum)
            
            # 奇偶分析
            odd_count = sum(1 for ball in red_balls if ball % 2 == 1)
            patterns["odd_even"].append(odd_count)
        
        # 基于模式生成推荐
        recommendations = []
        
        # 模式1：基于平均连号数
        avg_consecutive = sum(patterns["consecutive"]) / len(patterns["consecutive"])
        target_consecutive = round(avg_consecutive)
        
        pattern_red = []
        if target_consecutive > 0:
            # 生成包含连号的组合
            start = random.randint(1, 33 - target_consecutive)
            for i in range(target_consecutive + 1):
                if len(pattern_red) < 6:
                    pattern_red.append(start + i)
        
        # 补充其他号码
        while len(pattern_red) < 6:
            ball = random.randint(1, 33)
            if ball not in pattern_red:
                pattern_red.append(ball)
        
        # 模式2：基于和值范围
        avg_sum = sum(patterns["sum_range"]) / len(patterns["sum_range"])
        target_sum = round(avg_sum)
        
        # 生成目标和值附近的组合
        sum_red = []
        attempts = 0
        while len(sum_red) < 6 and attempts < 100:
            ball = random.randint(1, 33)
            if ball not in sum_red:
                temp_sum = sum(sum_red) + ball
                if temp_sum <= target_sum + 20:  # 允许一定偏差
                    sum_red.append(ball)
            attempts += 1
        
        if len(sum_red) < 6:
            while len(sum_red) < 6:
                ball = random.randint(1, 33)
                if ball not in sum_red:
                    sum_red.append(ball)
        
        # 蓝球基于历史模式
        blue_counter = Counter(draw.blue_ball for draw in draws)
        most_common_blue = blue_counter.most_common(1)[0][0] if blue_counter else random.randint(1, 16)
        
        recommendations.extend([
            {
                "type": "连号模式",
                "red_balls": sorted(pattern_red),
                "blue_ball": most_common_blue,
                "confidence": 0.65,
                "description": f"基于平均{avg_consecutive:.1f}个连号的模式"
            },
            {
                "type": "和值模式",
                "red_balls": sorted(sum_red),
                "blue_ball": most_common_blue,
                "confidence": 0.65,
                "description": f"基于平均和值{avg_sum:.0f}的模式"
            }
        ])
        
        return {
            "recommendations": recommendations,
            "analysis_period": len(draws),
            "patterns": {
                "avg_consecutive": avg_consecutive,
                "avg_sum": avg_sum,
                "avg_odd_count": sum(patterns["odd_even"]) / len(patterns["odd_even"])
            }
        }
    
    def get_comprehensive_recommendations(self, periods: int = 30) -> Dict[str, Any]:
        """
        综合推荐（结合多种算法）
        
        Args:
            periods: 分析期数
        
        Returns:
            Dict[str, Any]: 综合推荐结果
        """
        # 获取各种推荐
        frequency_rec = self.get_frequency_recommendations(periods)
        markov_rec = self.get_markov_recommendations(periods)
        trend_rec = self.get_trend_recommendations(periods)
        pattern_rec = self.get_pattern_recommendations(periods)
        
        # 合并所有推荐
        all_recommendations = []
        all_recommendations.extend(frequency_rec.get("recommendations", []))
        all_recommendations.extend(markov_rec.get("recommendations", []))
        all_recommendations.extend(trend_rec.get("recommendations", []))
        all_recommendations.extend(pattern_rec.get("recommendations", []))
        
        # 按置信度排序
        all_recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        # 选择前5个推荐
        top_recommendations = all_recommendations[:5]
        
        return {
            "recommendations": top_recommendations,
            "analysis_period": periods,
            "algorithm_count": 4,
            "total_recommendations": len(all_recommendations)
        }