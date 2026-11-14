# Diário automático de experimentos

Este arquivo é gerado pelo executor. Os dados completos estão em results.csv.

## Cenário e protocolo

Cenário: reduzido; seed: não se aplica; bateria: ambas; profundidades: [1, 2, 3]; repetições: 3; algoritmos: ['minimax', 'alfa_beta']. Plano desta invocação: 36 decisões. Estado: 2b4f5cec2d428c7a5f703fc4a86661a703215edb942382057d6b0d8a297216cf. Cenário sintético de validação: reserva vazia, um escocês em Moray, um galês em Gwynedd e uma Assemble na mão de cada jogador.

Cada execução mede UMA decisão de jogada, não uma partida inteira.
A busca usa o jogador atual como referência. As execuções rodam sequencialmente
no terminal, sem Pygame. Não há limite automático de tempo; Ctrl+C interrompe
a execução atual e encerra a bateria preservando os registros anteriores.

Atual: avaliação estática do jogo. Inicial: reconstrução da fórmula anterior
à otimização, com expansão de ameaças e mobilidade. As fórmulas e pesos
diferem: comparar seus tempos não comprova qual joga melhor.

O tempo inclui apenas escolher_jogada (geração, simulações e avaliação).
Não inclui preparação, carregamento, salvamento, impressão ou relatórios.
Em interrupções, os contadores são parciais e a pontuação/jogada ficam vazias.
Os contadores do Minimax não incluem simulações internas da heurística antiga.

## Execuções registradas

| Nº | Cenário | Heurística | Algoritmo | Prof. | Rep. | Estado | Tempo (s) | Nós | Cortes |
|---|---|---|---|---:|---:|---|---:|---:|---:|
| 1 | reduzido | atual | minimax | 1 | 1 | concluido | 0.000879 | 4 | 0 |
| 2 | reduzido | atual | alfa_beta | 1 | 1 | concluido | 0.000703 | 4 | 0 |
| 3 | reduzido | atual | minimax | 1 | 2 | concluido | 0.000702 | 4 | 0 |
| 4 | reduzido | atual | alfa_beta | 1 | 2 | concluido | 0.000703 | 4 | 0 |
| 5 | reduzido | atual | minimax | 1 | 3 | concluido | 0.000718 | 4 | 0 |
| 6 | reduzido | atual | alfa_beta | 1 | 3 | concluido | 0.001043 | 4 | 0 |
| 7 | reduzido | atual | minimax | 2 | 1 | concluido | 0.002158 | 11 | 0 |
| 8 | reduzido | atual | alfa_beta | 2 | 1 | concluido | 0.002070 | 10 | 1 |
| 9 | reduzido | atual | minimax | 2 | 2 | concluido | 0.002777 | 11 | 0 |
| 10 | reduzido | atual | alfa_beta | 2 | 2 | concluido | 0.002900 | 10 | 1 |
| 11 | reduzido | atual | minimax | 2 | 3 | concluido | 0.002409 | 11 | 0 |
| 12 | reduzido | atual | alfa_beta | 2 | 3 | concluido | 0.002205 | 10 | 1 |
| 13 | reduzido | atual | minimax | 3 | 1 | concluido | 0.007777 | 34 | 0 |
| 14 | reduzido | atual | alfa_beta | 3 | 1 | concluido | 0.007792 | 31 | 2 |
| 15 | reduzido | atual | minimax | 3 | 2 | concluido | 0.007144 | 34 | 0 |
| 16 | reduzido | atual | alfa_beta | 3 | 2 | concluido | 0.008275 | 31 | 2 |
| 17 | reduzido | atual | minimax | 3 | 3 | concluido | 0.007170 | 34 | 0 |
| 18 | reduzido | atual | alfa_beta | 3 | 3 | concluido | 0.006906 | 31 | 2 |
| 19 | reduzido | inicial | minimax | 1 | 1 | concluido | 0.003001 | 4 | 0 |
| 20 | reduzido | inicial | alfa_beta | 1 | 1 | concluido | 0.002246 | 4 | 0 |
| 21 | reduzido | inicial | minimax | 1 | 2 | concluido | 0.002257 | 4 | 0 |
| 22 | reduzido | inicial | alfa_beta | 1 | 2 | concluido | 0.003680 | 4 | 0 |
| 23 | reduzido | inicial | minimax | 1 | 3 | concluido | 0.003631 | 4 | 0 |
| 24 | reduzido | inicial | alfa_beta | 1 | 3 | concluido | 0.003415 | 4 | 0 |
| 25 | reduzido | inicial | minimax | 2 | 1 | concluido | 0.007117 | 11 | 0 |
| 26 | reduzido | inicial | alfa_beta | 2 | 1 | concluido | 0.006588 | 10 | 1 |
| 27 | reduzido | inicial | minimax | 2 | 2 | concluido | 0.007988 | 11 | 0 |
| 28 | reduzido | inicial | alfa_beta | 2 | 2 | concluido | 0.007037 | 10 | 1 |
| 29 | reduzido | inicial | minimax | 2 | 3 | concluido | 0.008762 | 11 | 0 |
| 30 | reduzido | inicial | alfa_beta | 2 | 3 | concluido | 0.007206 | 10 | 1 |
| 31 | reduzido | inicial | minimax | 3 | 1 | concluido | 0.021043 | 34 | 0 |
| 32 | reduzido | inicial | alfa_beta | 3 | 1 | concluido | 0.027365 | 31 | 2 |
| 33 | reduzido | inicial | minimax | 3 | 2 | concluido | 0.032259 | 34 | 0 |
| 34 | reduzido | inicial | alfa_beta | 3 | 2 | concluido | 0.027676 | 31 | 2 |
| 35 | reduzido | inicial | minimax | 3 | 3 | concluido | 0.020004 | 34 | 0 |
| 36 | reduzido | inicial | alfa_beta | 3 | 3 | concluido | 0.024142 | 31 | 2 |

## Tempos das execuções concluídas

- reduzido, seed não se aplica, atual, minimax, profundidade 1: n=3, média=0.000766 s, mínimo=0.000702 s, máximo=0.000879 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, atual, alfa_beta, profundidade 1: n=3, média=0.000816 s, mínimo=0.000703 s, máximo=0.001043 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, atual, minimax, profundidade 2: n=3, média=0.002448 s, mínimo=0.002158 s, máximo=0.002777 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, atual, alfa_beta, profundidade 2: n=3, média=0.002392 s, mínimo=0.002070 s, máximo=0.002900 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, atual, minimax, profundidade 3: n=3, média=0.007364 s, mínimo=0.007144 s, máximo=0.007777 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, atual, alfa_beta, profundidade 3: n=3, média=0.007658 s, mínimo=0.006906 s, máximo=0.008275 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, minimax, profundidade 1: n=3, média=0.002963 s, mínimo=0.002257 s, máximo=0.003631 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, alfa_beta, profundidade 1: n=3, média=0.003114 s, mínimo=0.002246 s, máximo=0.003680 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, minimax, profundidade 2: n=3, média=0.007956 s, mínimo=0.007117 s, máximo=0.008762 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, alfa_beta, profundidade 2: n=3, média=0.006944 s, mínimo=0.006588 s, máximo=0.007206 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, minimax, profundidade 3: n=3, média=0.024435 s, mínimo=0.020004 s, máximo=0.032259 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.
- reduzido, seed não se aplica, inicial, alfa_beta, profundidade 3: n=3, média=0.026394 s, mínimo=0.024142 s, máximo=0.027676 s. Estado/código: 2b4f5cec2d42/bf602fadc05a.

## Comparação e limites

Pares concluídos comparáveis entre Minimax e alfa-beta: 18.
Pares com divergência de nota ou jogada: 0.
Compare somente pares da mesma heurística, posição, código e profundidade.
Interrompido não significa derrota ou erro do algoritmo; não é tempo de conclusão.
Uma execução longa não estabelece o limite máximo viável. Ainda é necessário
definir o tempo aceitável para o usuário e analisar outras posições e seeds.

## Ambiente e rastreabilidade

- Código/Python/SO/CPU/CPUs lógicas: bf602fadc05aeea5bb6ef06f30092b8b3e505830865138f8206b57d8da805350 / 3.13.14 / Windows-11-10.0.26300-SP0 / Intel64 Family 6 Model 141 Stepping 1, GenuineIntel / 12

## Erros e interrupções

Nenhum erro ou interrupção registrado.

As posições são arquivadas em states/<estado_sha256>.json.
O hash do código identifica os fontes usados, inclusive alterações sem commit.
Não foram medidos consumo de memória, taxa de vitória ou treinamento.
