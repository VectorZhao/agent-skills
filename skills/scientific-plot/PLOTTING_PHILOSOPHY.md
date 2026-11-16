---
name: scientific-plotting-philosophy
description: 科学诚实的数据可视化哲学 - 何时展示趋势，何时只展示散点
type: reference
version: 1.0
date: 2026-07-26
---

# 🎨 科学可视化哲学指南

## 核心原则

> **"只在有统计支撑的地方展示趋势，不强行拟合弱相关"**

这是区分**顶级期刊论文**和**普通论文**的关键。

---

## 📐 决策树：何时使用置信区间 vs 只散点

```
数据输入
  ↓
├─ 样本量足够？(n ≥ 15)
│   ├─ 否 → 只散点
│   ├─ 是 → 继续
│       ↓
│       ├─ 数据范围足够？(x范围 > 3σ)
│       │   ├─ 否 → 只散点
│       │   ├─ 是 → 继续
│       │       ↓
│       │       ├─ Bootstrap后CI宽度？
│       │       │   ├─ 宽（>50%数据范围）→ 只散点
│       │       │   ├─ 窄 → 继续
│       │       │       ↓
│       │       │       ├─ 视觉趋势明显？
│       │       │       │   ├─ 否 → 只散点
│       │       │       │   ├─ 是 → 展示Bootstrap CI
```

---

## ✅ 何时展示置信区间

### 必须同时满足以下条件：

1. **样本量充足**
   - 最少 n ≥ 15
   - 推荐 n ≥ 20

2. **数据范围充足**
   - X轴范围 > 3倍标准差
   - 覆盖有意义的地质/化学范围

3. **Bootstrap CI窄**
   - 置信带宽度 < 数据范围的30%
   - 表明趋势稳健

4. **视觉趋势明显**
   - R² > 0.3（线性）
   - 或有明确的非线性模式

5. **有地质学/化学意义**
   - 趋势符合理论预期
   - 或提供新的科学见解

### 示例（本次作图）

| 参数 | 样本量 | 趋势强度 | 决策 | 理由 |
|------|--------|---------|------|------|
| **A-D (Hydrothermal)** | n=30 | 明显 | ✅ Bootstrap CI | 满足所有条件 |
| **A-D (Wall rock)** | n=8 | 无 | ❌ 只散点 | 样本量不足，范围窄 |
| **E (δ¹³C vs MnO)** | n=30 | 弱 | ❌ 只散点 | 数据高度分散，无趋势 |
| **F (δ⁵⁶Fe vs δ¹³C)** | n=30 | 无 | ❌ 只散点 | 两个独立过程，无相关性 |

---

## ❌ 常见的过度拟合陷阱

### 1. 样本量不足强行拟合
```
错误：n=5的数据画置信带
问题：Bootstrap会严重过拟合
正确：只散点 + 文字说明"样本量有限"
```

### 2. 数据分散强行拟合
```
错误：R²=0.1也画趋势线
问题：审稿人会质疑"趋势的统计显著性"
正确：只散点 + Caption说明"无系统性趋势"
```

### 3. 为了"好看"强行拟合
```
错误：觉得空白不好看，画个趋势
问题：科学诚实 > 视觉效果
正确：诚实展示数据分散性
```

### 4. 所有子图"统一"风格
```
错误：所有子图都画置信带保持一致
问题：不同参数相关性不同
正确：根据数据特征分别处理
```

---

## 🎯 Caption写作原则

### 必须说明"为什么有的有CI，有的没有"

#### 好的写法 ✅
> "Shaded bands represent 90% confidence intervals for parameters showing statistically significant trends (subplots A-D). Subplots E-F display scatter plots only due to the absence of systematic correlations."

#### 不好的写法 ❌
> "Some plots show confidence intervals." （没解释原因）

---

## 📊 实战案例：地球化学多子图

### 场景
6个子图，4种岩石类型，需要决策每个子图是否展示趋势。

### 分析过程

#### Wall rock（所有子图）
- 样本量：n=8 ❌
- 结论：只散点，不拟合

#### Hydrothermal - 子图A (Ce/Ce* vs MnO)
- 样本量：n=30 ✅
- 数据范围：5-38 wt% MnO ✅
- Bootstrap CI：窄 ✅
- 视觉趋势：Ce/Ce*随MnO增加 ✅
- 地质意义：热液流体携带Ce ✅
- **决策：展示Bootstrap 90% CI**

#### Hydrothermal - 子图E (δ¹³C vs MnO)
- 样本量：n=30 ✅
- 数据范围：5-38 wt% MnO ✅
- Bootstrap CI：极宽 ❌
- 视觉趋势：高度分散 ❌
- 地质意义：δ¹³C受多因素控制 ⚠️
- **决策：只散点**

#### Hydrothermal - 子图F (δ⁵⁶Fe vs δ¹³C)
- 样本量：n=30 ✅
- 相关性：两个独立过程 ❌
- 演化箭头：无数据支撑 ❌
- **决策：只散点，不画演化箭头**

---

## 🔬 统计学严谨性检查清单

在画置信区间前，问自己：

- [ ] Bootstrap重采样次数足够？(n ≥ 300)
- [ ] 置信水平合理？(90-95%)
- [ ] CI带宽合理？(不是整个Y轴范围的80%)
- [ ] 趋势线平滑合理？(不是过拟合的锯齿)
- [ ] Caption中说明了方法？
- [ ] 如果审稿人问"为什么这里有CI"，我能回答吗？

---

## 📝 审稿回复模板

### 审稿人："Why are there no confidence intervals in subplots E-F?"

**好的回答**：
> "We performed Bootstrap analysis (n=400) on all parameters. Subplots A-D demonstrate statistically robust trends with narrow confidence intervals (CI width < 20% of data range), indicating significant correlations (p < 0.05 based on permutation tests). In contrast, subplots E-F show high data scatter and very wide confidence intervals (CI width > 60% of data range), reflecting weak or absent systematic correlations. We chose to present raw scatter plots for E-F to avoid over-interpretation. This approach follows the principle of presenting confidence intervals only where trends are statistically meaningful."

**不好的回答**：
> "We didn't think there was a trend." （太主观）

---

## 💡 与其他领域的类比

| 领域 | 相同原则 |
|------|---------|
| **机器学习** | 不在测试集R²<0.3时声称模型有效 |
| **医学统计** | 不在p>0.05时声称治疗有效 |
| **经济学** | 不在标准误大于系数时声称显著 |
| **我们的原则** | 不在CI极宽时声称有趋势 |

---

## 🏆 顶级期刊的标准

### Nature/Science论文的特征
1. ✅ 置信区间**有选择性**地使用
2. ✅ Caption**明确说明**为什么某些图没有CI
3. ✅ 方法学部分**详细描述**统计判断标准
4. ✅ 不回避数据的**局限性**

### 普通期刊论文的问题
1. ❌ 所有图都画趋势线
2. ❌ 不说明为什么
3. ❌ 强行解释弱相关
4. ❌ 回避数据质量问题

---

## 🔧 技术实现

### 判断函数（Python）

```python
def should_show_confidence_interval(x_data, y_data, min_samples=15, 
                                    max_ci_ratio=0.3, min_r2=0.25):
    """
    判断是否应该展示置信区间
    
    Parameters:
    -----------
    x_data, y_data : array-like
        数据
    min_samples : int
        最小样本量
    max_ci_ratio : float
        CI宽度占数据范围的最大比例
    min_r2 : float
        最小R²阈值（线性拟合）
    
    Returns:
    --------
    bool, str : (是否展示CI, 原因)
    """
    n = len(x_data)
    
    # 检查1: 样本量
    if n < min_samples:
        return False, f"Sample size too small (n={n} < {min_samples})"
    
    # 检查2: 数据范围
    x_range = np.max(x_data) - np.min(x_data)
    x_std = np.std(x_data)
    if x_range < 3 * x_std:
        return False, "Data range too narrow"
    
    # 检查3: Bootstrap CI宽度
    _, _, y_lower, y_upper = bootstrap_confidence_band(x_data, y_data, 
                                                       n_bootstrap=300, ci=90)
    if y_lower is not None:
        ci_width = np.mean(y_upper - y_lower)
        y_range = np.max(y_data) - np.min(y_data)
        ci_ratio = ci_width / y_range
        
        if ci_ratio > max_ci_ratio:
            return False, f"CI too wide (ratio={ci_ratio:.2f} > {max_ci_ratio})"
    
    # 检查4: R²
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)
    r2 = r_value ** 2
    
    if r2 < min_r2:
        return False, f"Correlation too weak (R²={r2:.3f} < {min_r2})"
    
    return True, f"All criteria met (n={n}, R²={r2:.3f}, CI ratio={ci_ratio:.2f})"


# 使用示例
show_ci, reason = should_show_confidence_interval(hydrothermal['MnO'], 
                                                   hydrothermal['Ce/Ce*'])
if show_ci:
    # 绘制置信区间
    plot_bootstrap_ci(...)
else:
    # 只散点
    ax.scatter(...)
    print(f"Only scatter: {reason}")
```

---

## 📚 推荐阅读

1. **Wickham, H. (2016).** "ggplot2: Elegant Graphics for Data Analysis"
   - 第4章：不要过度拟合

2. **Tufte, E. R. (2001).** "The Visual Display of Quantitative Information"
   - 原则：数据-墨水比

3. **Cleveland, W. S. (1993).** "Visualizing Data"
   - 何时使用LOWESS平滑

4. **Nature指南** - "Points of Significance" 系列
   - 特别推荐："Error bars" (2013)

---

## 🎯 快速参考卡

打印这个贴在显示器上：

```
┌─────────────────────────────────────────┐
│  画置信区间前问自己：                    │
│                                          │
│  1. n ≥ 15？                             │
│  2. 数据范围 > 3σ？                      │
│  3. Bootstrap CI < 30%数据范围？         │
│  4. 视觉上有明显趋势？                    │
│  5. 有科学意义？                         │
│                                          │
│  全是 YES → 画CI                         │
│  有一个 NO → 只散点                      │
│                                          │
│  记住：科学诚实 > 视觉效果                │
└─────────────────────────────────────────┘
```

---

## 📌 本次作图的经验总结

### 学到的教训

1. **不是所有子图都需要统一风格**
   - 根据数据特征分别处理才是专业的

2. **Wall rock样本少就不要拟合**
   - n=8的数据只适合散点展示

3. **E和F图数据分散就不要强行解释**
   - 承认"无系统性趋势"是科学诚实的表现

4. **Caption必须说明为什么**
   - 读者和审稿人需要知道你的判断依据

### 核心哲学

> **"Let the data speak for itself. If there's no trend, don't force one."**
> 
> 让数据自己说话。如果没有趋势，就不要强行制造一个。

---

## 🔄 持续改进

这个哲学会随着实践不断完善。每次作图后问自己：
- 这次的判断合理吗？
- 审稿人会怎么看？
- 5年后回看会觉得尴尬吗？

**好的科学可视化经得起时间检验。**

---

**版本历史**
- v1.0 (2026-07-26): 首次创建，基于地球化学6子图案例

**下次更新方向**
- 添加更多领域的案例（生物、金融、工程）
- 补充交互式图表的判断标准
- 添加常见审稿意见及回复
