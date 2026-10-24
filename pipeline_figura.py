"""Figura 11: pipeline experimental (paneles a–f) desde el código y los datos del proyecto."""
import os
import sys
import math
import itertools
import warnings
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Arc

from formulations import build_traditional_qubo, build_gps_qubo
from statistical_analysis_v2 import load_results, evaluate_quality, get_dist_matrix, traditional_tour

N_EJ = 4                      # instancia de ejemplo para (a), (b) y (e)
INST = f"synth0{N_EJ}"
REPS = 2                      # parámetros de run_aws_full.py
MAXITER = 30
RESULTS_DIR = "results_aws_final"
CSV_PATH = os.path.join(RESULTS_DIR, "aws_consolidated.csv")
OUT = "figuras"
BN = "--bn" in sys.argv

BLUE = "#333333" if BN else "#2E6094"
GREEN = "#555555" if BN else "#6AA84F"
LGREEN = "#DDDDDD" if BN else "#E6F2DC"
DGREEN = "#222222" if BN else "#3F7A2A"
GATE = "#A6A6A6"
INK = "#111111"
GREY = "#777777"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "Helvetica", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none",
})
PX = 0.72  # 1 px del lienzo (1360 x 640 a 100 dpi) = 0.72 pt

T = {
    "es": {
        "a": "instancia TSP", "b": "codificación QUBO", "c": "circuito QAOA",
        "d": "bucle híbrido", "e": "decodificación", "f": "evaluación",
        "trad": "QUBO Tradicional", "gps": "GPS",
        "trad_sub": "ciudad × posición", "gps_sub": "origen × destino · depósito duplicado",
        "arcos": "arcos", "prec": "i después de j", "ning": "i antes (no adyac.)", "capas": "capas alternas de costo y mezcla",
        "circ": ["circuito", "QAOA"], "opt": ["optimizador", "clásico"],
        "replicas": "réplicas", "grid_cm": "ciudad × posición", "grid_pm": "posición × ciudad",
        "fact": "factible", "infact": "infactible", "viola": "viola restricciones",
        "m": ["factibilidad", "brecha", "tiempo", "recursos"],
        "vs": "vs", "med": "mediana",
    },
    "en": {
        "a": "TSP instance", "b": "QUBO encoding", "c": "QAOA circuit",
        "d": "hybrid loop", "e": "decoding", "f": "evaluation",
        "trad": "Traditional QUBO", "gps": "GPS",
        "trad_sub": "city × position", "gps_sub": "origin × destination · split depot",
        "arcos": "arcs", "prec": "i after j", "ning": "i before (non-adj.)", "capas": "alternating cost and mixer layers",
        "circ": ["QAOA", "circuit"], "opt": ["classical", "optimizer"],
        "replicas": "replicas", "grid_cm": "city × position", "grid_pm": "position × city",
        "fact": "feasible", "infact": "infeasible", "viola": "violates constraints",
        "m": ["feasibility", "gap", "time", "resources"],
        "vs": "vs", "med": "median",
    },
}

n = N_EJ
dist = np.asarray(get_dist_matrix(INST, n), float)
letras = [chr(ord("A") + i) for i in range(n)]

# posiciones 2D desde la matriz de distancias (MDS clásico; exacto si es euclidiana)
J = np.eye(n) - np.ones((n, n)) / n
B = -0.5 * J @ (dist ** 2) @ J
w, v = np.linalg.eigh(B)
idx = np.argsort(w)[::-1][:2]
XY = v[:, idx] * np.sqrt(np.maximum(w[idx], 0))


def costo(t):
    return sum(dist[t[i], t[(i + 1) % n]] for i in range(n))


tour = min(([0] + list(p) for p in itertools.permutations(range(1, n))), key=costo)
aristas = lambda t: {frozenset((t[i], t[(i + 1) % len(t)])) for i in range(len(t))}

q_trad = np.asarray(build_traditional_qubo(dist)).shape[0]
q_gps = np.asarray(build_gps_qubo(dist)[0]).shape[0]


def codificar(t, ciudad_mayor):
    b = [0] * (n * n)
    for p, c in enumerate(t):
        b[c * n + p if ciudad_mayor else p * n + c] = 1
    return b


# traditional_tour fija un solo orden; se prueban ciudad×posición y posición×ciudad.
orden = None
for cm in (True, False):
    try:
        dec = traditional_tour(codificar(tour, cm), n)
    except Exception:
        dec = None
    if dec is not None and aristas(list(dec)) == aristas(tour):
        orden = cm
        break
if orden is None:
    warnings.warn("traditional_tour no reconoció el bitstring en ningún orden; se usa ciudad×posición.")
    orden = True
bits = codificar(tour, orden)

df = evaluate_quality(load_results(RESULTS_DIR, CSV_PATH))
df["feasible_f"] = df["feasible"].astype(float)
tr = df[df["formulation"] == "traditional"]
grupos = defaultdict(list)
for nn, c in tr.groupby("n_cities")["replica"].count().items():
    grupos[int(c)].append(int(nn))
rep_txt = ", ".join(f"{c} (n = {', '.join(map(str, ns))})" for c, ns in sorted(grupos.items(), reverse=True))
d3 = df[df["n_cities"] == 3]
fk = {f: (int(d3[d3["formulation"] == f]["feasible_f"].sum()), int(d3[d3["formulation"] == f]["feasible_f"].count()))
      for f in ("gps", "traditional")}
tmed = {f: d3[d3["formulation"] == f]["execution_time_sec"].median() for f in ("gps", "traditional")}


def txt(ax, x, y, s, size=14, ha="left", color=INK, **kw):
    ax.text(x, y, s, fontsize=size * PX, ha=ha, va="baseline", color=color, **kw)


def line(ax, x1, y1, x2, y2, color=INK, lw=1.6, **kw):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw * PX, solid_capstyle="round", **kw)


def circ(ax, x, y, r, fc="none", ec=GREY, lw=1.6, z=3):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw * PX, zorder=z))


def rbox(ax, x, y, w, h, fc="white", ec="none", lw=1.6, r=4, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw * PX, zorder=z))


def corchete_h(ax, x1, x2, y, label=None, ly=None):
    line(ax, x1, y, x2, y, BLUE, 3); line(ax, x1, y - 8, x1, y + 8, BLUE, 3); line(ax, x2, y - 8, x2, y + 8, BLUE, 3)
    if label:
        txt(ax, (x1 + x2) / 2, ly or y + 28, label, 20, "center", BLUE, fontweight="bold", fontstyle="italic")


def corchete_v(ax, x, y1, y2, label=None):
    line(ax, x, y1, x, y2, BLUE, 3); line(ax, x - 8, y1, x + 8, y1, BLUE, 3); line(ax, x - 8, y2, x + 8, y2, BLUE, 3)
    if label:
        txt(ax, x - 14, (y1 + y2) / 2 + 7, label, 20, "right", BLUE, fontweight="bold", fontstyle="italic")


def flecha(ax, x1, y1, x2, y2, color="#333333", lw=1.6):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw * PX, mutation_scale=14))


def encajar(P, x0, x1, y0, y1):
    P = P - P.min(axis=0)
    esc = min((x1 - x0) / max(P[:, 0].max(), 1e-9), (y1 - y0) / max(P[:, 1].max(), 1e-9))
    P = P * esc
    off = np.array([x0 + (x1 - x0 - P[:, 0].max()) / 2, y0 + (y1 - y0 - P[:, 1].max()) / 2])
    return P + off


def panel(ax, x, y, letra, titulo, cx):
    txt(ax, x, y, f"({letra})", 26, fontweight="bold")
    txt(ax, cx, y, titulo, 18, "center")


def dibujar(lang):
    t = T[lang]
    fig = plt.figure(figsize=(13.6, 6.4), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1360); ax.set_ylim(640, 0); ax.set_aspect("equal"); ax.axis("off")

    panel(ax, 20, 45, "a", t["a"], 165)
    P = encajar(XY, 60, 270, 90, 290)
    ta = aristas(tour)
    for i, j in itertools.combinations(range(n), 2):
        if frozenset((i, j)) not in ta:
            line(ax, *P[i], *P[j], "#BBBBBB", 1.5, ls=(0, (5, 4)))
    for k in range(n):
        i, j = tour[k], tour[(k + 1) % n]
        line(ax, *P[i], *P[j], "#222222", 3)
    c0 = P.mean(axis=0)
    for i in range(n):
        circ(ax, *P[i], 7, fc=INK, ec=INK, z=4)
        d = P[i] - c0
        d = d / (np.linalg.norm(d) + 1e-9) * 18
        txt(ax, P[i][0] + d[0], P[i][1] + d[1] + 5, letras[i], 13, "center", "#333333")
    m = (P[tour[0]] + P[tour[1]]) / 2
    nrm = np.array([-(P[tour[1]] - P[tour[0]])[1], (P[tour[1]] - P[tour[0]])[0]])
    nrm = nrm / (np.linalg.norm(nrm) + 1e-9) * 16
    if np.dot(nrm, m - c0) < 0:
        nrm = -nrm
    txt(ax, m[0] + nrm[0], m[1] + nrm[1] + 5, r"$d_{ij}$", 17, "center", BLUE)
    corchete_h(ax, 60, 270, 332, rf"$n = {n}$", 362)

    panel(ax, 330, 45, "b", t["b"], 575)
    s1, ox, oy = 34, 410, 110
    for p in range(n):
        txt(ax, ox + s1 * p, 90, str(p + 1), 14, "center", "#333333")
    for c in range(n):
        txt(ax, 390, oy + s1 * c + 5, letras[c], 14, "right", "#333333")
        for p in range(n):
            on = tour[p] == c
            circ(ax, ox + s1 * p, oy + s1 * c, 13, LGREEN if on else "none", GREEN if on else GREY, 3 if on else 1.6)
    corchete_v(ax, 362, oy - 13, oy + s1 * (n - 1) + 13, r"$n$")
    corchete_h(ax, ox - 13, ox + s1 * (n - 1) + 13, oy + s1 * (n - 1) + 32, r"$n$")
    txt(ax, 461, 302, t["trad"], 16, "center", fontweight="bold")
    txt(ax, 461, 324, f"n² = {q_trad} qubits", 14, "center", "#444444")
    txt(ax, 461, 343, t["trad_sub"], 13, "center", "#666666")

    # GPS como en build_gps_qubo: N = n-1, nodos aumentados 0..N+1 (depósito duplicado:
    # 0 = salida, N+1 = llegada); se excluyen la diagonal y el par {0, N+1}.
    M = n + 1
    s2, gx, gy, rr = 24, 613, 133, 8.5
    for dx, fc, ec in [(32, "#EFEFEF", "#999999"), (16, "#F6F6F6", "#999999"), (0, "white", GREY)]:
        rbox(ax, 600 + dx, 120 - dx, 126, 126, fc, ec, 1.5, 6, z=2)
    aug_lbl = [letras[0]] + letras[1:] + [letras[0] + "′"]
    ruta = [0] + list(tour[1:]) + [M - 1]          # índices aumentados del tour óptimo
    arcos = {(ruta[k], ruta[k + 1]) for k in range(len(ruta) - 1)}
    for i in range(M):
        txt(ax, 596, gy + s2 * i + 4, aug_lbl[i], 12, "right", "#333333")
        txt(ax, gx + s2 * i, 262, aug_lbl[i], 12, "center", "#333333")
        for j in range(M):
            x, y = gx + s2 * j, gy + s2 * i
            if i == j or {i, j} == {0, M - 1}:
                circ(ax, x, y, 2, "#CCCCCC", "#CCCCCC", z=3)
                continue
            on = (i, j) in arcos
            circ(ax, x, y, rr, LGREEN if on else "none", GREEN if on else GREY, 2.6 if on else 1.3)
    txt(ax, 770, 98, "r = 2", 14, color="#444444", fontstyle="italic")
    txt(ax, 770, 113, t["prec"], 12, color="#666666")
    txt(ax, 770, 136, "r = 0", 14, color="#444444", fontstyle="italic")
    txt(ax, 770, 151, t["ning"], 12, color="#666666")
    txt(ax, 770, 176, "r = 1", 14, color=DGREEN, fontstyle="italic", fontweight="bold")
    txt(ax, 770, 191, t["arcos"], 12, color=DGREEN)
    corchete_v(ax, 566, gy - 12, gy + s2 * (M - 1) + 12)
    txt(ax, 566, gy - 24, r"$n+1$", 18, "center", BLUE, fontweight="bold")
    formula = 3 * (n - 1) * (n + 2)
    gps_lbl = f"3(n−1)(n+2) = {q_gps} qubits" if formula == q_gps else f"{q_gps} qubits"
    txt(ax, 672, 302, t["gps"], 16, "center", fontweight="bold")
    txt(ax, 672, 324, gps_lbl, 14, "center", "#444444")
    txt(ax, 672, 343, t["gps_sub"], 13, "center", "#666666")

    panel(ax, 840, 45, "c", t["c"], 1090)
    wires = [95, 130, 165, 245]
    for y in wires:
        line(ax, 900, y, 1272, y, INK, 1.6)
        txt(ax, 896, y + 5, r"$|0\rangle$", 15, "right")
    for x in (884, 1284):
        for y in (193, 205, 217):
            circ(ax, x, y, 2.6, INK, INK, z=4)
    gx_rx = [1040, 1176]
    for y in wires:
        rbox(ax, 910, y - 12, 30, 24, GATE, r=3, z=3)
        txt(ax, 925, y + 5, "H", 14, "center", fontweight="bold", zorder=5)
        for xr in gx_rx:
            rbox(ax, xr, y - 12, 36, 24, GATE, r=3, z=3)
            txt(ax, xr + 18, y + 5, r"$\mathbf{R_X}$", 14, "center", zorder=5)
        rbox(ax, 1228, y - 12, 30, 24, "white", INK, 1.5, 3, z=3)
        ax.add_patch(Arc((1243, y + 7), 20, 20, theta1=180, theta2=360, ec=INK, lw=1.4 * PX, zorder=5))
        line(ax, 1243, y + 7, 1251, y - 6, INK, 1.4, zorder=5)
    for xc in (955, 1091):
        rbox(ax, xc, 80, 70, 180, GATE, r=4, z=3)
        txt(ax, xc + 35, 176, r"$\mathbf{U_C}$", 18, "center", zorder=5)
    for x, s in [(990, r"$\gamma_1$"), (1058, r"$\beta_1$"), (1126, r"$\gamma_2$"), (1194, r"$\beta_2$")]:
        txt(ax, x, 72, s, 16, "center", BLUE, fontweight="bold")
    corchete_v(ax, 862, 88, 252, r"$N$")
    corchete_h(ax, 910, 1258, 286, rf"$p = {REPS}$", 314)
    txt(ax, 1084, 336, t["capas"], 14, "center", "#444444")

    panel(ax, 20, 400, "d", t["d"], 230)
    rbox(ax, 45, 440, 140, 70, GATE, r=6)
    rbox(ax, 275, 440, 140, 70, "white", "#444444", 1.6, 6)
    for (x, l1, l2) in [(115, *t["circ"]), (345, *t["opt"])]:
        txt(ax, x, 471, l1, 15, "center", fontweight="bold", zorder=5)
        txt(ax, x, 491, l2, 15, "center", fontweight="bold", zorder=5)
    flecha(ax, 187, 460, 273, 460, BLUE, 2)
    flecha(ax, 273, 490, 187, 490, BLUE, 2)
    txt(ax, 230, 451, r"$E(\gamma,\beta)$", 15, "center", BLUE)
    txt(ax, 230, 512, r"$\gamma,\ \beta$", 15, "center", BLUE)
    txt(ax, 230, 556, f"maxiter = {MAXITER} · p = {REPS}", 15, "center", "#222222")
    txt(ax, 230, 580, f"{t['replicas']}: {rep_txt}", 13, "center", "#555555")

    panel(ax, 460, 400, "e", t["e"], 685)
    gw = n * 21 + 10
    x0 = 665 - (n * gw - 10) / 2
    for g in range(n):
        for b in range(n):
            x = x0 + g * gw + b * 21
            on = bits[g * n + b] == 1
            ax.add_patch(Rectangle((x, 425), 19, 22, fc=LGREEN if on else "white",
                                   ec=GREEN if on else "#999999", lw=(2 if on else 1.2) * PX, zorder=3))
            txt(ax, x + 9.5, 441, str(bits[g * n + b]), 14, "center", fontweight="bold",
                family="monospace", zorder=5)
        etiqueta = letras[g] if orden else str(g + 1)
        txt(ax, x0 + g * gw + (n * 21) / 2, 464, etiqueta, 12, "center", "#555555")
    flecha(ax, 600, 472, 600, 502)
    cs, mx, my = 18, 560, 508
    for r_ in range(n):
        txt(ax, mx - 6, my + cs * r_ + 13, letras[r_] if orden else str(r_ + 1), 12, "right", "#333333")
        for c_ in range(n):
            ax.add_patch(Rectangle((mx + cs * c_, my + cs * r_), cs, cs, fc="white", ec="#999999", lw=1.2 * PX, zorder=3))
            if bits[r_ * n + c_]:
                ax.add_patch(Rectangle((mx + cs * c_ + 3, my + cs * r_ + 3), cs - 6, cs - 6, fc=GREEN, ec="none", zorder=4))
    txt(ax, mx + cs * n / 2, my + cs * n + 20, t["grid_cm"] if orden else t["grid_pm"], 12, "center", "#555555")
    flecha(ax, 645, 544, 690, 544)
    Pe = encajar(XY, 712, 805, 512, 588)
    for k in range(n):
        i, j = tour[k], tour[(k + 1) % n]
        line(ax, *Pe[i], *Pe[j], GREEN, 3)
    ce = Pe.mean(axis=0)
    for i in range(n):
        circ(ax, *Pe[i], 6, INK, INK, z=5)
        d = Pe[i] - ce
        d = d / (np.linalg.norm(d) + 1e-9) * 15
        txt(ax, Pe[i][0] + d[0], Pe[i][1] + d[1] + 4, letras[i], 12, "center", "#333333")
    ax.plot([843, 848, 857], [528, 534, 521], color=DGREEN, lw=3 * PX, solid_capstyle="round", solid_joinstyle="round")
    txt(ax, 862, 534, t["fact"], 15, color=DGREEN, fontweight="bold")
    line(ax, 844, 551, 854, 561, "#888888", 2.2); line(ax, 854, 551, 844, 561, "#888888", 2.2)
    txt(ax, 862, 561, t["infact"], 14, color="#777777")
    txt(ax, 862, 578, t["viola"], 12, color="#777777")

    panel(ax, 940, 400, "f", t["f"], 1140)
    det = [
        f"n = 3: GPS {fk['gps'][0]}/{fk['gps'][1]} · Trad. {fk['traditional'][0]}/{fk['traditional'][1]}",
        r"$(E-E_{opt})/A$ · LOWESS",
        f"{t['med']} n = 3: {tmed['gps']:.0f} s {t['vs']} {tmed['traditional']:.1f} s",
        f"n = {n}: {q_gps} {t['vs']} {q_trad} qubits",
    ]
    for k, (nom, dd) in enumerate(zip(t["m"], det)):
        y = 425 + 50 * k
        rbox(ax, 965, y, 370, 40, "white", "#BBBBBB", 1.4, 20)
        circ(ax, 988, y + 20, 8, LGREEN, GREEN, 2.5, z=4)
        txt(ax, 1004, y + 25, nom, 15, fontweight="bold", zorder=5)
        txt(ax, 1112, y + 25, dd, 13, color="#555555", zorder=5)

    out = os.path.join(OUT, lang)
    os.makedirs(out, exist_ok=True)
    suf = "_bn" if BN else ""
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(out, f"fig11_pipeline{suf}.{ext}"), dpi=300, facecolor="white")
    plt.close(fig)
    print(f"  ✓ {lang}/fig11_pipeline{suf}.png  (+ .svg)")


print(f"Instancia {INST}: tour óptimo {'→'.join(letras[i] for i in tour)}→{letras[tour[0]]}, "
      f"costo {costo(tour):.3f}; qubits Trad {q_trad}, GPS {q_gps}; "
      f"bits {'ciudad×posición' if orden else 'posición×ciudad'}")
for lang in ("es", "en"):
    dibujar(lang)