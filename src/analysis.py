"""
Reproduces all statistical analyses reported in the paper.

Usage:
    python src/analysis.py

Prints every statistic cited in the manuscript, organized by paper section.
"""

import pandas as pd
import numpy as np
from scipy import stats
from utils import (
    load_wave2, load_wave1, get_satisfaction, get_drivers, get_use_cases,
    platform_count, complete_mask, LIKERT_MAP, MODEL_IDS, DRIVER_LABELS,
    USE_CASE_LABELS, MODEL_COLS,
)


def cronbach_alpha(df):
    """Compute Cronbach's alpha for a DataFrame of item scores."""
    df = df.dropna()
    k = df.shape[1]
    if k < 2 or len(df) < 2:
        return np.nan
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    data, _ = load_wave2()
    d1, _ = load_wave1()

    # ========== SECTION 3.2: Sample ==========
    print_header("Section 3.2: Sample Description")
    print(f"Wave 2 rows: {len(data)}")
    print(f"Wave 1 rows: {len(d1)}")
    print(f"Total: {len(data) + len(d1)}")

    mask = complete_mask(data)
    print(f"Wave 2 usable (occ + model): {mask.sum()}")
    finished = (data["Finished"].astype(str).str.strip().str.lower() == "true").sum()
    fin1 = (pd.to_numeric(d1["Finished"], errors="coerce") == 1).sum()
    print(f"Fully completed: {finished} + {fin1} = {finished + fin1}")

    # Demographics
    print(f"\nOccupation (n={data['QID2'].notna().sum()}):")
    print(data["QID2"].value_counts().to_string())

    freq = data["QID4"].value_counts()
    total_freq = freq.sum()
    print(f"\nUsage frequency (n={total_freq}):")
    for cat, n in freq.items():
        print(f"  {cat}: {n} ({n/total_freq*100:.1f}%)")

    # ========== SECTION 3.5: Robustness Checks ==========
    print_header("Section 3.5: Robustness Checks")
    gpt_sat = get_satisfaction(data, 1)

    # Full vs partial completers
    is_finished = data["Finished"].astype(str).str.strip().str.lower() == "true"
    full_gpt = data.loc[is_finished, "1_QID14_1"].map(LIKERT_MAP).dropna()
    part_gpt = data.loc[~is_finished, "1_QID14_1"].map(LIKERT_MAP).dropna()
    u, p = stats.mannwhitneyu(full_gpt, part_gpt, alternative="two-sided")
    print(f"Full completers ChatGPT: M={full_gpt.mean():.2f}, n={len(full_gpt)}")
    print(f"Partial responders ChatGPT: M={part_gpt.mean():.2f}, n={len(part_gpt)}")
    print(f"Mann-Whitney U={u:.0f}, p={p:.3f}")

    # Early vs late
    mid = len(data) // 2
    early = data.iloc[:mid]["1_QID14_1"].map(LIKERT_MAP).dropna()
    late = data.iloc[mid:]["1_QID14_1"].map(LIKERT_MAP).dropna()
    u2, p2 = stats.mannwhitneyu(early, late, alternative="two-sided")
    print(f"\nEarly half ChatGPT: M={early.mean():.2f}, n={len(early)}")
    print(f"Late half ChatGPT: M={late.mean():.2f}, n={len(late)}")
    print(f"Mann-Whitney U={u2:.0f}, p={p2:.3f}")

    # ========== SECTION 4.1: Market Structure ==========
    print_header("Section 4.1: Market Structure")

    # Model usage
    print("Model usage (N=237):")
    for i, name in MODEL_IDS.items():
        n = data[f"QID5_{i}"].notna().sum()
        print(f"  {name}: {n} ({n/237*100:.1f}%)")

    # Multi-platform
    pc = platform_count(data)
    active = pc[complete_mask(data)]
    print(f"\nMulti-platform (n={len(active)}):")
    print(f"  Mean: {active.mean():.2f}, SD: {active.std():.2f}, Median: {active.median():.0f}")
    print(f"  2+ platforms: {(active>=2).sum()}/{len(active)} = {(active>=2).mean()*100:.1f}%")
    print(f"  3+ platforms: {(active>=3).sum()}/{len(active)} = {(active>=3).mean()*100:.1f}%")
    print(f"  Single platform: {(active==1).sum()}/{len(active)} = {(active==1).mean()*100:.1f}%")
    print(f"  6-7 platforms: {(active>=6).sum()}/{len(active)} = {(active>=6).mean()*100:.1f}%")

    # Switching
    print("\nSwitching-in rates:")
    for m_id, m_name in MODEL_IDS.items():
        col = f"{m_id}_.3"
        if col in data.columns:
            sw = (data[col] == "Yes").sum()
            total = get_satisfaction(data, m_id).shape[0]
            if total > 0:
                print(f"  {m_name}: {sw}/{total} = {sw/total*100:.1f}%")

    # Switching sources
    print("\nSwitching sources:")
    for m_id, m_name in MODEL_IDS.items():
        if m_id == 1:
            continue
        col = f"{m_id}_.4"
        if col in data.columns:
            sources = data[col].dropna()
            if len(sources) > 0:
                print(f"  To {m_name}: {sources.value_counts().to_dict()}")

    # ========== SECTION 4.2: Satisfaction ==========
    print_header("Section 4.2: Satisfaction Convergence")

    groups = []
    for m_id, m_name in MODEL_IDS.items():
        sat = get_satisfaction(data, m_id)
        if len(sat) > 0:
            ci_lo = sat.mean() - 1.96 * sat.std() / np.sqrt(len(sat))
            ci_hi = sat.mean() + 1.96 * sat.std() / np.sqrt(len(sat))
            print(f"  {m_name}: M={sat.mean():.2f}, SD={sat.std():.2f}, "
                  f"95%CI [{ci_lo:.2f}, {ci_hi:.2f}], n={len(sat)}")
            groups.append(sat.values)

    h, p = stats.kruskal(*groups)
    N = sum(len(g) for g in groups)
    eps2 = h / (N - 1)
    print(f"\nKruskal-Wallis: H={h:.2f}, df={len(groups)-1}, p={p:.3f}, eps^2={eps2:.3f}")

    # Post-hoc: top platforms vs Llama
    gpt = get_satisfaction(data, 1)
    llama = get_satisfaction(data, 4)
    claude = get_satisfaction(data, 2)
    deepseek = get_satisfaction(data, 6)

    for name, sat in [("ChatGPT", gpt), ("Claude", claude), ("DeepSeek", deepseek)]:
        u, p = stats.mannwhitneyu(sat, llama, alternative="two-sided")
        d = (sat.mean() - llama.mean()) / np.sqrt((sat.std()**2 + llama.std()**2) / 2)
        print(f"  {name} vs Llama: d={d:.2f}, U={u:.0f}, p_uncorrected={p:.3f}")

    # NSS
    print("\nNet Satisfaction Scores:")
    for m_id, m_name in MODEL_IDS.items():
        col = f"{m_id}_QID14_1"
        vals = data[col].dropna()
        if len(vals) > 0:
            ext_sat = (vals == "Extremely satisfied").sum() / len(vals) * 100
            dis = ((vals == "Extremely dissatisfied").sum() +
                   (vals == "Somewhat dissatisfied").sum()) / len(vals) * 100
            print(f"  {m_name}: NSS={ext_sat - dis:+.1f}%, ExtSat={ext_sat:.1f}%")

    # Free vs paid
    print("\nFree vs Paid (ChatGPT):")
    free = data[data["1__1"].notna() & data["1__2"].isna() & data["1__3"].isna()]
    paid = data[data["1__2"].notna() | data["1__3"].notna()]
    free_sat = free["1_QID14_1"].map(LIKERT_MAP).dropna()
    paid_sat = paid["1_QID14_1"].map(LIKERT_MAP).dropna()
    u, p = stats.mannwhitneyu(free_sat, paid_sat, alternative="two-sided")
    print(f"  Free: M={free_sat.mean():.2f}, n={len(free_sat)}")
    print(f"  Paid: M={paid_sat.mean():.2f}, n={len(paid_sat)}")
    print(f"  U={u:.0f}, p={p:.3f}")

    # Tenure-satisfaction correlation
    tenure_map = {"Less than 1 month": 1, "1–3 months": 2, "3–6 months": 3,
                  "6–12 months": 4, "12–18 months": 5, "More than 18 months": 6}
    tenure = data["1_.1"].map(tenure_map)
    sat_gpt = data["1_QID14_1"].map(LIKERT_MAP)
    both = tenure.notna() & sat_gpt.notna()
    rho, p = stats.spearmanr(tenure[both], sat_gpt[both])
    print(f"\nTenure-satisfaction (ChatGPT): rho={rho:.2f}, p={p:.3f}, n={both.sum()}")

    # ========== SECTION 4.3: Adoption Drivers ==========
    print_header("Section 4.3: Adoption Drivers & Use Cases")

    for m_id, m_name in [(1, "ChatGPT"), (2, "Claude"), (6, "DeepSeek"), (5, "Grok")]:
        drivers = get_drivers(data, m_id)
        if len(drivers) > 0:
            print(f"\n{m_name} drivers (n={len(drivers)}):")
            for label in DRIVER_LABELS:
                vals = drivers[label].dropna()
                print(f"  {label}: M={vals.mean():.2f}, SD={vals.std():.2f}")

    # Use case performance
    print("\nUse case performance (Technical Tasks):")
    for m_id, m_name in [(1, "ChatGPT"), (2, "Claude"), (3, "Gemini"), (6, "DeepSeek")]:
        uc = get_use_cases(data, m_id)
        if "Technical" in uc.columns:
            tech = uc["Technical"].dropna()
            print(f"  {m_name}: M={tech.mean():.2f}, SD={tech.std():.2f}, n={len(tech)}")

    # KW test on Technical Tasks
    tech_groups = []
    for m_id in [1, 2, 3, 6]:
        uc = get_use_cases(data, m_id)
        if "Technical" in uc.columns:
            tech_groups.append(uc["Technical"].dropna().values)
    h, p = stats.kruskal(*tech_groups)
    print(f"  KW Technical: H={h:.2f}, df={len(tech_groups)-1}, p={p:.3f}")

    # ========== SECTION 4.3: Scale Reliability ==========
    print_header("Scale Reliability (Cronbach's Alpha)")

    for m_id, m_name in [(1, "ChatGPT"), (2, "Claude"), (3, "Gemini"), (6, "DeepSeek")]:
        uc = get_use_cases(data, m_id)
        dr = get_drivers(data, m_id)
        a_uc = cronbach_alpha(uc)
        a_dr = cronbach_alpha(dr)
        print(f"  {m_name}: Use case alpha={a_uc:.2f} (n={len(uc.dropna())}), "
              f"Driver alpha={a_dr:.2f} (n={len(dr.dropna())})")

    # ========== SECTION 4.4: First-Mover & Subgroups ==========
    print_header("Section 4.4: First-Mover & Anchoring")

    # First model %
    print("First model percentages:")
    for m_id, m_name in MODEL_IDS.items():
        col = f"{m_id}_"
        if col in data.columns:
            yes = (data[col] == "Yes").sum()
            no = (data[col] == "No").sum()
            total = yes + no
            if total > 0:
                print(f"  {m_name}: {yes}/{total} = {yes/total*100:.1f}%")

    # Subgroup: first-model status
    first_yes = data[data["1_"] == "Yes"]["1_QID14_1"].map(LIKERT_MAP).dropna()
    first_no = data[data["1_"] == "No"]["1_QID14_1"].map(LIKERT_MAP).dropna()
    u, p = stats.mannwhitneyu(first_yes, first_no, alternative="two-sided")
    print(f"\nFirst-model effect:")
    print(f"  First=Yes: M={first_yes.mean():.2f}, n={len(first_yes)}")
    print(f"  First=No: M={first_no.mean():.2f}, n={len(first_no)}")
    print(f"  Gap: {first_yes.mean() - first_no.mean():.2f}")
    print(f"  U={u:.0f}, p={p:.6f}")

    # Subgroup: daily vs non-daily
    daily = data[data["QID4"] == "Daily or almost daily"]
    nondaily = data[data["QID4"] != "Daily or almost daily"]
    daily_sat = daily["1_QID14_1"].map(LIKERT_MAP).dropna()
    nondaily_sat = nondaily["1_QID14_1"].map(LIKERT_MAP).dropna()
    u, p = stats.mannwhitneyu(daily_sat, nondaily_sat, alternative="two-sided")
    print(f"\nDaily vs non-daily (ChatGPT):")
    print(f"  Daily: M={daily_sat.mean():.2f}, n={len(daily_sat)}")
    print(f"  Non-daily: M={nondaily_sat.mean():.2f}, n={len(nondaily_sat)}")
    print(f"  U={u:.0f}, p={p:.3f}")

    # ========== SECTION 4.5: Pricing ==========
    print_header("Section 4.5: Pricing")

    # Subscription plans
    print("Subscription plans:")
    for m_id, m_name in MODEL_IDS.items():
        free = data[f"{m_id}__1"].notna().sum()
        paid_ind = data[f"{m_id}__2"].notna().sum()
        team = data[f"{m_id}__3"].notna().sum() if f"{m_id}__3" in data.columns else 0
        total = free + paid_ind + team
        if total > 0:
            print(f"  {m_name}: Free={free}({free/total*100:.1f}%), "
                  f"Paid={paid_ind}({paid_ind/total*100:.1f}%), n={total}")

    # Price response
    price_col = "1_.2"
    if price_col in data.columns:
        paid_users = data[data["1__2"].notna() | data["1__3"].notna()]
        price = paid_users[price_col].dropna()
        print(f"\nPrice response (ChatGPT paid, n={len(price)}):")
        for resp, n in price.value_counts().items():
            print(f"  {resp}: {n} ({n/len(price)*100:.1f}%)")

    # ========== SECTION 4.6: Qualitative ==========
    print_header("Section 4.6: Qualitative")

    q16 = data["QID16"].dropna().shape[0]
    q17 = data["QID17"].dropna().shape[0]
    q16_w1 = d1["QID16"].dropna().shape[0] if "QID16" in d1.columns else 0
    q17_w1 = d1["QID17"].dropna().shape[0] if "QID17" in d1.columns else 0
    print(f"Frustrations: {q16} + {q16_w1} = {q16 + q16_w1}")
    print(f"Features: {q17} + {q17_w1} = {q17 + q17_w1}")
    print(f"Total qualitative: {q16 + q16_w1 + q17 + q17_w1}")

    print("\n=== ANALYSIS COMPLETE ===")


if __name__ == "__main__":
    main()
