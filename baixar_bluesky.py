"""Baixa posts sobre uma entidade da API do Bluesky (protocolo AT).

A busca do Bluesky responde HTTP 403 sem autenticacao, entao e preciso uma
conta gratis e uma *app password* (Settings -> Privacy and Security -> App
Passwords). Nunca use a senha normal da conta: a app password e revogavel e
serve exatamente para isto.

As credenciais vem de variaveis de ambiente, para nao ficarem no codigo nem no
historico do git:

    export BSKY_USUARIO="seu-usuario.bsky.social"
    export BSKY_SENHA="xxxx-xxxx-xxxx-xxxx"
    .venv/bin/python baixar_bluesky.py

Vantagem sobre o Mastodon (`baixar_posts.py`): a busca aceita texto livre em
vez de hashtag, e filtra idioma na origem. Isso evita o vies de so encontrar
quem escreveu a hashtag -- vies que aparece no `achados.md`.
"""

import csv
import os
import re
import sys
import time

import requests
from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0

SERVIDOR = "https://bsky.social"
BUSCA = "https://public.api.bsky.app"
CONSULTA = "Argentina"
IDIOMA = "en"
ALVO = 1000          # quantos posts em ingles queremos
POR_PAGINA = 100     # maximo aceito pela API
DESTINO = "data/posts_bluesky.csv"
PAUSA = 0.3


def entrar(usuario, senha):
    """Troca usuario + app password por um token de acesso."""
    resposta = requests.post(
        f"{SERVIDOR}/xrpc/com.atproto.server.createSession",
        json={"identifier": usuario, "password": senha},
        timeout=20,
    )
    if resposta.status_code == 401:
        sys.exit("Usuario ou app password invalidos. Gere uma nova em "
                 "Settings -> Privacy and Security -> App Passwords.")
    resposta.raise_for_status()
    return resposta.json()["accessJwt"]


def texto_limpo(texto):
    return re.sub(r"\s+", " ", texto).strip()


def e_ingles(texto):
    """Confere o idioma, porque a etiqueta da API nao basta.

    No Mastodon, a etiqueta marcou como ingles 372 posts que eram espanhol ou
    italiano. Nao ha motivo para confiar mais na do Bluesky.
    """
    if len(texto) < 20:
        return False
    try:
        return detect(texto) == "en"
    except LangDetectException:
        return False


def buscar(token):
    """Pagina a busca ate juntar ALVO posts em ingles."""
    sessao = requests.Session()
    sessao.headers.update({
        "Authorization": f"Bearer {token}",
        "User-Agent": "projeto-nlp-anew/1.0 (trabalho academico)",
    })

    coletados, vistos, cursor = [], set(), None
    while len(coletados) < ALVO:
        parametros = {"q": CONSULTA, "limit": POR_PAGINA, "lang": IDIOMA}
        if cursor:
            parametros["cursor"] = cursor

        try:
            resposta = sessao.get(f"{BUSCA}/xrpc/app.bsky.feed.searchPosts",
                                  params=parametros, timeout=25)
            resposta.raise_for_status()
            dados = resposta.json()
        except (requests.RequestException, ValueError) as erro:
            print(f"  parou: {type(erro).__name__}", file=sys.stderr)
            break

        posts = dados.get("posts", [])
        if not posts:
            break

        for post in posts:
            uri = post["uri"]
            if uri in vistos:
                continue
            vistos.add(uri)
            texto = texto_limpo(post["record"].get("text", ""))
            if texto and e_ingles(texto):
                coletados.append({
                    "id": uri,
                    "idioma_api": (post["record"].get("langs") or [None])[0],
                    "texto": texto,
                })

        cursor = dados.get("cursor")
        if not cursor:
            break
        print(f"  {len(coletados)} posts em ingles...", end="\r")
        time.sleep(PAUSA)

    return coletados


def main():
    usuario = os.environ.get("BSKY_USUARIO")
    senha = os.environ.get("BSKY_SENHA")
    if not usuario or not senha:
        sys.exit(__doc__)

    print("  entrando no Bluesky...")
    token = entrar(usuario, senha)

    print(f"  buscando “{CONSULTA}”...")
    posts = buscar(token)

    with open(DESTINO, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["id", "idioma_api", "texto"])
        escritor.writeheader()
        escritor.writerows(posts)

    print(f"\n  {len(posts)} posts em ingles gravados em {DESTINO}")


if __name__ == "__main__":
    main()
