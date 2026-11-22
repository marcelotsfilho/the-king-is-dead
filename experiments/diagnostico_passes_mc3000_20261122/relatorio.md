# Diagnóstico de passes e resoluções — MC3000 x Minimax 1

## Protocolo

Repeti 10 partidas (seeds 0–9) com Monte Carlo de 3.000 simulações contra Minimax 1 com alfa-beta ativado. O primeiro jogador e o lado do MC foram balanceados. O experimento executou o modelo do jogo sem renderizar o Pygame e registrou todas as ações, contagem de cartas nas mãos e resoluções da trilha.

O jogo não passa simultaneamente: os jogadores passam em turnos sucessivos. Uma região é resolvida quando o segundo passe consecutivo é aplicado; se um jogador joga uma carta entre os passes, a sequência é reiniciada.

## Resultado agregado

- 10/10 partidas foram concluídas; resultado: 5 vitórias do MC e 5 do Minimax.
- As 10 partidas tiveram 80 resoluções de regiões provocadas por passes consecutivos: todas as 8 regiões por partida.
- Foram registrados 207 passes individuais: 101 do MC e 106 do Minimax. Houve 80 pares consecutivos que resolveram região; os demais passes foram interrompidos por uma jogada de carta.
- Ambos os agentes usaram todas as 8 cartas em cada partida (80 cartas por algoritmo no total).
- O MC passou 101 vezes e **em nenhuma delas ainda tinha cartas na mão**. Em todas as 10 partidas, ele usou suas 8 cartas antes da primeira resolução de região.
- O Minimax passou 106 vezes; em 45 delas ainda tinha cartas na mão.
- Em 9 das 10 partidas, a primeira região foi resolvida quando o MC já estava sem cartas e o Minimax ainda tinha de 2 a 6 cartas. Na seed 6, ambos já estavam sem cartas na primeira resolução.
- Ao longo das 80 resoluções, 19 aconteceram com alguma carta ainda na mão de pelo menos um jogador. **Nenhuma** aconteceu enquanto os dois jogadores ainda tinham cartas.

## Primeira resolução por seed

| Seed | Região | Cartas MC restantes | Cartas Minimax restantes | Resoluções com cartas restantes na partida |
|---:|---|---:|---:|---:|
| 0 | Strathclyde | 0 | 2 | 1 |
| 1 | Devon | 0 | 3 | 3 |
| 2 | Devon | 0 | 2 | 3 |
| 3 | Northumbria | 0 | 3 | 1 |
| 4 | Strathclyde | 0 | 6 | 4 |
| 5 | Essex | 0 | 5 | 2 |
| 6 | Devon | 0 | 0 | 0 |
| 7 | Devon | 0 | 3 | 1 |
| 8 | Moray | 0 | 3 | 1 |
| 9 | Northumbria | 0 | 2 | 3 |

## Leitura do padrão

A suspeita está confirmada para estas partidas: **o Monte Carlo não escolheu passar enquanto ainda tinha cartas**. A primeira sequência de passes que resolveu uma região só aconteceu depois que o MC usou suas oito cartas. O Minimax, por outro lado, às vezes passava com cartas restantes; isso isoladamente não resolvia a região, pois o MC jogava uma carta e reiniciava a sequência.

Portanto, passes ocorreram nos testes, mas não no momento em que você esperava: as resoluções por passes apareceram depois de o MC esgotar a própria mão. Em 9/10 partidas, o adversário ainda guardava cartas quando a primeira região foi resolvida. A amostra não indica resolução com ambos ainda tendo cartas.

## Arquivos e limites

- `partidas.csv`: totais de passes, pares, resoluções, cartas usadas, tempos e vencedores por seed.
- `eventos.csv`: histórico ação a ação, incluindo ator, sequência de passes, região resolvida e cartas restantes nas duas mãos.
- `../torneio_mc_alfa_beta.py`: script reproduzível que gera os registros.

Este resultado descreve MC3000 contra Minimax 1 com alfa-beta nesta configuração. Não prova que o MC nunca passará com cartas em outras posições, parâmetros ou seeds; contudo, isso não ocorreu em nenhuma das 10 partidas medidas.
