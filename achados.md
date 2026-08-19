# O que o classificador acerta e o que ele erra

Investigação do comportamento do classificador sobre **2.400 posts baixados**
do Mastodon pela hashtag `#argentina`, dos quais **632 confirmados em inglês**
e **308 com palavras suficientes** para receber nota.

Os números vêm de `analise_classificador.py`, que roda sobre `data/posts.csv`
e não altera nada do algoritmo — só observa.

---

## Um erro de método que corrigimos no meio do caminho

A primeira versão buscava `#argentina`, `#buenosaires`, `#argentine` e
`#patagonia`, para conseguir mais posts em inglês. Isso estava **errado**: o
enunciado pede uma entidade, e Buenos Aires e Patagônia são outras entidades.

O estrago era mensurável. Naquele corpus, `nature` (157) e `mountain` (128)
estavam entre as três palavras mais frequentes, vindas de posts de turismo na
Patagônia — que são quase sempre elogiosos. E `air` aparecia em 164 posts em
vez dos 34 de agora.

Voltamos para `#argentina` apenas. Os números deste documento são os do corpus
corrigido.

---

## Sucessos

### 1. A lematização recupera 25% mais palavras

| método | palavras encontradas |
|---|---|
| só casamento exato | 1.563 |
| com lematização | **1.954** (+25%) |

As reduções irregulares funcionam: `won` → `win`, `best` → `good`,
`fell` → `fall`, `fought` → `fight`.

### 2. A calibração muda o resultado por completo

| régua | resultado |
|---|---|
| corte ingênuo em 50 | **96% positivo** |
| faixa calibrada em 58 | 2% negativo · 40% neutro · 56% positivo |

Sem a calibração, o trabalho concluiria que quase todo mundo elogia a
Argentina — o que é composição do dicionário, não opinião das pessoas.

### 3. A verificação de idioma pega o que a API deixa passar

A etiqueta do Mastodon marcou como inglês **282 posts que não eram**, quase
todos notícia em espanhol ou italiano.

**Mas ela erra para o outro lado também.** O post *"Memories of Buenos Aires
for #SilentSunday"* é inglês e foi rejeitado: num texto curto, os nomes
próprios em espanhol dominam a detecção. Trocamos alguns falsos positivos por
alguns falsos negativos, e vale a pena, porque uma palavra espanhola pontuada
com nota de inglês é o erro pior.

---

## Limitações

### 1. Metade do corpus é futebol, e futebol é positivo por vocabulário

**O achado mais importante para interpretar o resultado.**

| palavra | vezes | nota |
|---|---|---|
| `world` | 273 | 74 |
| `news` | 113 | 60 |
| `social` | 107 | 78 |
| `win` | 65 | **95** |
| `champion` | 32 | **96** |

**321 dos 632 posts (50%)** citam futebol — Copa do Mundo, Messi, campeonato.
E o vocabulário do futebol é elogioso por construção: `win` vale 95 e
`champion` vale 96, quase o topo da escala.

Ou seja: boa parte do “56% positivo” não é gente elogiando a Argentina como
país. É gente narrando que a Argentina **ganhou um jogo**. O método não
distingue as duas coisas.

### 2. Uma palavra decide o post em 29% dos casos

Removendo de cada post apenas a **palavra mais extrema**, **92 de 308 posts
(29%) mudam de classe**. A classificação de quase um terço do corpus está
pendurada numa única palavra.

### 3. O nome da cidade vira palavra com nota

O lematizador reduz `aires` → `air`, que existe no ANEW valendo **71,9
(positiva)**. Isso acontece em **34 posts**, e **8 deles** só entraram no
resultado porque essa palavra completou o mínimo de três.

O problema não é o ANEW nem a lematização em si, é a combinação dos dois com
**nome próprio**. Vale para qualquer entidade cujo nome contenha uma palavra
comum.

### 4. Palavra de assunto pontua como se fosse opinião

O ANEW mede o afeto da palavra isolada. Ele não separa “o post é sobre um tema
triste” de “o autor está triste”.

O caso mais claro: um post que **homenageia** o General San Martín contém
`death` (18) e por isso tende ao negativo. Uma notícia sobre o luto de Messi
cai na mesma armadilha.

### 5. Posts longos ficam mais perto do meio

| palavras no post | distância média do centro |
|---|---|
| 3 a 4 | 13,4 |
| 5 a 8 | 12,7 |
| 9 ou mais | **9,2** |

Posts longos convergem para a média do dicionário: ficam “neutros” por
diluição, não por serem equilibrados.

*(Ressalva: no corpus anterior essa escada não era monotônica. Com 23 posts
apenas na faixa de 9 ou mais, o número da última linha é frágil.)*

### 6. `goods` vira `good`

A lematização junta palavras que só coincidem na forma: `goods` (mercadorias)
vira `good`, o adjetivo positivo com nota 85. O mesmo colapso atinge `party`
(festa × partido político), `bar`, `kind`, `present`, `spring` e `watch`.

### 7. Negação não é tratada — mas o impacto é pequeno

Só **7 de 308 posts (2%)** têm negação antes de uma palavra do ANEW. Quando
acontece, o efeito é literal: *"no time"* faz `time` contar como 60.

### 8. O ANEW enxerga 5,4% do texto

De 36.068 tokens, apenas **1.954 estão no dicionário**.

| palavras do ANEW no post | posts |
|---|---|
| 0 | 103 |
| 1 | 110 |
| 2 | 111 |
| 3 ou mais (classificados) | 308 |

**Menos da metade dos posts (48%) chega a ser classificada.**

O caso que motivou a regra de três palavras é este, e está no slide 2:

> *"An elderly lady of the indigenous Humahuaca community in Jujuy **cries** as
> the puppet regime in Argentina **evicts** her from her **home** and land..."*

De 63 palavras, o ANEW reconheceu **uma**: `home` = 90. Sem a regra, o post
sairia como positivo. `cries`, `evicts` e `protests` não estão no dicionário —
nem `cry`, `tears`, `loss` ou `die`.

### 9. Média ou mediana muda 20% dos casos

Trocando a média pela mediana, **62 de 308 posts (20%) mudam de classe**. A
decisão de como combinar as notas — que o enunciado deixa em aberto — pesa
tanto quanto a própria calibração.

---

## Correções que estes achados sugerem

Nenhuma foi aplicada — cada uma muda o resultado e precisa ser decidida.

1. **Reportar futebol à parte.** Metade do corpus é jogo, e “ganhamos” não é
   opinião sobre o país. Separar os dois daria dois retratos mais honestos que
   um só.
2. **Ignorar o nome da entidade e da cidade antes de pontuar.** Remove o `air`
   fantasma. Custo: 8 posts saem do resultado.
3. **Usar mediana em vez de média.** Reduz a alavancagem de uma palavra
   extrema. Custo: muda 20% das classificações.
4. **Separar palavra de assunto de palavra de opinião** — `death` num obituário
   não é crítica à Argentina.
5. **Trocar a hashtag por busca em texto livre.** Hoje só encontramos quem
   escreveu `#argentina`, o que já é um recorte. O `baixar_bluesky.py` faz isso,
   mas depende de uma credencial que não temos.
