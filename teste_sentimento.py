"""Testes da secao 'Verificacao' da spec. Rodar: .venv/bin/python teste_sentimento.py"""

from sentimento import (
    calibrar,
    carregar_anew,
    classificar,
    forma_base,
    palavras_encontradas,
    pontuar,
)

anew = carregar_anew()
limites = calibrar(anew)
falhas = 0


def checar(descricao, obtido, esperado):
    global falhas
    ok = obtido == esperado
    falhas += not ok
    print(f"  [{'ok ' if ok else 'FALHOU'}] {descricao}")
    if not ok:
        print(f"          esperado={esperado!r}  obtido={obtido!r}")


print(f"faixa neutra calibrada: [{limites[0]:.1f} , {limites[1]:.1f}]")
print()

print("frases de resultado conhecido:")
for frase, esperado in [
    ("Argentina is beautiful, I love the people and the food", "positivo"),
    ("terrible trip, the hotel was awful and I hate the traffic", "negativo"),
    ("the meeting starts at four", "sem sinal"),
]:
    checar(f'"{frase[:46]}..."', classificar(pontuar(frase, anew), limites), esperado)

print()
print("lematizador (o bug que derrubou o prototipo):")
checar("hating vira hate, nao hat", forma_base("hating", anew), "hate")
checar("beaches vira beach", forma_base("beaches", anew), "beach")
checar("happier vira happy", forma_base("happier", anew), "happy")
checar("friends vira friend", forma_base("friends", anew), "friend")

print()
print("minimo de palavras:")
poucas = "just landed in Argentina, party time"
checar("post com poucas palavras nao e classificado", pontuar(poucas, anew), None)
caso_home = (
    "An elderly lady of the indigenous Humahuaca community in Jujuy cries "
    "as the regime in Argentina evicts her from her home and land"
)
checar(
    "post da senhora despejada nao sai como positivo",
    classificar(pontuar(caso_home, anew), limites),
    "sem sinal",
)

print()
print("hashtag colada vira texto:")
achadas = dict(palavras_encontradas("#LoveArgentina", anew))
checar("#LoveArgentina encontra 'love'", "love" in achadas, True)

print()
print(f"{'TODOS OS TESTES PASSARAM' if not falhas else f'{falhas} TESTE(S) FALHARAM'}")
raise SystemExit(1 if falhas else 0)
