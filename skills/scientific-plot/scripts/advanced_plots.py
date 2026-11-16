"""
Advanced Comparison & Uncertainty Plots - 高级比较与不确定性可视化
包含：哑铃图、斜率图、瀑布图、扇形图、Spaghetti图等

Author: Enhanced by Claude
Date: 2026-07-26
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# 导入配置
try:
    from plot_config_v2 import (setup_matplotlib, fig_size, save_figure,
                                 get_colors, add_subplot_labels)
except ImportError:
    from plot_config import (setup_matplotlib, fig_size, save_figure, get_colors)


# ========== 1. 比较 & 排名类 ==========

def plot_dumbbell(categories, values_before, values_after, labels=None,
                 save_path=None, title=None):
    """
    哑铃图（Dumbbell Chart）- 展示前后对比

    Parameters:
    -----------
    categories : list
        类别名称列表
    values_before : array-like
        前值（基准值）
    values_after : array-like
        后值（对比值）
    labels : tuple or None
        (before_label, after_label)，例如 ('2020', '2025')
    save_path : str or None
    title : str or None

    Example:
    --------
    categories = ['Product A', 'Product B', 'Product C']
    before = [50, 60, 45]
    after = [65, 55, 70]
    plot_dumbbell(categories, before, after, labels=('2020', '2025'))
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.5 * len(categories) / 5))

    categories = np.array(categories)
    values_before = np.array(values_before)
    values_after = np.array(values_after)

    y_pos = np.arange(len(categories))
    colors = get_colors(2, palette='wong')

    # 绘制连接线
    for i, (cat, v_before, v_after) in enumerate(zip(categories, values_before, values_after)):
        ax.plot([v_before, v_after], [i, i], 'k-', linewidth=1.5, alpha=0.4, zorder=1)

        # 绘制圆点
        ax.scatter([v_before], [i], s=100, c=[colors[0]], edgecolors='k',
                  linewidths=1, zorder=3, label='Before' if i == 0 else '')
        ax.scatter([v_after], [i], s=100, c=[colors[1]], edgecolors='k',
                  linewidths=1, zorder=3, label='After' if i == 0 else '')

        # 标注数值
        ax.text(v_before - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.02, i,
               f'{v_before:.1f}', ha='right', va='center', fontsize=7)
        ax.text(v_after + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.02, i,
               f'{v_after:.1f}', ha='left', va='center', fontsize=7)

        # 变化箭头（可选）
        if v_after > v_before:
            arrow_color = 'green'
            arrow_symbol = '↑'
        else:
            arrow_color = 'red'
            arrow_symbol = '↓'

        change_pct = (v_after - v_before) / v_before * 100
        ax.text((v_before + v_after) / 2, i + 0.2, f'{arrow_symbol} {abs(change_pct):.1f}%',
               ha='center', va='bottom', fontsize=6, color=arrow_color, fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.set_xlabel('Value')
    ax.set_ylim(-0.5, len(categories) - 0.5)

    if labels:
        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles[:2], labels, loc='best', frameon=False, fontsize=8)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


def plot_slope_chart(categories, time_points, values_matrix, save_path=None, title=None):
    """
    斜率图（Slope Chart）- 展示多个时间点之间的趋势变化

    Parameters:
    -----------
    categories : list
        类别名称
    time_points : list
        时间点列表，例如 ['2020', '2022', '2025']
    values_matrix : 2D array
        值矩阵，shape = (n_categories, n_timepoints)
    save_path : str or None
    title : str or None

    Example:
    --------
    categories = ['A', 'B', 'C']
    time_points = ['2020', '2022', '2025']
    values = [[10, 15, 20],
              [20, 18, 25],
              [15, 20, 18]]
    plot_slope_chart(categories, time_points, values)
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.7))

    values_matrix = np.array(values_matrix)
    n_categories, n_timepoints = values_matrix.shape

    x_pos = np.arange(n_timepoints)
    colors = get_colors(n_categories, palette='tol_muted')

    # 绘制斜率线
    for i, (cat, values, color) in enumerate(zip(categories, values_matrix, colors)):
        ax.plot(x_pos, values, 'o-', color=color, linewidth=1.5, markersize=6,
               markeredgecolor='k', markeredgewidth=0.5, label=cat, zorder=2)

        # 在首尾标注数值
        ax.text(x_pos[0] - 0.1, values[0], f'{values[0]:.1f}', ha='right', va='center',
               fontsize=7, color=color, fontweight='bold')
        ax.text(x_pos[-1] + 0.1, values[-1], f'{values[-1]:.1f}', ha='left', va='center',
               fontsize=7, color=color, fontweight='bold')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(time_points)
    ax.set_xlabel('Time Point')
    ax.set_ylabel('Value')
    ax.legend(loc='best', frameon=False, fontsize=7)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


def plot_waterfall(categories, values, start_value=0, save_path=None, title=None):
    """
    瀑布图（Waterfall Chart）- 展示累积变化

    Parameters:
    -----------
    categories : list
        类别名称
    values : array-like
        增量值（正值为增加，负值为减少）
    start_value : float
        起始值
    save_path : str or None
    title : str or None

    Example:
    --------
    categories = ['Initial', 'Sales', 'Marketing', 'R&D', 'Final']
    values = [100, 50, -20, -15, 0]  # 最后一个0表示只是显示总计
    plot_waterfall(categories, values)
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.7))

    values = np.array(values)
    n = len(categories)

    # 计算累积值和条形位置
    cumulative = np.zeros(n + 1)
    cumulative[0] = start_value

    for i in range(n):
        if i == n - 1 and values[i] == 0:
            # 最后一个是总计
            cumulative[i + 1] = cumulative[i]
        else:
            cumulative[i + 1] = cumulative[i] + values[i]

    # 条形底部位置
    bottoms = cumulative[:-1]

    # 绘制条形
    colors_positive = get_colors(1, palette='wong')[2]  # 绿色
    colors_negative = get_colors(1, palette='wong')[5]  # 红色
    colors_total = get_colors(1, palette='wong')[4]     # 蓝色

    for i, (cat, val, bottom) in enumerate(zip(categories, values, bottoms)):
        if i == 0:
            # 起始值
            color = colors_total
        elif i == n - 1:
            # 总计
            color = colors_total
            val = cumulative[i + 1]
            bottom = 0
        elif val > 0:
            color = colors_positive
        else:
            color = colors_negative

        ax.bar(i, abs(val), bottom=bottom if val >= 0 else bottom + val,
              color=color, edgecolor='k', linewidth=0.8, width=0.6)

        # 标注数值
        if i != n - 1:
            label_y = bottom + val / 2
            ax.text(i, label_y, f'{val:+.1f}' if val != 0 else f'{bottom:.1f}',
                   ha='center', va='center', fontsize=7, fontweight='bold')
        else:
            ax.text(i, cumulative[i + 1] / 2, f'{cumulative[i + 1]:.1f}',
                   ha='center', va='center', fontsize=7, fontweight='bold')

        # 连接线（虚线）
        if i < n - 1:
            ax.plot([i + 0.3, i + 0.7], [cumulative[i + 1], cumulative[i + 1]],
                   'k--', linewidth=0.8, alpha=0.5)

    ax.set_xticks(range(n))
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_ylabel('Value')
    ax.axhline(0, color='k', linewidth=0.8, linestyle='-')

    # 图例
    handles = [
        mpatches.Patch(color=colors_positive, label='Increase'),
        mpatches.Patch(color=colors_negative, label='Decrease'),
        mpatches.Patch(color=colors_total, label='Total')
    ]
    ax.legend(handles=handles, loc='best', frameon=False, fontsize=7)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


def plot_bullet_chart(categories, values, targets, ranges=None, save_path=None, title=None):
    """
    子弹图（Bullet Chart）- KPI vs 目标对比

    Parameters:
    -----------
    categories : list
        指标名称
    values : array-like
        实际值
    targets : array-like
        目标值
    ranges : list of tuples or None
        范围区间，例如 [(0, 50, 'Poor'), (50, 80, 'Fair'), (80, 100, 'Good')]
    save_path : str or None
    title : str or None

    Example:
    --------
    categories = ['Sales', 'Revenue', 'Profit']
    values = [85, 92, 78]
    targets = [90, 100, 80]
    plot_bullet_chart(categories, values, targets)
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.4 * len(categories) / 3))

    values = np.array(values)
    targets = np.array(targets)
    n = len(categories)

    y_pos = np.arange(n)
    bar_height = 0.3

    # 颜色方案
    colors = get_colors(3, palette='wong')

    for i, (cat, val, target) in enumerate(zip(categories, values, targets)):
        # 背景范围（如果提供）
        if ranges:
            for j, (start, end, label) in enumerate(ranges):
                alpha = 0.2 + j * 0.15
                ax.barh(i, end - start, left=start, height=bar_height * 1.8,
                       color='gray', alpha=alpha, zorder=1)

        # 实际值条形
        color = colors[1] if val >= target else colors[5]  # 达标绿色，未达标红色
        ax.barh(i, val, height=bar_height, color=color, edgecolor='k',
               linewidth=0.8, zorder=2)

        # 目标线
        ax.plot([target, target], [i - bar_height * 0.7, i + bar_height * 0.7],
               'k-', linewidth=2.5, zorder=3)

        # 标注数值
        ax.text(val + 2, i, f'{val:.1f}', va='center', ha='left', fontsize=7)
        ax.text(target, i + bar_height * 0.9, f'Target: {target:.1f}',
               va='bottom', ha='center', fontsize=6, color='black', fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.set_xlabel('Value')
    ax.set_ylim(-0.5, n - 0.5)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


# ========== 2. 不确定性可视化 ==========

def plot_fan_chart(time_points, mean_values, percentiles_dict, save_path=None, title=None):
    """
    扇形图（Fan Chart）- 预测不确定性可视化

    Parameters:
    -----------
    time_points : array-like
        时间点
    mean_values : array-like
        均值预测
    percentiles_dict : dict
        百分位数字典，例如 {5: lower_5, 25: lower_25, 75: upper_75, 95: upper_95}
    save_path : str or None
    title : str or None

    Example:
    --------
    time = np.arange(0, 20)
    mean = time * 2 + 10
    p5 = mean - time * 0.5
    p25 = mean - time * 0.3
    p75 = mean + time * 0.3
    p95 = mean + time * 0.5
    plot_fan_chart(time, mean, {5: p5, 25: p25, 75: p75, 95: p95})
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.7))

    time_points = np.array(time_points)
    mean_values = np.array(mean_values)

    # 绘制均值线
    ax.plot(time_points, mean_values, 'k-', linewidth=2, label='Mean', zorder=5)

    # 绘制扇形区间（从外到内）
    colors = get_colors(1, palette='wong')
    base_color = colors[0]

    # 假设成对出现：(5, 95), (25, 75)
    percentile_pairs = []
    sorted_keys = sorted(percentiles_dict.keys())

    for i in range(len(sorted_keys) // 2):
        lower_key = sorted_keys[i]
        upper_key = sorted_keys[-(i + 1)]
        percentile_pairs.append((lower_key, upper_key))

    # 从外到内，透明度递减
    n_bands = len(percentile_pairs)
    for i, (lower_key, upper_key) in enumerate(percentile_pairs):
        alpha = 0.15 + (i * 0.15)
        ax.fill_between(time_points,
                        percentiles_dict[lower_key],
                        percentiles_dict[upper_key],
                        color=base_color, alpha=alpha,
                        label=f'{lower_key}-{upper_key}%', zorder=i + 1)

    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend(loc='best', frameon=False, fontsize=7)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


def plot_spaghetti(time_points, scenarios_matrix, mean_line=True, save_path=None, title=None):
    """
    Spaghetti 图（意大利面图）- 多情景轨迹可视化

    Parameters:
    -----------
    time_points : array-like
        时间点
    scenarios_matrix : 2D array
        情景矩阵，shape = (n_scenarios, n_timepoints)
    mean_line : bool
        是否显示均值线
    save_path : str or None
    title : str or None

    Example:
    --------
    time = np.arange(0, 20)
    n_scenarios = 100
    scenarios = np.array([time * 2 + np.random.normal(0, 5, len(time)) for _ in range(n_scenarios)])
    plot_spaghetti(time, scenarios, mean_line=True)
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.7))

    time_points = np.array(time_points)
    scenarios_matrix = np.array(scenarios_matrix)

    n_scenarios = scenarios_matrix.shape[0]
    colors = get_colors(1, palette='wong')

    # 绘制所有情景（半透明）
    for scenario in scenarios_matrix:
        ax.plot(time_points, scenario, color=colors[0], alpha=0.05, linewidth=0.5, zorder=1)

    # 绘制均值线
    if mean_line:
        mean_trajectory = np.mean(scenarios_matrix, axis=0)
        ax.plot(time_points, mean_trajectory, 'k-', linewidth=2, label='Mean', zorder=5)

    # 绘制百分位数区间（可选）
    p5 = np.percentile(scenarios_matrix, 5, axis=0)
    p95 = np.percentile(scenarios_matrix, 95, axis=0)
    ax.fill_between(time_points, p5, p95, color='gray', alpha=0.2,
                    label='5-95% Range', zorder=2)

    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend(loc='best', frameon=False, fontsize=8)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')
    else:
        ax.set_title(f'Spaghetti Plot ({n_scenarios} scenarios)', fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


# ========== 辅助函数 ==========

if __name__ == '__main__':
    print("Advanced Comparison & Uncertainty Plots Library loaded successfully!")
    print("\nAvailable functions:")
    print("- plot_dumbbell (哑铃图)")
    print("- plot_slope_chart (斜率图)")
    print("- plot_waterfall (瀑布图)")
    print("- plot_bullet_chart (子弹图)")
    print("- plot_fan_chart (扇形图)")
    print("- plot_spaghetti (Spaghetti图)")
