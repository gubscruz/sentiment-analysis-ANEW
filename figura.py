"""Gera as figuras da apresentacao."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Paleta divergente: polos vermelho/azul validados (dE 23,6 em protanopia,
# 31,9 em visao normal) com cinza neutro no meio.
NEGATIVO, NEUTRO, POSITIVO = "#e34948", "#898781", "#3987e5"
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "Arial"]


def _moldura(largura=11, altura=5.6, topo=0.74):
    fig, ax = plt.subplots(figsize=(largura, altura), dpi=200)
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    fig.subplots_adjust(left=0.075, right=0.975, top=topo, bottom=0.16)
    return fig, ax


def _cabecalho(fig, titulo, subtitulo):
    fig.text(0.075, 0.945, titulo, fontsize=19, color=TINTA,
             ha="left", va="top", fontweight="600")
    fig.text(0.075, 0.855, subtitulo, fontsize=11.5, color=MUDO,
             ha="left", va="top")


def _limpar_eixos(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRADE, lw=1)
    ax.xaxis.grid(False)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EIXO)
    ax.tick_params(colors=MUDO, labelsize=11, length=0)


def histograma(notas, limites, entidade, n_baixados, caminho="figuras/sentimento.png",
               largura=11, altura=5.6, cabecalho=True):
    """Histograma das notas, faixa neutra sombreada e media do ANEW marcada."""
    baixo, alto = limites
    centro = (baixo + alto) / 2
    notas = np.asarray(notas)
    n = len(notas)
    neg = int((notas < baixo).sum())
    pos = int((notas > alto).sum())
    neu = n - neg - pos

    # Sem cabecalho quando o proprio slide ja traz titulo e contagem.
    fig, ax = _moldura(largura=largura, altura=altura,
                       topo=0.79 if cabecalho else 0.97)

    bordas = np.arange(10, 101, 5)
    contagens, _ = np.histogram(notas, bins=bordas)
    for esquerda, altura in zip(bordas[:-1], contagens):
        if altura:
            meio = esquerda + 2.5
            cor = NEGATIVO if meio < baixo else POSITIVO if meio > alto else NEUTRO
            ax.bar(meio, altura, width=4.4, color=cor, zorder=3)

    teto = max(contagens.max() * 1.28, 1)
    ax.set_ylim(0, teto)
    ax.axvline(centro, color=TINTA_2, lw=1.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate(
        f"média do dicionário = {centro:.0f}\né daqui que medimos, não de 50",
        xy=(centro, teto), xytext=(-8, -6), textcoords="offset points",
        ha="right", va="top", fontsize=11, color=TINTA_2, linespacing=1.5,
    )

    _limpar_eixos(ax)
    ax.set_xlim(10, 100)
    ax.set_xticks([10, 25, 47, 70, 85, 100])
    ax.set_xlabel("nota do post   (0 = desagradável · 100 = agradável)",
                  fontsize=12, color=TINTA_2, labelpad=12)
    ax.set_ylabel("posts", fontsize=12, color=TINTA_2, labelpad=10)

    if cabecalho:
        _cabecalho(
            fig,
            f"O que as pessoas falam sobre “{entidade}”",
            f"{n} posts analisados, de {n_baixados} baixados. "
            f"Os outros não tinham palavras suficientes no dicionário.",
        )

    ax.legend(
        handles=[
            Patch(facecolor=NEGATIVO, label=f"negativo   {100*neg//n}%"),
            Patch(facecolor=NEUTRO, label=f"neutro   {100*neu//n}%"),
            Patch(facecolor=POSITIVO, label=f"positivo   {100*pos//n}%"),
        ],
        loc="upper right", frameon=False, fontsize=12, labelcolor=TINTA_2,
        handlelength=1.2, handleheight=1.2, borderpad=0, labelspacing=0.8,
    )

    fig.savefig(caminho, facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho


def comparacao_regua(notas, limites, caminho="figuras/comparacao.png"):
    """Duas barras empilhadas: cortar em 50 x cortar na media do dicionario."""
    baixo, alto = limites
    notas = np.asarray(notas)
    n = len(notas)

    ingenuo = [int((notas <= 50).sum()), 0, int((notas > 50).sum())]
    calibrado = [int((notas < baixo).sum()),
                 int(((notas >= baixo) & (notas <= alto)).sum()),
                 int((notas > alto).sum())]

    fig, ax = _moldura(altura=4.2, topo=0.70)
    fig.subplots_adjust(left=0.20, bottom=0.20)

    for y, valores in [(1, ingenuo), (0, calibrado)]:
        esquerda = 0
        for valor, cor in zip(valores, (NEGATIVO, NEUTRO, POSITIVO)):
            if not valor:
                continue
            largura = 100 * valor / n
            ax.barh(y, largura, left=esquerda, height=0.5, color=cor, zorder=3)
            if largura > 7:
                ax.text(esquerda + largura / 2, y, f"{largura:.0f}%",
                        ha="center", va="center", color="white",
                        fontsize=13, fontweight="600", zorder=4)
            esquerda += largura

    ax.set_yticks([1, 0])
    ax.set_yticklabels(["cortando no meio\nda escala (50)",
                        "cortando na média\ndo dicionário (58)"],
                       fontsize=12, color=TINTA_2, linespacing=1.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xticks([])
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)

    _cabecalho(
        fig,
        "A régua errada faz o resultado parecer outro",
        "Os mesmos posts, classificados de duas formas.",
    )
    ax.legend(
        handles=[Patch(facecolor=NEGATIVO, label="negativo"),
                 Patch(facecolor=NEUTRO, label="neutro"),
                 Patch(facecolor=POSITIVO, label="positivo")],
        loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3,
        frameon=False, fontsize=12, labelcolor=TINTA_2,
        handlelength=1.2, handleheight=1.2, columnspacing=2.5,
    )

    fig.savefig(caminho, facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho
