import random
import math
import argparse
from collections import Counter, defaultdict
from typing import Dict, Tuple, List

"""
双色球策略模拟器

目的：比较不同选号策略在长期（多期）内的命中表现是否优于随机。

模拟方法：
- 每期真实开奖结果用统一随机过程生成（符合1-33选6、1-16选1的规则）。
- 多种策略生成当期投注号码；与真实开奖结果匹配，统计奖级命中。
- 奖级判定遵循公开规则（不涉及奖金金额，仅统计等级）。

注意：本模拟仅用于验证“策略是否优于随机”。真实开奖为独立随机事件，
任何策略在长期都不会优于随机选择（除非策略本身也是随机）。
"""


def draw_official():
    """随机生成一期开奖结果：6红（升序）+ 1蓝"""
    reds = sorted(random.sample(range(1, 34), 6))
    blue = random.randint(1, 16)
    return tuple(reds), blue


def judge_prize(chosen_reds, chosen_blue, result_reds, result_blue):
    """根据命中数量判定奖级，返回奖级字符串或None"""
    red_hits = len(set(chosen_reds) & set(result_reds))
    blue_hit = int(chosen_blue == result_blue)

    # 规则参考：中福彩/500彩票网公开说明
    # 一等: 6+1；二等: 6+0；三等: 5+1；四等: 5+0 或 4+1
    # 五等: 4+0 或 3+1；六等: 2+1 或 1+1 或 0+1
    if red_hits == 6 and blue_hit == 1:
        return "一等奖"
    if red_hits == 6 and blue_hit == 0:
        return "二等奖"
    if red_hits == 5 and blue_hit == 1:
        return "三等奖"
    if (red_hits == 5 and blue_hit == 0) or (red_hits == 4 and blue_hit == 1):
        return "四等奖"
    if (red_hits == 4 and blue_hit == 0) or (red_hits == 3 and blue_hit == 1):
        return "五等奖"
    if blue_hit == 1 and red_hits <= 2:
        return "六等奖"
    return None


# ------------------ 策略定义 ------------------

def strategy_random():
    """纯随机策略：等概率选择6红+1蓝"""
    reds = sorted(random.sample(range(1, 34), 6))
    blue = random.randint(1, 16)
    return reds, blue


def strategy_hot_cold(red_frequency=None, blue_frequency=None):
    """
    热冷号策略（演示）：
    - 红球：偏向选择出现频次较高的号码（这里使用简单权重，若未提供频率则退化为随机）。
    - 蓝球：偏向选择高频蓝球。
    提示：此策略在长期并不会优于随机，仅为对比用途。
    """
    if not red_frequency or not blue_frequency:
        return strategy_random()
    # 唯一性加权采样（无放回）：按频率加权挑选6个不同红球
    red_items = [i for i in range(1, 34)]
    red_weights = [max(int(red_frequency.get(i, 0)), 0) + 1 for i in red_items]

    def weighted_sample_without_replacement(items: List[int], weights: List[float], k: int) -> List[int]:
        selected = []
        pool = items[:]
        w = weights[:]
        for _ in range(k):
            total = sum(w)
            r = random.uniform(0, total)
            cum = 0.0
            for idx, wi in enumerate(w):
                cum += wi
                if r <= cum:
                    selected.append(pool[idx])
                    del pool[idx]
                    del w[idx]
                    break
        return selected

    chosen_reds = sorted(weighted_sample_without_replacement(red_items, red_weights, 6))

    # 蓝球加权采样（有放回即可，因为只选1个）
    blue_items = [i for i in range(1, 17)]
    blue_weights = [max(int(blue_frequency.get(i, 0)), 0) + 1 for i in blue_items]
    # 手写choices以避免旧Python兼容问题
    total_b = sum(blue_weights)
    r = random.uniform(0, total_b)
    cum = 0.0
    chosen_blue = blue_items[-1]
    for idx, wi in enumerate(blue_weights):
        cum += wi
        if r <= cum:
            chosen_blue = blue_items[idx]
            break

    return chosen_reds, chosen_blue


def strategy_odd_even_balance():
    """奇偶平衡策略：尽量挑选3奇3偶的红球"""
    reds = []
    # 选3个奇数
    odd_candidates = list(range(1, 34, 2))
    even_candidates = list(range(2, 34, 2))
    reds.extend(random.sample(odd_candidates, 3))
    reds.extend(random.sample(even_candidates, 3))
    reds = sorted(reds)
    blue = random.randint(1, 16)
    return reds, blue


def strategy_avoid_popular_patterns():
    """
    避免大众常用组合策略：
    - 排除明显整齐/顺子/同尾等模式，选取“非典型”组合以降低分奖风险。
    - 注意：这不提高中奖率，仅可能在中奖时减少与他人撞号的概率。
    """
    while True:
        reds = sorted(random.sample(range(1, 34), 6))
        # 排除顺子（全部间隔为1）
        intervals = [reds[i+1] - reds[i] for i in range(5)]
        if all(d == 1 for d in intervals):
            continue
        # 排除同尾号过多（>=4个同尾）
        tails = Counter([r % 10 for r in reds])
        if max(tails.values()) >= 4:
            continue
        # 排除全在一个小区间（跨度<8）
        if reds[-1] - reds[0] < 8:
            continue
        blue = random.randint(1, 16)
        return reds, blue


# ------------------ 模拟引擎 ------------------

def run_simulation(n_periods=100000, n_tickets_per_strategy=1, red_frequency=None, blue_frequency=None, seed=42):
    random.seed(seed)
    prize_counter = defaultdict(lambda: Counter())

    strategies = {
        "随机": strategy_random,
        "热冷号": lambda: strategy_hot_cold(red_frequency, blue_frequency),
        "奇偶平衡": strategy_odd_even_balance,
        "避开大众组合": strategy_avoid_popular_patterns,
    }

    for period in range(n_periods):
        result_reds, result_blue = draw_official()

        for name, strat in strategies.items():
            for _ in range(n_tickets_per_strategy):
                reds, blue = strat()
                prize = judge_prize(reds, blue, result_reds, result_blue)
                if prize:
                    prize_counter[name][prize] += 1

    return prize_counter


def summarize(prize_counter, n_periods, n_tickets_per_strategy):
    lines = []
    lines.append(f"模拟期数: {n_periods}；每策略每期投注: {n_tickets_per_strategy} 注")
    for name, counter in prize_counter.items():
        total_bets = n_periods * n_tickets_per_strategy
        total_hits = sum(counter.values())
        lines.append(f"\n策略：{name}")
        lines.append(f"  命中奖级分布: {dict(counter)}")
        lines.append(f"  总命中次数: {total_hits} (占比 {total_hits/total_bets*100:.4f}%)")
    return "\n".join(lines)


# ------------------ 频率加载 ------------------

def load_frequency_from_csv(data_file: str) -> Tuple[Dict[int, int], Dict[int, int]]:
    try:
        import pandas as pd
        df = pd.read_csv(data_file, encoding='utf-8')
        red_cols = ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']
        # 红球频次：对六列分别计数后求和
        red_freq = {i: 0 for i in range(1, 34)}
        for col in red_cols:
            vc = df[col].value_counts()
            for num, cnt in vc.items():
                if pd.notna(num):
                    red_freq[int(num)] = red_freq.get(int(num), 0) + int(cnt)
        # 蓝球频次
        blue_freq_series = df['蓝球'].value_counts()
        blue_freq = {i: 0 for i in range(1, 17)}
        for num, cnt in blue_freq_series.items():
            if pd.notna(num):
                blue_freq[int(num)] = int(cnt)
        return red_freq, blue_freq
    except Exception as e:
        print(f"从CSV加载频率失败：{e}，将使用均匀频率")
        return {i: 1 for i in range(1, 34)}, {i: 1 for i in range(1, 17)}


def load_frequency_with_analyzer(data_file: str) -> Tuple[Dict[int, int], Dict[int, int]]:
    try:
        from ssq_data_analysis import SSQDataAnalyzer
        analyzer = SSQDataAnalyzer(data_file=data_file)
        if not analyzer.load_and_preprocess_data():
            raise RuntimeError("分析器加载数据失败")
        red_freq, blue_freq = analyzer.basic_statistics_analysis()
        # red_freq/blue_freq 已为字典
        return red_freq, blue_freq
    except Exception as e:
        print(f"从分析模块加载频率失败：{e}，回退到直接CSV统计")
        return load_frequency_from_csv(data_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="双色球策略模拟器")
    parser.add_argument('--use-history', action='store_true', help='使用历史频率作为热冷号权重')
    parser.add_argument('--data-file', type=str, default='ssq_data_20251001.csv', help='历史数据CSV文件路径')
    parser.add_argument('--periods', type=int, default=100000, help='模拟期数')
    parser.add_argument('--tickets', type=int, default=1, help='每策略每期投注注数')
    parser.add_argument('--seed', type=int, default=2025, help='随机种子')
    parser.add_argument('--report-out', type=str, default='', help='将结果保存到指定Markdown文件')
    args = parser.parse_args()

    if args.use_history:
        # 优先尝试通过分析器获取频率，失败则回退到CSV统计
        red_freq, blue_freq = load_frequency_with_analyzer(args.data_file)
        print("已加载历史频率，用于热冷号策略权重")
    else:
        red_freq = {i: 1 for i in range(1, 34)}
        blue_freq = {i: 1 for i in range(1, 17)}
        print("使用均匀频率（等效随机）")

    res = run_simulation(args.periods, args.tickets, red_freq, blue_freq, seed=args.seed)
    summary = summarize(res, args.periods, args.tickets)
    print(summary)

    if args.report_out:
        with open(args.report_out, 'w', encoding='utf-8') as f:
            f.write('# 双色球策略模拟（自动历史频率）\n\n')
            f.write(f'- 模拟期数：{args.periods}\n')
            f.write(f'- 每策略每期投注：{args.tickets} 注\n')
            f.write(f'- 历史频率来源：{args.data_file if args.use_history else "均匀"}\n\n')
            f.write('## 结果摘要\n')
            f.write('```\n')
            f.write(summary)
            f.write('\n```\n')
        print(f"结果已保存到 {args.report_out}")