# Monte Carlo contra Minimax 1

Protocolo com 10 partidas completas, seeds 0 a 9. O jogador inicial do Monte Carlo alterna entre partidas. Minimax usa profundidade 1 sem alfa-beta. Monte Carlo usa 100 simulações por decisão e semente de sorteio fixa derivada da seed da partida.

Os tempos de decisão são medidos diretamente ao redor da chamada do agente. A duração da partida exclui setup, inicialização e apresentação gráfica do Pygame.

- Vitórias do Monte Carlo: 9/10
- Vitórias do Minimax 1: 1/10
- Média de tempo por decisão do Monte Carlo: 0.279 s
- Média de tempo por decisão do Minimax 1: 0.537 s
- Média de duração das partidas: 15.187 s
- Mediana de duração: 15.037 s
- Duração mínima e máxima: 13.018 s / 19.276 s

## Resultados por seed

| Seed | Monte Carlo joga como | Vencedor | Turnos | Decisões MC | Tempo médio MC (s) | Decisões Minimax | Tempo médio Minimax (s) | Duração (s) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | Jogador 1 | Monte Carlo | 36 | 18 | 0.266 | 18 | 0.563 | 14.938 |
| 1 | Jogador 2 | Monte Carlo | 41 | 20 | 0.299 | 21 | 0.438 | 15.185 |
| 2 | Jogador 1 | Monte Carlo | 34 | 17 | 0.265 | 17 | 0.528 | 13.480 |
| 3 | Jogador 2 | Monte Carlo | 35 | 17 | 0.267 | 18 | 0.491 | 13.390 |
| 4 | Jogador 1 | Monte Carlo | 40 | 20 | 0.295 | 20 | 0.356 | 13.018 |
| 5 | Jogador 2 | Minimax 1 | 37 | 18 | 0.284 | 19 | 0.653 | 17.524 |
| 6 | Jogador 1 | Monte Carlo | 36 | 18 | 0.273 | 18 | 0.452 | 13.054 |
| 7 | Jogador 2 | Monte Carlo | 37 | 18 | 0.291 | 19 | 0.612 | 16.868 |
| 8 | Jogador 1 | Monte Carlo | 38 | 19 | 0.291 | 19 | 0.724 | 19.276 |
| 9 | Jogador 2 | Monte Carlo | 37 | 18 | 0.258 | 19 | 0.552 | 15.135 |

## Interpretação

Resultado observado: Monte Carlo venceu 9 e Minimax 1 venceu 1 partidas. A amostra alterna o jogador inicial, mas dez partidas ainda são uma bateria exploratória. O tempo médio por decisão é calculado sobre todas as decisões daquele algoritmo nas dez partidas.

CSV com medições por partida: partidas.csv.
