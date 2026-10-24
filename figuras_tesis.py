"""Figuras y tablas de resultados (cap. 5 y 6), en español e inglés."""
# synth03/gps/réplica 1 se excluye de energía y brecha (objective_value idéntico
# al E_opt de Tradicional: dato contaminado). Se conserva para el tiempo.
# Con bitstring, la energía usada es E_recalc = x^T Q x, no objective_value.
# Brecha = (E - E_opt) / A.
import os
import math
import itertools
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import statsmodels.api as sm

from formulations import build_traditional_qubo, build_gps_qubo
from statistical_analysis_v2 import load_results, evaluate_quality, get_dist_matrix

RESULTS_DIR = "results_aws_final"
CSV_PATH = os.path.join(RESULTS_DIR, "aws_consolidated.csv")
RECURSOS = "recursos_circuito.csv"
OUT = "figuras"
RAM_GB = 31
IDIOMAS = ["es", "en"]

T = {
    "es": {
        "trad": "QUBO Tradicional", "gps": "GPS",
        "trad_n2": "QUBO Tradicional (n²)", "gps_impl": "GPS implementada, 3(n−1)(n+2)",
        "nativa": "Nativa (n³, teórica)",
        "n_ciudades": "Número de ciudades (n)",
        "var_i": "Índice de variable i", "var_j": "Índice de variable j",
        "variables": "variables", "densidad": "densidad",
        "panel_a_q": "(a) QUBO Tradicional", "panel_b_q": "(b) GPS",
        "qubits_log": "Qubits lógicos (escala log)",
        "limite": "Límite de simulación (~{q} qubits, {gb} GB)",
        "profundidad": "Profundidad del circuito", "cnot": "Número de compuertas CNOT",
        "factibles_pct": "Réplicas factibles (%)",
        "tiempo_log": "Tiempo por réplica (s, escala log)",
        "brecha": "Brecha energética normalizada (E − E$_{opt}$)/A",
        "trad_rep": "QUBO Tradicional (réplicas)", "gps_rep": "GPS, n = 3 (réplicas)",
        "lowess_trad": "LOWESS (Tradicional)",
        "no_sim": "no simulable",
        "frac_fact": "Estados factibles (% del espacio, log)",
        "densidad_pct": "Densidad de Q (% de pares con interacción)",
        "grado": "Conectividad media por qubit",
    },
    "en": {
        "trad": "Traditional QUBO", "gps": "GPS",
        "trad_n2": "Traditional QUBO (n²)", "gps_impl": "GPS as implemented, 3(n−1)(n+2)",
        "nativa": "Native (n³, theoretical)",
        "n_ciudades": "Number of cities (n)",
        "var_i": "Variable index i", "var_j": "Variable index j",
        "variables": "variables", "densidad": "density",
        "panel_a_q": "(a) Traditional QUBO", "panel_b_q": "(b) GPS",
        "qubits_log": "Logical qubits (log scale)",
        "limite": "Simulation limit (~{q} qubits, {gb} GB)",
        "profundidad": "Circuit depth", "cnot": "Number of CNOT gates",
        "factibles_pct": "Feasible replicas (%)",
        "tiempo_log": "Time per replica (s, log scale)",
        "brecha": "Penalty-normalized energy gap (E − E$_{opt}$)/A",
        "trad_rep": "Traditional QUBO (replicas)", "gps_rep": "GPS, n = 3 (replicas)",
        "lowess_trad": "LOWESS (Traditional)",
        "no_sim": "not simulable",
        "frac_fact": "Feasible states (% of space, log)",
        "densidad_pct": "Q density (% of pairs with interaction)",
        "grado": "Mean connectivity per qubit",
    },
}

serif = ["Times New Roman", "Liberation Serif", "Nimbus Roman", "TeX Gyre Termes", "DejaVu Serif"]
disponibles = {f.name for f in font_manager.fontManager.ttflist}
fuente = next((f for f in serif if f in disponibles), "serif")
if fuente != "Times New Roman":
    warnings.warn(f"Times New Roman no está instalada; usando '{fuente}'. "
                  f"(En Arch/Manjaro: instala ttf-ms-fonts y borra ~/.cache/matplotlib)")
plt.rcParams.update({
    "font.family": "serif", "font.serif": [fuente], "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.88", "grid.linewidth": 0.6,
    "savefig.dpi": 300, "savefig.bbox": "tight", "figure.dpi": 100,
})
C_GPS, C_TRA, C_NAT = "0.25", "0.65", "0.45"


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return max(0.0, c - h), min(1.0, c + h)


def densidad(Q):
    Q = np.asarray(Q, float)
    Qs = (Q + Q.T) / 2
    nz = np.abs(Qs) > 1e-12
    off = np.triu(nz, 1).sum()
    return nz, off / (Qs.shape[0] * (Qs.shape[0] - 1) / 2)


print("Cargando y evaluando resultados...")
df = evaluate_quality(load_results(RESULTS_DIR, CSV_PATH))
df["feasible_f"] = df["feasible"].astype(float)
df["E_usada"] = df["E_recalc"].where(df["E_recalc"].notna(), df["objective_value"])
df["brecha"] = (df["E_usada"] - df["E_opt"]) / df["A"]
df["excluir_energia"] = (df["instance"] == "synth03") & (df["formulation"] == "gps") & (df["replica"] == 1)
os.makedirs(OUT, exist_ok=True)
df.to_csv(os.path.join(OUT, "datos_consolidados_corregidos.csv"), index=False)

rec = pd.read_csv(RECURSOS)
rec["densidad_Q"] = rec["terminos_cuadraticos"] / (rec["qubits_activos"] * (rec["qubits_activos"] - 1) / 2)
rec["grado_medio"] = 2 * rec["terminos_cuadraticos"] / rec["qubits_activos"]
tr_r = rec[rec["formulacion"] == "traditional"].sort_values("n")
gp_r = rec[rec["formulacion"] == "gps"].sort_values("n")
n3 = df[df["instance"] == "synth03"]
trad = df[df["formulation"] == "traditional"]
dist3 = get_dist_matrix("synth03", 3)
Qt3 = build_traditional_qubo(dist3)
Qg3 = build_gps_qubo(dist3)[0]
ns = np.array([3, 4, 5, 6])
lim_q = int(math.floor(math.log2(RAM_GB * 1e9 / 16)))


def generar(lang):
    t = T[lang]
    out = os.path.join(OUT, lang)
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(0)

    def guardar(fig, nombre):
        fig.savefig(os.path.join(out, nombre))
        plt.close(fig)
        print(f"  ✓ {lang}/{nombre}")

    fig, axs = plt.subplots(1, 2, figsize=(9, 4.4))
    for ax, Q, nombre in [(axs[0], Qt3, t["panel_a_q"]), (axs[1], Qg3, t["panel_b_q"])]:
        nz, dens = densidad(Q)
        ax.imshow(nz, cmap="Greys", interpolation="nearest")
        ax.set_title(f"{nombre}\n{nz.shape[0]} {t['variables']} · {t['densidad']} {dens:.0%}", fontsize=11)
        ax.set_xlabel(t["var_j"])
        ax.set_ylabel(t["var_i"])
        ax.grid(False)
    guardar(fig, "fig01_estructura_Q_n3.png")

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.axhspan(lim_q, 400, color="0.92", zorder=0)
    ax.axhline(lim_q, color="0.3", ls=":", lw=1)
    ax.text(3.05, lim_q * 1.08, t["limite"].format(q=lim_q, gb=RAM_GB), fontsize=9)
    ax.plot(tr_r["n"], tr_r["qubits_activos"], color=C_TRA, marker="o", lw=2, label=t["trad_n2"])
    ax.plot(gp_r["n"], gp_r["qubits_activos"], color=C_GPS, marker="s", lw=2, label=t["gps_impl"])
    ax.plot(ns, ns**3, color=C_NAT, marker="^", ls="--", lw=1.5, label=t["nativa"])
    ax.set_yscale("log")
    ax.set_ylim(5, 400)
    ax.set_xticks(ns)
    ax.set_xlabel(t["n_ciudades"])
    ax.set_ylabel(t["qubits_log"])
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    guardar(fig, "fig02_qubits_vs_n.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, col, ylab in [(axs[0], "profundidad_transpilada", t["profundidad"]), (axs[1], "cx", t["cnot"])]:
        ax.plot(tr_r["n"], tr_r[col], color=C_TRA, marker="o", lw=2, label=t["trad"])
        ax.plot(gp_r["n"], gp_r[col], color=C_GPS, marker="s", lw=2, label=t["gps"])
        ax.set_xticks(ns)
        ax.set_xlabel(t["n_ciudades"])
        ax.set_ylabel(ylab)
    axs[0].text(-0.15, 1.04, "(a)", transform=axs[0].transAxes)
    axs[1].text(-0.15, 1.04, "(b)", transform=axs[1].transAxes)
    axs[0].legend(frameon=False, fontsize=9)
    guardar(fig, "fig03_profundidad_cnot.png")

    fig, ax = plt.subplots(figsize=(5, 3.8))
    for i, form in enumerate(["gps", "traditional"]):
        s = n3[n3["formulation"] == form]["feasible_f"].dropna()
        k, n = int(s.sum()), len(s)
        lo, hi = wilson(k, n)
        p = k / n if n else np.nan
        ax.bar(i, p * 100, width=0.55, color="white" if form == "gps" else C_TRA,
               edgecolor="black", hatch="//" if form == "gps" else "", lw=0.8)
        ax.errorbar(i, p * 100, yerr=[[(p - lo) * 100], [(hi - p) * 100]], color="black", capsize=5, lw=1)
        ax.text(i, max(hi * 100, 3) + 3, f"{k}/{n}", ha="center", fontsize=10)
    ax.set_xticks([0, 1], [t["gps"], t["trad"]])
    ax.set_ylim(0, 110)
    ax.set_ylabel(t["factibles_pct"])
    ax.grid(axis="x", visible=False)
    guardar(fig, "fig04_factibilidad_n3.png")

    fig, ax = plt.subplots(figsize=(5, 3.8))
    datos = [n3[n3["formulation"] == f]["execution_time_sec"].values for f in ("gps", "traditional")]
    bp = ax.boxplot(datos, widths=0.5, patch_artist=True, medianprops=dict(color="black"))
    for patch, f in zip(bp["boxes"], ("gps", "traditional")):
        patch.set_facecolor("white" if f == "gps" else C_TRA)
        patch.set_hatch("//" if f == "gps" else "")
        patch.set_edgecolor("black")
    for i, d in enumerate(datos, start=1):
        ax.scatter(i + rng.uniform(-0.1, 0.1, len(d)), d, s=10, color="black", zorder=3)
    ax.set_xticks([1, 2], [t["gps"], t["trad"]])
    ax.set_yscale("log")
    ax.set_ylabel(t["tiempo_log"])
    ax.grid(axis="x", visible=False)
    guardar(fig, "fig05_tiempo_n3.png")

    t_ok = trad[~trad["excluir_energia"]].dropna(subset=["brecha"])
    g3 = n3[(n3["formulation"] == "gps") & (~n3["excluir_energia"])].dropna(subset=["brecha"])
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(t_ok["n_cities"] + rng.uniform(-0.07, 0.07, len(t_ok)), t_ok["brecha"],
               s=18, color=C_TRA, edgecolor="black", lw=0.4, marker="o", label=t["trad_rep"])
    ax.scatter(g3["n_cities"] + 0.18 + rng.uniform(-0.05, 0.05, len(g3)), g3["brecha"],
               s=20, color="white", edgecolor="black", lw=0.8, marker="s", label=t["gps_rep"])
    lw = pd.DataFrame(sm.nonparametric.lowess(t_ok["brecha"], t_ok["n_cities"], frac=1.0, it=0),
                      columns=["n", "y"]).drop_duplicates("n")
    ax.plot(lw["n"], lw["y"], color="black", lw=1.5, label=t["lowess_trad"])
    ax.set_xticks([3, 4, 5])
    ax.set_xlabel(t["n_ciudades"])
    ax.set_ylabel(t["brecha"])
    ax.legend(frameon=False, fontsize=9)
    guardar(fig, "fig06_brecha_vs_n.png")

    fac = trad.groupby("n_cities")["feasible_f"].agg(["sum", "count"]).reset_index()
    g_k = int(n3[n3["formulation"] == "gps"]["feasible_f"].sum())
    g_n = int(n3[n3["formulation"] == "gps"]["feasible_f"].count())
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    x = np.arange(len(fac))
    ax.bar(x - 0.15, fac["sum"] / fac["count"] * 100, width=0.3, color=C_TRA, edgecolor="black", lw=0.8, label=t["trad"])
    ax.bar(0.15, g_k / g_n * 100, width=0.3, color="white", edgecolor="black", hatch="//", lw=0.8, label=t["gps"])
    for i, r in fac.iterrows():
        ax.text(i - 0.15, r["sum"] / r["count"] * 100 + 3, f"{int(r['sum'])}/{int(r['count'])}", ha="center", fontsize=9)
    ax.text(0.15, 3, f"{g_k}/{g_n}", ha="center", fontsize=9)
    for i in range(1, len(fac)):
        ax.text(i + 0.15, 3, t["no_sim"], ha="center", fontsize=8, rotation=90, va="bottom")
    ax.set_xticks(x, [f"n = {int(v)}" for v in fac["n_cities"]])
    ax.set_ylim(0, 110)
    ax.set_ylabel(t["factibles_pct"])
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="x", visible=False)
    guardar(fig, "fig07_factibilidad_vs_n.png")

    frac = np.array([math.factorial(n) / 2 ** (n * n) for n in ns])
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(ns, frac * 100, color="black", marker="o", lw=1.5)
    for n, f in zip(ns, frac):
        ax.annotate(f"{math.factorial(n)} / 2^{n*n}", (n, f * 100), textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.set_yscale("log")
    ax.set_xticks(ns)
    ax.set_xlabel(t["n_ciudades"])
    ax.set_ylabel(t["frac_fact"])
    guardar(fig, "fig08_fraccion_factible.png")

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.scatter(trad["n_cities"] + rng.uniform(-0.07, 0.07, len(trad)), trad["execution_time_sec"],
               s=18, color=C_TRA, edgecolor="black", lw=0.4)
    lw_t = pd.DataFrame(sm.nonparametric.lowess(trad["execution_time_sec"], trad["n_cities"], frac=1.0, it=0),
                        columns=["n", "y"]).drop_duplicates("n")
    ax.plot(lw_t["n"], lw_t["y"], color="black", lw=1.5)
    ax.set_yscale("log")
    ax.set_xticks([3, 4, 5])
    ax.set_xlabel(t["n_ciudades"])
    ax.set_ylabel(t["tiempo_log"])
    guardar(fig, "fig09_tiempo_vs_n.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.9))
    for ax, col, ylab, esc in [(axs[0], "densidad_Q", t["densidad_pct"], 100),
                               (axs[1], "grado_medio", t["grado"], 1)]:
        w = 0.36
        ax.bar(tr_r["n"] - w / 2, tr_r[col] * esc, width=w, color=C_TRA, edgecolor="black", lw=0.8, label=t["trad"])
        ax.bar(gp_r["n"] + w / 2, gp_r[col] * esc, width=w, color="white", edgecolor="black", hatch="//", lw=0.8, label=t["gps"])
        for _, r in tr_r.iterrows():
            v = r[col] * esc
            ax.text(r["n"] - w / 2, v * 1.02 + 0.5, f"{v:.0f}" if esc == 100 else f"{v:.1f}", ha="center", fontsize=8)
        for _, r in gp_r.iterrows():
            v = r[col] * esc
            ax.text(r["n"] + w / 2, v * 1.02 + 0.5, f"{v:.0f}" if esc == 100 else f"{v:.1f}", ha="center", fontsize=8)
        ax.set_xticks(ns)
        ax.set_xlabel(t["n_ciudades"])
        ax.set_ylabel(ylab)
        ax.grid(axis="x", visible=False)
    axs[0].set_ylim(0, 112)
    axs[0].text(-0.15, 1.04, "(a)", transform=axs[0].transAxes)
    axs[1].text(-0.15, 1.04, "(b)", transform=axs[1].transAxes)
    axs[0].legend(frameon=False, fontsize=9)
    guardar(fig, "fig10_dispersion_Q.png")


print("\nGenerando figuras:")
for lang in IDIOMAS:
    generar(lang)

cols = ["n", "formulacion", "qubits_activos", "terminos_lineales", "terminos_cuadraticos", "densidad_Q",
        "grado_medio", "profundidad_transpilada", "compuertas_total", "cx", "memoria_statevector_GB"]
if "terminos_lineales" not in rec.columns:
    warnings.warn("recursos_circuito.csv no tiene 'terminos_lineales': vuelve a correr recursos_circuito.py")
    cols.remove("terminos_lineales")
tab_rec = rec[cols].copy()
# Restricciones contadas desde build_gps_qubo / gps_violations (N = n-1, n+1 nodos aumentados):
#   GPS igualdades = one-hot por par (n²+n-2) + salida (n) + entrada (n) + orden (n(n+1)/2 - 1)
#                  = (3n² + 7n - 6)/2      -> n = 3: 21 (coincide con el análisis v2)
#   GPS transitividad (penalización λ) = (n-1)(n-2)(n-3)
#   Tradicional = 2n (cada ciudad una vez + cada posición una vez)
nn = tab_rec["n"]
es_gps = tab_rec["formulacion"] == "gps"
tab_rec["restr_igualdad"] = np.where(es_gps, (3 * nn**2 + 7 * nn - 6) // 2, 2 * nn)
tab_rec["restr_transitividad"] = np.where(es_gps, (nn - 1) * (nn - 2) * (nn - 3), 0)
tab_rec["restricciones_total"] = tab_rec["restr_igualdad"] + tab_rec["restr_transitividad"]
assert int(tab_rec.loc[es_gps & (nn == 3), "restr_igualdad"].iloc[0]) == 21
tab_rec.to_csv(os.path.join(OUT, "tabla_recursos.csv"), index=False)

res = (df[~df["excluir_energia"]]
       .groupby(["n_cities", "formulation"])
       .agg(replicas=("replica", "count"), factibles=("feasible_f", "sum"),
            brecha_mediana=("brecha", "median"), brecha_media=("brecha", "mean"),
            brecha_std=("brecha", "std"), tiempo_mediana_s=("execution_time_sec", "median"))
       .reset_index())
res.to_csv(os.path.join(OUT, "tabla_resultados.csv"), index=False)

# OE3: brecha de RUTA (costo del tour decodificado vs óptimo por fuerza bruta), solo soluciones factibles
def costo_optimo(dist):
    n = dist.shape[0]
    return min(sum(dist[t[i], t[(i + 1) % n]] for i in range(n))
               for t in ([0] + list(p) for p in itertools.permutations(range(1, n))))

filas = []
for (inst, n, form), g in df.groupby(["instance", "n_cities", "formulation"]):
    opt = costo_optimo(np.asarray(get_dist_matrix(inst, int(n)), float))
    fac = g[g["feasible_f"] == 1].dropna(subset=["tour_cost"])
    br = (fac["tour_cost"] - opt) / opt * 100
    filas.append({"n": int(n), "formulacion": form, "replicas": len(g),
                  "factibles": int(g["feasible_f"].sum()), "costo_optimo": opt,
                  "brecha_ruta_media_pct": br.mean() if len(br) else np.nan,
                  "brecha_ruta_max_pct": br.max() if len(br) else np.nan,
                  "nota": "" if len(br) else "no definida (0 soluciones factibles)"})
tab_ruta = pd.DataFrame(filas).sort_values(["n", "formulacion"])
tab_ruta.to_csv(os.path.join(OUT, "tabla_brecha_ruta.csv"), index=False)
print("\nBrecha de ruta (OE3, solo factibles):")
print(tab_ruta.to_string(index=False))

print("\nTabla de resultados (réplica GPS 1 excluida de brecha):")
print(res.to_string(index=False))
print("\nTabla de recursos:")
print(tab_rec.to_string(index=False))
print(f"\nListo. Figuras en ./{OUT}/es y ./{OUT}/en, tablas en ./{OUT}/")