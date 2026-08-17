"""Pontuacao de sentimento de posts usando o dicionario ANEW.

O notebook importa estas funcoes. A logica fica aqui para poder ser testada
sem depender da API nem de rodar celulas em ordem.
"""

import re
import statistics as st

import pandas as pd
from nltk.corpus import wordnet as wn

# Menor numero em que uma frase claramente emocional ainda passa: a frase de
# teste "terrible trip, the hotel was awful and I hate the traffic" encontra
# exatamente 3 palavras, porque 'trip', 'awful' e 'traffic' nao estao no ANEW.
MINIMO_PALAVRAS = 3


def carregar_anew(caminho="data/anew.csv"):
    """Le o ANEW e devolve {palavra: nota de agrado}.

    Atencao: o arquivo do OSF esta na escala 0-100, e nao na escala 1-9
    descrita no paper de Bradley & Lang.
    """
    tabela = pd.read_csv(caminho, encoding="utf-8-sig")
    return dict(zip(tabela["term"], tabela["pleasure"]))


def calibrar(anew):
    """Devolve os limites da faixa neutra, centrados na media do proprio ANEW.

    A media do dicionario e 58, nao 50. Cortar em 50 classificaria a maioria
    dos posts como positivos so pela composicao do dicionario.
    """
    notas = list(anew.values())
    media, desvio = st.mean(notas), st.stdev(notas)
    return media - 0.5 * desvio, media + 0.5 * desvio


def separar_hashtag(termo):
    """#ClassWar -> 'class war'. Hashtag toda minuscula fica inteira."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", termo)


def limpar(texto):
    """Tira URL, mencao e HTML. Hashtag vira texto normal."""
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"@\w+", " ", texto)
    texto = re.sub(r"#(\w+)", lambda m: separar_hashtag(m.group(1)), texto)
    return texto.lower()


def forma_base(palavra, anew):
    """Reduz a palavra a uma forma que exista no ANEW.

    Regra: casamento exato primeiro; senao, entre os lemas que o WordNet
    gera, usa o mais longo que esteja no dicionario. O criterio do mais longo
    evita reducoes agressivas demais -- sem ele, 'hating' vira 'hat' (que
    existe no ANEW) em vez de 'hate'.
    """
    if palavra in anew:
        return palavra
    candidatos = {c for pos in "vna" for c in wn._morphy(palavra, pos)}
    no_anew = [c for c in candidatos if c in anew]
    return max(no_anew, key=len) if no_anew else palavra


def palavras_encontradas(texto, anew):
    """Devolve [(palavra base, nota)] das palavras do post que estao no ANEW."""
    achadas = {}
    for token in re.findall(r"[a-z']{2,}", limpar(texto)):
        base = forma_base(token, anew)
        if base in anew:
            achadas[base] = anew[base]
    return sorted(achadas.items())


def pontuar(texto, anew):
    """Nota do post = media do agrado das palavras distintas encontradas.

    Devolve None se o post nao alcancar o minimo de palavras: com poucas
    palavras a nota fica instavel e uma palavra isolada decide o post todo.
    """
    achadas = palavras_encontradas(texto, anew)
    if len(achadas) < MINIMO_PALAVRAS:
        return None
    return st.mean(nota for _, nota in achadas)


def classificar(nota, limites):
    baixo, alto = limites
    if nota is None:
        return "sem sinal"
    if nota < baixo:
        return "negativo"
    if nota > alto:
        return "positivo"
    return "neutro"
