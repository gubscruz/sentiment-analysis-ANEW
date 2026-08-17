"""Investiga o comportamento do classificador: onde acerta e onde falha.

Roda sobre o corpus de posts e produz os numeros e exemplos que vao para o
relatorio. Nao altera nada do algoritmo -- so observa.
"""

import re
import statistics as st
from collections import Counter

import pandas as pd

from sentimento import (
    MINIMO_PALAVRAS,
    calibrar,
    carregar_anew,
    classificar,
    limpar,
    palavras_encontradas,
)

anew = carregar_anew()
limites = calibrar(anew)
centro = sum(limites) / 2

posts = pd.read_csv("data/posts_exemplo.csv")["texto"].dropna().tolist()
analisados = [(p, palavras_encontradas(p, anew)) for p in posts]
com_nota = [(p, a, st.mean(v for _, v in a)) for p, a in analisados if len(a) >= MINIMO_PALAVRAS]


def titulo(t):
    print()
    print("=" * 70)
    print(t)
    print("=" * 70)


def curto(texto, n=64):
    return re.sub(r"\s+", " ", texto).strip()[:n]


# ----------------------------------------------------------------- cobertura
titulo("COBERTURA — quanto do texto o ANEW enxerga")

tokens_tot = sum(len(re.findall(r"[a-z']{2,}", limpar(p))) for p in posts)
tokens_achados = sum(len(a) for _, a in analisados)
print(f"  posts no corpus                : {len(posts)}")
print(f"  posts classificados (>= {MINIMO_PALAVRAS} palavras): {len(com_nota)} "
      f"({100*len(com_nota)//len(posts)}%)")
print(f"  palavras distintas encontradas : {tokens_achados} de {tokens_tot} tokens "
      f"({100*tokens_achados/max(tokens_tot,1):.1f}%)")

qtd = Counter(len(a) for _, a in analisados)
print("\n  palavras do ANEW por post:")
for k in sorted(qtd)[:12]:
    print(f"    {k:2} palavra(s): {qtd[k]:3} posts  {'#' * min(qtd[k], 46)}")

# --------------------------------------------------- ganho da lematizacao
titulo("SUCESSO 1 — quanto a lematizacao recupera")

exato = lemat = 0
recuperadas = Counter()
for p, achadas in analisados:
    tokens = set(re.findall(r"[a-z']{2,}", limpar(p)))
    diretas = {t for t in tokens if t in anew}
    exato += len(diretas)
    lemat += len(achadas)
    for palavra, _ in achadas:
        if palavra not in tokens:
            recuperadas[palavra] += 1

print(f"  so casamento exato : {exato} palavras")
print(f"  com lematizacao    : {lemat} palavras  (+{100*(lemat-exato)/max(exato,1):.0f}%)")
print(f"\n  palavras que so a lematizacao achou: "
      f"{', '.join(w for w, _ in recuperadas.most_common(12)) or '(nenhuma)'}")

# ------------------------------------------------------------- calibracao
titulo("SUCESSO 2 — o efeito da calibracao")

notas = [n for _, _, n in com_nota]
ing = Counter("positivo" if n > 50 else "negativo" for n in notas)
cal = Counter(classificar(n, limites) for n in notas)
t = len(notas)
print(f"  corte ingenuo em 50 : " + "  ".join(f"{k}={v} ({100*v//t}%)" for k, v in sorted(ing.items())))
print(f"  faixa calibrada     : " + "  ".join(f"{k}={v} ({100*v//t}%)" for k, v in sorted(cal.items())))

# ---------------------------------------------- alavancagem de uma palavra
titulo("LIMITACAO 1 — uma palavra sozinha muda a classe?")

viradas = []
for p, achadas, nota in com_nota:
    classe = classificar(nota, limites)
    extrema = max(achadas, key=lambda x: abs(x[1] - centro))
    resto = [v for w, v in achadas if w != extrema[0]]
    if not resto:
        continue
    nova = classificar(st.mean(resto), limites)
    if nova != classe:
        viradas.append((p, achadas, classe, nova, extrema))

print(f"  tirando so a palavra mais extrema, {len(viradas)} de {len(com_nota)} posts "
      f"({100*len(viradas)//max(len(com_nota),1)}%) mudam de classe")
print("\n  exemplos:")
for p, a, antes, depois, ex in viradas[:4]:
    print(f'    "{curto(p)}..."')
    print(f"      {len(a)} palavras · sem '{ex[0]}'({ex[1]:.0f}):  {antes} -> {depois}")

# ------------------------------------------------------------- negacao
titulo("LIMITACAO 2 — negacao nao e tratada")

NEG = r"\b(not|no|never|isn't|aren't|wasn't|don't|doesn't|didn't|can't|won't|nothing)\b"
casos = []
for p, achadas, nota in com_nota:
    texto = limpar(p)
    for m in re.finditer(NEG + r"\s+(?:\w+\s+){0,2}?(\w+)", texto):
        if m.group(2) in anew:
            casos.append((p, m.group(0).strip(), m.group(2), anew[m.group(2)]))
            break
print(f"  {len(casos)} de {len(com_nota)} posts classificados tem negacao antes de "
      f"palavra do ANEW ({100*len(casos)//max(len(com_nota),1)}%)")
print("\n  exemplos (a palavra pontua como se fosse afirmativa):")
for p, trecho, palavra, v in casos[:5]:
    print(f'    "{trecho}"  ->  {palavra} conta como {v:.0f}')
    print(f"       em: \"{curto(p, 58)}...\"")

# ------------------------------------- palavras que puxam o corpus inteiro
titulo("LIMITACAO 3 — quais palavras decidem o resultado do corpus")

freq = Counter()
for _, achadas in analisados:
    for w, _ in achadas:
        freq[w] += 1
print("  as 18 palavras mais frequentes e suas notas:")
for w, c in freq.most_common(18):
    lado = "neg" if anew[w] < limites[0] else "POS" if anew[w] > limites[1] else " . "
    print(f"    {w:14} {c:3}x   {anew[w]:5.1f}  {lado}")

# ------------------------------------------ palavra de tema x de emocao
titulo("LIMITACAO 4 — palavra de TEMA pontua como se fosse EMOCAO")

TEMA = ["war", "death", "cancer", "murder", "crime", "victim", "gun", "bomb",
        "money", "cash", "money", "police", "court", "hospital", "funeral",
        "birthday", "christmas", "wedding", "baby", "family", "home", "party"]
achados_tema = [(w, anew[w], freq[w]) for w in dict.fromkeys(TEMA) if freq.get(w)]
print("  palavras presentes no corpus que descrevem ASSUNTO, nao opiniao:")
for w, v, c in sorted(achados_tema, key=lambda x: -x[2]):
    print(f"    {w:12} {c:3}x  nota {v:5.1f}  -> empurra o post para "
          f"{'positivo' if v > limites[1] else 'negativo' if v < limites[0] else 'neutro'}")

# ------------------------------------- comprimento x distancia da media
titulo("LIMITACAO 5 — post mais longo tende ao meio (regressao a media)")

por_tam = {}
for _, achadas, nota in com_nota:
    faixa = "3-4" if len(achadas) <= 4 else "5-8" if len(achadas) <= 8 else "9+"
    por_tam.setdefault(faixa, []).append(abs(nota - centro))
print("  distancia media do centro da faixa neutra, por tamanho do post:")
for faixa in ["3-4", "5-8", "9+"]:
    v = por_tam.get(faixa, [])
    if v:
        print(f"    {faixa:4} palavras: {len(v):3} posts, distancia media {st.mean(v):5.1f}")
print("\n  quanto mais palavras, mais a nota converge para a media do dicionario:")
print("  posts longos ficam 'neutros' por diluicao, nao por serem equilibrados.")

# ---------------------------------------------------- media x mediana
titulo("EXPERIMENTO — e se usassemos mediana em vez de media?")

mudou = 0
exemplos = []
for p, achadas, nota in com_nota:
    med = st.median([v for _, v in achadas])
    if classificar(med, limites) != classificar(nota, limites):
        mudou += 1
        if len(exemplos) < 3:
            exemplos.append((p, achadas, nota, med))
print(f"  {mudou} de {len(com_nota)} posts mudam de classe "
      f"({100*mudou//max(len(com_nota),1)}%)")
for p, a, mea, med in exemplos:
    print(f'    "{curto(p)}..."')
    print(f"      media {mea:.1f} ({classificar(mea, limites)})  ·  "
          f"mediana {med:.1f} ({classificar(med, limites)})")

# ------------------------------------------------------------- acertos
titulo("LIMITACAO 6 — os posts com MAIS palavras sao os que mais erram")

# Rotulado inicialmente como "sucesso", partindo da hipotese de que mais
# palavras dariam mais precisao. O corpus mostrou o contrario: os posts mais
# longos sao os mais diluidos, e e neles que aparecem os erros mais graves.
fortes = sorted(com_nota, key=lambda x: -len(x[1]))[:3]
for p, a, n in fortes:
    print(f'  [{classificar(n, limites):8}] nota {n:5.1f} · {len(a)} palavras')
    print(f'    "{curto(p, 78)}..."')
    print(f"    {[f'{w}={v:.0f}' for w, v in sorted(a, key=lambda x: x[1])[:8]]}")
    print()
