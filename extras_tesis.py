"""Figuras extra del cap. 4: requisitos, formulaciones y GIF one-hot vs GPS."""
# GPS (build_gps_qubo): N = n-1, nodos 0..N+1, se excluye el par {0, N+1}.
# eq_one(terms, A) = A(1 - sum x)^2 (sin la constante); λ = A.
# r = 1 arco directo i→j; r = 0 i antes que j (no adyacente); r = 2 i después de j.
import os
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

OUT = "figuras"
RAM_GB = 31
LIM_Q = int(np.floor(np.log2(RAM_GB * 1e9 / 16)))

serif = ["Times New Roman", "Liberation Serif", "Nimbus Roman", "TeX Gyre Termes", "DejaVu Serif"]
disp = {f.name for f in font_manager.fontManager.ttflist}
FUENTE = next((f for f in serif if f in disp), "serif")
plt.rcParams.update({"font.family": "serif", "font.serif": [FUENTE], "mathtext.fontset": "stix",
                     "savefig.dpi": 300, "savefig.bbox": "tight"})

q_trad = lambda n: n * n
q_gps = lambda n: 3 * (n - 1) * (n + 2)
mem_gb = lambda q: 2 ** q * 16 / 1e9


def fmt_mem(g):
    for u, f in [("PB", 1e6), ("TB", 1e3), ("GB", 1), ("MB", 1e-3), ("KB", 1e-6)]:
        if g >= f:
            return f"{g / f:.1f} {u}"
    return f"{g * 1e9:.0f} B"


REQ = {
    "es": {
        "cols": ["ID", "Tipo", "Requisito", "Criterio de verificación", "Componente", "OE"],
        "rows": [
            ["RF01", "Funcional", "Generar instancias TSP sintéticas euclidianas y reproducibles (n = 3, 4, 5).",
             "Misma semilla produce la misma matriz de distancias.", "synthetic_instances.py", "OE2"],
            ["RF02", "Funcional", "Construir la matriz Q de la formulación Tradicional (one-hot ciudad × posición).",
             f"Q tiene n² variables (n = 3: {q_trad(3)}).", "build_traditional_qubo", "OE1"],
            ["RF03", "Funcional", "Construir la matriz Q de GPS con depósito duplicado y tres estados por par.",
             f"Q tiene 3(n−1)(n+2) variables (n = 3: {q_gps(3)}).", "build_gps_qubo", "OE1"],
            ["RF04", "Funcional", "Resolver cada Q con QAOA (p = 2, maxiter = 30) en réplicas independientes.",
             "20 réplicas pareadas en n = 3; 8 réplicas por tamaño en n = 4, 5.", "run_aws_full.py", "OE2"],
            ["RF05", "Funcional", "Persistir cada réplica (bitstring, energía, tiempo, recursos).",
             "Un JSON por réplica y fila CSV escrita dentro del bucle.", "run_aws_full.py", "OE2, OE3"],
            ["RF06", "Funcional", "Decodificar el bitstring y verificar todas las restricciones.",
             "Tour válido o lista de violaciones por réplica.", "traditional_tour, gps_violations", "OE3"],
            ["RF07", "Funcional", "Calcular factibilidad, brecha, tiempo y pruebas estadísticas.",
             "Fisher exacto, Mann-Whitney U, LOWESS reproducibles.", "statistical_analysis_v2.py", "OE3, OE4"],
            ["RF08", "Funcional", "Contar recursos del circuito sin simular (profundidad, CNOT) para n = 3–6.",
             "Transpilación a {rz, sx, x, cx} con semilla fija.", "recursos_circuito.py", "OE2, OE4"],
            ["RNF01", "Rendimiento", f"El statevector debe caber en la RAM disponible ({RAM_GB} GB).",
             f"2^q · 16 B ≤ {RAM_GB} GB  →  q ≤ {LIM_Q} qubits.", "EC2 t2.2xlarge (CPU)", "OE4"],
            ["RNF02", "Reproducibilidad", "Semillas fijas y versiones de software registradas.",
             "Re-ejecución produce los mismos recursos y matrices Q.", "Qiskit 2.x, Python", "OE2"],
            ["RNF03", "Tolerancia a fallos", "Las ejecuciones largas sobreviven a desconexiones.",
             "Sesión tmux; ninguna réplica perdida por caída de SSH.", "tmux, escritura por réplica", "OE2"],
            ["RNF04", "Integridad de datos", "Separar corridas de prueba y producción; verificar energías.",
             "x^T Q x = objective_value en filas con bitstring.", "statistical_analysis_v2.py", "OE3"],
            ["RNF05", "Comparabilidad", "Ambas formulaciones usan el mismo ansatz, optimizador, réplicas y hardware.",
             "Solo varía la matriz Q entre tratamientos.", "run_aws_full.py", "OE2"],
            ["RNF06", "Trazabilidad", "Toda figura y tabla se regenera desde scripts versionados.",
             "Un comando reconstruye figuras/ completo.", "figuras_tesis.py, extras_tesis.py", "Todos"],
        ],
        "widths": [0.06, 0.11, 0.31, 0.27, 0.18, 0.07],
    },
    "en": {
        "cols": ["ID", "Type", "Requirement", "Verification criterion", "Component", "SO"],
        "rows": [
            ["FR01", "Functional", "Generate reproducible synthetic Euclidean TSP instances (n = 3, 4, 5).",
             "Same seed yields the same distance matrix.", "synthetic_instances.py", "SO2"],
            ["FR02", "Functional", "Build the Q matrix of the Traditional formulation (one-hot city × position).",
             f"Q has n² variables (n = 3: {q_trad(3)}).", "build_traditional_qubo", "SO1"],
            ["FR03", "Functional", "Build the GPS Q matrix with split depot and three states per pair.",
             f"Q has 3(n−1)(n+2) variables (n = 3: {q_gps(3)}).", "build_gps_qubo", "SO1"],
            ["FR04", "Functional", "Solve each Q with QAOA (p = 2, maxiter = 30) in independent replicas.",
             "20 paired replicas at n = 3; 8 replicas per size at n = 4, 5.", "run_aws_full.py", "SO2"],
            ["FR05", "Functional", "Persist every replica (bitstring, energy, time, resources).",
             "One JSON per replica and a CSV row written inside the loop.", "run_aws_full.py", "SO2, SO3"],
            ["FR06", "Functional", "Decode the bitstring and check every constraint.",
             "Valid tour or list of violations per replica.", "traditional_tour, gps_violations", "SO3"],
            ["FR07", "Functional", "Compute feasibility, gap, time and statistical tests.",
             "Reproducible Fisher exact, Mann-Whitney U, LOWESS.", "statistical_analysis_v2.py", "SO3, SO4"],
            ["FR08", "Functional", "Count circuit resources without simulation (depth, CNOT) for n = 3–6.",
             "Transpilation to {rz, sx, x, cx} with fixed seed.", "recursos_circuito.py", "SO2, SO4"],
            ["NFR01", "Performance", f"The statevector must fit in available RAM ({RAM_GB} GB).",
             f"2^q · 16 B ≤ {RAM_GB} GB  →  q ≤ {LIM_Q} qubits.", "EC2 t2.2xlarge (CPU)", "SO4"],
            ["NFR02", "Reproducibility", "Fixed seeds and recorded software versions.",
             "Re-running yields the same resources and Q matrices.", "Qiskit 2.x, Python", "SO2"],
            ["NFR03", "Fault tolerance", "Long runs survive disconnections.",
             "tmux session; no replica lost to SSH drops.", "tmux, per-replica writes", "SO2"],
            ["NFR04", "Data integrity", "Separate test and production runs; verify energies.",
             "x^T Q x = objective_value on rows with bitstring.", "statistical_analysis_v2.py", "SO3"],
            ["NFR05", "Comparability", "Both formulations share ansatz, optimizer, replicas and hardware.",
             "Only the Q matrix varies between treatments.", "run_aws_full.py", "SO2"],
            ["NFR06", "Traceability", "Every figure and table is regenerated from versioned scripts.",
             "One command rebuilds the whole figuras/ folder.", "figuras_tesis.py, extras_tesis.py", "All"],
        ],
        "widths": [0.06, 0.11, 0.31, 0.27, 0.18, 0.07],
    },
}


def tabla_requisitos(lang):
    R = REQ[lang]
    df = pd.DataFrame(R["rows"], columns=R["cols"])
    if lang == "es":
        df.to_csv(os.path.join(OUT, "tabla_requisitos.csv"), index=False, encoding="utf-8-sig")
    else:
        df.to_csv(os.path.join(OUT, "tabla_requisitos_en.csv"), index=False, encoding="utf-8-sig")
    chars = [int(w * 150) for w in R["widths"]]
    celdas = [["\n".join(textwrap.wrap(str(v), c)) for v, c in zip(fila, chars)] for fila in R["rows"]]
    lineas = [max(c.count("\n") + 1 for c in fila) for fila in celdas]
    alto = 0.6 + 0.19 * sum(lineas) + 0.12 * len(lineas)
    fig, ax = plt.subplots(figsize=(11, alto))
    ax.axis("off")
    tb = ax.table(cellText=celdas, colLabels=R["cols"], colWidths=R["widths"], loc="upper center", cellLoc="left")
    tb.auto_set_font_size(False)
    tb.set_fontsize(9)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("white")
        cell.PAD = 0.03
        if r == 0:
            cell.set_text_props(fontweight="bold")
            cell.visible_edges = "B"
            cell.set_edgecolor("black")
            cell.set_height(0.35 / alto)
        else:
            cell.set_height((0.19 * lineas[r - 1] + 0.1) / alto)
            cell.visible_edges = "B" if r == len(celdas) else ""
            cell.set_edgecolor("black")
            if R["rows"][r - 1][1] in ("Funcional", "Functional"):
                cell.set_facecolor("white")
            else:
                cell.set_facecolor("#F2F2F2")
    fig.savefig(os.path.join(OUT, lang, "fig12_requisitos.png"), facecolor="white")
    plt.close(fig)
    print(f"  ✓ {lang}/fig12_requisitos.png")


FORM = {
    "es": {
        "trad": "(a) QUBO Tradicional (one-hot ciudad × posición)",
        "gps": "(b) GPS — formulación matricial posicional, implementación de build_gps_qubo",
        "vt": r"Variables: $x_{v,p}\in\{0,1\}$, ciudad $v$, posición $p$  $\Rightarrow$  $n^2$ qubits",
        "vg": r"Variables: $x_{ij}^{r}$,  $i\neq j\in\{0,\ldots,N+1\}$,  $\{i,j\}\neq\{0,N+1\}$,  $r\in\{0,1,2\}$,  $N=n-1$  $\Rightarrow$  $3(n-1)(n+2)$ qubits",
        "lt": ["cada ciudad una vez", "cada posición una vez", "costo del recorrido ($p+1$ mód $n$)"],
        "lg": ["costo", "un estado por par", "salida", "entrada", "orden", "transitividad"],
        "sem": r"Estados: $r=1$ arco directo $i\to j$ · $r=0$ $i$ antes que $j$ (no adyacente) · $r=2$ $i$ después de $j$.   Depósito duplicado: $0$ = salida, $N+1$ = llegada.   Por defecto $\lambda=A$.",
    },
    "en": {
        "trad": "(a) Traditional QUBO (one-hot city × position)",
        "gps": "(b) GPS — positional matrix formulation, as implemented in build_gps_qubo",
        "vt": r"Variables: $x_{v,p}\in\{0,1\}$, city $v$, position $p$  $\Rightarrow$  $n^2$ qubits",
        "vg": r"Variables: $x_{ij}^{r}$,  $i\neq j\in\{0,\ldots,N+1\}$,  $\{i,j\}\neq\{0,N+1\}$,  $r\in\{0,1,2\}$,  $N=n-1$  $\Rightarrow$  $3(n-1)(n+2)$ qubits",
        "lt": ["each city once", "each position once", "tour cost ($p+1$ mod $n$)"],
        "lg": ["cost", "one state per pair", "out-degree", "in-degree", "order", "transitivity"],
        "sem": r"States: $r=1$ direct arc $i\to j$ · $r=0$ $i$ before $j$ (not adjacent) · $r=2$ $i$ after $j$.   Split depot: $0$ = start, $N+1$ = end.   Default $\lambda=A$.",
    },
}

EQ_T = [r"$A\sum_{v}\left(1-\sum_{p}x_{v,p}\right)^{2}$",
        r"$+\;A\sum_{p}\left(1-\sum_{v}x_{v,p}\right)^{2}$",
        r"$+\;\sum_{u\neq v}d_{uv}\sum_{p}x_{u,p}\,x_{v,p+1}$"]
EQ_G = [r"$\sum_{(i,j)}d_{ij}\,x_{ij}^{1}$",
        r"$+\;A\sum_{(i,j)}\left(1-\sum_{r=0}^{2}x_{ij}^{r}\right)^{2}$",
        r"$+\;A\sum_{i=0}^{N}\left(1-\sum_{j}x_{ij}^{1}\right)^{2}$",
        r"$+\;A\sum_{j=1}^{N+1}\left(1-\sum_{i}x_{ij}^{1}\right)^{2}$",
        r"$+\;A\sum_{i<j}\left(1-x_{ij}^{2}-x_{ji}^{2}\right)^{2}$",
        r"$+\;\lambda\sum_{i,j,k\,\in\,[1,N]}\left(x_{ji}^{2}x_{kj}^{2}-x_{ji}^{2}x_{ki}^{2}-x_{kj}^{2}x_{ki}^{2}+x_{ki}^{2}\right)$"]


def formulaciones(lang):
    F = FORM[lang]
    fig = plt.figure(figsize=(11, 8.2))
    y = 0.97
    fig.text(0.02, y, F["trad"], fontsize=13, fontweight="bold", va="top")
    y -= 0.055
    fig.text(0.04, y, F["vt"], fontsize=11.5, va="top")
    y -= 0.075
    fig.text(0.04, y, r"$H_{T}=$", fontsize=15, va="center")
    x = 0.105
    for eq, lab, w in zip(EQ_T, F["lt"], (0.215, 0.235, 0.30)):
        fig.text(x, y, eq, fontsize=15, va="center")
        fig.text(x + 0.02, y - 0.055, f"({F['lt'].index(lab) + 1}) {lab}", fontsize=10, color="0.35", va="center")
        x += w
    y -= 0.13
    fig.add_artist(plt.Line2D([0.02, 0.98], [y, y], color="0.75", lw=0.8, transform=fig.transFigure))
    y -= 0.03
    fig.text(0.02, y, F["gps"], fontsize=13, fontweight="bold", va="top")
    y -= 0.055
    fig.text(0.04, y, F["vg"], fontsize=11.5, va="top")
    y -= 0.08
    fig.text(0.04, y, r"$H_{GPS}=$", fontsize=15, va="center")
    for k, (eq, lab) in enumerate(zip(EQ_G, F["lg"])):
        fig.text(0.13, y, eq, fontsize=15, va="center")
        fig.text(0.80, y, f"({k + 1}) {lab}", fontsize=10.5, color="0.35", va="center")
        y -= 0.082
    y -= 0.005
    fig.text(0.04, y, F["sem"], fontsize=10, color="0.25", va="center")
    fig.savefig(os.path.join(OUT, lang, "fig13_formulaciones.png"), facecolor="white")
    plt.close(fig)
    print(f"  ✓ {lang}/fig13_formulaciones.png")


GIF = {
    "es": {"trad": "QUBO Tradicional", "r1": "GPS · r = 1 (arco)", "r0": "GPS · r = 0 (antes)",
           "r2": "GPS · r = 2 (después)", "pos": "posición", "orig": "i (origen)", "dest": "j (destino)",
           "tour": "tour", "cnt": "variables en 1:  Tradicional {a}/{A} · GPS {b}/{B}",
           "pasos": ["Ninguna ciudad visitada.",
                     "Se sale del depósito A.",
                     "A → B: Tradicional marca (B, pos. 2); GPS marca el arco A→B y la precedencia.",
                     "B → C: cada ciudad nueva fija su relación con TODAS las anteriores en GPS.",
                     "C → D: GPS crece por pares; Tradicional, por ciudad.",
                     "D → A′: GPS necesita el depósito de llegada A′; Tradicional cierra el ciclo implícitamente."]},
    "en": {"trad": "Traditional QUBO", "r1": "GPS · r = 1 (arc)", "r0": "GPS · r = 0 (before)",
           "r2": "GPS · r = 2 (after)", "pos": "position", "orig": "i (origin)", "dest": "j (destination)",
           "tour": "tour", "cnt": "variables set to 1:  Traditional {a}/{A} · GPS {b}/{B}",
           "pasos": ["No city visited yet.",
                     "Leave depot A.",
                     "A → B: Traditional sets (B, pos. 2); GPS sets arc A→B and the precedence.",
                     "B → C: in GPS each new city fixes its relation with ALL previous ones.",
                     "C → D: GPS grows by pairs; Traditional by city.",
                     "D → A′: GPS needs the end depot A′; Traditional closes the cycle implicitly."]},
}


def gif(lang, n=4):
    G = GIF[lang]
    L = [chr(65 + i) for i in range(n)]
    aug = L + [L[0] + "′"]
    M = n + 1
    ruta = list(range(M))                     # tour de ejemplo A→B→C→D→A′ en índices aumentados
    pos = {v: k for k, v in enumerate(ruta)}
    xy = np.array([[0, 0], [1, 0.15], [1.1, 1], [0.1, 0.9]])
    excl = lambda i, j: i == j or {i, j} == {0, M - 1}
    VERDE, VERDE_N, GRIS = "#B7D7A8", "#6AA84F", "#BBBBBB"

    fig = plt.figure(figsize=(13, 5.2), dpi=100)
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1.1, 1.1, 1.1], wspace=0.35, left=0.03, right=0.99, top=0.82, bottom=0.2)
    axs = [fig.add_subplot(gs[0, k]) for k in range(5)]
    txt_cnt = fig.text(0.5, 0.93, "", ha="center", fontsize=13, fontweight="bold")
    txt_paso = fig.text(0.5, 0.07, "", ha="center", fontsize=12, color="0.2")

    def grid(ax, filas, cols, titulo, xl, yl):
        ax.clear()
        ax.set_xlim(-0.5, cols - 0.5); ax.set_ylim(filas - 0.5, -0.5); ax.set_aspect("equal")
        ax.set_xticks(range(cols)); ax.set_yticks(range(filas))
        ax.tick_params(length=0, labelsize=10)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(titulo, fontsize=11)
        ax.set_xlabel(xl, fontsize=9, color="0.4"); ax.set_ylabel(yl, fontsize=9, color="0.4")

    def cuadro(ax, i, j, estado):
        fc = {"off": "white", "on": VERDE, "nuevo": VERDE_N, "excl": "#F0F0F0"}[estado]
        ax.add_patch(Rectangle((j - 0.42, i - 0.42), 0.84, 0.84, fc=fc,
                               ec=GRIS if estado in ("off", "excl") else "#4E7F38", lw=0.8))

    def frame(s):
        vis = ruta[:s]
        ax = axs[0]; ax.clear(); ax.axis("off"); ax.set_title(G["tour"], fontsize=11)
        ax.set_xlim(-0.3, 1.4); ax.set_ylim(-0.3, 1.25); ax.set_aspect("equal")
        for k in range(n):
            ax.plot(*xy[k], "o", color="0.1", ms=9)
            ax.annotate(L[k], xy[k], xytext=(-14, 6), textcoords="offset points", fontsize=11)
        for k in range(1, len(vis)):
            a, b = vis[k - 1] % n, vis[k] % n
            ax.annotate("", xy=xy[b], xytext=xy[a],
                        arrowprops=dict(arrowstyle="-|>", color=VERDE_N if k == len(vis) - 1 else "#4E7F38", lw=2.4))
        ax = axs[1]
        grid(ax, n, n, G["trad"], G["pos"], "ciudad" if lang == "es" else "city")
        ax.set_xticklabels([str(p + 1) for p in range(n)]); ax.set_yticklabels(L)
        n_trad = 0
        for v in range(n):
            for p in range(n):
                on = p < min(s, n) and ruta[p] == v
                n_trad += on
                cuadro(ax, v, p, ("nuevo" if p == s - 1 else "on") if on else "off")
        n_gps = 0
        for ax, r, tit in [(axs[2], 1, G["r1"]), (axs[3], 0, G["r0"]), (axs[4], 2, G["r2"])]:
            grid(ax, M, M, tit, G["dest"], G["orig"] if r == 1 else "")
            ax.set_xticklabels(aug); ax.set_yticklabels(aug)
            for i in range(M):
                for j in range(M):
                    if excl(i, j):
                        cuadro(ax, i, j, "excl"); continue
                    est = "off"
                    if i in vis and j in vis:
                        rr = 1 if pos[j] == pos[i] + 1 else (0 if pos[i] < pos[j] else 2)
                        if rr == r:
                            est = "nuevo" if s - 1 in (pos[i], pos[j]) else "on"
                            n_gps += 1
                    cuadro(ax, i, j, est)
        txt_cnt.set_text(G["cnt"].format(a=n_trad, A=n * n, b=n_gps, B=3 * (n - 1) * (n + 2)))
        txt_paso.set_text(G["pasos"][s])
        return []

    secuencia = [0, 1, 2, 3, 4, 5, 5, 5]      # el último cuadro se mantiene
    anim = FuncAnimation(fig, frame, frames=secuencia, blit=False)
    ruta_gif = os.path.join(OUT, lang, "anim_onehot_vs_gps.gif")
    anim.save(ruta_gif, writer=PillowWriter(fps=0.7), dpi=110)
    plt.close(fig)
    print(f"  ✓ {lang}/anim_onehot_vs_gps.gif")


if __name__ == "__main__":
    for lang in ("es", "en"):
        os.makedirs(os.path.join(OUT, lang), exist_ok=True)
        tabla_requisitos(lang)
        formulaciones(lang)
        gif(lang)
    print(f"\nListo. CSV: {OUT}/tabla_requisitos.csv · imágenes y GIF en {OUT}/es y {OUT}/en")