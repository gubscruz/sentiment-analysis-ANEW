# O que o classificador acerta e o que ele erra

Investigação do comportamento do classificador sobre um corpus de **517 posts
em inglês** que mencionam Argentina, Buenos Aires ou Patagônia.

Todos os números vêm de `analise_classificador.py`, que roda sobre
`data/posts_exemplo.csv` e não altera nada do algoritmo — só observa.

> **Ressalva:** o corpus é do Mastodon, coletado enquanto o acesso ao Bluesky
> não estava disponível. Os padrões de falha valem para qualquer corpus; as
> proporções exatas vão mudar.

---

## Sucessos

### 1. A lematização recupera 36% mais palavras

| método | palavras encontradas |
|---|---|
| só casamento exato | 1.116 |
| com lematização | **1.523** (+36%) |

Palavras que só a lematização alcançou: `win`, `good`, `moment`, `child`,
`time`, `flag`, `fall`, `insult`, `cut`, `present`.

As reduções irregulares funcionam corretamente: `won` → `win`, `best` → `good`,
`fell` → `fall`, `fought` → `fight`, `feet` → `foot`.

### 2. A calibração muda o resultado por completo

| régua | resultado |
|---|---|
| corte ingênuo em 50 | negativo 3% · **positivo 96%** |
| faixa calibrada em 58 | negativo 2% · neutro 49% · positivo 48% |

Sem a calibração, o trabalho concluiria que 96% dos posts sobre a Argentina são
positivos — o que é composição do dicionário, não opinião das pessoas.

### 3. O filtro de palavras remove o lixo

Dos 517 posts, **112 (22%) não têm nenhuma palavra do ANEW** e 120 têm apenas
uma. O filtro de 3 palavras derruba os casos em que uma palavra isolada
decidiria o post inteiro.

---

## Limitações

### 1. "Buenos Aires" injeta uma palavra positiva fantasma

**O achado mais grave.** O lematizador reduz `aires` → `air`, que existe no
ANEW com nota **71,9 (positiva)**.

| medida | valor |
|---|---|
| posts em que isso acontece | **177** |
| posts do corpus que citam "Aires" | 251 de 517 (48%) |
| posts classificados **só** por causa dessa palavra | **18** |

Ou seja: todo post que menciona a capital argentina ganha de graça uma palavra
positiva que ninguém escreveu. E 18 posts só entraram no resultado porque o
nome da cidade doou a terceira palavra que faltava.

`air` é, disparado, a palavra mais frequente do corpus — 177 ocorrências contra
66 da segunda colocada (`news`).

**Por que isso importa:** o problema não é o ANEW nem a lematização em si, é a
combinação dos dois com **nome próprio**. Qualquer projeto que analise uma
entidade cujo nome contenha uma palavra comum vai sofrer disso.

### 2. Diluição: um massacre classificado como neutro

Este post foi classificado **NEUTRO (51,2)**:

> *"Today in Labor History January 16, 1919: Semana Tragica (Tragic week) ended
> on this date in Buenos Aires. The authorities **slaughtered** as many as 700
> workers..."*

| lado | palavras encontradas |
|---|---|
| negativas (8) | `funeral`=16 · `slaughter`=19 · `assault`=23 · `massacre`=26 · `burn`=31 · `fire`=37 · `gun`=39 · `fight`=43 |
| positivas (4) | `air`=72 · `people`=83 · `good`=85 · `car`=88 |

Oito palavras sobre um massacre, e a média as neutraliza. Note que o `air` é o
fantasma do item 1, e que `good` veio de `goods` (mercadorias) e `car` de `cars`
— num texto sobre bens destruídos e carros queimados.

### 3. Quanto mais palavras, pior — não melhor

A intuição diz que mais palavras dão mais precisão. O corpus mostra o contrário:

| palavras no post | distância média do centro da faixa |
|---|---|
| 3 a 4 | 12,3 |
| 5 a 8 | 11,7 |
| 9 ou mais | **9,9** |

Posts longos convergem para a média do dicionário. Eles ficam "neutros" por
**diluição**, não por serem equilibrados. É por isso que o post do massacre,
com 19 palavras, saiu neutro.

Outro exemplo, com 19 palavras e contendo `war`=24 e `bloody`=33, saiu
**positivo (74,9)**.

### 4. Uma palavra decide o post em 27% dos casos

Removendo de cada post apenas a **palavra mais extrema**, **51 de 185 posts
(27%) mudam de classe**.

| post | mudança |
|---|---|
| *"⚡ Argentina commemorates the **death** of General José de San Martín"* | sem `death`(18): neutro → positivo |
| *"Un bar nello storico **cimitero**..."* | sem `cemetery`(30): neutro → positivo |
| *"My ISP is doing the most bizarre website **failure**..."* | sem `failure`(19): negativo → neutro |

A classificação de um quarto dos posts está pendurada numa única palavra.

### 5. Palavra de assunto pontua como se fosse opinião

O ANEW mede o afeto da palavra isolada. Ele não distingue "o post é sobre um
tema triste" de "o autor está triste".

| palavra | ocorrências | nota | empurra o post para |
|---|---|---|---|
| `death` | 19 | 18,3 | negativo |
| `home` | 13 | 89,7 | positivo |
| `family` | 12 | 86,7 | positivo |
| `war` | 7 | 23,6 | negativo |
| `party` | 4 | 89,1 | positivo |
| `funeral` | 3 | 15,8 | negativo |

O post que *"comemora"* (`commemorates`) San Martín contém `death` e por isso
tende ao negativo — quando o texto é uma homenagem.

### 6. `goods` vira `good`

A lematização junta palavras que só coincidem na forma: `goods` (mercadorias)
vira `good`, o adjetivo positivo com nota 85. São palavras diferentes. O mesmo
tipo de colapso atinge `party` (festa × partido político), `bar`, `kind`,
`present`, `spring` e `watch`.

### 7. Negação não é tratada — mas o impacto é pequeno

Só **7 de 185 posts (3%)** têm negação antes de uma palavra do ANEW. Menor do
que se esperaria, mas o efeito é literal quando acontece:

| trecho | como pontua |
|---|---|
| *"**not guilty**"* | `guilty` conta como 30 (negativo) |
| *"**no time**"* | `time` conta como 60 |
| *"**not lie**"* | `lie` conta como 32 (negativo) |

*"not guilty"* — uma absolvição — pontua como culpa.

### 8. O ANEW enxerga 3,7% do texto

De 41.509 tokens no corpus, apenas **1.523 estão no dicionário (3,7%)**. O resto
são artigos, preposições, nomes próprios, verbos comuns e todo o vocabulário que
as 1.034 palavras do ANEW não cobrem.

| palavras do ANEW no post | posts |
|---|---|
| 0 | 112 |
| 1 | 120 |
| 2 | 100 |
| 3 ou mais (classificados) | 185 |

**Só 35% dos posts chegam a ser classificados.**

### 9. A escolha de média em vez de mediana muda 18% dos casos

Trocando a média pela mediana, **34 de 185 posts (18%) mudam de classe**. A
decisão de como combinar as notas — que o enunciado deixa em aberto — tem peso
comparável ao da própria calibração.

---

## O que levar para o slide

Se couber apenas um achado, use o do **"Buenos Aires" → `air`**: é concreto,
inesperado, e mostra que o problema não estava no dicionário nem no código, mas
na interação entre os dois com nome próprio.

Se couber um segundo, use o **massacre classificado como neutro**: ele resume as
limitações 2, 3 e 5 de uma vez só, num exemplo que ninguém esquece.

---

## Correções que estes achados sugerem

Nenhuma foi aplicada ainda — são consequências a decidir.

1. **Ignorar o nome da entidade e da cidade antes de pontuar.** Remove o `air`
   fantasma. Custo: 18 posts saem do resultado.
2. **Usar mediana em vez de média.** Reduz a alavancagem de uma palavra
   extrema. Custo: muda 18% das classificações, precisa ser justificado.
3. **Limitar o peso de posts muito longos**, ou reportar a distribuição por
   tamanho de post em vez de uma classificação única.
4. **Filtrar posts de veículo de notícia.** Boa parte do corpus é manchete, não
   opinião — e o método pressupõe alguém expressando sentimento.
