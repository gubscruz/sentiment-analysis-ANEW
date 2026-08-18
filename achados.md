# O que o classificador acerta e o que ele erra

Investigação do comportamento do classificador sobre o corpus real: **2.880
posts baixados** do Mastodon, **905 confirmados em inglês**, dos quais **463
tinham palavras suficientes** para receber nota.

Todos os números vêm de `analise_classificador.py`, que roda sobre
`data/posts.csv` e não altera nada do algoritmo — só observa.

---

## Sucessos

### 1. A lematização recupera 33% mais palavras

| método | palavras encontradas |
|---|---|
| só casamento exato | 2.601 |
| com lematização | **3.450** (+33%) |

Palavras que só a lematização alcançou: `air`, `mountain`, `good`, `prairie`,
`flower`, `win`, `bird`, `watch`, `moment`, `cut`, `glacier`, `water`.

As reduções irregulares funcionam: `won` → `win`, `best` → `good`,
`fell` → `fall`, `fought` → `fight`.

### 2. A calibração muda o resultado por completo

| régua | resultado |
|---|---|
| corte ingênuo em 50 | **97% positivo** |
| faixa calibrada em 58 | 2% negativo · 37% neutro · 61% positivo |

Sem a calibração, o trabalho concluiria que praticamente todo mundo elogia a
Argentina — o que é composição do dicionário, não opinião das pessoas.

### 3. A verificação de idioma pega o que a API deixa passar

A etiqueta de idioma do Mastodon marcou como inglês **372 posts que não eram**.
Quase todos eram notícia em espanhol (*"Los desalojos sin juez ya son
mayoría"*) ou italiano (ANSA, Il Fatto Quotidiano). O `langdetect` derrubou
esses antes de qualquer palavra ser pontuada.

**Mas ele erra para o outro lado também.** O post *"Memories of Buenos Aires
for #SilentSunday #BuenosAires #Argentina #Travel"* é inglês e foi rejeitado:
num texto curto, os nomes próprios em espanhol dominam a detecção. Trocamos
alguns falsos positivos por alguns falsos negativos, e isso vale a pena porque
uma palavra espanhola pontuada com nota de inglês é um erro pior.

---

## Limitações

### 1. "Buenos Aires" injeta uma palavra positiva fantasma

**O achado mais grave.** O lematizador reduz `aires` → `air`, que existe no
ANEW com nota **71,9 (positiva)**.

| medida | valor |
|---|---|
| posts que recebem essa palavra | **164** |
| posts classificados **só** por causa dela | **17** |
| posição de `air` no ranking do corpus | **1º lugar**, com 164 aparições |

Todo post que menciona a capital argentina ganha de graça uma palavra positiva
que ninguém escreveu. E 17 posts só entraram no resultado porque o nome da
cidade doou a terceira palavra que faltava.

**Por que isso importa:** o problema não é o ANEW nem a lematização em si, é a
combinação dos dois com **nome próprio**. Qualquer projeto que analise uma
entidade cujo nome contenha uma palavra comum vai sofrer disso.

### 2. As hashtags escolhidas decidem a resposta

As três palavras mais frequentes do corpus são `air` (164), `nature` (157) e
`mountain` (128). As duas últimas vêm de `#patagonia`, uma das hashtags que
escolhemos para buscar.

Posts de natureza e turismo são quase sempre elogiosos. Ou seja: **parte do
"61% positivo" foi decidida na hora em que escolhemos as hashtags**, não pelo
que as pessoas pensam da Argentina. Trocar `#patagonia` por `#mileipresidente`
provavelmente daria outro retrato.

### 3. Diluição: um massacre classificado como neutro

Este post continua saindo **NEUTRO (51,2)**:

> *"Today in Labor History January 16, 1919: Semana Tragica (Tragic week) ended
> on this date in Buenos Aires. The authorities **slaughtered** as many as 700
> workers..."*

| lado | palavras encontradas |
|---|---|
| negativas (8) | `funeral`=16 · `slaughter`=19 · `assault`=23 · `massacre`=26 · `burn`=31 · `fire`=37 · `gun`=39 · `fight`=43 |
| positivas (4) | `air`=72 · `people`=83 · `good`=85 · `car`=88 |

Oito palavras sobre um massacre, e a média as neutraliza. Note que o `air` é o
fantasma do item 1, e que `good` veio de `goods` (mercadorias) e `car` de
`cars` — num texto sobre bens destruídos e carros queimados.

### 4. Posts longos ficam mais perto do meio

| palavras no post | distância média do centro |
|---|---|
| 3 a 4 | 14,4 |
| 5 a 8 | 15,0 |
| 9 ou mais | **11,1** |

**Correção honesta:** no corpus anterior isso parecia uma escada perfeita, e eu
descrevi como se cada palavra a mais aproximasse do centro. Não é. Posts de 5 a
8 palavras estão até um pouco mais longe do centro que os de 3 a 4. O que se
sustenta é o extremo: **posts com 9 ou mais palavras ficam claramente mais perto
do meio**, e é por isso que o post do massacre, com 19 palavras, saiu neutro.

### 5. Uma palavra decide o post em 23% dos casos

Removendo de cada post apenas a **palavra mais extrema**, **107 de 463 posts
(23%) mudam de classe**.

| post | mudança |
|---|---|
| *"Argentina commemorates the **death** of General José de San Martín"* | sem `death`(18): neutro → positivo |
| *"Lionel Messi Says He May Not Play Much Longer After Father's **Death**"* | sem `death`(18): neutro → positivo |
| *"My ISP is doing the most bizarre website **failure**..."* | sem `failure`(19): negativo → neutro |

Os dois primeiros são o mesmo problema: `death` descreve o **assunto**, não a
opinião. Uma homenagem a San Martín e uma notícia sobre o luto de Messi não são
posts negativos sobre a Argentina.

### 6. `goods` vira `good`

A lematização junta palavras que só coincidem na forma: `goods` (mercadorias)
vira `good`, o adjetivo positivo com nota 85. São palavras diferentes. O mesmo
colapso atinge `party` (festa × partido político), `bar`, `kind`, `present`,
`spring` e `watch`.

### 7. Negação não é tratada — mas o impacto é pequeno

Só **10 de 463 posts (2%)** têm negação antes de uma palavra do ANEW. Quando
acontece, o efeito é literal: *"no time"* faz `time` contar como 60, e
*"not lie"* faz `lie` contar como 32.

### 8. O ANEW enxerga 5,5% do texto

De 62.545 tokens no corpus, apenas **3.450 estão no dicionário (5,5%)**.

| palavras do ANEW no post | posts |
|---|---|
| 0 | 69 |
| 1 | 185 |
| 2 | 188 |
| 3 ou mais (classificados) | 463 |

**Pouco mais da metade dos posts (51%) chega a ser classificada.**

### 9. Média ou mediana muda 17% dos casos

Trocando a média pela mediana, **79 de 463 posts (17%) mudam de classe**. A
decisão de como combinar as notas — que o enunciado deixa em aberto — tem peso
comparável ao da própria calibração.

---

## O que levar para o slide

O achado do **"Buenos Aires" → `air`** é o mais concreto e inesperado: mostra
que o problema não estava no dicionário nem no código, mas na interação dos dois
com nome próprio.

O **massacre classificado como neutro** resume as limitações 3, 4 e 5 de uma vez
só, num exemplo que ninguém esquece.

---

## Correções que estes achados sugerem

Nenhuma foi aplicada — são consequências a decidir.

1. **Ignorar o nome da entidade e da cidade antes de pontuar.** Remove o `air`
   fantasma. Custo: 17 posts saem do resultado.
2. **Usar mediana em vez de média.** Reduz a alavancagem de uma palavra
   extrema. Custo: muda 17% das classificações.
3. **Diversificar as hashtags de busca**, ou reportar o resultado separado por
   hashtag, para que a escolha da busca não decida a resposta.
4. **Separar palavra de assunto de palavra de opinião** — `death` num obituário
   não é crítica à Argentina.
5. **Filtrar posts de veículo de notícia.** Boa parte do corpus é manchete, e o
   método pressupõe alguém expressando sentimento próprio.
