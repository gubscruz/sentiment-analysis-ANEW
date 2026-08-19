# Sentiment Analysis with ANEW

Análise de sentimento dos posts sobre **Argentina** no Mastodon, usando o
dicionário ANEW (Bradley & Lang, 1999).

**Entrega:** [`apresentacao/apresentacao.pdf`](apresentacao/apresentacao.pdf) —
os três slides mais a capa. Há também `apresentacao.pptx`, **com texto editável**,
gerado por `apresentacao/gerar_pptx.py`.

**Leia primeiro:** [`conteudo.md`](conteudo.md) — todas as decisões, o que foi
testado, as inconsistências encontradas no ANEW e o rascunho dos dois slides.

## Como rodar

```bash
uv venv                                    # se ainda não existir
VIRTUAL_ENV=.venv uv pip install requests nltk pandas matplotlib langdetect
.venv/bin/python -c "import nltk; nltk.download('wordnet')"
.venv/bin/python teste_sentimento.py       # 9 testes de verificação
.venv/bin/python baixar_posts.py           # baixa os posts (~4 min)
```

## Arquivos

| arquivo | o que faz |
|---|---|
| `conteudo.md` | documento de referência do projeto |
| `achados.md` | **o que o classificador acerta e o que erra**, medido em 632 posts |
| `baixar_posts.py` | baixa os posts do Mastodon e confere o idioma |
| `baixar_bluesky.py` | alternativa pelo Bluesky — **precisa de app password** |
| `sentimento.py` | limpeza, lematização, pontuação e classificação |
| `teste_sentimento.py` | testes de verificação |
| `analise_classificador.py` | investigação que gerou o `achados.md` |
| `figura.py` | gera o histograma do slide 2 |
| `data/anew.csv` | dicionário ANEW, 1.034 palavras |
| `data/posts.csv` | 632 posts em inglês sobre Argentina, gerados por `baixar_posts.py` |
| `apresentacao/` | os três slides: template HTML, PDF e PPTX |

## Estado

O trabalho está completo: download, pontuação, testes, investigação e os dois
slides.

Sobre a fonte: a intenção inicial era o Bluesky, mas a busca dele exige
autenticação (responde 403 sem login). Reddit e webscraping também foram
testados e estão bloqueados. O Mastodon foi o que funcionou sem credencial —
a tabela de testes está na seção 2 do `conteudo.md`.

O `baixar_bluesky.py` está pronto para quando houver uma app password. Vale a
troca: a busca do Bluesky aceita texto livre em vez de hashtag. Hoje só
encontramos quem escreveu `#argentina`, o que já é um recorte — e metade desses
posts acaba sendo sobre futebol (ver `achados.md`).

```bash
export BSKY_USUARIO="seu-usuario.bsky.social"
export BSKY_SENHA="xxxx-xxxx-xxxx-xxxx"
.venv/bin/python baixar_bluesky.py
```
