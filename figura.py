"""Gera o histograma de sentimento para o slide 2."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Paleta divergente: polos vermelho/azul validados (dE 23,6 daltonismo,
# 31,9 visao normal) com cinza neutro no meio.
NEGATIVO, NEUTRO, POSITIVO = "#e34948", "#898781", "#3987e5"
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

FONTE = ["system-ui", "-apple-system", "Segoe UI", "Helvetica Neue", "sans-serif"]


def histograma(notas, limites, entidade, n_baixados, caminho="figuras/sentimento.png"):
    """Histograma das notas, faixa neutra sombreada e media do ANEW marcada."""
    baixo, alto = limites
    centro = (baixo + alto) / 2
    notas = np.asarray(notas)

    plt.rcParams["font.family"] = FONTE
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)

    # Uma barra por faixa de 5 pontos, pintada pela classe em que cai.
    bordas = np.arange(10, 101, 5)
    contagens, _ = np.histogram(notas, bins=bordas)
    for esquerda, altura in zip(bordas[:-1], contagens):
        if altura == 0:
            continue
        meio = esquerda + 2.5
        cor = NEGATIVO if meio < baixo else POSITIVO if meio > alto else NEUTRO
        # width 4.4 em passo de 5 deixa o vao de superficie entre as barras
        ax.bar(meio, altura, width=4.4, color=cor, zorder=3)

    ax.axvline(centro, color=TINTA_2, lw=1.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate(
        f"média do ANEW = {centro:.0f}\n(e não 50)",
        xy=(centro, ax.get_ylim()[1] * 0.94),
        xytext=(6, 0), textcoords="offset points",
        ha="left", va="top", fontsize=9.5, color=TINTA_2, linespacing=1.4,
    )

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRADE, lw=1)
    ax.xaxis.grid(False)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EIXO)
    ax.tick_params(colors=MUDO, labelsize=9.5, length=0)

    ax.set_xlim(10, 100)
    ax.set_xticks([10, 25, 47, 70, 85, 100])
    ax.set_xlabel("nota de agrado do post  (0 = desagradável · 100 = agradável)",
                  fontsize=10, color=TINTA_2, labelpad=10)
    ax.set_ylabel("posts", fontsize=10, color=TINTA_2, labelpad=10)

    n = len(notas)
    neg = int((notas < baixo).sum())
    pos = int((notas > alto).sum())
    neu = n - neg - pos
    ax.set_title(
        f"Sentimento dos posts sobre “{entidade}” no Bluesky",
        fontsize=15, color=TINTA, pad=16, loc="left", fontweight="600",
    )
    fig.text(
        0.125, 0.895,
        f"{n} posts classificados de {n_baixados} baixados  ·  "
        f"os outros não tinham palavras suficientes do ANEW",
        fontsize=9.5, color=MUDO, ha="left", va="top",
    )

    ax.legend(
        handles=[
            Patch(facecolor=NEGATIVO, label=f"negativo — {neg} ({100*neg//n}%)"),
            Patch(facecolor=NEUTRO, label=f"neutro — {neu} ({100*neu//n}%)"),
            Patch(facecolor=POSITIVO, label=f"positivo — {pos} ({100*pos//n}%)"),
        ],
        loc="upper right", frameon=False, fontsize=10, labelcolor=TINTA_2,
        handlelength=1.1, handleheight=1.1, borderpad=0, labelspacing=0.7,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(caminho, facecolor=SUPERFICIE, bbox_inches="tight")
    return caminho
