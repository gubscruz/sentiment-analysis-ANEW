"""Baixa posts sobre uma entidade da API publica do Mastodon.

Uso:
    .venv/bin/python baixar_posts.py

O resultado vai para data/posts.csv. O download roda uma vez; as etapas
seguintes leem o arquivo, entao o resultado nao muda entre execucoes.

Sobre a escolha da fonte: a busca do Bluesky exige autenticacao (responde 403
sem login), o Reddit bloqueia a API (403) e o HTML antigo (302), e a busca por
texto livre do Mastodon devolve resposta vazia sem conta. O que funciona sem
credencial e a linha do tempo por hashtag do Mastodon, usada aqui.
"""

import csv
import re
import sys
import time

import requests
from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0  # torna a deteccao de idioma reproduzivel

INSTANCIA = "https://mastodon.social"
TAGS = ["argentina", "buenosaires", "argentine", "patagonia"]
PAGINAS_POR_TAG = 18
POR_PAGINA = 40
DESTINO = "data/posts.csv"
PAUSA = 0.25  # segundos entre requisicoes, para nao sobrecarregar a instancia


def texto_limpo(html):
    """O Mastodon devolve o post em HTML. Aqui vira texto corrido."""
    texto = re.sub(r"<br\s*/?>", " ", html)
    texto = re.sub(r"</p>", " ", texto)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = (texto.replace("&amp;", "&").replace("&lt;", "<")
                  .replace("&gt;", ">").replace("&quot;", '"')
                  .replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", texto).strip()


def e_ingles(texto):
    """Confere o idioma por conta propria.

    A etiqueta de idioma da API nao e confiavel: no teste, posts em espanhol e
    italiano vieram marcados como ingles. Como o ANEW e um dicionario de
    ingles, uma palavra espanhola nunca casaria, mas uma palavra que existe nos
    dois idiomas casaria com a nota errada.
    """
    if len(texto) < 20:
        return False
    try:
        return detect(texto) == "en"
    except LangDetectException:
        return False


def baixar_tag(sessao, tag):
    """Percorre a linha do tempo de uma hashtag, pagina a pagina."""
    url = f"{INSTANCIA}/api/v1/timelines/tag/{tag}"
    parametros = {"limit": POR_PAGINA}
    coletados = []

    for _ in range(PAGINAS_POR_TAG):
        try:
            resposta = sessao.get(url, params=parametros, timeout=25)
            resposta.raise_for_status()
            lote = resposta.json()
        except (requests.RequestException, ValueError) as erro:
            print(f"    parou em #{tag}: {type(erro).__name__}", file=sys.stderr)
            break

        if not lote:
            break

        for post in lote:
            coletados.append({
                "id": post["id"],
                "tag": tag,
                "idioma_api": post.get("language"),
                "texto": texto_limpo(post["content"]),
            })

        parametros = {"limit": POR_PAGINA, "max_id": lote[-1]["id"]}
        time.sleep(PAUSA)

    return coletados


def main():
    sessao = requests.Session()
    sessao.headers["User-Agent"] = "projeto-nlp-anew/1.0 (trabalho academico)"

    brutos = []
    for tag in TAGS:
        print(f"  baixando #{tag}...")
        brutos += baixar_tag(sessao, tag)

    # Um post pode aparecer em mais de uma hashtag.
    unicos = {p["id"]: p for p in brutos}.values()

    ingleses = [p for p in unicos if p["texto"] and e_ingles(p["texto"])]

    # Quantos a etiqueta da API teria deixado passar errado
    falsos = [p for p in unicos
              if p["idioma_api"] == "en" and p["texto"] and not e_ingles(p["texto"])]

    with open(DESTINO, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["id", "tag", "idioma_api", "texto"])
        escritor.writeheader()
        escritor.writerows(ingleses)

    print()
    print(f"  posts baixados        : {len(brutos)}")
    print(f"  depois de tirar repetidos: {len(unicos)}")
    print(f"  confirmados em ingles : {len(ingleses)}")
    print(f"  a API dizia 'en' mas nao era: {len(falsos)}")
    print(f"  gravados em {DESTINO}")


if __name__ == "__main__":
    main()
