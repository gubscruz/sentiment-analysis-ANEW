# Análise de sentimento sobre "Argentina" com o dicionário ANEW

**Data:** 2026-08-17 · **Entidade:** Argentina · **Rede social:** Bluesky

---

## Objetivo

Descobrir se os posts sobre a Argentina são, em média, positivos ou
negativos, usando o dicionário ANEW (Bradley & Lang, 1999).

Entrega: um notebook Jupyter que baixa os posts, pontua cada um e gera a
figura. Os dois slides são montados à mão depois.

---

## Pipeline

```
Bluesky (login) ──> posts em inglês sobre "Argentina" ──> posts.csv
                                                              │
OSF ──> anew.csv ────────────────────────────────────────────>│
                                                              ▼
                                                    pontuar cada post
                                                              ▼
                                                   histograma + números
```

Os posts são baixados uma vez e gravados em `posts.csv`. Assim o notebook
roda offline depois e o resultado não muda entre execuções.

---

## Fonte dos posts

**Bluesky, autenticado.** A busca (`app.bsky.feed.searchPosts`) responde 403
sem login, então o código faz `createSession` com uma app password e usa o
token retornado. A busca aceita `lang=en` nativamente.

Alternativas foram testadas e descartadas: Reddit bloqueia tanto a API
(403) quanto o HTML antigo (302), e o Mastodon só entrega 16% dos posts em
inglês. Webscraping seria mais frágil que a API.

**Meta:** 300 posts analisáveis, com teto de 2.000 baixados.

**Filtro de idioma próprio.** A etiqueta de idioma da API não é confiável —
no teste passaram posts em espanhol e italiano marcados como inglês. Como o
ANEW é dicionário de inglês, o notebook confere o idioma por conta própria.

---

## O dicionário

`anew.csv`, de `https://osf.io/download/cq6ng/`. São 1.034 palavras com as
colunas `term`, `pleasure`, `arousal` e `dominance`. Sem duplicatas.

Este trabalho usa apenas `pleasure`. Média 58,4 · mediana 60,0 · desvio 22,6.

**Inconsistências e tratamento.** O arquivo do OSF está na escala 0–100, e
não na escala 1–9 descrita no paper — o notebook documenta isso para a
origem dos números ficar clara. O dicionário também puxa para o positivo:
62% das palavras estão acima do meio da escala, o que é corrigido pela
calibração do limiar abaixo. Por fim, algumas palavras são ambíguas
(`party` vale 89, mas pode significar partido político); isso não tem
conserto dentro do método e fica declarado como limitação.

---

## Pontuação

Para cada post: limpar URLs e menções, separar em palavras, reduzir cada uma
à forma base com o lematizador WordNet do NLTK, procurar no ANEW e tirar a
média da coluna `pleasure`.

```
nota(post) = média do pleasure das palavras encontradas
```

A lematização é necessária porque o dicionário tem `love` e `hate`, mas os
posts escrevem `loved` e `hating`. Cortar sufixo na mão não serve: no teste,
`caring` virou `car` em vez de `care`.

---

## Classificação

| nota | classe |
|---|---|
| abaixo de 47 | negativo |
| entre 47 e 70 | neutro |
| acima de 70 | positivo |

**Por que não cortar em 50.** A média do próprio ANEW é 58, não 50. Usando
50 como referência, 93% dos posts reais saíram como positivos — isso é
característica do dicionário, não da Argentina. A faixa é centrada em 58,
então "positivo" significa que o post usa palavras mais agradáveis que a
palavra média do dicionário.

**Mínimo de 3 palavras.** Post que bate em menos de 3 palavras distintas do
ANEW não é classificado. Com poucas palavras a nota é instável e uma palavra
isolada decide o post inteiro — no teste, um post sobre uma senhora sendo
despejada saiu como positivo porque a única palavra encontrada foi `home`.

O número 3 é o menor limiar em que uma frase claramente emocional ainda
passa: `"terrible trip, the hotel was awful and I hate the traffic"` encontra
exatamente 3 palavras, porque `trip`, `awful` e `traffic` não estão no ANEW.
Exigir 4 rejeitaria essa frase.

Os posts descartados são contados e reportados.

---

## Figura

Histograma das notas, com a faixa neutra sombreada e a média do ANEW marcada
como linha de referência. Histograma em vez de três barras porque mostra se
a opinião é concentrada ou dividida. O enunciado proíbe gráfico de pizza.

O número de posts descartados aparece na legenda, como resultado e não como
omissão.

---

## Verificação

Três frases de resultado conhecido, mais um teste do lematizador:

| entrada | esperado |
|---|---|
| `"Argentina is beautiful, I love the people and the food"` | positivo |
| `"terrible trip, the hotel was awful and I hate the traffic"` | negativo |
| `"the meeting starts at four"` | sem sinal |
| `caring` | vira `care`, não `car` |

---

## Limitações (vão para o slide)

- O algoritmo lê palavras soltas, não frases. "Despejada da sua casa"
  pontua igual a "amo minha casa".
- Não trata negação: `"not good"` pontua como `good`.
- O dicionário tem 1.034 palavras. Conhece `sad` e `grief`, mas não conhece
  `cry`, `tears` nem `die`.

---

## Bibliotecas

`requests` (API), `nltk` (lematizador), `pandas` (dados), `matplotlib`
(figura), `langdetect` (idioma). Instaladas no `.venv` existente.

---

## Fora de escopo

O classificador por LLM do capstone (o enunciado pede o método ANEW), as
dimensões `arousal` e `dominance` (descritas no notebook, mas não decidem a
classificação), e a montagem dos slides.
