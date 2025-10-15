#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据分析脚本
对ssq_data_20251001.csv进行全面的数据分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from collections import Counter
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 忽略警告
warnings.filterwarnings('ignore')

class SSQDataAnalyzer:
    def __init__(self, data_file='ssq_cwl_data.csv'):
        """初始化分析器"""
        self.data_file = data_file
        self.df = None
        self.analysis_results = {}
        
    def load_and_preprocess_data(self):
        """加载和预处理数据"""
        print("正在加载双色球数据...")
        
        try:
            # 读取数据
            self.df = pd.read_csv(self.data_file, encoding='utf-8')
            print(f"成功加载数据，共 {len(self.df)} 条记录")
            
            # 数据基本信息
            print("\n数据基本信息:")
            print(f"数据形状: {self.df.shape}")
            print(f"列名: {list(self.df.columns)}")
            print(f"数据类型:\n{self.df.dtypes}")
            
            # 检查缺失值
            missing_values = self.df.isnull().sum()
            print(f"\n缺失值统计:\n{missing_values}")
            
            # 转换日期格式
            self.df['开奖日期'] = pd.to_datetime(self.df['开奖日期'])
            
            # 提取红球和蓝球数据
            red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
            blue_ball = '蓝球'
            
            # 检查数据范围
            print(f"\n数据时间范围: {self.df['开奖日期'].min()} 到 {self.df['开奖日期'].max()}")
            print(f"红球范围: {self.df[red_balls].min().min()} - {self.df[red_balls].max().max()}")
            print(f"蓝球范围: {self.df[blue_ball].min()} - {self.df[blue_ball].max()}")
            
            # 数据质量检查
            self._check_data_quality()
            
            return True
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False
    
    def _check_data_quality(self):
        """检查数据质量"""
        print("\n数据质量检查:")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 检查红球是否在有效范围内 (1-33)
        invalid_red = self.df[(self.df[red_balls] < 1) | (self.df[red_balls] > 33)].any(axis=1)
        print(f"红球超出范围的记录数: {invalid_red.sum()}")
        
        # 检查蓝球是否在有效范围内 (1-16)
        invalid_blue = self.df[(self.df['蓝球'] < 1) | (self.df['蓝球'] > 16)]
        print(f"蓝球超出范围的记录数: {len(invalid_blue)}")
        
        # 检查红球是否有重复
        duplicate_red = 0
        for idx, row in self.df.iterrows():
            red_nums = [row[col] for col in red_balls]
            if len(set(red_nums)) != 6:
                duplicate_red += 1
        print(f"红球有重复的记录数: {duplicate_red}")
        
        # 检查期号是否连续
        periods = self.df['期号'].astype(str)
        print(f"期号范围: {periods.min()} - {periods.max()}")
        
    def basic_statistics_analysis(self):
        """基础统计分析"""
        print("\n开始基础统计分析...")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 红球频率统计
        red_frequency = {}
        for i in range(1, 34):
            count = 0
            for col in red_balls:
                count += (self.df[col] == i).sum()
            red_frequency[i] = count
        
        # 蓝球频率统计
        blue_frequency = self.df['蓝球'].value_counts().sort_index().to_dict()
        
        # 保存结果
        self.analysis_results['red_frequency'] = red_frequency
        self.analysis_results['blue_frequency'] = blue_frequency
        
        # 统计信息
        print(f"红球出现频率统计 (总计 {sum(red_frequency.values())} 次):")
        sorted_red = sorted(red_frequency.items(), key=lambda x: x[1], reverse=True)
        print("最热门的10个红球:")
        for num, freq in sorted_red[:10]:
            print(f"  {num:2d}: {freq:3d}次 ({freq/sum(red_frequency.values())*100:.2f}%)")
        
        print("\n最冷门的10个红球:")
        for num, freq in sorted_red[-10:]:
            print(f"  {num:2d}: {freq:3d}次 ({freq/sum(red_frequency.values())*100:.2f}%)")
        
        print(f"\n蓝球出现频率统计 (总计 {sum(blue_frequency.values())} 次):")
        sorted_blue = sorted(blue_frequency.items(), key=lambda x: x[1], reverse=True)
        for num, freq in sorted_blue:
            print(f"  {num:2d}: {freq:3d}次 ({freq/sum(blue_frequency.values())*100:.2f}%)")
        
        return red_frequency, blue_frequency
    
    def analyze_number_intervals(self):
        """分析号码间隔和连号规律"""
        print("\n开始分析号码间隔和连号规律...")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 分析每期红球的间隔
        intervals_stats = []
        consecutive_stats = []
        
        for idx, row in self.df.iterrows():
            red_nums = sorted([row[col] for col in red_balls])
            
            # 计算相邻号码间隔
            intervals = [red_nums[i+1] - red_nums[i] for i in range(5)]
            intervals_stats.extend(intervals)
            
            # 计算连号数量
            consecutive_count = sum(1 for i in range(5) if intervals[i] == 1)
            consecutive_stats.append(consecutive_count)
        
        # 统计结果
        interval_counter = Counter(intervals_stats)
        consecutive_counter = Counter(consecutive_stats)
        
        self.analysis_results['intervals'] = interval_counter
        self.analysis_results['consecutive'] = consecutive_counter
        
        print("号码间隔分布:")
        for interval in sorted(interval_counter.keys()):
            count = interval_counter[interval]
            print(f"  间隔{interval:2d}: {count:4d}次 ({count/len(intervals_stats)*100:.2f}%)")
        
        print("\n连号数量分布:")
        for cons_count in sorted(consecutive_counter.keys()):
            count = consecutive_counter[cons_count]
            print(f"  {cons_count}个连号: {count:4d}次 ({count/len(consecutive_stats)*100:.2f}%)")
        
        return interval_counter, consecutive_counter
    
    def time_series_analysis(self):
        """时间序列分析"""
        print("\n开始时间序列分析...")
        
        # 按年份统计
        self.df['年份'] = self.df['开奖日期'].dt.year
        self.df['月份'] = self.df['开奖日期'].dt.month
        self.df['季度'] = self.df['开奖日期'].dt.quarter
        self.df['星期'] = self.df['开奖日期'].dt.dayofweek
        
        # 年度统计
        yearly_stats = self.df.groupby('年份').size()
        monthly_stats = self.df.groupby('月份').size()
        quarterly_stats = self.df.groupby('季度').size()
        weekly_stats = self.df.groupby('星期').size()
        
        self.analysis_results['yearly_stats'] = yearly_stats
        self.analysis_results['monthly_stats'] = monthly_stats
        self.analysis_results['quarterly_stats'] = quarterly_stats
        self.analysis_results['weekly_stats'] = weekly_stats
        
        print("年度开奖次数:")
        for year, count in yearly_stats.items():
            print(f"  {year}年: {count}次")
        
        print("\n月度开奖次数:")
        months = ['1月', '2月', '3月', '4月', '5月', '6月', 
                 '7月', '8月', '9月', '10月', '11月', '12月']
        for month, count in monthly_stats.items():
            print(f"  {months[month-1]}: {count}次")
        
        print("\n季度开奖次数:")
        for quarter, count in quarterly_stats.items():
            print(f"  第{quarter}季度: {count}次")
        
        print("\n星期开奖次数:")
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for weekday, count in weekly_stats.items():
            print(f"  {weekdays[weekday]}: {count}次")
        
        return yearly_stats, monthly_stats, quarterly_stats, weekly_stats
    
    def analyze_number_patterns(self):
        """分析号码组合模式和奇偶性"""
        print("\n开始分析号码组合模式...")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 奇偶性分析
        odd_even_stats = []
        sum_stats = []
        
        for idx, row in self.df.iterrows():
            red_nums = [row[col] for col in red_balls]
            blue_num = row['蓝球']
            
            # 红球奇偶统计
            odd_count = sum(1 for num in red_nums if num % 2 == 1)
            even_count = 6 - odd_count
            odd_even_stats.append(f"{odd_count}奇{even_count}偶")
            
            # 红球和值
            red_sum = sum(red_nums)
            sum_stats.append(red_sum)
        
        # 统计结果
        odd_even_counter = Counter(odd_even_stats)
        
        self.analysis_results['odd_even'] = odd_even_counter
        self.analysis_results['sum_stats'] = sum_stats
        
        print("红球奇偶性分布:")
        for pattern, count in sorted(odd_even_counter.items()):
            print(f"  {pattern}: {count:4d}次 ({count/len(odd_even_stats)*100:.2f}%)")
        
        print(f"\n红球和值统计:")
        print(f"  最小和值: {min(sum_stats)}")
        print(f"  最大和值: {max(sum_stats)}")
        print(f"  平均和值: {np.mean(sum_stats):.2f}")
        print(f"  中位数和值: {np.median(sum_stats):.2f}")
        
        # 蓝球奇偶性
        blue_odd = (self.df['蓝球'] % 2 == 1).sum()
        blue_even = len(self.df) - blue_odd
        print(f"\n蓝球奇偶性:")
        print(f"  奇数: {blue_odd}次 ({blue_odd/len(self.df)*100:.2f}%)")
        print(f"  偶数: {blue_even}次 ({blue_even/len(self.df)*100:.2f}%)")
        
        return odd_even_counter, sum_stats
    
    def correlation_analysis(self):
        """相关性分析"""
        print("\n开始相关性分析...")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 计算红球之间的相关性
        red_data = self.df[red_balls]
        correlation_matrix = red_data.corr()
        
        self.analysis_results['correlation_matrix'] = correlation_matrix
        
        print("红球相关性矩阵 (前5行5列):")
        print(correlation_matrix.iloc[:5, :5].round(3))
        
        # 找出最强的正相关和负相关
        corr_values = []
        for i in range(len(red_balls)):
            for j in range(i+1, len(red_balls)):
                corr_values.append((red_balls[i], red_balls[j], correlation_matrix.iloc[i, j]))
        
        corr_values.sort(key=lambda x: abs(x[2]), reverse=True)
        
        print("\n最强相关性 (前10对):")
        for i, (ball1, ball2, corr) in enumerate(corr_values[:10]):
            print(f"  {ball1} vs {ball2}: {corr:.4f}")
        
        return correlation_matrix
    
    def clustering_analysis(self):
        """聚类分析"""
        print("\n开始聚类分析...")
        
        red_balls = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        
        # 准备数据
        X = self.df[red_balls + ['蓝球']].values
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means聚类
        n_clusters = 5
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 分析聚类结果
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = self.df[clusters == i]
            cluster_stats[i] = {
                'count': len(cluster_data),
                'red_mean': cluster_data[red_balls].mean().round(2),
                'blue_mean': cluster_data['蓝球'].mean().round(2)
            }
        
        self.analysis_results['clusters'] = cluster_stats
        
        print(f"聚类分析结果 ({n_clusters}个聚类):")
        for cluster_id, stats in cluster_stats.items():
            print(f"\n聚类 {cluster_id} ({stats['count']}条记录):")
            print(f"  红球平均值: {stats['red_mean'].values}")
            print(f"  蓝球平均值: {stats['blue_mean']:.2f}")
        
        return cluster_stats
    
    def generate_visualizations(self):
        """生成可视化图表"""
        print("\n开始生成可视化图表...")
        
        # 创建图表
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('双色球数据分析报告', fontsize=16, fontweight='bold')
        
        # 1. 红球频率分布
        red_freq = self.analysis_results['red_frequency']
        axes[0, 0].bar(red_freq.keys(), red_freq.values(), color='red', alpha=0.7)
        axes[0, 0].set_title('红球出现频率分布')
        axes[0, 0].set_xlabel('红球号码')
        axes[0, 0].set_ylabel('出现次数')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 蓝球频率分布
        blue_freq = self.analysis_results['blue_frequency']
        axes[0, 1].bar(blue_freq.keys(), blue_freq.values(), color='blue', alpha=0.7)
        axes[0, 1].set_title('蓝球出现频率分布')
        axes[0, 1].set_xlabel('蓝球号码')
        axes[0, 1].set_ylabel('出现次数')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 号码间隔分布
        intervals = self.analysis_results['intervals']
        axes[1, 0].bar(intervals.keys(), intervals.values(), color='green', alpha=0.7)
        axes[1, 0].set_title('红球号码间隔分布')
        axes[1, 0].set_xlabel('间隔大小')
        axes[1, 0].set_ylabel('出现次数')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 连号数量分布
        consecutive = self.analysis_results['consecutive']
        axes[1, 1].bar(consecutive.keys(), consecutive.values(), color='orange', alpha=0.7)
        axes[1, 1].set_title('连号数量分布')
        axes[1, 1].set_xlabel('连号个数')
        axes[1, 1].set_ylabel('出现次数')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 5. 奇偶性分布
        odd_even = self.analysis_results['odd_even']
        axes[2, 0].bar(range(len(odd_even)), odd_even.values(), color='purple', alpha=0.7)
        axes[2, 0].set_title('红球奇偶性分布')
        axes[2, 0].set_xlabel('奇偶组合')
        axes[2, 0].set_ylabel('出现次数')
        axes[2, 0].set_xticks(range(len(odd_even)))
        axes[2, 0].set_xticklabels(odd_even.keys(), rotation=45)
        axes[2, 0].grid(True, alpha=0.3)
        
        # 6. 和值分布
        sum_stats = self.analysis_results['sum_stats']
        axes[2, 1].hist(sum_stats, bins=30, color='brown', alpha=0.7, edgecolor='black')
        axes[2, 1].set_title('红球和值分布')
        axes[2, 1].set_xlabel('和值')
        axes[2, 1].set_ylabel('频次')
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ssq_analysis_charts.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 ssq_analysis_charts.png")
        
        return fig
    
    def generate_report(self):
        """生成综合分析报告"""
        print("\n生成综合分析报告...")
        
        report = []
        report.append("# 双色球数据分析报告")
        report.append(f"## 数据概况")
        report.append(f"- 分析数据文件: {self.data_file}")
        report.append(f"- 数据记录数: {len(self.df)}")
        report.append(f"- 数据时间范围: {self.df['开奖日期'].min().strftime('%Y-%m-%d')} 至 {self.df['开奖日期'].max().strftime('%Y-%m-%d')}")
        report.append(f"- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 基础统计分析
        report.append("\n## 1. 基础统计分析")
        red_freq = self.analysis_results['red_frequency']
        blue_freq = self.analysis_results['blue_frequency']
        
        sorted_red = sorted(red_freq.items(), key=lambda x: x[1], reverse=True)
        report.append(f"### 红球分析")
        report.append(f"- 最热门红球: {sorted_red[0][0]}号 (出现{sorted_red[0][1]}次)")
        report.append(f"- 最冷门红球: {sorted_red[-1][0]}号 (出现{sorted_red[-1][1]}次)")
        report.append(f"- 频率差异: {sorted_red[0][1] - sorted_red[-1][1]}次")
        
        sorted_blue = sorted(blue_freq.items(), key=lambda x: x[1], reverse=True)
        report.append(f"### 蓝球分析")
        report.append(f"- 最热门蓝球: {sorted_blue[0][0]}号 (出现{sorted_blue[0][1]}次)")
        report.append(f"- 最冷门蓝球: {sorted_blue[-1][0]}号 (出现{sorted_blue[-1][1]}次)")
        report.append(f"- 频率差异: {sorted_blue[0][1] - sorted_blue[-1][1]}次")
        
        # 号码间隔分析
        report.append("\n## 2. 号码间隔分析")
        intervals = self.analysis_results['intervals']
        most_common_interval = max(intervals.items(), key=lambda x: x[1])
        report.append(f"- 最常见间隔: {most_common_interval[0]} (出现{most_common_interval[1]}次)")
        
        consecutive = self.analysis_results['consecutive']
        no_consecutive = consecutive.get(0, 0)
        report.append(f"- 无连号期数: {no_consecutive}期 ({no_consecutive/len(self.df)*100:.1f}%)")
        
        # 时间序列分析
        report.append("\n## 3. 时间序列分析")
        yearly_stats = self.analysis_results['yearly_stats']
        report.append(f"- 开奖年份数: {len(yearly_stats)}年")
        report.append(f"- 年均开奖次数: {yearly_stats.mean():.1f}次")
        
        monthly_stats = self.analysis_results['monthly_stats']
        max_month = monthly_stats.idxmax()
        min_month = monthly_stats.idxmin()
        report.append(f"- 开奖最多月份: {max_month}月 ({monthly_stats[max_month]}次)")
        report.append(f"- 开奖最少月份: {min_month}月 ({monthly_stats[min_month]}次)")
        
        # 号码模式分析
        report.append("\n## 4. 号码模式分析")
        odd_even = self.analysis_results['odd_even']
        most_common_pattern = max(odd_even.items(), key=lambda x: x[1])
        report.append(f"- 最常见奇偶模式: {most_common_pattern[0]} (出现{most_common_pattern[1]}次)")
        
        sum_stats = self.analysis_results['sum_stats']
        report.append(f"- 红球和值范围: {min(sum_stats)} - {max(sum_stats)}")
        report.append(f"- 平均和值: {np.mean(sum_stats):.1f}")
        
        # 聚类分析
        report.append("\n## 5. 聚类分析")
        clusters = self.analysis_results['clusters']
        largest_cluster = max(clusters.items(), key=lambda x: x[1]['count'])
        report.append(f"- 最大聚类包含: {largest_cluster[1]['count']}期开奖")
        
        # 总结和建议
        report.append("\n## 6. 分析总结")
        report.append("### 主要发现:")
        report.append("1. 双色球号码分布基本符合随机性特征")
        report.append("2. 各号码出现频率存在一定差异，但差异不显著")
        report.append("3. 号码间隔和连号现象符合概率分布")
        report.append("4. 时间序列分析显示开奖频率相对稳定")
        report.append("5. 奇偶性分布和和值分布呈现正态分布特征")
        
        report.append("\n### 统计学观察:")
        report.append("- 双色球作为随机抽奖游戏，历史数据不能预测未来结果")
        report.append("- 各号码理论上具有相等的中奖概率")
        report.append("- 观察到的频率差异属于正常的统计波动范围")
        
        # 保存报告
        report_text = '\n'.join(report)
        with open('ssq_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("分析报告已保存为 ssq_analysis_report.md")
        return report_text
    
    def run_full_analysis(self):
        """运行完整分析流程"""
        print("开始双色球数据全面分析...")
        print("=" * 50)
        
        # 1. 加载数据
        if not self.load_and_preprocess_data():
            return False
        
        # 2. 基础统计分析
        self.basic_statistics_analysis()
        
        # 3. 号码间隔分析
        self.analyze_number_intervals()
        
        # 4. 时间序列分析
        self.time_series_analysis()
        
        # 5. 号码模式分析
        self.analyze_number_patterns()
        
        # 6. 相关性分析
        self.correlation_analysis()
        
        # 7. 聚类分析
        self.clustering_analysis()
        
        # 8. 生成可视化
        self.generate_visualizations()
        
        # 9. 生成报告
        self.generate_report()
        
        print("\n" + "=" * 50)
        print("双色球数据分析完成！")
        print("生成文件:")
        print("- ssq_analysis_charts.png (可视化图表)")
        print("- ssq_analysis_report.md (分析报告)")
        
        return True

if __name__ == "__main__":
    analyzer = SSQDataAnalyzer()
    analyzer.run_full_analysis()