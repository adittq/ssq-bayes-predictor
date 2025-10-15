# SSQ Bayes Predictor

基于贝叶斯后验概率、采样与纳什再博弈的双色球候选号码生成器。脚本位于 `ssq_bayes_predict.py`，数据文件为 `ssq_cwl_data.csv`。

## 特性
- 贝叶斯后验筛选：根据过往数据计算每个球的后验概率，输出 Top 方案。
- 采样生成候选：在后验分布上采样生成多组候选号码。
- 纳什再博弈：在候选之间进行再博弈，平衡“高概率”与“多样性”，选出胜出组合。

## 默认行为
- `method=sample`、`num-sets=6`、`seed=42`
- 纳什再博弈默认开启（可用 `--no-nash` 关闭）
- 输出顺序：总是先打印“Top方案”，在 `sample` 模式打印各“采样方案”，若开启纳什则最后输出“纳什胜出组合”。

## 快速开始
- 直接运行（使用默认）：
  - `python ssq_bayes_predict.py`
- 只看 Top 方案：
  - `python ssq_bayes_predict.py --method top`
- 采样 + 纳什（显式参数）：
  - `python ssq_bayes_predict.py --method sample --num-sets 6 --seed 42 --nash`
- 采样 + 纳什 + 平衡型预设：
  - `python ssq_bayes_predict.py --method sample --num-sets 6 --seed 42 --nash --profile balanced`

## 常用参数
- `--method {top,sample}`：运行模式（默认 `sample`）。
- `--num-sets N`：采样生成的候选组数（默认 6，`sample` 模式生效）。
- `--seed S`：采样随机种子（默认 42）。
- `--nash` / `--no-nash`：启用或关闭纳什再博弈（默认启用）。
- `--profile balanced`：应用平衡型预设，提升候选的多样性与稳健性。

## 输出说明
- Top方案：示例 `02 06 09 14 17 22 | 蓝球 16`
- 采样方案：按序号打印每组候选（仅 `sample` 模式）。
- 纳什胜出组合：示例 `06 11 13 23 25 32 | 蓝球 08`（候选#5），并附带分数。

## 评分含义（为何常为负数）
- 评分公式：`U = log_likelihood − beta × overlap_penalty`。
- `log_likelihood = Σ log(p(红球)) + log(p(蓝球))`，因为概率都小于 1，`log(小于1)` 为负，七个球相加通常较负。
- `overlap_penalty` 为正，乘以 `beta` 后从 `U` 中扣除，分数进一步变小。
- 因此分数为负是正常现象，关键看“相对高低”。例如 `-26` 优于 `-29`。

## 示例输出（节选）
- 采样 + 纳什：
  - Top方案：`02 06 09 14 17 22 | 蓝球 16`
  - 纳什胜出：`06 11 13 23 25 32 | 蓝球 08`，得分约 `-29.05`

## 目录结构提示
- 脚本与数据位于仓库根目录；`lottery-simulator/` 为独立的前后端模拟器工程，使用说明见其目录下的文档。

## 备注
- 如需更直观的分数展示（概率乘积或归一化到 [0,1]），可提出需求，我可以新增 `--score-view prob|norm` 选项。