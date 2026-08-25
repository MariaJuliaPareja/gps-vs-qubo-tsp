"""
statistical_analysis.py
Statistical analysis plan: descriptive stats, Shapiro-Wilk, Wilcoxon
(paired by replica), correlation, LOWESS regression.

Usage:
    python statistical_analysis.py --input results/consolidated.csv
"""

import argparse
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ALPHA = 0.05

def descriptive_analysis(df, metric):
    return df.groupby("formulation")[metric].agg(mean="mean", std="std",
                                                   min="min", max="max", n="count")

def normality_test(df, metric):
    results = {}
    for form in df["formulation"].unique():
        values = df.loc[df["formulation"] == form, metric].dropna()
        if len(values) < 3:
            results[form] = {"W": None, "p_value": None, "is_normal": None}
            continue
        stat, p = stats.shapiro(values)
        results[form] = {"W": stat, "p_value": p, "is_normal": p > ALPHA}
    return results

def wilcoxon_test(df, metric, id_cols=("instance", "replica")):
    pivot = df.pivot_table(index=list(id_cols), columns="formulation", values=metric).dropna()
    if "gps" not in pivot.columns or "traditional" not in pivot.columns or len(pivot) < 1:
        return {"error": "Missing complete GPS/Traditional pairs for this metric."}
    stat, p = stats.wilcoxon(pivot["gps"], pivot["traditional"])
    return {
        "n_pairs": len(pivot), "W_statistic": stat, "p_value": p,
        "significant": p < ALPHA,
        "mean_diff_gps_minus_traditional": (pivot["gps"] - pivot["traditional"]).mean(),
    }

def correlation_analysis(df, metric_x, metric_y):
    sub = df[[metric_x, metric_y]].dropna()
    if len(sub) < 3:
        return {"error": "Insufficient data."}
    _, p_x = stats.shapiro(sub[metric_x])
    _, p_y = stats.shapiro(sub[metric_y])
    if p_x > ALPHA and p_y > ALPHA:
        r, p = stats.pearsonr(sub[metric_x], sub[metric_y])
        method = "Pearson"
    else:
        r, p = stats.spearmanr(sub[metric_x], sub[metric_y])
        method = "Spearman"
    return {"method": method, "coefficient": r, "p_value": p, "significant": p < ALPHA}

def scalability_lowess(df, metric, frac=0.5):
    results = {}
    for form in df["formulation"].unique():
        sub = df[df["formulation"] == form][["n_cities", metric]].dropna().sort_values("n_cities")
        if len(sub) < 3:
            results[form] = {"error": "At least 3 points (distinct sizes) are required."}
            continue
        smoothed = sm.nonparametric.lowess(sub[metric], sub["n_cities"], frac=frac)
        results[form] = {"n_points": smoothed[:, 0].tolist(), "smoothed_value": smoothed[:, 1].tolist()}
    return results

def full_report(df, metrics=("execution_time_sec", "circuit_depth", "gate_count",
                              "n_qubits", "objective_value")):
    report = {}
    for metric in metrics:
        if metric not in df.columns:
            continue
        report[metric] = {
            "descriptive": descriptive_analysis(df, metric).to_dict(),
            "normality": normality_test(df, metric),
            "wilcoxon": wilcoxon_test(df, metric),
            "scalability_lowess": scalability_lowess(df, metric),
        }
    pairs = [("circuit_depth", "execution_time_sec"), ("n_qubits", "objective_value"),
             ("gate_count", "execution_time_sec")]
    report["correlations"] = {f"{x}_vs_{y}": correlation_analysis(df, x, y)
                               for x, y in pairs if x in df.columns and y in df.columns}
    return report

def print_report(report):
    for metric, content in report.items():
        if metric == "correlations":
            continue
        print(f"\n=== {metric} ===")
        print(pd.DataFrame(content["descriptive"]))
        for form, r in content["normality"].items():
            print(f"Shapiro-Wilk {form}: W={r.get('W')}, p={r.get('p_value')}, normal={r.get('is_normal')}")
        w = content["wilcoxon"]
        print("Wilcoxon:", w.get("error") or
              f"n={w['n_pairs']}, W={w['W_statistic']:.4f}, p={w['p_value']:.4f}, sig={w['significant']}")

    print("\n=== Correlations ===")
    for pair, r in report.get("correlations", {}).items():
        print(pair, ":", r.get("error") or f"{r['method']} r={r['coefficient']:.4f}, p={r['p_value']:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="results/consolidated.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    print_report(full_report(df))