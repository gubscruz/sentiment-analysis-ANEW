# Análise de sentimento sobre "Argentina" com ANEW — conteúdo para o relatório

Documento de referência: tudo que foi decidido, testado e descoberto.
Serve de matéria-prima para os dois slides.

**Entidade:** Argentina · **Rede social:** Bluesky · **Data:** 2026-08-17

---

## 1. O que o enunciado pede

| Etapa | Exigência |
|---|---|
| Entidade | escolher uma, de preferência conhecida e não polêmica |
| Baixar posts | **escrever o programa que baixa** — API ou webscraping |
| Sentimento | usar o **ANEW**, ler o paper, lidar com inconsistências dele |
| Combinar | inventar uma forma de virar nota de palavra em decisão de post |
| Apresentar | **2 slides**: como funciona o algoritmo + figura de resultado |

Duas exigências explícitas que orientaram o projeto:

> *"There might be inconsistencies in ANEW. You are expected to figure out how
> to deal with them."*

> *"Although we have an affective rating for each word, we do not have a rating
> for the whole post. You are expected to figure out a possible way to combine
> this information."*

Proibição explícita: **nunca usar gráfico de pizza.**

---

## 2. Escolha da rede social — o que foi testado

Todas as opções foram testadas com requisição real antes de decidir.

| Fonte | Resultado | Veredito |
|---|---|---|
| Bluesky, busca sem login | HTTP 403 | inviável |
| **Bluesky, busca com login** | **funciona** | **escolhido** |
| Reddit, API `.json` | HTTP 403 | inviável |
| Reddit, scraping `old.reddit` | HTTP 302, zero resultados | inviável |
| Mastodon, busca por texto livre | HTTP 200 mas resposta vazia | inviável |
| Mastodon, hashtag | funciona, mas só 16% em inglês | descartado |

**Conclusão que vale registrar:** webscraping **não** é mais fácil que API.
O Reddit bloqueia as duas portas, e o site do Bluesky é renderizado em
JavaScript, o que exigiria Selenium — mais lento e mais frágil.

**Como o Bluesky é acessado:** conta grátis + *app password* →
`com.atproto.server.createSession` devolve um token →
`app.bsky.feed.searchPosts` com `q=Argentina` e `lang=en` → paginar pelo cursor.

**Problema encontrado:** a etiqueta de idioma da API não é confiável. No teste,
posts em espanhol (*"Un conductor daña Pampa del Leoncito"*) e italiano
(*"Diventa mamma a 62 anni"*) vieram marcados como inglês. Como o ANEW é
dicionário de inglês, o código confere o idioma por conta própria.

---

## 3. O dicionário ANEW

### O que é

Bradley & Lang (1999) pediram a muitas pessoas que avaliassem palavras em
inglês em três dimensões. Cada palavra ficou com a média das avaliações.

| dimensão | o que mede |
|---|---|
| **Pleasure** (valência) | quão agradável ou desagradável — **é a que usamos** |
| Arousal (ativação) | quão calmo ou agitado |
| Dominance (domínio) | quanto de controle a palavra transmite |

Usamos só `pleasure`, porque a pergunta do projeto é "positivo ou negativo",
que é exatamente o eixo da valência. As outras duas são descritas no notebook
para mostrar entendimento do paper, mas não decidem a classificação.

### O arquivo

`anew.csv`, de `https://osf.io/download/cq6ng/`. Colunas `term`, `pleasure`,
`arousal`, `dominance`.

| propriedade | valor |
|---|---|
| palavras | 1.034 |
| duplicatas | nenhuma |
| termos com espaço, hífen ou maiúscula | nenhum |
| `pleasure` mínimo | 14,2 (`rape`) |
| `pleasure` máximo | 100,0 (`triumphant`) |
| **`pleasure` média** | **58,4** |
| `pleasure` mediana | 60,0 |
| `pleasure` desvio-padrão | 22,6 |

### As três inconsistências encontradas

**1. A escala do arquivo não é a escala do paper.**
O paper descreve escala de 1 a 9, com meio em 5. O CSV do OSF está de 0 a 100,
com meio em 50. Quem lê o paper e usa o arquivo direto erra por um fator de
aproximadamente onze.
*Tratamento:* trabalhar na escala 0–100 e documentar a diferença.

**2. O dicionário puxa para o positivo.**
645 das 1.034 palavras (62%) estão acima de 50. A média é 58,4, oito pontos
acima do meio da escala.
*Consequência medida:* cortando em 50, **93% dos posts reais saíram positivos**
— isso é composição do dicionário, não opinião sobre a Argentina.
*Tratamento:* calibrar o limiar na média do próprio ANEW (seção 5).

**3. Palavras ambíguas têm nota única.**
`bar` (72,8), `kind` (86,1), `present` (78,8), `spring` (88,0), `watch` (65,5).
*Caso real:* um post sobre *"the ruling La Libertad Avanza **party**"* saiu
positivo porque `party` vale 89 — mas ali significa partido político.
*Tratamento:* não tem conserto dentro do método. O mínimo de palavras reduz o
dano; o resto vira limitação declarada.

---

## 4. O algoritmo

Para cada post:

1. **Limpar** — tirar URL, menção `@` e HTML. Hashtag colada é separada pelas
   maiúsculas (`#ClassWar` → `class war`) em vez de descartada.
2. **Separar em palavras** e passar para minúsculas.
3. **Reduzir à forma base** com o lematizador WordNet do NLTK.
4. **Procurar** cada forma base no ANEW.
5. **Pontuar** — a nota do post é a média do `pleasure` das palavras distintas
   encontradas.

```
nota(post) = média do pleasure das palavras distintas encontradas
```

### Por que lematizar

O dicionário tem `love` e `hate`, mas os posts escrevem `loved` e `hating`.
Sem reduzir à forma base, essas palavras se perdem.

**Cortar sufixo à mão não serve.** No protótipo, `caring` virou `car`
(nota 88, bem positiva) em vez de `care`. O NLTK também erra sozinho:
`hating` vira `hat` (que existe no ANEW!) em vez de `hate`.

**Regra adotada:** casamento exato primeiro; se não achar, entre os lemas que o
WordNet gera, usar **o mais longo que esteja no dicionário**. O critério do mais
longo evita a redução agressiva demais que produz `hat`.

---

## 5. Classificação em três classes

| nota do post | classe |
|---|---|
| abaixo de 47 | negativo |
| entre 47 e 70 | neutro |
| acima de 70 | positivo |

### Por que a faixa não é centrada em 50

A média do próprio ANEW é 58, não 50. A faixa é centrada em 58, com largura de
um desvio-padrão do dicionário.

A leitura fica: **"positivo" significa que o post usa palavras mais agradáveis
que a palavra média do dicionário.** É uma régua relativa e explicável.

Efeito medido nos posts reais: de "93% positivo" (corte ingênuo em 50) para uma
distribuição equilibrada.

### Por que o mínimo de 3 palavras

Post que bate em menos de 3 palavras distintas do ANEW não é classificado.
Com poucas palavras, uma palavra isolada decide o post inteiro.

**O caso que motivou a regra.** Este post de 63 palavras saiu **positivo (89,7)**:

> *"An elderly lady of the indigenous Humahuaca community in Jujuy **cries** as
> the ... regime in Argentina **evicts** her from her **home** and land."*

O ANEW encontrou **uma única palavra**: `home` = 90. Os termos negativos
(`cries`, `elderly`, `evicts`, `protests`) não constam no dicionário. E `cry`,
`tears`, `loss` e `die` também não constam.

**Por que 3 e não 4.** Três é o menor limiar em que uma frase claramente
emocional ainda passa. A frase de teste *"terrible trip, the hotel was awful and
I hate the traffic"* encontra exatamente 3 palavras (`terrible`, `hotel`,
`hate`), porque `trip`, `awful` e `traffic` não estão no ANEW. Exigir 4
rejeitaria uma frase que qualquer leitor humano classifica como negativa.

**Palavras distintas, não ocorrências.** O post do partido político encontrou
`party` duas vezes — são duas ocorrências de uma palavra só.

---

## 6. A figura

**Histograma** das notas dos posts:

- eixo horizontal: nota de agrado do post, de 0 a 100
- eixo vertical: quantos posts caíram em cada faixa de 5 pontos
- cor da barra: vermelho negativo, cinza neutro, azul positivo
- linha tracejada: a média do ANEW (58), a régua de comparação
- legenda: contagem e percentual de cada classe
- subtítulo: quantos posts foram classificados e quantos foram baixados

**Por que histograma e não três barras.** Três barras mostram só o placar final.
O histograma mostra o **formato** da distribuição — se a opinião é concentrada
num ponto ou dividida em dois grupos — e deixa a calibração visível na figura.

**Por que a paleta é essa.** Vermelho e azul são polos opostos com cinza neutro
no meio (paleta divergente, adequada para polaridade). O par foi validado para
daltonismo: ΔE 23,6 em protanopia e 31,9 em visão normal, bem acima do piso.

Os posts descartados aparecem na legenda como número, não são omitidos.

---

## 7. Limitações — vão para o slide

- **O algoritmo lê palavras soltas, não frases.** Não existe noção de que
  `evicts` age sobre `home`. "Despejada da sua casa" pontua igual a "amo minha
  casa".
- **Não trata negação.** `"not good"` pontua como `good`.
- **O dicionário é pequeno: 1.034 palavras.** Conhece `sad`, `grief` e `death`,
  mas não conhece `cry`, `tears`, `loss` nem `die`.
- **Palavras ambíguas têm nota única.** `party` vale 89 mesmo significando
  partido político.

---

## 8. Rascunho dos dois slides

### Slide 1 — como funciona

1. Baixei N posts em inglês sobre "Argentina" no Bluesky, via API autenticada.
2. O ANEW dá a cada palavra uma nota de agrado de 0 a 100. A nota do post é a
   **média** das palavras dele que estão no dicionário.
3. **O detalhe que muda tudo:** a média do próprio ANEW é 58, não 50. Comparar
   contra 50 rotula 93% dos posts como positivos. Comparei contra 58.
4. Post com menos de 3 palavras no dicionário foi descartado — uma palavra
   isolada decide errado (exemplo do `home`).

O item 3 é o ponto mais interessante do trabalho e deve ficar em destaque.

### Slide 2 — resultado

O histograma, sozinho, com legenda auto-suficiente.

---

## 9. Estado do código

| arquivo | o que faz | estado |
|---|---|---|
| `sentimento.py` | limpeza, lematização, pontuação, classificação | pronto |
| `teste_sentimento.py` | 9 testes de verificação | **todos passam** |
| `figura.py` | gera o histograma | rascunho, com defeito de layout |
| `data/anew.csv` | dicionário, 1.034 palavras | baixado |
| `data/posts_exemplo.csv` | 94 posts do Mastodon | **provisório** |

**Números provisórios.** Tudo que veio da amostra do Mastodon vai mudar quando
os posts do Bluesky entrarem. Os números do ANEW (58,4 / 22,6 / 1.034) são
definitivos.

---

## 10. O que falta

1. **Você:** criar conta grátis no bsky.app e gerar uma app password em
   *Settings → Privacy and Security → App Passwords*. Não usar a senha normal.
2. Escrever o código que baixa do Bluesky.
3. Rodar com dados reais e medir o aproveitamento. **Risco conhecido:** posts do
   Bluesky têm limite de 300 caracteres contra 500 do Mastodon, então podem
   render menos palavras do ANEW por post. Se o aproveitamento for ruim, o
   limiar de 3 precisa ser revisto com os números na mão.
4. Corrigir o layout da figura (o subtítulo colide com o título).
5. Montar os dois slides e exportar em PDF.
