---
name: scientific-plot
description: >
  Publication-quality scientific figure creation for geoscience research.
  Supports geochemistry diagrams (TAS, Harker, REE spider, trace element spider, discrimination diagrams),
  isotope plots (U-Pb concordia, isochrons, fluid source diagrams, sulfur isotopes),
  ternary diagrams (AFM, QAP, An-Ab-Or), statistical visualizations (scatter, box, violin, heatmap,
  regression), multi-panel combination figures, and stratigraphic/mineralization profiles.
  Output is PDF vector and 300 dpi JPG raster with journal-specific formatting presets
  (Nature, GCA, Lithos, EPSL, Chinese core journals). Uses pyrolite, mpltern, matplotlib, seaborn,
  cmcrameri for colorblind-safe palettes. When the user asks to create scientific figures, plot
  geochemical data, draw diagrams, make academic charts, or produce publication-ready figures.
  Trigger phrases include: "draw TAS diagram", "plot REE spider", "make Harker diagram",
  "plot concordia", "scientific figure", "publication figure", "geochemistry plot",
  "discrimination diagram", "ternary diagram", "isotope plot", "spider diagram",
  "multi-panel figure", "box plot", "scatter plot with regression",
  "draw REE pattern", "trace element spider", "Pearce diagram",
  "fluid source diagram", "stratigraphic column",
  "画TAS图", "画REE蛛网图", "画Harker图", "画谐和图", "画判别图",
  "画三角图", "画散点图", "画箱线图", "科研绘图", "学术图表",
  "画蛛网图", "稀土配分图", "微量元素蛛网图", "同位素图",
  "画图", "作图", "绘制图件", "画地球化学图".
  Also trigger when the user provides Excel/CSV data and asks to visualize it for a paper,
  or when they say "plot this data" or "make a figure from this".
---

# Scientific Plot Skill

> Publication-quality scientific figures for geoscience research. Output: PDF (vector) and JPG (300 dpi).

## Workflow

```
1. Understand request → identify plot type
2. Read data source (Excel/CSV/manual)
3. Select journal format (ask user if not specified, default="default")
4. Generate figure using scripts/ utilities
5. Quality check (data accuracy + visual clarity + format compliance)
6. Save to the requested project location as PDF + JPG at 300 dpi
```

## Core Rules

1. **Always use `scripts/plot_config.py`** for matplotlib setup, colors, and save helpers
2. **Always use `scripts/geo_templates.py`** for geochemistry diagram fields and normalization data
3. **Output**: Save `.pdf` and `.jpg` at 300 dpi; do not save SVG or PNG. Crop outer whitespace with `bbox_inches="tight", pad_inches=0` without clipping labels.
4. **Colorblind-safe**: Use Wong/Tol palettes for categorical, cmcrameri for sequential
5. **No chart junk**: No 3D effects, no unnecessary gridlines, no decorative elements
6. **Subscript/superscript**: Always use LaTeX for chemical formulas (SiO$_2$, $^{207}$Pb/$^{235}$U)
7. **Error bars**: Always include when uncertainty data is available
8. **Figure size**: Match target journal specs from `plot_config.JOURNAL_SPECS`
9. **Script execution**: Use an existing local Python or conda environment. Do not install Python environments in OneDrive; retain only essential scripts and figures there.
10. **Chinese labels**: When user requests Chinese labels (lang="cn"), use SimSun font + unicode_minus=False
11. **⭐ Scientific honesty**: Follow `PLOTTING_PHILOSOPHY.md` - only show confidence intervals where statistically justified. Don't force trends on scattered data.

## Script Execution Pattern

Use the bundled scripts from this skill's `scripts/` directory, resolving their path in the current environment. Save essential scripts and final figures in the requested project directory; use temporary local storage for intermediate files. Use an existing local Python or conda environment.

```python
from plot_config import setup_matplotlib, fig_size, save_figure, add_subplot_labels
import matplotlib.pyplot as plt

spec = setup_matplotlib(journal="default", locale="en")
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
# Plot data and set labels before saving.
save_figure(fig, "path/to/figure_name")  # PDF + JPG, 300 dpi, tightly cropped
plt.close(fig)
```

---

## Part 1: Geochemistry Diagrams

### 1.1 TAS Diagram (Total Alkali-Silica)

**When**: User has major element data (SiO2, Na2O, K2O) and wants to classify volcanic rocks.

**Template**:
```python
from geo_templates import draw_tas_fields

fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
draw_tas_fields(ax, lang="en")  # or lang="cn"

# Plot data points (group by rock type/sample set)
colors = get_colors(n_groups)
for i, (name, group) in enumerate(df.groupby("Group")):
    ax.scatter(group["SiO2"], group["Na2O"] + group["K2O"],
               c=colors[i], marker=MARKERS[i], s=30, label=name,
               edgecolors='k', linewidths=0.3, zorder=5)

ax.legend(loc='upper left', fontsize=6)
```

**Data requirements**: SiO2, Na2O, K2O (wt%). Must be recalculated to anhydrous (LOI-free) basis.

**Common mistakes to avoid**:
- Not recalculating to anhydrous basis
- Including altered samples without noting it
- Not distinguishing different sample groups

### 1.2 Harker Variation Diagrams

**When**: User wants to show major element trends vs SiO2.

**Template**:
```python
from geo_templates import setup_harker_grid, get_axis_label

fig, axes, elements = setup_harker_grid(
    elements=["TiO2", "Al2O3", "Fe2O3T", "MgO", "CaO", "Na2O", "K2O", "P2O5"],
    ncols=4
)

colors = get_colors(n_groups)
for ax, elem in zip(axes, elements):
    for i, (name, group) in enumerate(df.groupby("Group")):
        ax.scatter(group["SiO2"], group[elem],
                   c=colors[i], marker=MARKERS[i], s=20, label=name,
                   edgecolors='k', linewidths=0.2)

# Add legend only to first panel
axes[0].legend(fontsize=5)
add_subplot_labels(axes)
```

### 1.3 REE Spider Diagram

**When**: User has rare earth element data and wants normalized patterns.

**Key decisions**:
- **Normalization**: Chondrite (Sun & McDonough, 1989) for igneous rocks; PAAS for sedimentary
- **Y-axis**: Always log scale
- **X-axis**: Elements ordered La→Lu (or La→Lu+Y for REEY)

**Template**:
```python
from geo_templates import normalize_data, CHONDRITE_SM89
from plot_config import REE_ORDER

fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))

for idx, row in df.iterrows():
    raw = {elem: row[elem] for elem in REE_ORDER if elem in row.index}
    normed = normalize_data(raw, reference="chondrite_sm89")
    values = [normed.get(e, np.nan) for e in REE_ORDER]
    ax.plot(range(len(REE_ORDER)), values, 'o-', markersize=3, linewidth=0.8)

ax.set_yscale('log')
ax.set_xticks(range(len(REE_ORDER)))
ax.set_xticklabels(REE_ORDER, fontsize=6)
ax.set_ylabel("Sample / Chondrite")
ax.set_xlabel("Rare Earth Elements")
```

**Alternative using pyrolite** (if data is in DataFrame):
```python
import pyrolite.plot  # Monkey-patches pandas DataFrame
df[REE_ORDER].pyroplot.REE(ax=ax, unity_line=True, normalize_to="Chondrite_SM89")
```

### 1.4 Trace Element Spider Diagram

**When**: Extended trace element patterns (Cs→Lu), typically normalized to Primitive Mantle or N-MORB.

Same pattern as REE but use `TRACE_ELEMENT_ORDER_SM89` and `PM_SM89` or `NMORB_SM89`.

### 1.5 Discrimination Diagrams

**Pearce et al. (1984) Granite Rb vs Y+Nb**:
```python
from geo_templates import draw_pearce_granite_rb_ynb
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
draw_pearce_granite_rb_ynb(ax, lang="en")
# Plot data
ax.scatter(df["Y"] + df["Nb"], df["Rb"], ...)
```

**Other common diagrams** (generate field boundaries inline):
- **Nb/Y vs Zr/Ti** (Pearce, 1996) — volcanic rock classification
- **Th-Hf-Ta** (Wood, 1980) — basalt tectonic setting
- **La/Yb vs Yb** (Martin, 1986) — adakite discrimination
- **Zr vs Zr/Y** (Pearce & Norry, 1979) — basalt tectonic setting
- **10000×Ga/Al vs Zr, Nb, Ce, Y** (Whalen et al., 1987) — A-type granite
- **Nb/Yb vs Th/Yb** (Pearce, 2008) — mantle array

### 1.6 Ternary Diagrams

**Using mpltern**:
```python
import mpltern

fig, ax = plt.subplots(subplot_kw={"projection": "ternary"},
                        figsize=fig_size(spec["single_col_width_cm"], aspect=1.0))
ax.scatter(df["A"], df["F"], df["M"], c=colors, s=30, edgecolors='k', linewidths=0.3)
ax.set_tlabel("A (Na$_2$O + K$_2$O)")
ax.set_llabel("F (FeO$^T$)")
ax.set_rlabel("M (MgO)")
```

**Common ternary diagrams**: AFM, QAP, ACF, An-Ab-Or (see `geo_templates.TERNARY_DIAGRAMS`)

---

## Part 2: Isotope Diagrams

### 2.1 U-Pb Concordia Diagram

**Template**:
```python
from geo_templates import draw_concordia

fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
draw_concordia(ax, t_range_ma=(0, 3000), tick_ages_ma=[500, 1000, 1500, 2000, 2500, 3000])

# Plot data with error ellipses
for _, row in df.iterrows():
    ax.scatter(row["207Pb/235U"], row["206Pb/238U"], s=20, zorder=5)
    # Error ellipse: use matplotlib.patches.Ellipse for 2-sigma
```

### 2.2 Isochron Diagrams

**Rb-Sr, Sm-Nd, Re-Os isochrons**: Simple x-y scatter with linear regression.
- X: parent/stable ratio (e.g., 87Rb/86Sr)
- Y: daughter/stable ratio (e.g., 87Sr/86Sr)
- Include regression line with MSWD and age calculation

### 2.3 Fluid Source Diagram (delta18O vs deltaD)

```python
from geo_templates import draw_fluid_source_diagram

fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
draw_fluid_source_diagram(ax, show_fields=["meteoric_water_line", "magmatic_water", "metamorphic_water"])
# Plot sample data
ax.scatter(df["d18O"], df["dD"], s=30, edgecolors='k', linewidths=0.3, zorder=5)
```

### 2.4 Sulfur Isotope Histogram

Show delta34S distribution with reference ranges for different sulfur sources.

### 2.5 epsilon-Nd vs epsilon-Hf

Common for crustal evolution studies. Plot with mantle array line and reference fields (MORB, OIB, continental crust).

### 2.6 Pb-Pb Diagrams

206Pb/204Pb vs 207Pb/204Pb or 208Pb/204Pb. Include NHRL (Northern Hemisphere Reference Line), mantle reservoirs (DMM, EM1, EM2, HIMU).

---

## Part 3: Statistical Visualizations

### 3.1 Scatter Plot with Regression

```python
import scipy.stats as stats

fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
ax.scatter(x, y, s=25, c=colors[0], edgecolors='k', linewidths=0.3)

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
x_fit = np.linspace(x.min(), x.max(), 100)
ax.plot(x_fit, slope * x_fit + intercept, 'r-', linewidth=0.8)
ax.text(0.05, 0.95, f"R² = {r_value**2:.3f}\ny = {slope:.2f}x + {intercept:.2f}",
        transform=ax.transAxes, fontsize=7, va='top')
```

### 3.2 Box / Violin Plot

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
sns.violinplot(data=df, x="Group", y="Value", ax=ax, palette=get_colors(n_groups),
               inner="quartile", linewidth=0.5)
```

### 3.3 Heatmap / Correlation Matrix

```python
import seaborn as sns
corr = df[element_cols].corr()
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"], aspect=1.0))
sns.heatmap(corr, ax=ax, cmap=get_cmap("roma"), center=0,
            annot=True, fmt=".2f", linewidths=0.5,
            square=True, cbar_kws={"shrink": 0.8})
```

### 3.4 Histogram / KDE (Kernel Density Estimation)

Useful for zircon age distributions, trace element distributions, etc.

```python
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
ax.hist(data, bins=30, density=True, alpha=0.7, color=colors[0], edgecolor='k', linewidth=0.3)
# Overlay KDE
from scipy.stats import gaussian_kde
kde = gaussian_kde(data)
x_kde = np.linspace(data.min(), data.max(), 200)
ax.plot(x_kde, kde(x_kde), 'r-', linewidth=1.0)
```

### 3.5 Error Bar Plot

```python
ax.errorbar(x, y, yerr=y_err, xerr=x_err, fmt='o', markersize=4,
            capsize=2, capthick=0.5, elinewidth=0.5, color=colors[0])
```

---

## Part 4: Geological Diagrams

### 4.1 Stratigraphic Column

Build from bottom to top using `ax.barh()` or `ax.fill_between()` with lithology patterns.

Key elements:
- Age scale on left y-axis
- Lithology column with standard geological patterns (stipple=sandstone, brick=limestone, etc.)
- Formation names and thicknesses
- Fossil/mineralization markers

### 4.2 Mineralization Profile / Cross-Section

Schematic diagrams showing:
- Surface topography
- Drill hole traces
- Ore body outlines
- Grade contours (use `ax.contourf()` for interpolated data)
- Geological boundaries

### 4.3 Grade-Tonnage / Grade Distribution

```python
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
ax.scatter(df["Tonnage_Mt"], df["Grade_pct"], s=30, c=colors, edgecolors='k', linewidths=0.3)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel("Tonnage (Mt)")
ax.set_ylabel("Grade (%)")
```

---

## Part 5: Multi-Panel Figures

### 5.1 Layout Rules

- Use `plt.subplots()` with `constrained_layout=True` (preferred over `tight_layout`)
- Consistent axis limits across comparable panels
- Share x or y axis when appropriate (`sharex=True`)
- Subplot labels: (a), (b), (c)... in bold at the upper left, outside each axes. Align the horizontal center of each label with the horizontal center of its ylabel, so they form a vertical line. If a panel has no ylabel, align to its left edge. Verify labels do not overlap or clip.

### 5.2 Common Layouts

```python
# 2×2 layout
fig, axes = plt.subplots(2, 2, figsize=fig_size(spec["double_col_width_cm"], aspect=0.9),
                          constrained_layout=True)
add_subplot_labels(axes.flatten())

# 1 tall + 2 short (custom GridSpec)
fig = plt.figure(figsize=fig_size(spec["double_col_width_cm"], aspect=0.5))
gs = fig.add_gridspec(1, 3, width_ratios=[2, 1, 1])
ax0 = fig.add_subplot(gs[0])
ax1 = fig.add_subplot(gs[1])
ax2 = fig.add_subplot(gs[2])
```

### 5.3 Subplot Labels

Always use `add_subplot_labels()` from plot_config:
```python
from plot_config import add_subplot_labels
add_subplot_labels(axes.flatten(), style='lowercase_paren')  # → (a), (b), (c)
```

---

## Part 6: Journal Format Presets

### 6.1 Applying Journal Format

```python
from plot_config import setup_matplotlib, fig_size, get_journal_spec

spec = setup_matplotlib(journal="gca")  # or "nature", "lithos", "chinese_core", etc.
fig, ax = plt.subplots(figsize=fig_size(spec["single_col_width_cm"]))
```

### 6.2 Available Presets

| Key | Journals | Font | Size |
|-----|----------|------|------|
| `nature` | Nature, Nature Geoscience | Arial 7pt | 8.9cm single |
| `science` | Science | Arial 7pt | 9.0cm single |
| `elsevier` | GCA, EPSL, Lithos, Ore Geology Reviews, Chemical Geology | Arial 8pt | 9.0cm single |
| `geology_gsa` | Geology (GSA) | Arial 8pt | 8.5cm single |
| `springer` | Mineralium Deposita, CMP | Arial 8pt | 8.4cm single |
| `chinese_core` | All Chinese core journals | Times New Roman 8pt + SimSun | 7.5cm single |
| `default` | General scientific | Arial 8pt | 8.5cm single |

### 6.3 Chinese Labels

For Chinese core journals, pass `locale="cn"`:
```python
spec = setup_matplotlib(journal="chinese_core", locale="cn")
```

This sets SimSun as primary font for Chinese character rendering.

---

## Part 7: Quality Checklist

After generating every figure, verify these items before saving:

### 7.1 Data Accuracy (Critical)

- [ ] Data values match source (spot-check 3+ points visually)
- [ ] Axis ranges include all data points (no clipping)
- [ ] Normalization reference is correct and cited
- [ ] Error bars reflect actual uncertainty (1σ or 2σ, must be labeled)
- [ ] Log/linear scale is appropriate for the data range

### 7.2 Visual Clarity (High)

- [ ] Labels readable at target print size (check font size vs journal spec)
- [ ] Legend does not overlap data points
- [ ] Colors distinguishable in grayscale and by colorblind readers
- [ ] Marker shapes distinct when ≥3 categories
- [ ] No overlapping text labels (use adjustText if needed)
- [ ] Axis labels include units

### 7.3 Format Compliance (High)

- [ ] Figure dimensions match journal requirements
- [ ] DPI ≥ 300 for raster output
- [ ] Font family matches journal requirements
- [ ] Chemical formulas use proper subscripts/superscripts
- [ ] Subplot labels (a), (b), (c) present for multi-panel figures

### 7.4 Geoscience-Specific (Medium)

- [ ] Oxide data recalculated to anhydrous basis (if applicable)
- [ ] TAS/Harker: only fresh/unaltered samples included (or noted)
- [ ] REE: normalization reference clearly stated
- [ ] Isotope ratios: decay constants cited
- [ ] Coordinates: proper datum noted (WGS84 / CGCS2000)

### Severity Triage

| Severity | Examples | Action |
|----------|----------|--------|
| **Critical** | Wrong data values, wrong normalization, wrong axis scale | Must fix before output |
| **High** | Missing error bars, unreadable labels, wrong figure size | Must fix before output |
| **Warning** | Non-optimal color palette, minor layout issues | Fix if easy, note otherwise |
| **Suggestion** | Alternative presentation style | Include in output notes |

---

## Part 8: Output Rules

### 8.1 File Output

- **Final figures**: Save PDF and JPG at 300 dpi to the location requested by the user, with outer whitespace cropped and no labels clipped.
- **Naming**: `Figure_N_description.pdf` and `Figure_N_description.jpg`
- **Temporary files**: Use local temporary storage; keep only essential scripts and figures in OneDrive.

### 8.2 Post-Output

After saving, always:
1. Inspect and show the JPG figure to the user where possible
2. Report: figure dimensions, DPI, file paths
3. Note any data assumptions or limitations

### 8.3 Available Libraries

```
matplotlib, seaborn, plotly, numpy, pandas, scipy, sklearn
pyrolite     — geochemistry (REE, spider, TAS, classification)
mpltern      — ternary diagrams
adjustText   — automatic label placement
cmcrameri    — scientific color maps (colorblind-safe)
statsmodels  — regression, statistical analysis
```

### 8.4 Enhanced Statistical Plotting (v2.0)

New modules in `scripts/`:
- **plot_config_v2.py** — Enhanced config with SciencePlots integration, Wong/Tol palettes
- **statistical_plots.py** — Bootstrap CI, Q-Q plots, correlation matrices, regression diagnostics
- **advanced_plots.py** — Dumbbell, waterfall, fan charts, spaghetti plots
- **PLOTTING_PHILOSOPHY.md** ⭐ — Guidelines on when to use confidence intervals vs scatter-only

**Key principle**: Only show Bootstrap confidence intervals where data supports it (n≥15, narrow CI, clear trend). See `PLOTTING_PHILOSOPHY.md` for decision criteria.

---

## Appendix: Quick Reference

### Chemical Formula LaTeX Cheatsheet

| Element/Oxide | LaTeX |
|--------------|-------|
| SiO2 | `SiO$_2$` |
| Al2O3 | `Al$_2$O$_3$` |
| Fe2O3 | `Fe$_2$O$_3$` |
| Na2O+K2O | `Na$_2$O + K$_2$O` |
| 207Pb/235U | `$^{207}$Pb/$^{235}$U` |
| 87Sr/86Sr | `$^{87}$Sr/$^{86}$Sr` |
| delta18O | `$\delta^{18}$O` |
| epsilon-Nd | `$\varepsilon_{Nd}$` |
| permil | `\u2030` |

### Geological Pattern Reference

| Lithology | Pattern | matplotlib hatch |
|-----------|---------|-----------------|
| Sandstone | Stipple | `'.'` |
| Limestone | Brick | `'+'` |
| Shale | Horizontal lines | `'-'` |
| Granite | V-marks | `'v'` |
| Basalt | X-marks | `'x'` |
| Ore body | Solid fill | Color fill |
