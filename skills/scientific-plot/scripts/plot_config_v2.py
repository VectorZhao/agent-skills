"""
Enhanced Plot Configuration System v2.0
集成 SciencePlots + colorcet + cmcrameri + 自动样式优化

Author: Enhanced by Claude
Date: 2026-07-26
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ========== 期刊样式规范 ==========
JOURNAL_SPECS = {
    'nature': {
        'single_col_width_cm': 8.9,
        'double_col_width_cm': 18.3,
        'font_family': 'Arial',
        'font_size': 7,
        'dpi': 300,
        'line_width': 0.5,
        'marker_size': 3,
        'use_latex': False,
    },
    'science': {
        'single_col_width_cm': 9.0,
        'double_col_width_cm': 18.6,
        'font_family': 'Arial',
        'font_size': 7,
        'dpi': 300,
        'line_width': 0.5,
        'marker_size': 3,
        'use_latex': False,
    },
    'elsevier': {  # GCA, EPSL, Lithos, Ore Geology Reviews
        'single_col_width_cm': 9.0,
        'double_col_width_cm': 19.0,
        'font_family': 'Arial',
        'font_size': 8,
        'dpi': 300,
        'line_width': 0.6,
        'marker_size': 4,
        'use_latex': False,
    },
    'ieee': {
        'single_col_width_cm': 8.9,
        'double_col_width_cm': 18.3,
        'font_family': 'Times New Roman',
        'font_size': 8,
        'dpi': 600,
        'line_width': 0.5,
        'marker_size': 3,
        'use_latex': False,
    },
    'geology_gsa': {
        'single_col_width_cm': 8.5,
        'double_col_width_cm': 17.8,
        'font_family': 'Arial',
        'font_size': 8,
        'dpi': 300,
        'line_width': 0.6,
        'marker_size': 4,
        'use_latex': False,
    },
    'chinese_core': {
        'single_col_width_cm': 7.5,
        'double_col_width_cm': 16.0,
        'font_family': 'SimSun',
        'font_size': 9,
        'dpi': 300,
        'line_width': 0.7,
        'marker_size': 4,
        'use_latex': False,
    },
    'default': {
        'single_col_width_cm': 8.5,
        'double_col_width_cm': 17.0,
        'font_family': 'Arial',
        'font_size': 8,
        'dpi': 300,
        'line_width': 0.6,
        'marker_size': 4,
        'use_latex': False,
    },
}

# ========== 色板系统 ==========
COLOR_PALETTES = {
    # Nature NPG 风格（原有，保持兼容）
    'nature_npg': [
        '#E64B35', '#4DBBD5', '#00A087', '#3C5488',
        '#F39B7F', '#8491B4', '#91D1C2', '#DC0000', '#7E6148'
    ],

    # Wong 色盲友好色板（推荐用于学术发表）
    'wong': [
        '#E69F00',  # Orange
        '#56B4E9',  # Sky Blue
        '#009E73',  # Bluish Green
        '#F0E442',  # Yellow
        '#0072B2',  # Blue
        '#D55E00',  # Vermillion
        '#CC79A7',  # Reddish Purple
        '#000000',  # Black
    ],

    # Paul Tol 明亮色板（高对比度）
    'tol_bright': [
        '#4477AA', '#EE6677', '#228833', '#CCBB44',
        '#66CCEE', '#AA3377', '#BBBBBB'
    ],

    # Paul Tol 柔和色板（适合大数据集）
    'tol_muted': [
        '#CC6677', '#332288', '#DDCC77', '#117733',
        '#88CCEE', '#882255', '#44AA99', '#999933',
        '#AA4499', '#DDDDDD'
    ],

    # Paul Tol 高对比度（适合投影）
    'tol_vibrant': [
        '#EE7733', '#0077BB', '#33BBEE', '#EE3377',
        '#CC3311', '#009988', '#BBBBBB'
    ],

    # IBM 色盲安全色板
    'ibm': [
        '#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000'
    ],
}

# ========== 连续色图（推荐使用感知均匀色图）==========
SEQUENTIAL_CMAPS = {
    # cmcrameri 科学色图（需要安装 cmcrameri）
    'batlow': 'cmc.batlow',      # 深→浅，感知均匀
    'roma': 'cmc.roma',          # 发散色图，负→0→正
    'vik': 'cmc.vik',            # 发散色图（蓝-白-红）
    'lapaz': 'cmc.lapaz',        # 连续色图（蓝绿）
    'tokyo': 'cmc.tokyo',        # 连续色图（黑→红）
    'bam': 'cmc.bam',            # 连续色图（蓝→白→橙）

    # colorcet 色图（需要安装 colorcet）
    'fire': 'cc.fire',           # 火焰色
    'rainbow': 'cc.rainbow',     # 彩虹（仅用于相位数据）
    'isolum': 'cc.isolum',       # 等亮度彩虹

    # matplotlib 内置（后备选项）
    'viridis': 'viridis',        # 感知均匀
    'plasma': 'plasma',          # 感知均匀
    'cividis': 'cividis',        # 色盲友好
    'RdBu_r': 'RdBu_r',          # 发散色图（蓝-白-红）
}

# ========== 标记符号列表 ==========
MARKERS = ['o', 's', '^', 'v', 'D', 'p', '*', 'h', '<', '>', 'X', 'P']

# ========== 线型列表 ==========
LINESTYLES = ['-', '--', '-.', ':']

# ========== REE 元素顺序 ==========
REE_ORDER = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']

# ========== 微量元素顺序（Sun & McDonough, 1989）==========
TRACE_ELEMENT_ORDER_SM89 = ['Cs', 'Rb', 'Ba', 'Th', 'U', 'Nb', 'Ta', 'K', 'La', 'Ce', 'Pb', 'Pr', 'Sr',
                             'Nd', 'Sm', 'Zr', 'Hf', 'Eu', 'Ti', 'Gd', 'Tb', 'Dy', 'Y', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']

# ========== 统计显著性符号 ==========
SIGNIFICANCE_SYMBOLS = {
    0.001: '***',
    0.01: '**',
    0.05: '*',
    0.1: '†',
    1.0: 'ns',
}


def setup_matplotlib(journal='default', locale='en'):
    """
    统一样式设置函数

    Parameters:
    -----------
    journal : str
        期刊名称：'nature', 'science', 'elsevier', 'ieee', 'geology_gsa', 'chinese_core', 'default'
    locale : str
        语言环境：'en' 或 'cn'

    Returns:
    --------
    dict : 配置规范字典
    """
    spec = JOURNAL_SPECS.get(journal, JOURNAL_SPECS['default']).copy()

    # 尝试加载 SciencePlots 样式
    try:
        if journal == 'nature':
            plt.style.use(['science', 'nature'])
        elif journal == 'ieee':
            plt.style.use(['science', 'ieee'])
        else:
            plt.style.use(['science', 'no-latex'])
    except:
        # 如果 SciencePlots 未安装，使用手动配置
        pass

    # 覆盖/补充 matplotlib 参数
    plt.rcParams.update({
        'font.family': 'sans-serif' if spec['font_family'] != 'Times New Roman' else 'serif',
        'font.sans-serif': [spec['font_family']] if spec['font_family'] != 'Times New Roman' else [],
        'font.serif': ['Times New Roman'] if spec['font_family'] == 'Times New Roman' else [],
        'font.size': spec['font_size'],
        'axes.labelsize': spec['font_size'],
        'axes.titlesize': spec['font_size'] + 1,
        'axes.linewidth': spec['line_width'],
        'xtick.labelsize': spec['font_size'] - 1,
        'ytick.labelsize': spec['font_size'] - 1,
        'xtick.major.width': spec['line_width'],
        'ytick.major.width': spec['line_width'],
        'legend.fontsize': spec['font_size'] - 1,
        'legend.frameon': False,
        'lines.linewidth': spec['line_width'] * 1.5,
        'lines.markersize': spec['marker_size'],
        'figure.dpi': spec['dpi'],
        'savefig.dpi': spec['dpi'],
        'savefig.bbox': 'tight',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.unicode_minus': locale != 'cn',  # 中文环境下禁用 unicode minus
        'text.usetex': spec['use_latex'],
    })

    # 中文字体特殊处理
    if locale == 'cn':
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
        plt.rcParams['axes.unicode_minus'] = False

    return spec


def fig_size(width_cm, aspect=0.75):
    """
    计算图表尺寸（厘米 → 英寸）

    Parameters:
    -----------
    width_cm : float
        宽度（厘米）
    aspect : float
        高宽比（height / width），默认 0.75

    Returns:
    --------
    tuple : (width_inch, height_inch)
    """
    width_inch = width_cm / 2.54
    height_inch = width_inch * aspect
    return (width_inch, height_inch)


def save_figure(fig, filepath_no_ext, formats=None, dpi=300):
    """
    保存图表为多种格式（默认 PDF + JPG 双输出）

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        图表对象
    filepath_no_ext : str
        文件路径（不含扩展名），例如 "path/to/figure_1"
    formats : list
        输出格式列表，默认为 PDF 和 JPG
    dpi : int or None
        位图格式的分辨率（None 则使用当前 rcParams 设置）

    Returns:
    --------
    list : 保存的文件路径列表
    """
    saved_files = []
    if formats is None:
        formats = ['pdf', 'jpg']

    for fmt in formats:
        filepath = f"{filepath_no_ext}.{fmt}"
        if fmt in ['png', 'jpg', 'tiff']:
            # 位图格式指定 DPI
            fig.savefig(filepath, format=fmt, bbox_inches='tight', pad_inches=0,
                       dpi=dpi if dpi else plt.rcParams['savefig.dpi'])
        else:
            # 矢量格式不需要 DPI
            fig.savefig(filepath, format=fmt, bbox_inches='tight', pad_inches=0, dpi=300)

        saved_files.append(filepath)

    return saved_files


def get_colors(n, palette='wong'):
    """
    获取指定色板的前 n 个颜色

    Parameters:
    -----------
    n : int
        需要的颜色数量
    palette : str
        色板名称（见 COLOR_PALETTES）

    Returns:
    --------
    list : 颜色列表（HEX 格式）
    """
    colors = COLOR_PALETTES.get(palette, COLOR_PALETTES['wong'])

    if n <= len(colors):
        return colors[:n]
    else:
        # 颜色不够时循环使用
        return (colors * (n // len(colors) + 1))[:n]


def get_cmap(cmap_name):
    """
    获取连续色图对象

    Parameters:
    -----------
    cmap_name : str
        色图名称（见 SEQUENTIAL_CMAPS）

    Returns:
    --------
    matplotlib.colors.Colormap
    """
    cmap_path = SEQUENTIAL_CMAPS.get(cmap_name, 'viridis')

    # 尝试加载 cmcrameri 或 colorcet
    if cmap_path.startswith('cmc.'):
        try:
            import cmcrameri.cm as cmc
            return eval(cmap_path)
        except ImportError:
            print(f"Warning: cmcrameri not installed, falling back to viridis")
            return plt.cm.viridis
    elif cmap_path.startswith('cc.'):
        try:
            import colorcet as cc
            return eval(cmap_path)
        except ImportError:
            print(f"Warning: colorcet not installed, falling back to viridis")
            return plt.cm.viridis
    else:
        # matplotlib 内置色图
        return plt.cm.get_cmap(cmap_path)


def add_subplot_labels(axes, labels=None, style='lowercase_paren', fontsize=10, fontweight='bold'):
    """Align upper-left subplot labels vertically with each ylabel."""
    from plot_config import add_subplot_labels as add_labels
    return add_labels(np.asarray(axes, dtype=object).ravel().tolist(), labels=labels,
                      style=style, fontsize=fontsize, fontweight=fontweight)


def get_significance_symbol(p_value):
    """
    根据 p 值返回显著性符号

    Parameters:
    -----------
    p_value : float
        p 值

    Returns:
    --------
    str : 显著性符号
    """
    for threshold, symbol in sorted(SIGNIFICANCE_SYMBOLS.items()):
        if p_value < threshold:
            return symbol
    return 'ns'


def add_significance_bars(ax, pairs, p_values, y_max=None, h=0.02, linewidth=0.8):
    """
    在柱状图上添加显著性标注横杠

    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        坐标轴对象
    pairs : list of tuple
        需要标注的组对，例如 [(0, 1), (1, 2), (0, 2)]
    p_values : list
        对应的 p 值列表
    y_max : float or None
        Y 轴最大值（None 则自动获取）
    h : float
        横杠高度增量（相对于 Y 轴范围）
    linewidth : float
        线宽
    """
    if y_max is None:
        y_max = ax.get_ylim()[1]

    y_range = y_max - ax.get_ylim()[0]

    for i, ((x1, x2), p_val) in enumerate(zip(pairs, p_values)):
        y = y_max + y_range * h * (i + 1)
        symbol = get_significance_symbol(p_val)

        # 绘制横杠
        ax.plot([x1, x1, x2, x2], [y, y + y_range * h * 0.1, y + y_range * h * 0.1, y],
                'k-', linewidth=linewidth)

        # 添加符号
        ax.text((x1 + x2) / 2, y + y_range * h * 0.15, symbol,
                ha='center', va='bottom', fontsize=10)


def apply_nature_npg_style(fig, ax, title, data_source, top_y=0.90, bottom_y=0.08):
    """
    应用 Nature NPG 风格（带上下黑线 + 标题 + 数据来源）

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
    ax : matplotlib.axes.Axes
    title : str
        图表标题
    data_source : str
        数据来源
    top_y : float
        上方黑线位置（figure 坐标）
    bottom_y : float
        下方黑线位置（figure 坐标）
    """
    # 上方分隔线 + 标题
    line_top = plt.Line2D([0.01, 0.99], [top_y, top_y],
                          transform=fig.transFigure, color='black', linewidth=1)
    fig.add_artist(line_top)
    fig.text(0.01, top_y + 0.03, title, fontsize=12, fontweight='bold', ha='left')

    # 下方分隔线 + 数据来源
    line_bottom = plt.Line2D([0.01, 0.99], [bottom_y, bottom_y],
                            transform=fig.transFigure, color='black', linewidth=1)
    fig.add_artist(line_bottom)
    fig.text(0.01, bottom_y - 0.03, data_source, fontsize=9, ha='left', color='#404040')

    # 调整子图位置
    plt.subplots_adjust(top=top_y - 0.08, bottom=bottom_y + 0.10)


# ========== 辅助函数：自动选择最佳色板 ==========
def auto_select_palette(n_colors, context='categorical'):
    """
    根据颜色数量和场景自动选择最佳色板

    Parameters:
    -----------
    n_colors : int
        需要的颜色数
    context : str
        使用场景：'categorical' (分类), 'sequential' (连续), 'diverging' (发散)

    Returns:
    --------
    str : 推荐的色板名称
    """
    if context == 'categorical':
        if n_colors <= 8:
            return 'wong'  # 色盲友好
        elif n_colors <= 10:
            return 'tol_muted'
        else:
            return 'nature_npg'
    elif context == 'sequential':
        return 'batlow'  # cmcrameri 感知均匀
    elif context == 'diverging':
        return 'roma'  # cmcrameri 发散色图
    else:
        return 'wong'


if __name__ == '__main__':
    # 测试代码
    print("Testing plot_config_v2.py...")

    spec = setup_matplotlib(journal='nature')
    print(f"Journal spec loaded: {spec}")

    colors = get_colors(5, palette='wong')
    print(f"Wong palette (5 colors): {colors}")

    print("\nSetup complete!")
