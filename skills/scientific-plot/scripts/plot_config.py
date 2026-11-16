"""
Scientific Plot Configuration Module

Centralized configuration for publication-quality scientific figures:
- Journal-specific figure specs (size, DPI, fonts)
- Color palettes (colorblind-safe, print-friendly)
- Standard font setup for matplotlib
- Element ordering for spider diagrams
- Dual-output helper (PDF + JPG)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

# Try importing optional packages
try:
    import cmcrameri.cm as cmc
    HAS_CMCRAMERI = True
except ImportError:
    HAS_CMCRAMERI = False

try:
    from adjustText import adjust_text
    HAS_ADJUSTTEXT = True
except ImportError:
    HAS_ADJUSTTEXT = False


# ====================================================================
# Journal Figure Specifications
# ====================================================================

JOURNAL_SPECS = {
    # ── Nature / Science tier ──
    "nature": {
        "single_col_width_cm": 8.9,
        "double_col_width_cm": 18.3,
        "max_height_cm": 24.7,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 7,
        "tick_size": 6,
        "label_size": 8,
        "title_size": 8,
        "line_width": 0.5,
        "formats": ["pdf", "eps", "tiff"],
    },
    "science": {
        "single_col_width_cm": 9.0,
        "double_col_width_cm": 18.0,
        "max_height_cm": 24.0,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 7,
        "tick_size": 6,
        "label_size": 8,
        "title_size": 8,
        "line_width": 0.5,
        "formats": ["pdf", "eps"],
    },

    # ── Elsevier journals (GCA, Lithos, EPSL, Ore Geology Reviews) ──
    "elsevier": {
        "single_col_width_cm": 9.0,
        "double_col_width_cm": 18.0,
        "max_height_cm": 24.0,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 8,
        "tick_size": 7,
        "label_size": 9,
        "title_size": 9,
        "line_width": 0.6,
        "formats": ["pdf", "eps", "tiff"],
    },
    "gca": {"_inherit": "elsevier"},
    "lithos": {"_inherit": "elsevier"},
    "epsl": {"_inherit": "elsevier"},
    "ore_geology_reviews": {"_inherit": "elsevier"},
    "chemical_geology": {"_inherit": "elsevier"},

    # ── GSA / GSW journals ──
    "geology_gsa": {
        "single_col_width_cm": 8.5,
        "double_col_width_cm": 17.5,
        "max_height_cm": 23.5,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 8,
        "tick_size": 7,
        "label_size": 9,
        "title_size": 9,
        "line_width": 0.6,
        "formats": ["pdf", "tiff"],
    },

    # ── Springer journals (Mineralium Deposita, CMP) ──
    "springer": {
        "single_col_width_cm": 8.4,
        "double_col_width_cm": 17.4,
        "max_height_cm": 23.4,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 8,
        "tick_size": 7,
        "label_size": 9,
        "title_size": 9,
        "line_width": 0.6,
        "formats": ["pdf", "eps", "tiff"],
    },
    "mineralium_deposita": {"_inherit": "springer"},
    "contributions_mineral_petrol": {"_inherit": "springer"},

    # ── Chinese core journals ──
    "chinese_core": {
        "single_col_width_cm": 7.5,
        "double_col_width_cm": 16.0,
        "max_height_cm": 22.0,
        "dpi": 300,
        "font_family": "Times New Roman",
        "font_size": 8,
        "tick_size": 7,
        "label_size": 9,
        "title_size": 10,
        "line_width": 0.6,
        "formats": ["tiff", "eps"],
        "cjk_font": "SimSun",  # for Chinese labels
    },

    # ── Default (general scientific) ──
    "default": {
        "single_col_width_cm": 8.5,
        "double_col_width_cm": 17.0,
        "max_height_cm": 24.0,
        "dpi": 300,
        "font_family": "Arial",
        "font_size": 8,
        "tick_size": 7,
        "label_size": 9,
        "title_size": 10,
        "line_width": 0.6,
        "formats": ["pdf", "jpg"],
    },
}


def get_journal_spec(journal_key="default"):
    """Get journal spec, resolving inheritance."""
    spec = JOURNAL_SPECS.get(journal_key, JOURNAL_SPECS["default"])
    if "_inherit" in spec:
        parent = JOURNAL_SPECS[spec["_inherit"]].copy()
        parent.update({k: v for k, v in spec.items() if k != "_inherit"})
        return parent
    return spec.copy()


# ====================================================================
# Color Palettes
# ====================================================================

# Qualitative palettes (for categorical data, colorblind-safe)
PALETTE_QUALITATIVE = {
    "wong": [  # Bang Wong's Nature Methods palette
        "#E69F00", "#56B4E9", "#009E73", "#F0E442",
        "#0072B2", "#D55E00", "#CC79A7", "#000000",
    ],
    "tol_bright": [  # Paul Tol's bright
        "#4477AA", "#EE6677", "#228833", "#CCBB44",
        "#66CCEE", "#AA3377", "#BBBBBB",
    ],
    "okabe_ito": [  # Okabe-Ito
        "#E69F00", "#56B4E9", "#009E73", "#F0E442",
        "#0072B2", "#D55E00", "#CC79A7",
    ],
}

# Sequential palettes for heatmaps/density (colorblind-safe)
PALETTE_SEQUENTIAL = {
    "batlow": "cmc.batlow" if HAS_CMCRAMERI else "viridis",
    "roma": "cmc.roma" if HAS_CMCRAMERI else "RdYlBu_r",
    "lajolla": "cmc.lajolla" if HAS_CMCRAMERI else "YlOrRd",
    "viridis": "viridis",
    "plasma": "plasma",
}

# Diverging palettes
PALETTE_DIVERGING = {
    "roma": "cmc.roma" if HAS_CMCRAMERI else "RdBu_r",
    "vik": "cmc.vik" if HAS_CMCRAMERI else "coolwarm",
    "coolwarm": "coolwarm",
}

# Marker styles for scatter plots (max differentiation)
MARKERS_SEQUENCE = ['o', 's', '^', 'D', 'v', 'P', '*', 'X', '<', '>']


def get_colors(n, palette="wong"):
    """Get n colors from a qualitative palette, cycling if needed."""
    pal = PALETTE_QUALITATIVE.get(palette, PALETTE_QUALITATIVE["wong"])
    return [pal[i % len(pal)] for i in range(n)]


def get_cmap(name="batlow"):
    """Get a colormap by name, with cmcrameri fallback."""
    if HAS_CMCRAMERI and name.startswith("cmc."):
        return getattr(cmc, name.replace("cmc.", ""))
    cm_name = PALETTE_SEQUENTIAL.get(name, name)
    if isinstance(cm_name, str) and cm_name.startswith("cmc."):
        return plt.cm.get_cmap("viridis")  # fallback
    return plt.cm.get_cmap(cm_name)


# ====================================================================
# Standard Matplotlib Setup
# ====================================================================

def setup_matplotlib(journal="default", locale="en"):
    """Configure matplotlib rcParams for publication-quality figures.

    Args:
        journal: Journal key from JOURNAL_SPECS
        locale: "en" for English, "cn" for Chinese labels
    """
    spec = get_journal_spec(journal)

    plt.rcParams.update({
        # Font
        'font.family': 'sans-serif' if spec["font_family"] == "Arial" else 'serif',
        'font.sans-serif': [spec["font_family"], "DejaVu Sans"],
        'font.serif': [spec.get("font_family", "Times New Roman"), "DejaVu Serif"],
        'font.size': spec["font_size"],

        # Axes
        'axes.labelsize': spec["label_size"],
        'axes.titlesize': spec["title_size"],
        'axes.linewidth': spec["line_width"],
        'axes.labelpad': 4,
        'axes.unicode_minus': False,

        # Ticks
        'xtick.labelsize': spec["tick_size"],
        'ytick.labelsize': spec["tick_size"],
        'xtick.major.width': spec["line_width"],
        'ytick.major.width': spec["line_width"],
        'xtick.minor.width': spec["line_width"] * 0.7,
        'ytick.minor.width': spec["line_width"] * 0.7,
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.minor.size': 2.0,
        'ytick.minor.size': 2.0,
        'xtick.direction': 'in',
        'ytick.direction': 'in',

        # Legend
        'legend.fontsize': spec["font_size"],
        'legend.frameon': False,
        'legend.handlelength': 1.5,

        # Lines
        'lines.linewidth': 1.0,
        'lines.markersize': 5,

        # Figure
        'figure.dpi': spec["dpi"],
        'savefig.dpi': spec["dpi"],
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0,

        # Grid (off by default for publication)
        'axes.grid': False,

        # Math text
        'mathtext.default': 'regular',
    })

    # Chinese locale needs CJK font for labels
    if locale == "cn":
        cjk = spec.get("cjk_font", "SimSun")
        plt.rcParams['font.sans-serif'] = [cjk, spec["font_family"], "DejaVu Sans"]
        plt.rcParams['axes.unicode_minus'] = False

    return spec


def cm2inch(cm):
    """Convert centimeters to inches."""
    return cm / 2.54


def fig_size(width_cm, height_cm=None, aspect=0.75):
    """Create figure size tuple in inches from cm dimensions."""
    w = cm2inch(width_cm)
    h = cm2inch(height_cm) if height_cm else w * aspect
    return (w, h)


# ====================================================================
# Element Ordering for Spider Diagrams
# ====================================================================

# Standard trace element order (Sun & McDonough 1989 style)
TRACE_ELEMENT_ORDER_SM89 = [
    "Cs", "Rb", "Ba", "Th", "U", "Nb", "Ta", "K", "La", "Ce",
    "Pb", "Pr", "Sr", "Nd", "Zr", "Hf", "Sm", "Eu", "Ti", "Gd",
    "Tb", "Dy", "Y", "Ho", "Er", "Tm", "Yb", "Lu",
]

# REE order (La-Lu)
REE_ORDER = [
    "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb",
    "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
]

# Extended REE (REE + Y)
REEY_ORDER = [
    "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb",
    "Dy", "Y", "Ho", "Er", "Tm", "Yb", "Lu",
]

# Pearce (2008) style
TRACE_ELEMENT_ORDER_PEARCE = [
    "Th", "Nb", "Ta", "La", "Ce", "Pr", "Nd", "Zr", "Hf",
    "Sm", "Eu", "Ti", "Gd", "Tb", "Dy", "Y", "Ho", "Er",
    "Tm", "Yb", "Lu",
]


# ====================================================================
# Figure Save Helper
# ====================================================================

def save_figure(fig, output_path, formats=None, dpi=300, transparent=False):
    """Save figure in multiple formats (default: PDF + JPG).

    Args:
        fig: matplotlib figure object
        output_path: base path without extension (e.g., '/path/to/my_figure')
        formats: list of formats, default ["pdf", "jpg"]
        dpi: resolution for raster formats
        transparent: transparent background

    Returns:
        list of saved file paths
    """
    if formats is None:
        formats = ["pdf", "jpg"]

    base = Path(output_path)
    base.parent.mkdir(parents=True, exist_ok=True)

    saved = []
    for fmt in formats:
        fpath = base.with_suffix(f".{fmt}")
        fig.savefig(
            str(fpath),
            format=fmt,
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0,
            transparent=transparent,
            facecolor='white' if not transparent else 'none',
        )
        saved.append(str(fpath))
        print(f"  Saved: {fpath}")

    return saved


# ====================================================================
# Subplot Label Helper
# ====================================================================

def add_subplot_labels(axes, labels=None, x=-0.12, y=1.06, fontsize=10,
                       fontweight='bold', style='lowercase_paren'):
    """Add (a), (b), (c)... labels to subplots.

    Args:
        axes: list of matplotlib axes
        labels: custom labels, or auto-generate
        x, y: label position in axes coordinates
        style: 'lowercase_paren' → (a), 'lowercase' → a, 'uppercase' → A
    """
    if labels is None:
        n = len(axes)
        if style == 'lowercase_paren':
            labels = [f"({chr(97+i)})" for i in range(n)]
        elif style == 'lowercase':
            labels = [chr(97+i) for i in range(n)]
        elif style == 'uppercase':
            labels = [chr(65+i) for i in range(n)]
        else:
            labels = [f"({chr(97+i)})" for i in range(n)]

    # Update after layout resolves the ylabel position, including during export.
    for ax, label in zip(axes, labels):
        fig = ax.figure
        text = fig.text(0, 0, label, fontsize=fontsize, fontweight=fontweight,
                        va='bottom', ha='center')
        def position(event, ax=ax, text=text, fig=fig):
            renderer = event.renderer
            if ax.get_ylabel():
                box = ax.yaxis.label.get_window_extent(renderer)
                x_display = (box.x0 + box.x1) / 2
            else:
                x_display = ax.bbox.x0
            text.set_position(fig.transFigure.inverted().transform((x_display, ax.bbox.y1)))
        fig.canvas.mpl_connect('draw_event', position)
    fig.canvas.draw()



# ====================================================================
# Axis Formatting Helpers
# ====================================================================

def format_log_axis(ax, which='both'):
    """Format log-scale axes with proper tick labels."""
    if which in ('x', 'both'):
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    if which in ('y', 'both'):
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_minor_formatter(ticker.NullFormatter())


def clean_axes(ax, top=False, right=False):
    """Remove top/right spines for cleaner look."""
    ax.spines['top'].set_visible(top)
    ax.spines['right'].set_visible(right)
    if not top:
        ax.tick_params(top=False)
    if not right:
        ax.tick_params(right=False)
