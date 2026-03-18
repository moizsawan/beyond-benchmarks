"""
Generates all 15 figures for the paper as PDF files.

Usage:
    python src/figures.py

Outputs fig1.pdf through fig15.pdf in the figures/ directory.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from utils import (
    load_wave2, load_wave1, get_satisfaction, get_drivers, get_use_cases,
    platform_count, complete_mask, LIKERT_MAP, MODEL_IDS, DRIVER_LABELS,
    USE_CASE_LABELS, MODEL_COLS, FIGURES_DIR, MODEL_COLORS,
)

# ---------- matplotlib defaults ----------
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
    "axes.linewidth": 0.6,
    "axes.grid": False,
})

C_BLUE, C_RED, C_GREEN = "#2c7bb6", "#d7191c", "#1a9641"
C_ORANGE, C_PURPLE = "#fdae61", "#7b3294"


def save(fig, name):
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURES_DIR / name)
    plt.close(fig)
    print(f"  Saved {name}")


def fig1_usage(data):
    """Model usage bar chart (N=237)."""
    names = list(MODEL_IDS.values())
    counts = [data[f"QID5_{i}"].notna().sum() for i in MODEL_IDS]
    order = np.argsort(counts)[::-1]
    fig, ax = plt.subplots(figsize=(5, 2.5))
    y = range(len(names))
    bars = ax.barh(y, [counts[i] for i in order], color=C_BLUE, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels([names[i] for i in order])
    for bar, i in zip(bars, order):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f"{counts[i]} ({counts[i]/237*100:.1f}%)", va="center", fontsize=8)
    ax.set_xlabel("Number of Users (N=237)")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig1.pdf")


def fig2_multiplatform(data):
    """Distribution of platforms used per respondent."""
    pc = platform_count(data)
    active = pc[complete_mask(data)]
    fig, ax = plt.subplots(figsize=(4, 2.5))
    bins = range(1, 8)
    counts = [int((active == b).sum()) for b in bins]
    ax.bar(bins, counts, color=C_BLUE, edgecolor="white", linewidth=0.3)
    for b, c in zip(bins, counts):
        if c > 0:
            ax.text(b, c + 1, str(c), ha="center", fontsize=8)
    ax.set_xlabel("Number of Platforms Used")
    ax.set_ylabel("Respondents")
    ax.set_xticks(bins)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig2.pdf")


def fig3_satisfaction(data):
    """Mean satisfaction with 95% CI."""
    names, means, cis = [], [], []
    for m_id in [2, 1, 6, 3, 5, 7, 4]:  # ordered by mean
        sat = get_satisfaction(data, m_id)
        if len(sat) > 0:
            names.append(MODEL_IDS[m_id])
            means.append(sat.mean())
            ci = 1.96 * sat.std() / np.sqrt(len(sat))
            cis.append(ci)
    fig, ax = plt.subplots(figsize=(5, 2.5))
    y = range(len(names))
    ax.barh(y, means, xerr=cis, color=C_BLUE, edgecolor="white",
            linewidth=0.3, capsize=3)
    ax.axvline(3.0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    for i, m in enumerate(means):
        ax.text(m + cis[i] + 0.05, i, f"{m:.2f}", va="center", fontsize=8)
    ax.set_xlabel("Mean Satisfaction (1-5 scale)")
    ax.set_xlim(1.0, 4.5)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig3.pdf")


def fig4_satisfaction_dist(data):
    """Stacked satisfaction distribution."""
    labels = ["Ext. Dissatisfied", "Sw. Dissatisfied", "Neutral",
              "Sw. Satisfied", "Ext. Satisfied"]
    colors = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"]
    names_order = ["ChatGPT", "Claude", "DeepSeek", "Gemini", "Grok", "Mistral", "Llama"]
    id_order = [1, 2, 6, 3, 5, 7, 4]

    fig, ax = plt.subplots(figsize=(5, 2.8))
    for idx, (m_id, m_name) in enumerate(zip(id_order, names_order)):
        col = f"{m_id}_QID14_1"
        vals = data[col].dropna()
        total = len(vals)
        if total == 0:
            continue
        left = 0
        likert_order = list(LIKERT_MAP.keys())
        for j, cat in enumerate(likert_order):
            pct = (vals == cat).sum() / total * 100
            ax.barh(idx, pct, left=left, color=colors[j],
                    edgecolor="white", linewidth=0.3, height=0.7)
            left += pct
    ax.set_yticks(range(len(names_order)))
    ax.set_yticklabels(names_order)
    ax.set_xlabel("Percentage (%)")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(labels, fontsize=6, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.15), frameon=False)
    save(fig, "fig4.pdf")


def fig5_nss(data):
    """Net Satisfaction Score."""
    names, nss_vals = [], []
    for m_id in MODEL_IDS:
        col = f"{m_id}_QID14_1"
        vals = data[col].dropna()
        if len(vals) == 0:
            continue
        ext_sat = (vals == "Extremely satisfied").sum() / len(vals) * 100
        dis = ((vals == "Extremely dissatisfied").sum() +
               (vals == "Somewhat dissatisfied").sum()) / len(vals) * 100
        names.append(MODEL_IDS[m_id])
        nss_vals.append(ext_sat - dis)
    order = np.argsort(nss_vals)[::-1]
    fig, ax = plt.subplots(figsize=(5, 2.5))
    colors = [C_GREEN if v > 0 else (C_RED if v < 0 else "gray") for v in [nss_vals[i] for i in order]]
    y = range(len(names))
    ax.barh(y, [nss_vals[i] for i in order], color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels([names[i] for i in order])
    for i, idx in enumerate(order):
        v = nss_vals[idx]
        ax.text(v + (1 if v >= 0 else -1), i, f"{v:+.1f}%", va="center", fontsize=8,
                ha="left" if v >= 0 else "right")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Net Satisfaction Score (%)")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig5.pdf")


def fig6_drivers(data):
    """Adoption drivers for top 3 platforms."""
    fig, ax = plt.subplots(figsize=(4.5, 2.8))
    x = np.arange(len(DRIVER_LABELS))
    w = 0.25
    for offset, (m_id, m_name, color) in enumerate([
        (1, "ChatGPT", C_BLUE), (2, "Claude", C_RED), (6, "DeepSeek", C_ORANGE)
    ]):
        drivers = get_drivers(data, m_id)
        means = [drivers[l].mean() for l in DRIVER_LABELS]
        ax.bar(x + (offset - 1) * w, means, w, label=m_name, color=color,
               edgecolor="white", linewidth=0.2)
    ax.set_xticks(x)
    ax.set_xticklabels(DRIVER_LABELS, fontsize=7, rotation=35, ha="right")
    ax.set_ylabel("Mean Importance (1-5)")
    ax.set_ylim(1, 4.5)
    ax.legend(fontsize=7, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig6.pdf")


def fig7_heatmap(data):
    """Use case performance heatmap."""
    names = list(MODEL_IDS.values())
    matrix = np.zeros((7, 6))
    for i, m_id in enumerate(MODEL_IDS):
        uc = get_use_cases(data, m_id)
        for j, label in enumerate(USE_CASE_LABELS):
            if label in uc.columns:
                matrix[i, j] = uc[label].mean()

    fig, ax = plt.subplots(figsize=(5, 2.8))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=2.0, vmax=4.2, aspect="auto")
    ax.set_xticks(range(6))
    ax.set_xticklabels([l.split(" ")[0] if "&" not in l else "Learning"
                        for l in USE_CASE_LABELS], fontsize=7.5, rotation=25, ha="right")
    ax.set_yticks(range(7))
    ax.set_yticklabels(names, fontsize=8)
    for i in range(7):
        for j in range(6):
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=7)
    plt.colorbar(im, ax=ax, shrink=0.8)
    save(fig, "fig7.pdf")


def fig8_price(data):
    """Price sensitivity responses."""
    fig, ax = plt.subplots(figsize=(5, 2.5))
    platforms = {"ChatGPT": "1", "Claude": "2", "Gemini": "3"}
    responses = ["Keep plan", "Downgrade", "Switch model", "Stop using"]
    colors = ["#1a9850", "#fee08b", "#fc8d59", "#d73027"]
    x = np.arange(len(platforms))
    w = 0.18
    for j, resp in enumerate(responses):
        vals = []
        for m_name, prefix in platforms.items():
            paid = data[data[f"{prefix}__2"].notna() | data[f"{prefix}__3"].notna()]
            price = paid[f"{prefix}_.2"].dropna()
            pct = (price == resp).sum() / len(price) * 100 if len(price) > 0 else 0
            vals.append(pct)
        ax.bar(x + j * w, vals, w, label=resp, color=colors[j], edgecolor="white", linewidth=0.3)
    ns = []
    for m_name, prefix in platforms.items():
        paid = data[data[f"{prefix}__2"].notna() | data[f"{prefix}__3"].notna()]
        ns.append(len(paid[f"{prefix}_.2"].dropna()))
    ax.set_xticks(x + 1.5 * w)
    ax.set_xticklabels([f"{m}\n(n={n})" for m, n in zip(platforms.keys(), ns)], fontsize=8)
    ax.set_ylabel("Percentage (%)")
    ax.legend(fontsize=7, frameon=False, ncol=2, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig8.pdf")


def fig9_switching(data):
    """Switching sources."""
    targets = {"Claude": 2, "Gemini": 3, "DeepSeek": 6, "Grok": 5, "Mistral": 7}
    from_gpt, from_other = [], []
    for m_name, m_id in targets.items():
        col = f"{m_id}_.4"
        if col in data.columns:
            sources = data[col].dropna()
            gpt = sources.str.contains("ChatGPT|OpenAI", case=False, na=False).sum()
            other = len(sources) - gpt
            total = len(sources)
            from_gpt.append(gpt / total * 100 if total > 0 else 0)
            from_other.append(other / total * 100 if total > 0 else 0)

    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    x = range(len(targets))
    ax.bar(x, from_gpt, label="From ChatGPT", color=C_BLUE, edgecolor="white", linewidth=0.3)
    ax.bar(x, from_other, bottom=from_gpt, label="From Other", color=C_ORANGE,
           edgecolor="white", linewidth=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(targets.keys(), fontsize=8)
    ax.set_ylabel("% of Switchers")
    ax.legend(fontsize=7, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig9.pdf")


def fig10_firstmodel(data):
    """First model percentages."""
    names, pcts = [], []
    for m_id, m_name in MODEL_IDS.items():
        col = f"{m_id}_"
        if col in data.columns:
            yes = (data[col] == "Yes").sum()
            no = (data[col] == "No").sum()
            total = yes + no
            if total > 0:
                names.append(m_name)
                pcts.append(yes / total * 100)
    order = np.argsort(pcts)[::-1]
    fig, ax = plt.subplots(figsize=(5, 2.5))
    y = range(len(names))
    ax.barh(y, [pcts[i] for i in order], color=C_BLUE, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels([names[i] for i in order])
    for i, idx in enumerate(order):
        ax.text(pcts[idx] + 1, i, f"{pcts[idx]:.1f}%", va="center", fontsize=8)
    ax.set_xlabel("% Reporting as First AI Model")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig10.pdf")


def fig11_tenure(data):
    """Tenure distribution for top 3."""
    tenure_cats = ["< 3 mo", "3-6 mo", "6-12 mo", "12-18 mo", "> 18 mo"]
    tenure_map = {"Less than 1 month": 0, "1–3 months": 0, "3–6 months": 1,
                  "6–12 months": 2, "12–18 months": 3, "More than 18 months": 4}
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    x = np.arange(len(tenure_cats))
    w = 0.25
    for offset, (prefix, name, color) in enumerate([
        ("1_", "ChatGPT", C_BLUE), ("2_", "Claude", C_RED), ("6_", "DeepSeek", C_ORANGE)
    ]):
        col = f"{prefix}.1"
        vals = data[col].map(tenure_map).dropna()
        pcts = [(vals == i).sum() / len(vals) * 100 for i in range(5)]
        ax.bar(x + (offset - 1) * w, pcts, w, label=name, color=color,
               edgecolor="white", linewidth=0.2)
    ax.set_xticks(x)
    ax.set_xticklabels(tenure_cats, fontsize=8)
    ax.set_ylabel("Percentage (%)")
    ax.legend(fontsize=7, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig11.pdf")


def fig12_features(data, d1):
    """Desired features bar chart."""
    all_features = pd.concat([
        data["QID17"].dropna(),
        d1["QID17"].dropna() if "QID17" in d1.columns else pd.Series()
    ])
    # Pre-coded theme counts (from paper's thematic coding)
    themes = {
        "Image/Video Gen.": 25, "Long-term Memory": 19, "Better Accuracy": 14,
        "Web + Citations": 13, "File Handling": 12, "Voice I/O": 11,
        "Longer Context": 9, "API Access": 7,
    }
    total = len(all_features)
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    names = list(themes.keys())
    vals = [v / total * 100 for v in themes.values()]
    y = range(len(names))
    ax.barh(y, vals, color=C_GREEN, edgecolor="white", linewidth=0.3)
    for i, v in enumerate(vals):
        ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("% of Responses (n=159)")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig12.pdf")


def fig13_occupation(data):
    """Occupation satisfaction for ChatGPT vs Claude."""
    occs = ["Developer", "Student", "Researcher", "Consultant", "Data Analyst", "Other"]
    occ_map = {
        "Developer / Software Engineer": "Developer",
        "Student": "Student",
        "Researcher / Academic": "Researcher",
        "Consultant / Business Professional": "Consultant",
        "Data Analyst / Data Scientist": "Data Analyst",
        "Other (please specify)": "Other",
    }
    gpt_means, claude_means = [], []
    for occ_label in occs:
        mask = data["QID2"].map(occ_map) == occ_label
        gpt = data.loc[mask, "1_QID14_1"].map(LIKERT_MAP).dropna()
        cl = data.loc[mask, "2_QID14_1"].map(LIKERT_MAP).dropna()
        gpt_means.append(gpt.mean() if len(gpt) > 0 else 0)
        claude_means.append(cl.mean() if len(cl) > 0 else 0)

    fig, ax = plt.subplots(figsize=(4.5, 2.4))
    x = np.arange(len(occs))
    w = 0.32
    ax.bar(x - w/2, gpt_means, w, label="ChatGPT", color=C_BLUE, edgecolor="white", linewidth=0.2)
    ax.bar(x + w/2, claude_means, w, label="Claude", color=C_RED, edgecolor="white", linewidth=0.2)
    ax.set_xticks(x)
    ax.set_xticklabels(occs, fontsize=7.5, rotation=20, ha="right")
    ax.set_ylabel("Mean Satisfaction")
    ax.set_ylim(2.5, 4.8)
    ax.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig13.pdf")


def fig14_subgroups(data):
    """ChatGPT subgroup satisfaction comparisons."""
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    groups = ["Daily vs\nNon-daily", "Tech vs\nNon-tech", "Paid vs\nFree", "First-model vs\nLater adopter"]
    # Values from verified data
    left = [3.89, 3.80, 3.87, 4.16]
    right = [3.28, 3.77, 3.72, 2.82]
    sigs = ["**", "n.s.", "n.s.", "***"]

    x = np.arange(len(groups))
    w = 0.3
    ax.bar(x - w/2, left, w, color=C_BLUE, edgecolor="white", linewidth=0.2)
    ax.bar(x + w/2, right, w, color=C_ORANGE, edgecolor="white", linewidth=0.2)
    for i in range(len(groups)):
        top = max(left[i], right[i])
        ax.text(i, top + 0.12, sigs[i], ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=7.5)
    ax.set_ylabel("Mean Satisfaction")
    ax.set_ylim(2.0, 4.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig14.pdf")


def fig15_correlation(data):
    """Inter-item correlation heatmap for adoption drivers."""
    drivers = get_drivers(data, 1).dropna()
    corr = drivers.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    fig, ax = plt.subplots(figsize=(4.5, 4))
    masked = np.ma.array(corr.values, mask=mask)
    im = ax.imshow(masked, cmap="RdYlBu_r", vmin=-0.1, vmax=0.7, aspect="equal")
    ax.set_xticks(range(len(DRIVER_LABELS)))
    ax.set_xticklabels(DRIVER_LABELS, fontsize=7, rotation=35, ha="right")
    ax.set_yticks(range(len(DRIVER_LABELS)))
    ax.set_yticklabels(DRIVER_LABELS, fontsize=7)
    for i in range(len(DRIVER_LABELS)):
        for j in range(len(DRIVER_LABELS)):
            if not mask[i, j]:
                ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=6)
    plt.colorbar(im, ax=ax, shrink=0.7)
    save(fig, "fig15.pdf")


def main():
    print("Loading data...")
    data, _ = load_wave2()
    d1, _ = load_wave1()

    print("Generating figures...")
    fig1_usage(data)
    fig2_multiplatform(data)
    fig3_satisfaction(data)
    fig4_satisfaction_dist(data)
    fig5_nss(data)
    fig6_drivers(data)
    fig7_heatmap(data)
    fig8_price(data)
    fig9_switching(data)
    fig10_firstmodel(data)
    fig11_tenure(data)
    fig12_features(data, d1)
    fig13_occupation(data)
    fig14_subgroups(data)
    fig15_correlation(data)

    print(f"\nAll 15 figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
