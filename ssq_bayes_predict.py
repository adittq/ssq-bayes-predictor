#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球贝叶斯预测脚本

基于 ssq_cwl_data.csv 历史数据，使用对称Dirichlet先验对红球(1..33)与蓝球(1..16)的出现频率进行贝叶斯估计，
计算后验均值作为下一期号码的概率权重，并给出预测方案（Top方案与采样方案）。

使用示例（推荐）：
  # 只看Top方案（第一次筛选）
  python ssq_bayes_predict.py --csv ssq_cwl_data.csv --method top

  # 生成6组采样并进行纳什再博弈
  python ssq_bayes_predict.py --csv ssq_cwl_data.csv --method sample --num-sets 6 --seed 42 --nash

  # 在纳什再博弈中启用平衡型预设（覆盖beta/recent/decay）
  python ssq_bayes_predict.py --csv ssq_cwl_data.csv --method sample --num-sets 6 --seed 42 --nash --profile balanced

参数说明：
  --csv         数据文件路径（默认 ssq_cwl_data.csv）
  --method      预测方法：top（按后验均值取前6）或 sample（按权重无放回采样6）
  --num-sets    生成预测方案数量（method=sample时有效，默认5）
  --alpha-red   红球Dirichlet对称先验参数（默认1.0）
  --alpha-blue  蓝球Dirichlet对称先验参数（默认1.0）
  --seed        随机种子，用于采样复现（可选）
  --nash        对采样方案进行纳什再博弈，选择效用最大组合
  --beta        纳什重叠惩罚系数（默认0.5，越大越偏去重）
  --recent      仅使用最近N期数据计算后验（可选）
  --decay       时间衰减权重gamma∈(0,1]，越接近1越平滑（可选）
  --profile     预设调参方案：balanced / dedup / hot（覆盖beta/recent/decay）

默认行为：method=sample，num-sets=6，seed=42，纳什再博弈默认开启（可用 --no-nash 关闭）。

输出说明：脚本总是先打印“Top方案”（第一次筛选），在sample模式下继续打印各“采样方案”；启用--nash时，会基于后验概率对候选集进行再博弈并输出胜出组合。

说明：彩票属随机事件，任何统计/机器学习方法均无法保证准确率，本脚本仅作数据分析与学习参考。
"""

import argparse
import sys
from typing import List, Tuple

import numpy as np
import pandas as pd


RED_RANGE = list(range(1, 34))   # 1..33
BLUE_RANGE = list(range(1, 17))  # 1..16


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding='utf-8')
    # 规范数值类型
    red_cols = [f'红球{i}' for i in range(1, 7)]
    for c in red_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['蓝球'] = pd.to_numeric(df['蓝球'], errors='coerce')
    # 日期可选转换
    if '开奖日期' in df.columns:
        df['开奖日期'] = pd.to_datetime(df['开奖日期'], errors='coerce')
    # 去除缺失红/蓝球的记录
    df = df.dropna(subset=red_cols + ['蓝球'])
    # 期号转整型以便计算下一期
    if '期号' in df.columns:
        df['期号'] = pd.to_numeric(df['期号'], errors='coerce').astype('Int64')
    return df


def compute_red_counts(df: pd.DataFrame, weights: np.ndarray | None = None) -> np.ndarray:
    red_cols = [f'红球{i}' for i in range(1, 7)]
    if weights is None:
        reds = pd.concat([df[c] for c in red_cols], ignore_index=True)
        counts = np.zeros(len(RED_RANGE), dtype=np.int64)
        vc = reds.value_counts()
        for num, cnt in vc.items():
            if num in RED_RANGE:
                counts[num - 1] = int(cnt)
        return counts
    else:
        # 按行加权累加
        counts = np.zeros(len(RED_RANGE), dtype=np.float64)
        for w, (_, row) in zip(weights, df.iterrows()):
            for c in red_cols:
                num = int(row[c])
                if 1 <= num <= 33:
                    counts[num - 1] += float(w)
        return counts


def compute_blue_counts(df: pd.DataFrame, weights: np.ndarray | None = None) -> np.ndarray:
    if weights is None:
        blues = df['蓝球']
        counts = np.zeros(len(BLUE_RANGE), dtype=np.int64)
        vc = blues.value_counts()
        for num, cnt in vc.items():
            if num in BLUE_RANGE:
                counts[num - 1] = int(cnt)
        return counts
    else:
        counts = np.zeros(len(BLUE_RANGE), dtype=np.float64)
        for w, (_, row) in zip(weights, df.iterrows()):
            num = int(row['蓝球'])
            if 1 <= num <= 16:
                counts[num - 1] += float(w)
        return counts


def _build_weights(df: pd.DataFrame, recent: int | None, decay: float | None) -> tuple[pd.DataFrame, np.ndarray | None]:
    """
    按 recent 过滤最近N期，并按 decay=g 生成指数时间衰减权重：
    - 若提供 recent，则保留排序后最后N条记录；
    - 若提供 decay（g∈(0,1]），对排序后的记录按时间从旧到新设置权重 g^(age)，最近期权重最大；
    返回：过滤后的df与同长度权重数组（或None）。
    """
    sort_key = None
    if '期号' in df.columns and df['期号'].notna().any():
        sort_key = '期号'
    elif '开奖日期' in df.columns and df['开奖日期'].notna().any():
        sort_key = '开奖日期'

    df_sorted = df.sort_values(by=sort_key, ascending=True) if sort_key else df.copy()
    if recent is not None and recent > 0:
        df_sorted = df_sorted.tail(recent)

    weights = None
    if decay is not None:
        g = float(decay)
        if not (0.0 < g <= 1.0):
            raise ValueError('decay 参数需在 (0, 1] 区间')
        n = len(df_sorted)
        ages = np.arange(n)
        # 最近期权重最大：g^(n-1-age)
        weights = g ** (n - 1 - ages)
    return df_sorted, weights


def dirichlet_posterior_mean(counts: np.ndarray, alpha: float) -> np.ndarray:
    # 对称Dirichlet先验，后验参数 alpha_i = alpha + count_i
    alpha_vec = counts.astype(np.float64) + float(alpha)
    return alpha_vec / alpha_vec.sum()


def select_top_k(probs: np.ndarray, k: int) -> List[int]:
    # 依据概率取前k个（按索引从1开始映射）
    idx = np.argsort(probs)[::-1][:k]
    return [int(i + 1) for i in idx]


def sample_without_replacement(probs: np.ndarray, k: int, rng: np.random.Generator) -> List[int]:
    # 按权重进行无放回采样
    items = np.arange(1, len(probs) + 1)
    # numpy的choice在replace=False时支持p权重
    chosen = rng.choice(items, size=k, replace=False, p=probs)
    return [int(x) for x in np.sort(chosen)]


def predict_next(df: pd.DataFrame, method: str, num_sets: int, alpha_red: float, alpha_blue: float, seed: int = None,
                 recent: int | None = None, decay: float | None = None) -> Tuple[int, List[Tuple[List[int], int]]]:
    # 计算下一期期号（仅用于展示）
    try:
        last_issue = int(df['期号'].dropna().max())
        next_issue = last_issue + 1
    except Exception:
        next_issue = -1

    # 近N期与时间衰减权重
    df_used, weights = _build_weights(df, recent=recent, decay=decay)

    red_counts = compute_red_counts(df_used, weights=weights)
    blue_counts = compute_blue_counts(df_used, weights=weights)

    red_probs = dirichlet_posterior_mean(red_counts, alpha_red)
    blue_probs = dirichlet_posterior_mean(blue_counts, alpha_blue)

    rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()

    predictions = []  # List of (reds, blue)
    if method == 'top':
        reds = select_top_k(red_probs, 6)
        blue = select_top_k(blue_probs, 1)[0]
        predictions.append((sorted(reds), blue))
    elif method == 'sample':
        for _ in range(num_sets):
            reds = sample_without_replacement(red_probs, 6, rng)
            # 蓝球是单球，按权重采样
            blue_candidates = np.arange(1, len(blue_probs) + 1)
            blue = int(rng.choice(blue_candidates, size=1, replace=True, p=blue_probs)[0])
            predictions.append((reds, blue))
    else:
        raise ValueError("method 必须为 'top' 或 'e'")

    return next_issue, predictions


def format_combo(reds: List[int], blue: int) -> str:
    return ' '.join(f"{x:02d}" for x in reds) + f" | 蓝球 {blue:02d}"




def nash_select_best(predictions: List[Tuple[List[int], int]], red_probs: np.ndarray, blue_probs: np.ndarray, beta: float = 0.5) -> Tuple[int, float]:
    """
    使用简化的纳什均衡思想进行“再博弈”选择：
    - 每个候选组合视为在当前其他组合固定时的“最优回应”，其效用为：
      U = log-likelihood(组合) - beta * overlap_penalty(与其他组合的重叠程度)
    - 选择效用最大的组合，作为稳定解近似（在候选集sampl限制下的纳什优胜者）。

    参数：
      predictions: [(reds, blue)] 候选组合列表
      red_probs: 红球后验均值概率，长度33
      blue_probs: 蓝球后验均值概率，长度16
      beta: 重叠惩罚系数，默认0.5（数值越大越倾向去重、避免撞车）。
            红球使用概率加权的重叠惩罚（热门号惩罚更高），蓝球惩罚加倍以减少撞车。

    返回：winner_index, winner_score
    """
    eps = 1e-12
    # 预计算每个组合的log-likelihood
    def log_like(reds: List[int], blue: int) -> float:
        ll = 0.0
        for r in reds:
            ll += float(np.log(red_probs[r - 1] + eps))
        ll += float(np.log(blue_probs[blue - 1] + eps))
        return ll

    def overlap_penalty(i: int) -> float:
        # 红球：使用概率加权惩罚（-log(p)），热门号重叠惩罚更高
        # 蓝球：若相同，惩罚加倍以降低撞车风险
        reds_i, blue_i = predictions[i]
        s_i = set(reds_i)
        penalty_red = 0.0
        penalty_blue = 0.0
        for j in range(len(predictions)):
            if j == i:
                continue
            reds_j, blue_j = predictions[j]
            s_j = set(reds_j)
            inter = s_i.intersection(s_j)
            for r in inter:
                penalty_red += float(-np.log(red_probs[r - 1] + eps))
            if blue_j == blue_i:
                penalty_blue += float(-np.log(blue_probs[blue_i - 1] + eps))
        # 蓝球惩罚加倍（在惩罚项中体现），beta只在总效用处应用一次
        return penalty_red + 2.0 * penalty_blue

    scores = []
    for i, (reds, blue) in enumerate(predictions):
        ll = log_like(reds, blue)
        pen = overlap_penalty(i)
        # 依据文档：U = log-likelihood - beta * overlap_penalty
        score = ll - beta * pen
        scores.append(score)

    winner_index = int(np.argmax(scores))
    return winner_index, float(scores[winner_index])


def main():
    parser = argparse.ArgumentParser(description='使用贝叶斯方法预测下一期双色球号码')
    parser.add_argument('--csv', default='ssq_cwl_data.csv', help='历史数据CSV文件路径')
    parser.add_argument('--method', choices=['top', 'sample'], default='sample', help='预测方法')
    parser.add_argument('--num-sets', type=int, default=6, help='生成方案数量（采样法有效）')
    parser.add_argument('--alpha-red', type=float, default=1.0, help='红球Dirichlet对称先验参数')
    parser.add_argument('--alpha-blue', type=float, default=1.0, help='蓝球Dirichlet对称先验参数')
    parser.add_argument('--seed', type=int, default=42, help='随机种子（采样法可复现）')
    parser.add_argument('--nash', dest='nash', action='store_true', help='对采样方案进行纳什均衡再博弈选择最优组合')
    parser.add_argument('--no-nash', dest='nash', action='store_false', help='禁用纳什再博弈')
    parser.add_argument('--beta', type=float, default=0.5, help='纳什选择的重叠惩罚系数')
    parser.add_argument('--recent', type=int, default=None, help='仅使用最近N期数据计算后验（可选）')
    parser.add_argument('--decay', type=float, default=None, help='时间衰减权重gamma∈(0,1]，最近期权重最大（可选）')
    parser.add_argument('--profile', choices=['balanced', 'dedup', 'hot'], default=None, help='预设调参方案（覆盖beta/recent/decay）')
    # 默认启用纳什再博弈
    parser.set_defaults(nash=True)
    args = parser.parse_args()

    try:
        # 若指定调参方案，则覆盖 beta/recent/decay
        if args.profile:
            profiles = {
                'balanced': {'beta': 0.6, 'recent': 120, 'decay': 0.98},
                'dedup': {'beta': 0.9, 'recent': 90, 'decay': 0.97},
                'hot': {'beta': 0.3, 'recent': 300, 'decay': 1.0},
            }
            p = profiles[args.profile]
            args.beta = p['beta']
            args.recent = p['recent']
            args.decay = p['decay']
        df = load_data(args.csv)


        next_issue, predictions = predict_next(
            df, args.method, args.num_sets, args.alpha_red, args.alpha_blue, args.seed,
            recent=args.recent, decay=args.decay
        )
        # 统一输出：先打印“第一次筛选的号码”的Top方案；采样模式再列出各采样方案
        print("贝叶斯公式第一次筛选的号码")
        print("=====")
        # 计算后验概率以获得Top方案（与预测使用相同的Dirichlet设置）
        df_used, weights = _build_weights(df, recent=args.recent, decay=args.decay)
        red_counts = compute_red_counts(df_used, weights=weights)
        blue_counts = compute_blue_counts(df_used, weights=weights)
        red_probs = dirichlet_posterior_mean(red_counts, args.alpha_red)
        blue_probs = dirichlet_posterior_mean(blue_counts, args.alpha_blue)
        top_reds = select_top_k(red_probs, 6)
        top_blue = select_top_k(blue_probs, 1)[0]
        print(f"Top方案: {format_combo(sorted(top_reds), top_blue)}")

        if args.method == 'sample':
            for i, (reds, blue) in enumerate(predictions, start=1):
                print(f"采样方案 #{i}: {format_combo(reds, blue)}")

            # 若需要纳什选择，再博弈选出最优组合
            if args.nash and len(predictions) > 1:
                # 复用已计算的后验概率进行纳什选择
                winner_idx, winner_score = nash_select_best(predictions, red_probs, blue_probs, beta=args.beta)
                w_reds, w_blue = predictions[winner_idx]
                print("\n纳什再博弈选择结果")
                print("----------------")
                print(f"胜出组合: {format_combo(w_reds, w_blue)} (候选#{winner_idx+1}, 得分 {winner_score:.4f})")

    except Exception as e:
        print(f"运行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()