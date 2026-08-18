# -*- coding: utf-8 -*-
"""Graficas del Monte Carlo. Lee lo que dejo montecarlo.py, no vuelve a simular.

    python montecarlo_graficas.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from montecarlo import ESCENARIOS

BG, CARD, TXT, MUTED, LINE = "#0e1014", "#1a1f28", "#eef2f8", "#a3aebc", "#2b3340"
ACC, WARN, BAD, GOLD = "#00d29a", "#ffb454", "#ff6b6b", "#ffd166"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": TXT, "axes.labelcolor": TXT, "axes.edgecolor": LINE,
    "xtick.color": MUTED, "ytick.color": MUTED, "grid.color": LINE,
    "font.family": "DejaVu Sans", "font.size": 10,
})
usd = FuncFormatter(lambda v, p: f"{v:,.0f}".replace(",", ".") + " $")

S = np.load("montecarlo_series.npy")
NOMBRES = [n for n, _ in ESCENARIOS]
COLOR = {n: (ACC if "PLAN" in n else WARN if "entrenadores" in n else MUTED) for n in NOMBRES}


# ---------------------------------------------------------------- grafica 1
def caja_y_bigotes():
    fig, ax = plt.subplots(figsize=(11, 5.6))
    orden = np.argsort([np.median(S[i]) for i in range(len(NOMBRES))])
    for fila, i in enumerate(orden):
        x = S[i]
        p10, p25, p50, p75, p90 = np.percentile(x, [10, 25, 50, 75, 90])
        c = COLOR[NOMBRES[i]]
        ax.plot([p10, p90], [fila, fila], color=c, lw=1.4, alpha=.55, zorder=1)
        ax.plot([p25, p75], [fila, fila], color=c, lw=11, alpha=.85,
                solid_capstyle="round", zorder=2)
        ax.plot([p50], [fila], "o", color=BG, ms=7, zorder=4)
        ax.plot([p50], [fila], "o", color=c, ms=4.5, zorder=5)
        ax.text(p90 + 260, fila, f"{p50:,.0f} $".replace(",", "."),
                va="center", color=c, fontsize=10.5, fontweight="bold")
    ax.axvline(10000, color=BAD, ls="--", lw=1.2, alpha=.75)
    ax.text(10000, len(NOMBRES) - .35, " meta 10.000 $", color=BAD, fontsize=9.5, va="top")
    ax.set_yticks(range(len(orden)))
    ax.set_yticklabels([NOMBRES[i] for i in orden], fontsize=10.5)
    ax.set_xlim(0, 12500); ax.set_ylim(-.7, len(NOMBRES) - .3)
    ax.xaxis.set_major_formatter(usd)
    ax.set_xlabel("Ingreso neto en un año", labelpad=10)
    ax.set_title("Cuánto se gana en un año, por escenario", fontsize=14,
                 pad=16, loc="left", fontweight="medium")
    ax.text(0, 1.005, "punto = la mitad de las veces sales por debajo  ·  barra = 1 de cada 2 casos  ·  línea = 8 de cada 10",
            transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")
    ax.grid(axis="x", alpha=.22); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig("mc_1_comparacion.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- grafica 2
def distribuciones():
    ver = ["Solo publicar en Play", "Play + tus 100 conocidos",
           "Contenido en TikTok", "EL PLAN (todo junto)"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4))
    for ax, nombre in zip(axes.ravel(), ver):
        x = S[NOMBRES.index(nombre)]
        c = COLOR[nombre]
        ax.hist(np.clip(x, 0, 9000), bins=70, color=c, alpha=.8, edgecolor="none")
        med = np.median(x)
        ax.axvline(med, color=TXT, lw=1.3)
        ax.text(med + 150, ax.get_ylim()[1] * .88, f"mediana\n{med:,.0f} $".replace(",", "."),
                color=TXT, fontsize=9.5, va="top")
        ax.set_title(nombre, fontsize=11.5, loc="left", color=c, pad=8)
        ax.set_xlim(0, 9000); ax.set_yticks([])
        ax.xaxis.set_major_formatter(usd)
        ax.grid(axis="x", alpha=.18); ax.set_axisbelow(True)
        for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    fig.suptitle("La forma importa más que la media", fontsize=14, x=.012, ha="left",
                 y=.985, fontweight="medium")
    fig.text(.012, .938, "cada barra son 200.000 años simulados · la cola de la derecha es la que infla la media y casi nunca ocurre",
             color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig("mc_2_distribuciones.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- grafica 3
def probabilidad_acumulada():
    fig, ax = plt.subplots(figsize=(11, 5.4))
    metas = np.linspace(0, 12000, 300)
    for i, nombre in enumerate(NOMBRES):
        x = S[i]
        p = [(x >= m).mean() * 100 for m in metas]
        destaca = "PLAN" in nombre or "entrenadores" in nombre
        ax.plot(metas, p, color=COLOR[nombre], lw=2.6 if destaca else 1.3,
                alpha=1 if destaca else .5, label=nombre, zorder=3 if destaca else 2)
    ax.axvline(10000, color=BAD, ls="--", lw=1.2, alpha=.75)
    ax.text(10000, 96, " meta 10.000 $", color=BAD, fontsize=9.5)
    ax.set_xlim(0, 12000); ax.set_ylim(0, 100)
    ax.xaxis.set_major_formatter(usd)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    ax.set_xlabel("Ganar al menos...", labelpad=10)
    ax.set_ylabel("Probabilidad")
    ax.set_title("Qué probabilidad hay de llegar a cada cifra", fontsize=14,
                 pad=16, loc="left", fontweight="medium")
    ax.grid(alpha=.2); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper right", labelcolor=TXT)
    fig.tight_layout()
    fig.savefig("mc_3_probabilidad.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- grafica 4
def de_donde_sale():
    """El PLAN, desglosado. Que parte del dinero viene de cada cosa."""
    from montecarlo import (rng, lognormal_de, ingreso_consumo, licencias_b2b, N)
    cierres = rng.gamma(2.2, 1.0, N)
    lic = licencias_b2b(cierres, 19.0, 0.12, 0.40, 168.0)
    tal = rng.poisson(11, N) * rng.normal(62, 18, N).clip(20, 140)
    inst = rng.poisson(2, N)
    gr = rng.binomial(inst, 0.10) * rng.normal(1700, 500, N).clip(700, 3500)
    cons, anun, pro = ingreso_consumo(lognormal_de(450, 2500))
    partes = [("Licencias a entrenadores", np.median(lic), ACC),
              ("Talleres presenciales",    np.median(tal), GOLD),
              ("Venta institucional",      np.mean(gr),    WARN),
              ("Atlas Pro en Play",        np.median(pro) * .7, MUTED),
              ("Anuncios",                 np.median(anun) * .7, BAD)]
    fig, ax = plt.subplots(figsize=(11, 3.2))
    izq, total = 0, sum(p[1] for p in partes)
    for etq, v, c in partes:
        ax.barh([0], [v], left=izq, color=c, height=.5, edgecolor=BG, lw=2)
        if v / total > .04:
            ax.text(izq + v / 2, 0, f"{v:,.0f} $".replace(",", "."),
                    ha="center", va="center", color=BG, fontweight="bold", fontsize=10)
        ax.text(izq + v / 2, -.42, etq, ha="center", va="top", color=c, fontsize=9.5)
        izq += v
    ax.set_xlim(0, total * 1.02); ax.set_ylim(-.95, .45)
    ax.set_yticks([]); ax.xaxis.set_major_formatter(usd)
    ax.set_title(f"De dónde salen los {total:,.0f} $ del PLAN".replace(",", "."),
                 fontsize=14, pad=16, loc="left", fontweight="medium")
    ax.text(0, 1.02, "los anuncios y Atlas Pro son el 8% · no son el negocio, son la propina",
            transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", alpha=.18); ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig("mc_4_desglose.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    caja_y_bigotes(); distribuciones(); probabilidad_acumulada(); de_donde_sale()
    print("mc_1_comparacion.png\nmc_2_distribuciones.png\nmc_3_probabilidad.png\nmc_4_desglose.png")
