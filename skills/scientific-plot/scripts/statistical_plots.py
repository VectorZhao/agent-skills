"""
Statistical Plots Library - 统计分析图表库
支持 Bootstrap、置信区间、分布分析、回归诊断等高级统计可视化

Author: Enhanced by Claude
Date: 2026-07-26
Dependencies: matplotlib, numpy, scipy, seaborn, pandas
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import gaussian_kde
import seaborn as sns
from pathlib import Path

# 导入配置（兼容 v1 和 v2）
try:
    from plot_config_v2 import (setup_matplotlib, fig_size, save_figure,
                                 get_colors, get_cmap, add_significance_bars,
                                 get_significance_symbol)
except ImportError:
    from plot_config import (setup_matplotlib, fig_size, save_figure,
                             get_colors)


# ========== 1. Bootstrap & 置信区间类 ==========

def plot_bootstrap_distribution(data, n_bootstrap=10000, ci=95, statistic='mean',
                                save_path=None, title=None):
    """
    Bootstrap 重采样分布 + 置信区间可视化

    Parameters:
    -----------
    data : array-like
        原始数据
    n_bootstrap : int
        重采样次数（默认 10000）
    ci : float
        置信水平（百分比，默认 95）
    statistic : str or callable
        统计量：'mean', 'median', 'std', 或自定义函数
    save_path : str or None
        保存路径（不含扩展名）
    title : str or None
        图表标题

    Returns:
    --------
    dict : {'mean': float, 'ci_lower': float, 'ci_upper': float, 'bootstrap_values': array}
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.7))

    # 统计量映射
    stat_func_map = {
        'mean': np.mean,
        'median': np.median,
        'std': np.std,
    }
    stat_func = stat_func_map.get(statistic, statistic)

    # Bootstrap 重采样
    bootstrap_values = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_values.append(stat_func(sample))

    bootstrap_values = np.array(bootstrap_values)

    # 计算置信区间
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(bootstrap_values, alpha)
    ci_upper = np.percentile(bootstrap_values, 100 - alpha)
    mean_value = np.mean(bootstrap_values)

    # 绘制直方图
    colors = get_colors(1, palette='wong')
    ax.hist(bootstrap_values, bins=50, density=True, alpha=0.7,
            color=colors[0], edgecolor='black', linewidth=0.5, label='Bootstrap distribution')

    # 叠加 KDE
    kde = gaussian_kde(bootstrap_values)
    x_range = np.linspace(bootstrap_values.min(), bootstrap_values.max(), 200)
    ax.plot(x_range, kde(x_range), 'k-', linewidth=1.2, label='KDE')

    # 标注置信区间
    ax.axvline(ci_lower, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(ci_upper, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(mean_value, color='black', linewidth=2, label=f'Mean = {mean_value:.3f}')

    # 添加置信区间阴影
    y_max = kde(x_range).max()
    ax.fill_betweenx([0, y_max * 1.1], ci_lower, ci_upper, alpha=0.2, color='red',
                     label=f'{ci}% CI [{ci_lower:.3f}, {ci_upper:.3f}]')

    ax.set_xlabel(f'Bootstrap {statistic.capitalize()}')
    ax.set_ylabel('Density')
    ax.set_ylim(0, y_max * 1.15)
    ax.legend(loc='upper right', frameon=False, fontsize=7)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return {
        'mean': mean_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'bootstrap_values': bootstrap_values
    }


def plot_regression_with_ci(x, y, ci=95, n_bootstrap=1000, save_path=None, title=None):
    """
    线性回归 + 置信区间带 + 预测区间带

    Parameters:
    -----------
    x, y : array-like
        数据点
    ci : float
        置信水平（百分比）
    n_bootstrap : int
        Bootstrap 重采样次数
    save_path : str or None
    title : str or None

    Returns:
    --------
    dict : 回归统计信息
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.8))

    x = np.array(x)
    y = np.array(y)

    # 线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # 拟合值和残差
    y_pred = slope * x + intercept
    residuals = y - y_pred
    residual_std = np.std(residuals)

    # 绘制数据点
    colors = get_colors(1, palette='wong')
    ax.scatter(x, y, s=30, c=colors[0], alpha=0.6, edgecolors='k', linewidths=0.5, zorder=5)

    # 绘制回归线
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, 'k-', linewidth=1.5, label=f'y = {slope:.3f}x + {intercept:.3f}', zorder=4)

    # Bootstrap 置信区间
    slopes = []
    intercepts = []
    for _ in range(n_bootstrap):
        indices = np.random.choice(len(x), size=len(x), replace=True)
        x_boot = x[indices]
        y_boot = y[indices]
        slope_boot, intercept_boot, _, _, _ = stats.linregress(x_boot, y_boot)
        slopes.append(slope_boot)
        intercepts.append(intercept_boot)

    # 计算置信区间
    y_fit_boots = []
    for s, i in zip(slopes, intercepts):
        y_fit_boots.append(s * x_fit + i)

    y_fit_boots = np.array(y_fit_boots)
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(y_fit_boots, alpha, axis=0)
    ci_upper = np.percentile(y_fit_boots, 100 - alpha, axis=0)

    # 预测区间（更宽）
    pred_lower = y_fit - 1.96 * residual_std
    pred_upper = y_fit + 1.96 * residual_std

    # 绘制区间带
    ax.fill_between(x_fit, ci_lower, ci_upper, alpha=0.3, color='blue',
                    label=f'{ci}% Confidence Interval', zorder=2)
    ax.fill_between(x_fit, pred_lower, pred_upper, alpha=0.15, color='gray',
                    label='95% Prediction Interval', zorder=1)

    # 统计信息文本框
    textstr = f'R² = {r_value**2:.3f}\np = {p_value:.4f}\nn = {len(x)}'
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend(loc='lower right', frameon=False, fontsize=7)

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }


# ========== 2. 分布分析类 ==========

def plot_qq(data, distribution='norm', save_path=None, title=None):
    """
    Q-Q 图（分位数-分位数图）用于检验数据是否符合某个分布

    Parameters:
    -----------
    data : array-like
        数据
    distribution : str
        理论分布：'norm' (正态), 't', 'expon', 'uniform' 等
    save_path : str or None
    title : str or None

    Returns:
    --------
    dict : Shapiro-Wilk 正态性检验结果
    """
    setup_matplotlib(journal='nature')
    fig, ax = plt.subplots(figsize=fig_size(8.9, aspect=0.9))

    # 绘制 Q-Q 图
    stats.probplot(data, dist=distribution, plot=ax)

    # 美化
    ax.get_lines()[0].set_marker('o')
    ax.get_lines()[0].set_markersize(4)
    ax.get_lines()[0].set_markerfacecolor(get_colors(1, 'wong')[0])
    ax.get_lines()[0].set_markeredgecolor('k')
    ax.get_lines()[0].set_markeredgewidth(0.3)
    ax.get_lines()[0].set_linestyle('')

    ax.get_lines()[1].set_color('red')
    ax.get_lines()[1].set_linewidth(1.5)
    ax.get_lines()[1].set_linestyle('--')

    # 正态性检验
    if distribution == 'norm':
        w_stat, p_value = stats.shapiro(data)
        textstr = f'Shapiro-Wilk Test:\nW = {w_stat:.4f}\np = {p_value:.4f}'
        if p_value < 0.05:
            textstr += '\n(Reject normality)'
        else:
            textstr += '\n(Normal)'

        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=8,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold')
    else:
        ax.set_title('Q-Q Plot', fontsize=10, fontweight='bold')

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    if distribution == 'norm':
        return {'w_statistic': w_stat, 'p_value': p_value}
    else:
        return {}


def plot_ridgeplot(data_dict, save_path=None, title=None):
    """
    Ridge Plot（又名 Joy Plot）- 多组分布对比

    Parameters:
    -----------
    data_dict : dict
        {组名: 数据数组} 的字典
    save_path : str or None
    title : str or None
    """
    setup_matplotlib(journal='nature')

    n_groups = len(data_dict)
    fig, axes = plt.subplots(n_groups, 1, figsize=fig_size(8.9, aspect=0.3 * n_groups),
                             sharex=True)

    if n_groups == 1:
        axes = [axes]

    colors = get_colors(n_groups, palette='tol_muted')

    # 找全局 x 范围
    all_data = np.concatenate(list(data_dict.values()))
    x_min, x_max = all_data.min(), all_data.max()
    x_range = np.linspace(x_min, x_max, 200)

    for i, (label, data) in enumerate(data_dict.items()):
        ax = axes[i]

        # 计算 KDE
        kde = gaussian_kde(data)
        y = kde(x_range)

        # 绘制填充曲线
        ax.fill_between(x_range, 0, y, alpha=0.7, color=colors[i])
        ax.plot(x_range, y, color='black', linewidth=0.8)

        # 添加标签
        ax.text(0.02, 0.5, label, transform=ax.transAxes, fontsize=9,
                va='center', fontweight='bold')

        # 隐藏 y 轴
        ax.set_ylim(0, y.max() * 1.3)
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # 只在最后一个子图显示 x 轴标签
        if i < n_groups - 1:
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)

    axes[-1].set_xlabel('Value', fontsize=9)

    if title:
        fig.suptitle(title, fontsize=10, fontweight='bold', y=0.98)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


# ========== 3. 回归诊断类 ==========

def plot_regression_diagnostics(x, y, save_path=None, title=None):
    """
    回归诊断四合一图：
    1. 残差 vs 拟合值
    2. Q-Q 图
    3. Scale-Location 图
    4. 残差 vs 杠杆值

    Parameters:
    -----------
    x, y : array-like
        数据
    save_path : str or None
    title : str or None
    """
    setup_matplotlib(journal='nature')
    fig, axes = plt.subplots(2, 2, figsize=fig_size(18.3, aspect=0.9))

    x = np.array(x)
    y = np.array(y)

    # 线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    y_pred = slope * x + intercept
    residuals = y - y_pred
    standardized_residuals = residuals / np.std(residuals)

    colors = get_colors(1, palette='wong')

    # 1. 残差 vs 拟合值
    axes[0, 0].scatter(y_pred, residuals, alpha=0.6, s=25, c=colors[0],
                      edgecolors='k', linewidths=0.3)
    axes[0, 0].axhline(0, color='red', linestyle='--', linewidth=1)
    axes[0, 0].set_xlabel('Fitted values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title('Residuals vs Fitted', fontsize=9, fontweight='bold')

    # 2. Q-Q 图
    stats.probplot(residuals, dist="norm", plot=axes[0, 1])
    axes[0, 1].get_lines()[0].set_markersize(4)
    axes[0, 1].get_lines()[0].set_markerfacecolor(colors[0])
    axes[0, 1].get_lines()[0].set_markeredgecolor('k')
    axes[0, 1].get_lines()[0].set_markeredgewidth(0.3)
    axes[0, 1].get_lines()[1].set_color('red')
    axes[0, 1].get_lines()[1].set_linewidth(1.5)
    axes[0, 1].set_title('Normal Q-Q', fontsize=9, fontweight='bold')

    # 3. Scale-Location 图
    axes[1, 0].scatter(y_pred, np.sqrt(np.abs(standardized_residuals)),
                      alpha=0.6, s=25, c=colors[0], edgecolors='k', linewidths=0.3)
    axes[1, 0].set_xlabel('Fitted values')
    axes[1, 0].set_ylabel('√|Standardized residuals|')
    axes[1, 0].set_title('Scale-Location', fontsize=9, fontweight='bold')

    # 4. 残差 vs 顺序（简化版的 Leverage plot）
    axes[1, 1].scatter(range(len(residuals)), standardized_residuals,
                      alpha=0.6, s=25, c=colors[0], edgecolors='k', linewidths=0.3)
    axes[1, 1].axhline(0, color='red', linestyle='--', linewidth=1)
    axes[1, 1].axhline(2, color='orange', linestyle=':', linewidth=1, alpha=0.7)
    axes[1, 1].axhline(-2, color='orange', linestyle=':', linewidth=1, alpha=0.7)
    axes[1, 1].set_xlabel('Observation')
    axes[1, 1].set_ylabel('Standardized residuals')
    axes[1, 1].set_title('Residuals vs Order', fontsize=9, fontweight='bold')

    if title:
        fig.suptitle(title, fontsize=11, fontweight='bold', y=0.98)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return fig


# ========== 4. 相关性分析类 ==========

def plot_correlation_matrix(df, method='pearson', show_significance=True,
                            save_path=None, title=None):
    """
    相关性矩阵热力图 + 显著性标注

    Parameters:
    -----------
    df : pandas.DataFrame
        数据框（只包含数值列）
    method : str
        相关系数类型：'pearson', 'spearman', 'kendall'
    show_significance : bool
        是否显示显著性标注
    save_path : str or None
    title : str or None
    """
    setup_matplotlib(journal='nature')

    n_vars = len(df.columns)
    fig, ax = plt.subplots(figsize=fig_size(12, aspect=1.0))

    # 计算相关系数
    corr_matrix = df.corr(method=method)

    # 计算 p 值
    p_matrix = np.ones((n_vars, n_vars))
    if show_significance:
        for i in range(n_vars):
            for j in range(i+1, n_vars):
                if method == 'pearson':
                    _, p_val = stats.pearsonr(df.iloc[:, i], df.iloc[:, j])
                elif method == 'spearman':
                    _, p_val = stats.spearmanr(df.iloc[:, i], df.iloc[:, j])
                else:
                    _, p_val = stats.kendalltau(df.iloc[:, i], df.iloc[:, j])
                p_matrix[i, j] = p_val
                p_matrix[j, i] = p_val

    # 绘制热力图
    try:
        cmap = get_cmap('roma')  # 发散色图
    except:
        cmap = 'RdBu_r'

    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap=cmap, center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.5,
                cbar_kws={'shrink': 0.8, 'label': f'{method.capitalize()} Correlation'},
                ax=ax)

    # 添加显著性标注
    if show_significance:
        for i in range(n_vars):
            for j in range(n_vars):
                if i != j:
                    symbol = get_significance_symbol(p_matrix[i, j])
                    if symbol != 'ns':
                        # 根据背景颜色选择文字颜色
                        text_color = 'white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black'
                        ax.text(j + 0.5, i + 0.7, symbol, ha='center', va='center',
                               fontsize=10, color=text_color, fontweight='bold')

    if title:
        ax.set_title(title, fontsize=10, fontweight='bold', pad=15)
    else:
        ax.set_title('Correlation Matrix (* p<0.05, ** p<0.01, *** p<0.001)',
                    fontsize=9, pad=15)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return corr_matrix


# ========== 5. 时间序列分析类 ==========

def plot_time_series_decomposition(data, period=None, model='additive',
                                   save_path=None, title=None):
    """
    时间序列分解图（趋势 + 季节性 + 残差）

    Parameters:
    -----------
    data : array-like or pd.Series
        时间序列数据
    period : int or None
        周期长度（None 则自动检测）
    model : str
        分解模型：'additive' (加法) 或 'multiplicative' (乘法)
    save_path : str or None
    title : str or None
    """
    from statsmodels.tsa.seasonal import seasonal_decompose

    setup_matplotlib(journal='nature')

    # 时间序列分解
    if period is None:
        # 简单自相关检测周期
        from statsmodels.tsa.stattools import acf
        acf_values = acf(data, nlags=min(len(data)//2, 50))
        period = np.argmax(acf_values[1:]) + 1

    result = seasonal_decompose(data, model=model, period=period, extrapolate_trend='freq')

    # 四个子图：原始 + 趋势 + 季节 + 残差
    fig, axes = plt.subplots(4, 1, figsize=fig_size(18.3, aspect=1.2), sharex=True)

    colors = get_colors(4, palette='tol_vibrant')

    # 原始序列
    axes[0].plot(result.observed, color=colors[0], linewidth=0.8)
    axes[0].set_ylabel('Observed', fontsize=8)
    axes[0].set_title('Time Series Decomposition', fontsize=10, fontweight='bold')

    # 趋势
    axes[1].plot(result.trend, color=colors[1], linewidth=0.8)
    axes[1].set_ylabel('Trend', fontsize=8)

    # 季节性
    axes[2].plot(result.seasonal, color=colors[2], linewidth=0.8)
    axes[2].set_ylabel('Seasonal', fontsize=8)

    # 残差
    axes[3].plot(result.resid, color=colors[3], linewidth=0.8)
    axes[3].axhline(0, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    axes[3].set_ylabel('Residual', fontsize=8)
    axes[3].set_xlabel('Time', fontsize=8)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, formats=['pdf', 'jpg'])

    return result


# ========== 辅���函数 ==========

if __name__ == '__main__':
    print("Statistical Plots Library loaded successfully!")
    print("\nAvailable functions:")
    print("- plot_bootstrap_distribution")
    print("- plot_regression_with_ci")
    print("- plot_qq")
    print("- plot_ridgeplot")
    print("- plot_regression_diagnostics")
    print("- plot_correlation_matrix")
    print("- plot_time_series_decomposition")
