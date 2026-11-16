"""
Geochemistry Diagram Templates

Pre-built field boundaries, normalization data, and plotting functions for
common geoscience diagrams:
- TAS (Total Alkali-Silica) diagram
- Harker variation diagrams
- REE spider diagram (with multiple normalization references)
- Trace element spider diagram
- Common discrimination diagrams (Pearce, Wood)
- Ternary diagram helpers
- Isotope diagram templates
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection


# ====================================================================
# TAS Diagram (Le Bas et al., 1986 + Le Maitre et al., 2002)
# ====================================================================

# Field boundaries: list of (x_array, y_array) line segments
TAS_LINES = [
    # Outer boundary / dividing lines
    ([41, 41], [0, 7]),
    ([41, 52.5], [7, 14]),
    ([45, 45], [0, 5]),
    ([48.4, 53], [0, 7]),
    ([52, 52], [0, 5]),
    ([52, 57], [5, 5.9]),
    ([57, 57], [0, 5.9]),
    ([57, 63], [5.9, 7]),
    ([63, 63], [0, 7]),
    ([69, 69], [0, 8]),
    ([69, 77.3], [8, 0]),
    ([45, 52], [5, 5]),
    ([52, 57], [5, 5.9]),
    ([48.4, 52], [5, 5]),
    ([52.5, 57.6], [14, 11.7]),
    ([57.6, 63], [11.7, 7]),
    ([63, 69], [7, 8]),
    ([45, 49.4], [9.4, 7.3]),
    ([49.4, 53], [7.3, 7]),
    ([53, 57.6], [7, 11.7]),
    ([48.4, 53], [0, 7]),
    ([41, 45], [3, 3]),
    # Additional internal boundaries
    ([41, 45], [7, 9.4]),
    ([45, 48.4], [5, 0]),
]

# Field labels with positions: (x, y, label)
TAS_LABELS = [
    (43, 1.5, "Picrobasalt"),
    (44.5, 4, "Basalt"),
    (49, 2.5, "Basaltic\nandesite"),
    (54.5, 2.5, "Andesite"),
    (60, 3, "Dacite"),
    (68, 3.5, "Rhyolite"),
    (49, 6, "Trachy-\nbasalt"),
    (53.5, 8, "Basaltic\ntrachy-\nandesite"),
    (57.5, 9, "Trachy-\nandesite"),
    (63, 11.5, "Trachyte /\nTrachydacite"),
    (49, 9.5, "Tephrite /\nBasanite"),
    (45, 12, "Phono-\ntephrite"),
    (49, 13, "Tephri-\nphonolite"),
    (53, 14.5, "Phonolite"),
    (43, 6.5, "Foidite"),
]

TAS_LABELS_CN = [
    (43, 1.5, "\u82e6\u6a44\u5ca9"),
    (44.5, 4, "\u7384\u6b66\u5ca9"),
    (49, 2.5, "\u7384\u6b66\u5b89\u5c71\u5ca9"),
    (54.5, 2.5, "\u5b89\u5c71\u5ca9"),
    (60, 3, "\u82f1\u5b89\u5ca9"),
    (68, 3.5, "\u6d41\u7eb9\u5ca9"),
    (49, 6, "\u7c97\u9762\u7384\u6b66\u5ca9"),
    (53.5, 8, "\u7c97\u9762\u7384\u6b66\n\u5b89\u5c71\u5ca9"),
    (57.5, 9, "\u7c97\u9762\u5b89\u5c71\u5ca9"),
    (63, 11.5, "\u7c97\u9762\u5ca9"),
    (49, 9.5, "\u78b1\u7384\u5ca9"),
    (45, 12, "\u78b1\u7384\u54cd\u5ca9"),
    (49, 13, "\u54cd\u78b1\u7384\u5ca9"),
    (53, 14.5, "\u54cd\u5ca9"),
    (43, 6.5, "\u4f3c\u957f\u77f3\u5ca9"),
]


def draw_tas_fields(ax, lang="en", field_alpha=0.08, label_fontsize=6):
    """Draw TAS classification fields on an axes.

    Args:
        ax: matplotlib axes
        lang: "en" or "cn" for label language
        field_alpha: transparency of field fills
        label_fontsize: size for field labels
    """
    # Draw boundary lines
    for xdata, ydata in TAS_LINES:
        ax.plot(xdata, ydata, 'k-', linewidth=0.5, zorder=1)

    # Add labels
    labels = TAS_LABELS_CN if lang == "cn" else TAS_LABELS
    for x, y, text in labels:
        ax.text(x, y, text, fontsize=label_fontsize, ha='center', va='center',
                color='#555555', style='italic', zorder=0)

    # Axes setup
    ax.set_xlim(35, 80)
    ax.set_ylim(0, 16)
    ax.set_xlabel("SiO$_2$ (wt%)")
    ax.set_ylabel("Na$_2$O + K$_2$O (wt%)")


# ====================================================================
# REE Normalization References
# ====================================================================

# Chondrite (Sun & McDonough, 1989) - most commonly used
CHONDRITE_SM89 = {
    "La": 0.237, "Ce": 0.613, "Pr": 0.0928, "Nd": 0.457,
    "Sm": 0.148, "Eu": 0.0563, "Gd": 0.199, "Tb": 0.0361,
    "Dy": 0.246, "Ho": 0.0546, "Er": 0.160, "Tm": 0.0247,
    "Yb": 0.161, "Lu": 0.0246, "Y": 1.57,
}

# Primitive Mantle (Sun & McDonough, 1989)
PM_SM89 = {
    "Cs": 0.021, "Rb": 0.6, "Ba": 6.6, "Th": 0.0795, "U": 0.0203,
    "Nb": 0.658, "Ta": 0.037, "K": 240, "La": 0.648, "Ce": 1.675,
    "Pb": 0.15, "Pr": 0.254, "Sr": 19.9, "Nd": 1.250, "Zr": 10.5,
    "Hf": 0.283, "Sm": 0.406, "Eu": 0.154, "Ti": 1205,
    "Gd": 0.544, "Tb": 0.099, "Dy": 0.674, "Y": 4.3,
    "Ho": 0.149, "Er": 0.438, "Tm": 0.068, "Yb": 0.441, "Lu": 0.0675,
}

# N-MORB (Sun & McDonough, 1989)
NMORB_SM89 = {
    "Cs": 0.007, "Rb": 0.56, "Ba": 6.3, "Th": 0.12, "U": 0.047,
    "Nb": 2.33, "Ta": 0.132, "K": 600, "La": 2.50, "Ce": 7.5,
    "Pb": 0.30, "Pr": 1.32, "Sr": 90, "Nd": 7.3, "Zr": 74,
    "Hf": 2.05, "Sm": 2.63, "Eu": 1.02, "Ti": 7600,
    "Gd": 3.68, "Tb": 0.67, "Dy": 4.55, "Y": 28,
    "Ho": 1.01, "Er": 2.97, "Tm": 0.456, "Yb": 3.05, "Lu": 0.455,
}

# Upper Continental Crust (Rudnick & Gao, 2003)
UCC_RG2003 = {
    "La": 30, "Ce": 64, "Pr": 7.1, "Nd": 26, "Sm": 4.5,
    "Eu": 0.88, "Gd": 3.8, "Tb": 0.64, "Dy": 3.5, "Ho": 0.80,
    "Er": 2.3, "Tm": 0.33, "Yb": 2.2, "Lu": 0.32, "Y": 22,
}


def normalize_data(data_dict, reference="chondrite_sm89"):
    """Normalize geochemical data to a reference.

    Args:
        data_dict: {element: value} or pandas Series
        reference: one of "chondrite_sm89", "pm_sm89", "nmorb_sm89", "ucc_rg2003"

    Returns:
        dict of normalized values
    """
    refs = {
        "chondrite_sm89": CHONDRITE_SM89,
        "chondrite": CHONDRITE_SM89,
        "pm_sm89": PM_SM89,
        "pm": PM_SM89,
        "primitive_mantle": PM_SM89,
        "nmorb_sm89": NMORB_SM89,
        "nmorb": NMORB_SM89,
        "ucc_rg2003": UCC_RG2003,
        "ucc": UCC_RG2003,
    }
    ref = refs.get(reference.lower(), CHONDRITE_SM89)

    result = {}
    for elem, val in data_dict.items():
        if elem in ref and ref[elem] > 0 and val is not None:
            result[elem] = val / ref[elem]
    return result


# ====================================================================
# Harker Diagram Setup
# ====================================================================

# Common major element oxides for Harker diagrams
HARKER_Y_ELEMENTS = [
    "TiO2", "Al2O3", "Fe2O3T", "FeOT", "MnO",
    "MgO", "CaO", "Na2O", "K2O", "P2O5",
]

# Pretty labels for oxides
OXIDE_LABELS = {
    "SiO2": "SiO$_2$ (wt%)",
    "TiO2": "TiO$_2$ (wt%)",
    "Al2O3": "Al$_2$O$_3$ (wt%)",
    "Fe2O3": "Fe$_2$O$_3$ (wt%)",
    "Fe2O3T": "Fe$_2$O$_3^T$ (wt%)",
    "FeO": "FeO (wt%)",
    "FeOT": "FeO$^T$ (wt%)",
    "MnO": "MnO (wt%)",
    "MgO": "MgO (wt%)",
    "CaO": "CaO (wt%)",
    "Na2O": "Na$_2$O (wt%)",
    "K2O": "K$_2$O (wt%)",
    "P2O5": "P$_2$O$_5$ (wt%)",
    "LOI": "LOI (wt%)",
    "Na2O+K2O": "Na$_2$O + K$_2$O (wt%)",
    "FeOT/MgO": "FeO$^T$/MgO",
    "Mg#": "Mg#",
}

# Trace element labels
TRACE_LABELS = {
    "Ba": "Ba (ppm)", "Rb": "Rb (ppm)", "Sr": "Sr (ppm)",
    "Zr": "Zr (ppm)", "Nb": "Nb (ppm)", "Y": "Y (ppm)",
    "Th": "Th (ppm)", "U": "U (ppm)", "La": "La (ppm)",
    "Ce": "Ce (ppm)", "Nd": "Nd (ppm)", "Sm": "Sm (ppm)",
    "Eu": "Eu (ppm)", "Gd": "Gd (ppm)", "Yb": "Yb (ppm)",
    "Lu": "Lu (ppm)", "Hf": "Hf (ppm)", "Ta": "Ta (ppm)",
    "Pb": "Pb (ppm)", "Cr": "Cr (ppm)", "Ni": "Ni (ppm)",
    "V": "V (ppm)", "Co": "Co (ppm)", "Cu": "Cu (ppm)",
    "Zn": "Zn (ppm)",
}


def get_axis_label(element):
    """Get formatted axis label for an element/oxide."""
    return OXIDE_LABELS.get(element, TRACE_LABELS.get(element, element))


def setup_harker_grid(n_elements=None, elements=None, ncols=3):
    """Create a Harker diagram grid (SiO2 vs multiple oxides).

    Args:
        n_elements: number of elements (default 8)
        elements: specific element list (overrides n_elements)
        ncols: columns in the grid

    Returns:
        fig, axes_list, element_list
    """
    if elements is None:
        elements = ["TiO2", "Al2O3", "Fe2O3T", "MgO",
                     "CaO", "Na2O", "K2O", "P2O5"]
    if n_elements:
        elements = elements[:n_elements]

    nrows = (len(elements) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(ncols * 3.5, nrows * 3),
                              constrained_layout=True)
    axes_flat = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    # Hide unused axes
    for i in range(len(elements), len(axes_flat)):
        axes_flat[i].set_visible(False)

    # Set x-label on bottom row only
    for i, (ax, elem) in enumerate(zip(axes_flat, elements)):
        ax.set_ylabel(get_axis_label(elem))
        if i >= (nrows - 1) * ncols:
            ax.set_xlabel(get_axis_label("SiO2"))

    return fig, axes_flat[:len(elements)], elements


# ====================================================================
# Isotope Diagram Templates
# ====================================================================

# Common fluid source fields for delta18O vs deltaD diagram
FLUID_SOURCE_FIELDS = {
    "meteoric_water_line": {
        "slope": 8, "intercept": 10,
        "label": "Global Meteoric Water Line",
        "equation": r"$\delta D = 8\delta^{18}O + 10$",
    },
    "magmatic_water": {
        "d18O_range": (5.5, 10.0),
        "dD_range": (-80, -40),
        "label": "Magmatic Water",
    },
    "metamorphic_water": {
        "d18O_range": (5, 25),
        "dD_range": (-70, -20),
        "label": "Metamorphic Water",
    },
    "formation_water": {
        "d18O_range": (-5, 15),
        "dD_range": (-150, 10),
        "label": "Formation Water",
    },
    "seawater": {
        "d18O_range": (-1, 1),
        "dD_range": (-5, 5),
        "label": "Seawater (SMOW)",
    },
}


def draw_fluid_source_diagram(ax, show_fields=None, lang="en"):
    """Draw delta18O vs deltaD fluid source diagram.

    Args:
        ax: matplotlib axes
        show_fields: list of field names to show, None=all
        lang: "en" or "cn"
    """
    if show_fields is None:
        show_fields = list(FLUID_SOURCE_FIELDS.keys())

    # Meteoric water line
    if "meteoric_water_line" in show_fields:
        x_mwl = np.linspace(-25, 10, 100)
        y_mwl = 8 * x_mwl + 10
        ax.plot(x_mwl, y_mwl, 'b--', linewidth=0.8, alpha=0.7,
                label="GMWL")

    # Source fields (as rectangles)
    field_colors = {
        "magmatic_water": ("#FF6B6B", 0.15),
        "metamorphic_water": ("#4ECDC4", 0.15),
        "formation_water": ("#95E1D3", 0.10),
        "seawater": ("#0072B2", 0.20),
    }

    for name in show_fields:
        if name == "meteoric_water_line":
            continue
        field = FLUID_SOURCE_FIELDS.get(name)
        if not field or "d18O_range" not in field:
            continue

        color, alpha = field_colors.get(name, ("#CCCCCC", 0.1))
        x_range = field["d18O_range"]
        y_range = field["dD_range"]

        rect = mpatches.Rectangle(
            (x_range[0], y_range[0]),
            x_range[1] - x_range[0],
            y_range[1] - y_range[0],
            linewidth=0.5, edgecolor=color, facecolor=color,
            alpha=alpha, zorder=0
        )
        ax.add_patch(rect)
        cx = (x_range[0] + x_range[1]) / 2
        cy = (y_range[0] + y_range[1]) / 2
        ax.text(cx, cy, field["label"], fontsize=6, ha='center',
                va='center', color='#555555', style='italic')

    ax.set_xlabel(r"$\delta^{18}$O (\u2030, SMOW)")
    ax.set_ylabel(r"$\delta$D (\u2030, SMOW)")


# ====================================================================
# Sulfur Isotope Reference Ranges
# ====================================================================

SULFUR_SOURCE_RANGES = {
    "mantle": {"d34S_range": (-3, 3), "label": "Mantle", "color": "#E69F00"},
    "seawater_sulfate": {"d34S_range": (10, 35), "label": "Seawater sulfate", "color": "#56B4E9"},
    "sedimentary_sulfide": {"d34S_range": (-50, -10), "label": "Sedimentary sulfide", "color": "#009E73"},
    "magmatic": {"d34S_range": (-5, 5), "label": "Magmatic", "color": "#D55E00"},
    "evaporite": {"d34S_range": (10, 30), "label": "Evaporite", "color": "#CC79A7"},
}


# ====================================================================
# Discrimination Diagram Templates
# ====================================================================

# Nb-Y diagram (Pearce & Cann, 1973) for basalt tectonic settings
# Fields: VAB, WPB, MORB, OIB
PEARCE_NB_Y_FIELDS = {
    "VAB": {
        "description": "Volcanic Arc Basalt",
        "x_range": (0.1, 10),
        "y_range": (5, 100),
    },
    "WPB": {
        "description": "Within-Plate Basalt",
        "x_range": (10, 200),
        "y_range": (5, 200),
    },
    "MORB": {
        "description": "Mid-Ocean Ridge Basalt",
        "x_range": (0.5, 30),
        "y_range": (10, 100),
    },
}

# Rb vs Y+Nb diagram (Pearce et al., 1984) for granites
PEARCE_GRANITE_RB_YNB = {
    "boundary_lines": [
        # VAG-syncCOLG boundary
        {"x": [5, 50], "y": [3, 300]},
        # syncCOLG-WPG boundary
        {"x": [50, 50], "y": [3, 300]},
        # VAG-ORG boundary
        {"x": [5, 300], "y": [3, 3]},
    ],
    "labels": [
        (10, 100, "syn-COLG"),
        (200, 100, "WPG"),
        (10, 1.5, "VAG"),
        (200, 1.5, "ORG"),
    ],
}


def draw_pearce_granite_rb_ynb(ax, lang="en"):
    """Draw Pearce et al. (1984) Rb vs Y+Nb tectonic discrimination diagram.

    Args:
        ax: matplotlib axes
        lang: "en" or "cn"
    """
    # Boundary lines (log-log space)
    # VAG/syn-COLG boundary
    ax.plot([1, 80], [1, 400], 'k-', linewidth=0.6)
    # syn-COLG/WPG boundary
    ax.plot([80, 400], [400, 2000], 'k-', linewidth=0.6)
    # VAG/ORG boundary
    ax.plot([1, 400], [2, 50], 'k-', linewidth=0.6)
    # ORG/WPG boundary
    ax.plot([55, 400], [8, 600], 'k-', linewidth=0.6)

    # Field labels
    if lang == "cn":
        labels = [
            (7, 200, "\u540c\u78b0\u649e\u82b1\u5c97\u5ca9"),
            (250, 300, "\u677f\u5185\u82b1\u5c97\u5ca9"),
            (7, 3, "\u706b\u5c71\u5f27\u82b1\u5c97\u5ca9"),
            (200, 3, "\u6d0b\u810a\u82b1\u5c97\u5ca9"),
        ]
    else:
        labels = [
            (7, 200, "syn-COLG"),
            (250, 300, "WPG"),
            (7, 3, "VAG"),
            (200, 3, "ORG"),
        ]

    for x, y, text in labels:
        ax.text(x, y, text, fontsize=7, ha='center', va='center',
                color='#666666', style='italic')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 1000)
    ax.set_ylim(1, 2000)
    ax.set_xlabel("Y + Nb (ppm)")
    ax.set_ylabel("Rb (ppm)")


# ====================================================================
# Ternary Diagram Helpers
# ====================================================================

def ternary_to_cartesian(a, b, c):
    """Convert ternary coordinates (a, b, c) to Cartesian (x, y).

    Convention: a=top, b=left, c=right
    """
    total = a + b + c
    if total == 0:
        return 0, 0
    a, b, c = a / total, b / total, c / total
    x = 0.5 * (2 * c + a)
    y = (np.sqrt(3) / 2) * a
    return x, y


# Common ternary diagrams
TERNARY_DIAGRAMS = {
    "AFM": {
        "top": "A (Na2O + K2O)",
        "left": "F (FeOT)",
        "right": "M (MgO)",
        "description": "AFM diagram (Irvine & Baragar, 1971)",
    },
    "QAP": {
        "top": "Q (Quartz)",
        "left": "A (Alkali Feldspar)",
        "right": "P (Plagioclase)",
        "description": "QAP classification (Streckeisen, 1976)",
    },
    "ACF": {
        "top": "A (Al2O3)",
        "left": "C (CaO)",
        "right": "F (FeO+MgO)",
        "description": "ACF metamorphic facies diagram",
    },
    "AnAbOr": {
        "top": "An (Anorthite)",
        "left": "Ab (Albite)",
        "right": "Or (Orthoclase)",
        "description": "Feldspar classification triangle",
    },
}


# ====================================================================
# Concordia / Discordia for U-Pb Dating
# ====================================================================

# Physical constants for U-Pb system
LAMBDA_238 = 1.55125e-10  # yr^-1
LAMBDA_235 = 9.8485e-10   # yr^-1
U238_U235_RATIO = 137.818


def concordia_curve(t_min_ma=0, t_max_ma=4500, n_points=500):
    """Calculate concordia curve coordinates.

    Args:
        t_min_ma, t_max_ma: age range in Ma
        n_points: number of points

    Returns:
        (x_array, y_array) where x=207Pb/235U, y=206Pb/238U
    """
    t = np.linspace(t_min_ma * 1e6, t_max_ma * 1e6, n_points)
    x = np.exp(LAMBDA_235 * t) - 1  # 207Pb/235U
    y = np.exp(LAMBDA_238 * t) - 1  # 206Pb/238U
    return x, y


def concordia_age_ticks(ages_ma):
    """Get concordia curve positions for specific ages.

    Args:
        ages_ma: list of ages in Ma

    Returns:
        list of (x, y, age_label) tuples
    """
    ticks = []
    for age in ages_ma:
        t = age * 1e6
        x = np.exp(LAMBDA_235 * t) - 1
        y = np.exp(LAMBDA_238 * t) - 1
        ticks.append((x, y, f"{age} Ma"))
    return ticks


def draw_concordia(ax, t_range_ma=(0, 3500), tick_ages_ma=None):
    """Draw concordia curve with age tick marks.

    Args:
        ax: matplotlib axes
        t_range_ma: (min, max) age range in Ma
        tick_ages_ma: list of ages for tick marks (auto if None)
    """
    x, y = concordia_curve(t_range_ma[0], t_range_ma[1])
    ax.plot(x, y, 'k-', linewidth=1.0, zorder=2)

    if tick_ages_ma is None:
        # Auto tick marks every 500 Ma
        tick_ages_ma = list(range(0, int(t_range_ma[1]) + 1, 500))
        if t_range_ma[1] <= 600:
            tick_ages_ma = list(range(0, int(t_range_ma[1]) + 1, 100))

    ticks = concordia_age_ticks(tick_ages_ma)
    for tx, ty, label in ticks:
        ax.plot(tx, ty, 'ko', markersize=3, zorder=3)
        ax.annotate(label, (tx, ty), textcoords="offset points",
                    xytext=(5, 5), fontsize=5.5)

    ax.set_xlabel(r"$^{207}$Pb/$^{235}$U")
    ax.set_ylabel(r"$^{206}$Pb/$^{238}$U")
