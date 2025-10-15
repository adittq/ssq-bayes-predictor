"""
数据分析服务
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import json

from app.models.lottery import LotteryDraw
from app.models.analysis import AnalysisResult, UserAnalysis
from app.core.config import settings


class AnalysisService:
    """数据分析服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_historical_data(self, limit: int = 200) -> pd.DataFrame:
        """获取历史开奖数据"""
        draws = self.db.query(LotteryDraw).order_by(desc(LotteryDraw.draw_date)).limit(limit).all()
        
        data = []
        for draw in draws:
            data.append({
                'period': draw.period,
                'draw_date': draw.draw_date,
                'red_balls': draw.red_balls,
                'blue_ball': draw.blue_ball,
                'red_1': draw.red_balls[0] if len(draw.red_balls) > 0 else 0,
                'red_2': draw.red_balls[1] if len(draw.red_balls) > 1 else 0,
                'red_3': draw.red_balls[2] if len(draw.red_balls) > 2 else 0,
                'red_4': draw.red_balls[3] if len(draw.red_balls) > 3 else 0,
                'red_5': draw.red_balls[4] if len(draw.red_balls) > 4 else 0,
                'red_6': draw.red_balls[5] if len(draw.red_balls) > 5 else 0,
                'blue_ball': draw.blue_ball
            })
        
        return pd.DataFrame(data)
    
    def frequency_analysis(self, periods: int = 100) -> Dict[str, Any]:
        """频率分析"""
        df = self.get_historical_data(periods)
        
        if df.empty:
            return {"error": "没有足够的历史数据"}
        
        # 红球频率统计
        red_frequency = defaultdict(int)
        blue_frequency = defaultdict(int)
        
        for _, row in df.iterrows():
            for ball in row['red_balls']:
                red_frequency[ball] += 1
            blue_frequency[row['blue_ball']] += 1
        
        # 计算出现频率
        total_draws = len(df)
        red_freq_percent = {ball: (count / total_draws / 6) * 100 for ball, count in red_frequency.items()}
        blue_freq_percent = {ball: (count / total_draws) * 100 for ball, count in blue_frequency.items()}
        
        # 排序
        red_hot = sorted(red_freq_percent.items(), key=lambda x: x[1], reverse=True)[:10]
        red_cold = sorted(red_freq_percent.items(), key=lambda x: x[1])[:10]
        blue_hot = sorted(blue_freq_percent.items(), key=lambda x: x[1], reverse=True)[:5]
        blue_cold = sorted(blue_freq_percent.items(), key=lambda x: x[1])[:5]
        
        # 生成推荐号码
        recommended_red = [ball for ball, _ in red_hot[:6]]
        recommended_blue = blue_hot[0][0] if blue_hot else 1
        
        analysis_result = {
            "analysis_type": "frequency",
            "periods_analyzed": total_draws,
            "red_ball_frequency": dict(red_freq_percent),
            "blue_ball_frequency": dict(blue_freq_percent),
            "hot_red_balls": red_hot,
            "cold_red_balls": red_cold,
            "hot_blue_balls": blue_hot,
            "cold_blue_balls": blue_cold,
            "recommended_numbers": {
                "red_balls": recommended_red,
                "blue_ball": recommended_blue,
                "confidence": 0.6
            },
            "analysis_summary": f"基于最近{total_draws}期数据的频率分析，热门红球前6位推荐"
        }
        
        # 保存分析结果
        self._save_analysis_result("frequency", "频率分析", analysis_result)
        
        return analysis_result
    
    def markov_analysis(self, order: int = 2, periods: int = 150) -> Dict[str, Any]:
        """马尔可夫链分析"""
        df = self.get_historical_data(periods)
        
        if len(df) < order + 10:
            return {"error": "历史数据不足以进行马尔可夫分析"}
        
        # 构建状态转移矩阵
        red_transitions = defaultdict(lambda: defaultdict(int))
        blue_transitions = defaultdict(lambda: defaultdict(int))
        
        # 红球马尔可夫链
        for i in range(len(df) - order):
            # 当前状态：前order期的红球组合
            current_state = tuple(sorted(df.iloc[i:i+order]['red_balls'].apply(tuple).tolist()))
            # 下一状态：下一期的红球
            next_balls = tuple(sorted(df.iloc[i+order]['red_balls']))
            
            red_transitions[current_state][next_balls] += 1
        
        # 蓝球马尔可夫链
        for i in range(len(df) - order):
            current_state = tuple(df.iloc[i:i+order]['blue_ball'].tolist())
            next_ball = df.iloc[i+order]['blue_ball']
            
            blue_transitions[current_state][next_ball] += 1
        
        # 计算转移概率
        red_probabilities = {}
        for state, transitions in red_transitions.items():
            total = sum(transitions.values())
            red_probabilities[state] = {next_state: count/total for next_state, count in transitions.items()}
        
        blue_probabilities = {}
        for state, transitions in blue_transitions.items():
            total = sum(transitions.values())
            blue_probabilities[state] = {next_ball: count/total for next_ball, count in transitions.items()}
        
        # 预测下一期号码
        recent_red_state = tuple(sorted(df.head(order)['red_balls'].apply(tuple).tolist()))
        recent_blue_state = tuple(df.head(order)['blue_ball'].tolist())
        
        # 红球预测
        predicted_red = []
        if recent_red_state in red_probabilities:
            red_probs = red_probabilities[recent_red_state]
            if red_probs:
                best_red_combo = max(red_probs.items(), key=lambda x: x[1])
                predicted_red = list(best_red_combo[0])
        
        # 如果没有匹配的状态，使用频率分析作为备选
        if not predicted_red:
            freq_analysis = self.frequency_analysis(periods)
            if "recommended_numbers" in freq_analysis:
                predicted_red = freq_analysis["recommended_numbers"]["red_balls"]
        
        # 蓝球预测
        predicted_blue = 1
        if recent_blue_state in blue_probabilities:
            blue_probs = blue_probabilities[recent_blue_state]
            if blue_probs:
                predicted_blue = max(blue_probs.items(), key=lambda x: x[1])[0]
        
        # 计算置信度
        confidence = 0.7 if predicted_red and len(predicted_red) == 6 else 0.5
        
        analysis_result = {
            "analysis_type": "markov",
            "model_order": order,
            "periods_analyzed": len(df),
            "state_transitions_count": len(red_transitions),
            "predicted_numbers": {
                "red_balls": predicted_red[:6] if predicted_red else [],
                "blue_ball": predicted_blue,
                "confidence": confidence
            },
            "model_performance": {
                "states_captured": len(red_transitions),
                "average_transitions_per_state": np.mean([len(trans) for trans in red_transitions.values()]) if red_transitions else 0
            },
            "analysis_summary": f"基于{order}阶马尔可夫链模型分析最近{len(df)}期数据的预测结果"
        }
        
        # 保存分析结果
        self._save_analysis_result("markov", f"{order}阶马尔可夫链分析", analysis_result)
        
        return analysis_result
    
    def trend_analysis(self, periods: int = 50) -> Dict[str, Any]:
        """趋势分析"""
        df = self.get_historical_data(periods)
        
        if df.empty:
            return {"error": "没有足够的历史数据"}
        
        # 计算各种趋势指标
        trends = {
            "sum_trends": self._analyze_sum_trends(df),
            "parity_trends": self._analyze_parity_trends(df),
            "consecutive_trends": self._analyze_consecutive_trends(df),
            "zone_trends": self._analyze_zone_trends(df)
        }
        
        # 基于趋势生成推荐
        recommendations = self._generate_trend_recommendations(trends, df)
        
        analysis_result = {
            "analysis_type": "trend",
            "periods_analyzed": len(df),
            "trends": trends,
            "recommended_numbers": recommendations,
            "analysis_summary": f"基于最近{len(df)}期数据的趋势分析，综合考虑和值、奇偶、连号等因素"
        }
        
        # 保存分析结果
        self._save_analysis_result("trend", "趋势分析", analysis_result)
        
        return analysis_result
    
    def _analyze_sum_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析和值趋势"""
        sums = [sum(row['red_balls']) for _, row in df.iterrows()]
        
        return {
            "recent_sums": sums[:10],
            "average_sum": np.mean(sums),
            "sum_range": [min(sums), max(sums)],
            "trend_direction": "上升" if sums[0] > np.mean(sums[-10:]) else "下降"
        }
    
    def _analyze_parity_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析奇偶趋势"""
        parity_patterns = []
        for _, row in df.iterrows():
            odd_count = sum(1 for ball in row['red_balls'] if ball % 2 == 1)
            even_count = 6 - odd_count
            parity_patterns.append({"odd": odd_count, "even": even_count})
        
        recent_odd_avg = np.mean([p["odd"] for p in parity_patterns[:10]])
        
        return {
            "recent_patterns": parity_patterns[:10],
            "average_odd_count": recent_odd_avg,
            "recommended_odd_count": round(recent_odd_avg)
        }
    
    def _analyze_consecutive_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析连号趋势"""
        consecutive_counts = []
        for _, row in df.iterrows():
            balls = sorted(row['red_balls'])
            consecutive = 0
            for i in range(len(balls) - 1):
                if balls[i+1] - balls[i] == 1:
                    consecutive += 1
            consecutive_counts.append(consecutive)
        
        return {
            "recent_consecutive": consecutive_counts[:10],
            "average_consecutive": np.mean(consecutive_counts),
            "has_consecutive_trend": np.mean(consecutive_counts[:5]) > np.mean(consecutive_counts)
        }
    
    def _analyze_zone_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析区间趋势"""
        zone_distributions = []
        for _, row in df.iterrows():
            zones = {"zone1": 0, "zone2": 0, "zone3": 0}  # 1-11, 12-22, 23-33
            for ball in row['red_balls']:
                if ball <= 11:
                    zones["zone1"] += 1
                elif ball <= 22:
                    zones["zone2"] += 1
                else:
                    zones["zone3"] += 1
            zone_distributions.append(zones)
        
        avg_zones = {
            "zone1": np.mean([z["zone1"] for z in zone_distributions[:10]]),
            "zone2": np.mean([z["zone2"] for z in zone_distributions[:10]]),
            "zone3": np.mean([z["zone3"] for z in zone_distributions[:10]])
        }
        
        return {
            "recent_distributions": zone_distributions[:10],
            "average_distribution": avg_zones,
            "balanced_zones": abs(avg_zones["zone1"] - avg_zones["zone2"]) < 1 and abs(avg_zones["zone2"] - avg_zones["zone3"]) < 1
        }
    
    def _generate_trend_recommendations(self, trends: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """基于趋势生成推荐号码"""
        # 获取频率分析作为基础
        freq_analysis = self.frequency_analysis(len(df))
        base_red = freq_analysis.get("recommended_numbers", {}).get("red_balls", list(range(1, 7)))
        
        # 根据趋势调整推荐
        recommended_red = []
        
        # 考虑奇偶比例
        target_odd = trends["parity_trends"]["recommended_odd_count"]
        
        # 从热门号码中选择，保持奇偶平衡
        hot_balls = [ball for ball, _ in freq_analysis.get("hot_red_balls", [])]
        odd_balls = [ball for ball in hot_balls if ball % 2 == 1]
        even_balls = [ball for ball in hot_balls if ball % 2 == 0]
        
        # 选择奇数球
        recommended_red.extend(odd_balls[:target_odd])
        # 选择偶数球
        recommended_red.extend(even_balls[:6-target_odd])
        
        # 如果数量不够，补充其他号码
        while len(recommended_red) < 6:
            for ball in range(1, 34):
                if ball not in recommended_red:
                    recommended_red.append(ball)
                    if len(recommended_red) == 6:
                        break
        
        return {
            "red_balls": sorted(recommended_red[:6]),
            "blue_ball": freq_analysis.get("recommended_numbers", {}).get("blue_ball", 1),
            "confidence": 0.65,
            "strategy": "趋势综合分析"
        }
    
    def pattern_analysis(self, periods: int = 100) -> Dict[str, Any]:
        """模式分析"""
        df = self.get_historical_data(periods)
        
        if df.empty:
            return {"error": "没有足够的历史数据"}
        
        patterns = {
            "ac_values": self._analyze_ac_values(df),
            "span_values": self._analyze_span_values(df),
            "prime_composite": self._analyze_prime_composite(df)
        }
        
        analysis_result = {
            "analysis_type": "pattern",
            "periods_analyzed": len(df),
            "patterns": patterns,
            "analysis_summary": f"基于最近{len(df)}期数据的模式分析"
        }
        
        # 保存分析结果
        self._save_analysis_result("pattern", "模式分析", analysis_result)
        
        return analysis_result
    
    def _analyze_ac_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析AC值（算术复杂性）"""
        ac_values = []
        for _, row in df.iterrows():
            balls = sorted(row['red_balls'])
            differences = []
            for i in range(len(balls)):
                for j in range(i+1, len(balls)):
                    differences.append(abs(balls[i] - balls[j]))
            ac_value = len(set(differences)) - 1
            ac_values.append(ac_value)
        
        return {
            "recent_ac_values": ac_values[:10],
            "average_ac": np.mean(ac_values),
            "ac_range": [min(ac_values), max(ac_values)]
        }
    
    def _analyze_span_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析跨度值"""
        spans = []
        for _, row in df.iterrows():
            balls = sorted(row['red_balls'])
            span = balls[-1] - balls[0]
            spans.append(span)
        
        return {
            "recent_spans": spans[:10],
            "average_span": np.mean(spans),
            "span_range": [min(spans), max(spans)]
        }
    
    def _analyze_prime_composite(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析质数合数分布"""
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
        
        prime_counts = []
        for _, row in df.iterrows():
            prime_count = sum(1 for ball in row['red_balls'] if ball in primes)
            prime_counts.append(prime_count)
        
        return {
            "recent_prime_counts": prime_counts[:10],
            "average_prime_count": np.mean(prime_counts),
            "recommended_prime_count": round(np.mean(prime_counts[:5]))
        }
    
    def comprehensive_analysis(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """综合分析"""
        # 执行各种分析
        freq_result = self.frequency_analysis()
        markov_result = self.markov_analysis()
        trend_result = self.trend_analysis()
        
        # 综合推荐
        all_recommendations = []
        
        if "recommended_numbers" in freq_result:
            all_recommendations.append({
                "method": "频率分析",
                "red_balls": freq_result["recommended_numbers"]["red_balls"],
                "blue_ball": freq_result["recommended_numbers"]["blue_ball"],
                "confidence": freq_result["recommended_numbers"]["confidence"]
            })
        
        if "predicted_numbers" in markov_result:
            all_recommendations.append({
                "method": "马尔可夫分析",
                "red_balls": markov_result["predicted_numbers"]["red_balls"],
                "blue_ball": markov_result["predicted_numbers"]["blue_ball"],
                "confidence": markov_result["predicted_numbers"]["confidence"]
            })
        
        if "recommended_numbers" in trend_result:
            all_recommendations.append({
                "method": "趋势分析",
                "red_balls": trend_result["recommended_numbers"]["red_balls"],
                "blue_ball": trend_result["recommended_numbers"]["blue_ball"],
                "confidence": trend_result["recommended_numbers"]["confidence"]
            })
        
        # 计算综合推荐
        final_recommendation = self._calculate_ensemble_recommendation(all_recommendations)
        
        analysis_result = {
            "analysis_type": "comprehensive",
            "individual_analyses": {
                "frequency": freq_result,
                "markov": markov_result,
                "trend": trend_result
            },
            "all_recommendations": all_recommendations,
            "final_recommendation": final_recommendation,
            "analysis_summary": "综合多种分析方法的推荐结果"
        }
        
        # 保存分析结果
        result_id = self._save_analysis_result("comprehensive", "综合分析", analysis_result)
        
        # 如果有用户ID，保存用户分析记录
        if user_id and result_id:
            self._save_user_analysis(user_id, result_id, "综合分析推荐", "多模型综合分析结果")
        
        return analysis_result
    
    def _calculate_ensemble_recommendation(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算集成推荐"""
        if not recommendations:
            return {"red_balls": list(range(1, 7)), "blue_ball": 1, "confidence": 0.3}
        
        # 红球投票
        red_votes = defaultdict(float)
        blue_votes = defaultdict(float)
        
        for rec in recommendations:
            confidence = rec.get("confidence", 0.5)
            for ball in rec.get("red_balls", []):
                red_votes[ball] += confidence
            
            blue_ball = rec.get("blue_ball", 1)
            blue_votes[blue_ball] += confidence
        
        # 选择得票最高的红球
        top_red_balls = sorted(red_votes.items(), key=lambda x: x[1], reverse=True)[:6]
        final_red = [ball for ball, _ in top_red_balls]
        
        # 选择得票最高的蓝球
        final_blue = max(blue_votes.items(), key=lambda x: x[1])[0] if blue_votes else 1
        
        # 计算平均置信度
        avg_confidence = np.mean([rec.get("confidence", 0.5) for rec in recommendations])
        
        return {
            "red_balls": sorted(final_red),
            "blue_ball": final_blue,
            "confidence": min(avg_confidence * 1.1, 0.9),  # 集成方法稍微提高置信度
            "method": "集成学习"
        }
    
    def _save_analysis_result(self, analysis_type: str, model_name: str, result_data: Dict[str, Any]) -> Optional[int]:
        """保存分析结果"""
        try:
            analysis_result = AnalysisResult(
                analysis_type=analysis_type,
                model_name=model_name,
                parameters=json.dumps({"periods": result_data.get("periods_analyzed", 100)}),
                result_data=json.dumps(result_data),
                summary=result_data.get("analysis_summary", ""),
                accuracy=result_data.get("recommended_numbers", {}).get("confidence", 0.5),
                execution_time=1.0,  # 模拟执行时间
                data_size=result_data.get("periods_analyzed", 100),
                created_at=datetime.utcnow()
            )
            
            self.db.add(analysis_result)
            self.db.commit()
            self.db.refresh(analysis_result)
            
            return analysis_result.id
        except Exception as e:
            self.db.rollback()
            print(f"保存分析结果失败: {e}")
            return None
    
    def _save_user_analysis(self, user_id: int, analysis_result_id: int, title: str, description: str):
        """保存用户分析记录"""
        try:
            user_analysis = UserAnalysis(
                user_id=user_id,
                analysis_result_id=analysis_result_id,
                title=title,
                description=description,
                tags=["推荐", "综合分析"],
                is_favorite=False,
                is_shared=False,
                view_count=1,
                created_at=datetime.utcnow()
            )
            
            self.db.add(user_analysis)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"保存用户分析记录失败: {e}")
    
    def get_user_analysis_history(self, user_id: int, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取用户分析历史"""
        query = self.db.query(UserAnalysis).filter(UserAnalysis.user_id == user_id)
        
        total = query.count()
        analyses = query.order_by(desc(UserAnalysis.created_at)).offset((page - 1) * size).limit(size).all()
        
        return {
            "analyses": [analysis.to_dict() for analysis in analyses],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }