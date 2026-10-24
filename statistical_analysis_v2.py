"""Comparación estadística GPS vs QUBO tradicional: factibilidad y brecha (E - E_opt)/A."""
# Energías no comparables en crudo: cada QUBO tiene distinta escala.
# Independientes por defecto (Mann-Whitney, Fisher); --paired usa Wilcoxon y McNemar.
# Qubits, profundidad y compuertas son constantes: solo descriptivo, sin prueba de hipótesis.
# Sin correlaciones agrupadas entre formulaciones: quedan confundidas con el tamaño.

import argparse
import glob
import itertools
import json
import os
import warnings
warnings.filterwarnings("ignore", message=".*range zero.*")

import numpy as np
import pandas as pd
from scipy import stats

from formulations import (_default_penalty, build_gps_qubo,
                          build_traditional_qubo, decode_gps_solution)

ALPHA = 0.05
TOL = 1e-6  # tolerancia relativa para "energía igual al óptimo"


def get_dist_matrix(instance: str, n_cities: int) -> np.ndarray:
    """Matriz de distancias desde synthetic_instances.py; única función acoplada a su API."""
    import synthetic_instances as si
    for name in ("get_instance", "load_instance", "generate_instance",
                 "make_instance", "build_instance", "get_synthetic_instance"):
        fn = getattr(si, name, None)
        if fn is None:
            continue
        for arg in (instance, n_cities):
            try:
                out = fn(arg)
            except Exception:
                continue
            if isinstance(out, dict):
                for key in ("dist_matrix", "distance_matrix", "dist", "D"):
                    if key in out:
                        return np.asarray(out[key], dtype=float)
            elif isinstance(out, tuple):
                for item in out:
                    if isinstance(item, np.ndarray) and item.ndim == 2:
                        return item.astype(float)
            elif isinstance(out, np.ndarray) and out.ndim == 2:
                return out.astype(float)
    for name in ("INSTANCES", "SYNTHETIC_INSTANCES", "instances"):
        table = getattr(si, name, None)
        if isinstance(table, dict) and instance in table:
            val = table[instance]
            if isinstance(val, dict):
                for key in ("dist_matrix", "distance_matrix", "dist", "D"):
                    if key in val:
                        return np.asarray(val[key], dtype=float)
            return np.asarray(val, dtype=float)
    funcs = [f for f in dir(si) if not f.startswith("_")]
    raise RuntimeError(f"No pude obtener la matriz de '{instance}'. "
                       f"Ajusta get_dist_matrix(). Disponible en el módulo: {funcs}")


def load_results(results_dir: str, csv_path: str) -> pd.DataFrame:
    rows = []
    for path in sorted(glob.glob(os.path.join(results_dir, "**", "*.json"), recursive=True)):
        with open(path) as fh:
            rec = json.load(fh)
        rec["source"] = "backup" if "backup" in path.lower() else "json"
        rec["path"] = path
        rows.append(rec)
    df = pd.DataFrame(rows)

    # Réplicas de respaldo que colisionan de índice con otra ejecución: índice nuevo.
    main = df[df["source"] == "json"]
    for idx in df.index[df["source"] == "backup"]:
        r = df.loc[idx]
        same = main[(main["instance"] == r["instance"]) & (main["formulation"] == r["formulation"])]
        if r["replica"] in set(same["replica"]):
            new_rep = int(max(same["replica"].max(), r["replica"])) + 1
            print(f"[consolidación] {r['path']}: réplica {r['replica']} ya existe -> reasignada a {new_rep}")
            df.loc[idx, "replica"] = new_rep

    # Filas presentes solo en la CSV (JSON perdido): sin bitstring.
    if csv_path and os.path.exists(csv_path):
        csv = pd.read_csv(csv_path)
        keys = set(zip(df["instance"], df["formulation"], df["replica"]))
        for _, r in csv.iterrows():
            k = (r["instance"], r["formulation"], r["replica"])
            if k in keys:
                j = df[(df["instance"] == k[0]) & (df["formulation"] == k[1]) & (df["replica"] == k[2])]
                if abs(j["execution_time_sec"].iloc[0] - r["execution_time_sec"]) > 1.0:
                    print(f"[AVISO] {k}: tiempo distinto entre JSON y CSV. Revisar a mano.")
                continue
            rec = r.to_dict()
            rec.update(source="csv_sin_bitstring", path=csv_path, optimal_bitstring=None)
            rows_new = pd.DataFrame([rec])
            df = pd.concat([df, rows_new], ignore_index=True)
            print(f"[consolidación] {k}: solo en CSV (sin bitstring)")
    df["replica"] = df["replica"].astype(int)
    return df.sort_values(["instance", "formulation", "replica"]).reset_index(drop=True)


def qubo_energy(Q, bits):
    x = np.asarray(bits, dtype=float)
    return float(x @ Q @ x)


def traditional_tour(bits, n):
    X = np.asarray(bits).reshape(n, n)  # X[i, p]: ciudad i en posición p
    if not (np.all(X.sum(axis=0) == 1) and np.all(X.sum(axis=1) == 1)):
        return None
    return [int(np.argmax(X[:, p])) for p in range(n)]


def gps_violations(bits, var_index, N):
    """Replica las restricciones de build_gps_qubo; devuelve la lista de violaciones."""
    b = lambda i, j, r: bits[var_index[(i, j, r)]]
    num_aug, viol = N + 2, []
    pairs = {(i, j) for (i, j, _) in var_index}
    for (i, j) in pairs:
        if sum(b(i, j, r) for r in range(3)) != 1:
            viol.append(f"one-hot({i},{j})")
    for i in range(0, N + 1):
        if sum(b(i, j, 1) for j in range(num_aug) if (i, j) in pairs) != 1:
            viol.append(f"salida({i})")
    for j in range(1, N + 2):
        if sum(b(i, j, 1) for i in range(0, N + 1) if (i, j) in pairs) != 1:
            viol.append(f"entrada({j})")
    for (i, j) in pairs:
        if i < j and b(i, j, 2) + b(j, i, 2) != 1:
            viol.append(f"orden({i},{j})")
    for i, j, k in itertools.permutations(range(1, N + 1), 3):
        if b(j, i, 2) and b(k, j, 2) and not b(k, i, 2):
            viol.append(f"transitividad({i},{j},{k})")
    return viol


def tour_cost(dist, tour):
    return float(sum(dist[tour[t], tour[(t + 1) % len(tour)]] for t in range(len(tour))))


def optimum_energy(form, dist):
    """Energía mínima entre soluciones FACTIBLES de la QUBO (búsqueda exhaustiva)."""
    n = dist.shape[0]
    if form == "traditional":
        Q = build_traditional_qubo(dist)
        best = np.inf
        for perm in itertools.permutations(range(n)):
            bits = np.zeros(n * n)
            for p, city in enumerate(perm):
                bits[city * n + p] = 1
            best = min(best, qubo_energy(Q, bits))
        return best
    Q, var_index, N = build_gps_qubo(dist)
    n_pairs = len(var_index) // 3
    if n_pairs > 12:
        warnings.warn("GPS demasiado grande para enumeración exhaustiva; óptimo no calculado.")
        return np.nan
    best = np.inf
    for combo in itertools.product(range(3), repeat=n_pairs):
        bits = np.zeros(len(var_index), dtype=int)
        for p, r in enumerate(combo):
            bits[3 * p + r] = 1
        if decode_gps_solution(bits, var_index, N) is None:
            continue
        if gps_violations(bits, var_index, N):
            continue
        best = min(best, qubo_energy(Q, bits))
    return best


def evaluate_quality(df):
    cache, out = {}, []
    for _, r in df.iterrows():
        key = (r["instance"], int(r["n_cities"]))
        if key not in cache:
            dist = get_dist_matrix(*key)
            if not np.allclose(dist, dist.T):
                print(f"[AVISO] {key[0]}: matriz NO simétrica; el criterio por energía "
                      f"para filas sin bitstring deja de ser válido.")
            cache[key] = {"dist": dist, "A": _default_penalty(dist), "E_opt": {}}
        c = cache[key]
        if r["formulation"] not in c["E_opt"]:
            c["E_opt"][r["formulation"]] = optimum_energy(r["formulation"], c["dist"])
        dist, A, n = c["dist"], c["A"], int(r["n_cities"])
        E_opt = c["E_opt"][r["formulation"]]
        fval = float(r["objective_value"])
        bits = r.get("optimal_bitstring")
        has_bits = isinstance(bits, list)

        rec = {"A": A, "E_opt": E_opt, "gap_A": (fval - E_opt) / A,
               "gap_rel": (fval - E_opt) / abs(E_opt), "E_recalc": np.nan,
               "feasible": np.nan, "optimal": np.nan, "tour_cost": np.nan,
               "criterio": "", "violaciones": ""}
        if has_bits and r["formulation"] == "traditional":
            Q = build_traditional_qubo(dist)
            tour = traditional_tour(bits, n)
            rec.update(E_recalc=qubo_energy(Q, bits), feasible=tour is not None,
                       criterio="bitstring")
            if tour is not None:
                rec["tour_cost"] = tour_cost(dist, tour)
        elif has_bits and r["formulation"] == "gps":
            Q, var_index, N = build_gps_qubo(dist)
            viol = gps_violations(bits, var_index, N)
            tour = decode_gps_solution(bits, var_index, N)
            ok = tour is not None and not viol
            rec.update(E_recalc=qubo_energy(Q, bits), feasible=ok, criterio="bitstring",
                       violaciones=";".join(viol))
            if ok:
                rec["tour_cost"] = tour_cost(dist, tour)
        elif n == 3 and np.allclose(dist, dist.T):
            # Con 3 ciudades y distancias simétricas todas las rutas cuestan lo mismo:
            # factible <=> energía == óptimo.
            rec.update(feasible=abs(fval - E_opt) <= TOL * abs(E_opt), criterio="energía (n=3)")
        else:
            rec["criterio"] = "indeterminado (sin bitstring)"
        if rec["feasible"] is True or rec["feasible"] is np.True_:
            rec["optimal"] = abs(fval - E_opt) <= TOL * abs(E_opt)
        out.append(rec)
    res = pd.concat([df.reset_index(drop=True), pd.DataFrame(out)], axis=1)

    chk = res.dropna(subset=["E_recalc"])
    bad = chk[(chk["E_recalc"] - chk["objective_value"]).abs() > TOL * chk["objective_value"].abs()]
    if len(bad):
        print(f"[AVISO] {len(bad)} filas donde x^T Q x != objective_value. "
              f"Revisar offset/escala antes de interpretar gap:\n"
              f"{bad[['instance', 'formulation', 'replica', 'objective_value', 'E_recalc']]}")
    else:
        print(f"[verificación] x^T Q x coincide con objective_value en las {len(chk)} filas con bitstring.")
    return res


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    ci = stats.binomtest(k, n).proportion_ci(method="wilson")
    return (ci.low, ci.high)


def compare_time(p, paired):
    g = p[p["formulation"] == "gps"].set_index("replica")["execution_time_sec"]
    t = p[p["formulation"] == "traditional"].set_index("replica")["execution_time_sec"]
    res = {"mediana_gps_s": g.median(), "mediana_trad_s": t.median(),
           "razon_medianas": g.median() / t.median()}
    for name, s in (("gps", g), ("trad", t)):
        if len(s) >= 3:
            res[f"shapiro_p_{name}"] = stats.shapiro(s).pvalue
    if paired:
        common = g.index.intersection(t.index)
        w = stats.wilcoxon(g[common], t[common])
        res.update(prueba="Wilcoxon (pareada)", n_pares=len(common), estadistico=w.statistic, p=w.pvalue)
    else:
        u = stats.mannwhitneyu(g, t, alternative="two-sided")
        res.update(prueba="Mann-Whitney U", n_gps=len(g), n_trad=len(t),
                   estadistico=u.statistic, p=u.pvalue,
                   r_rank_biserial=2 * u.statistic / (len(g) * len(t)) - 1)
    return res


def compare_feasibility(p, paired):
    known = p.dropna(subset=["feasible"])
    g = known[known["formulation"] == "gps"].set_index("replica")["feasible"].astype(bool)
    t = known[known["formulation"] == "traditional"].set_index("replica")["feasible"].astype(bool)
    res = {"factibles_gps": f"{g.sum()}/{len(g)}", "factibles_trad": f"{t.sum()}/{len(t)}",
           "IC95_gps": wilson(int(g.sum()), len(g)), "IC95_trad": wilson(int(t.sum()), len(t))}
    if paired:
        common = g.index.intersection(t.index)
        b = int((t[common] & ~g[common]).sum())   # solo Tradicional factible
        c = int((g[common] & ~t[common]).sum())   # solo GPS factible
        pval = stats.binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
        res.update(prueba="McNemar exacto", discordantes_trad=b, discordantes_gps=c, p=pval)
    else:
        table = [[int(t.sum()), int((~t).sum())], [int(g.sum()), int((~g).sum())]]
        odds, pval = stats.fisher_exact(table)
        res.update(prueba="Fisher exacto", tabla_trad_gps=table, p=pval)
    return res


def resources_table(p):
    tab = p.groupby("formulation")[["n_qubits", "circuit_depth", "gate_count"]].agg(["min", "max"])
    ratio = {}
    for m in ("n_qubits", "circuit_depth", "gate_count"):
        g = p.loc[p["formulation"] == "gps", m].median()
        t = p.loc[p["formulation"] == "traditional", m].median()
        ratio[m] = g / t
    return tab, ratio


def scalability(df):
    tr = df[df["formulation"] == "traditional"]
    tab = tr.groupby("n_cities").agg(
        n_replicas=("replica", "count"), qubits=("n_qubits", "first"),
        tiempo_mediana_s=("execution_time_sec", "median"),
        factibilidad=("feasible", lambda s: np.nanmean(s.astype(float))),
        gap_A_mediana=("gap_A", "median"))
    lowess = None
    if tr["n_cities"].nunique() >= 3:
        import statsmodels.api as sm
        sm_out = sm.nonparametric.lowess(tr["execution_time_sec"], tr["n_cities"], frac=1.0, it=0)
        lowess = pd.DataFrame(sm_out, columns=["n_cities", "tiempo_suavizado_s"]).drop_duplicates()
    return tab, lowess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="results_aws_final")
    ap.add_argument("--csv", default="results_aws_final/aws_consolidated.csv")
    ap.add_argument("--outdir", default="analisis_v2")
    ap.add_argument("--paired", action="store_true",
                    help="Solo si GPS y Tradicional compartieron semilla por réplica.")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    pd.set_option("display.width", 160)

    df = evaluate_quality(load_results(args.results_dir, args.csv))
    df.drop(columns=["optimal_bitstring"]).to_csv(os.path.join(args.outdir, "datos_consolidados.csv"), index=False)

    print("\n=== 1. Auditoría de datos ===")
    print(df.groupby(["instance", "formulation", "source"]).size().rename("filas"))
    print(df.groupby(["instance", "formulation"])["criterio"].value_counts())

    paired_df = df[df["instance"] == "synth03"]
    print("\n=== 2. Recursos cuánticos (deterministas: solo descriptivo) ===")
    tab, ratio = resources_table(paired_df)
    print(tab)
    print("Razón GPS / Tradicional:", {k: round(v, 2) for k, v in ratio.items()})

    print("\n=== 3. Tiempo de ejecución (synth03) ===")
    for k, v in compare_time(paired_df, args.paired).items():
        print(f"  {k}: {v}")

    print("\n=== 4. Calidad de solución (synth03) ===")
    print(paired_df.groupby("formulation")[["E_opt", "gap_A", "gap_rel"]].describe().T.round(3))
    for k, v in compare_feasibility(paired_df, args.paired).items():
        print(f"  {k}: {v}")

    print("\n=== 5. Escalabilidad (Tradicional, synth03-05) ===")
    tab, lowess = scalability(df)
    print(tab)
    tab.to_csv(os.path.join(args.outdir, "escalabilidad.csv"))
    if lowess is None:
        print("  LOWESS: se necesitan al menos 3 tamaños distintos (faltan synth04/synth05).")
    else:
        print("  LOWESS (tiempo vs n; con 3 tamaños es orientativo, no inferencial):")
        print(lowess.to_string(index=False))

    print(f"\nTablas guardadas en: {args.outdir}/")


if __name__ == "__main__":
    main()