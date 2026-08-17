# Sentiment Analysis with ANEW

Análise de sentimento dos posts sobre **Argentina** no Bluesky, usando o
dicionário ANEW (Bradley & Lang, 1999).

**Leia primeiro:** [`conteudo.md`](conteudo.md) — todas as decisões, o que foi
testado, as inconsistências encontradas no ANEW e o rascunho dos dois slides.

## Como rodar

```bash
uv venv                                    # se ainda não existir
VIRTUAL_ENV=.venv uv pip install requests nltk pandas matplotlib langdetect
.venv/bin/python -c "import nltk; nltk.download('wordnet')"
.venv/bin/python teste_sentimento.py       # 9 testes de verificação
```

## Arquivos

| arquivo | o que faz |
|---|---|
| `conteudo.md` | documento de referência do projeto |
| `sentimento.py` | limpeza, lematização, pontuação e classificação |
| `teste_sentimento.py` | testes de verificação |
| `figura.py` | gera o histograma do slide 2 |
| `data/anew.csv` | dicionário ANEW, 1.034 palavras |
| `data/posts_exemplo.csv` | amostra **provisória** do Mastodon, só para desenvolver a figura |

## Estado

O pontuador está pronto e testado. Falta o código que baixa do Bluesky — ele
depende de uma conta grátis e de uma *app password* (Settings → Privacy and
Security → App Passwords). Ver seção 10 do `conteudo.md`.
