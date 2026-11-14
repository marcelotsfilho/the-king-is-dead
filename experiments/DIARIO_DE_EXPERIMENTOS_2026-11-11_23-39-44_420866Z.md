# Diário automático de experimentos

Este diário reúne os testes desta chamada do executor.
O [histórico completo](results.csv) reúne os registros de todas as baterias.

## Cenário e protocolo

Início (UTC) · 2026-11-11T23:39:44.420866+00:00

Cenário: inicial; seed: 42; bateria: ambas; profundidades: [1, 2]; repetições: 1; algoritmos: ['minimax', 'alfa_beta']. Plano desta invocação: 8 decisões. Estado: a7d0177a0303d829f91846d0fcc9b0d90549b72b1c595f23a5c596f6699f4496. Estado inicial completo criado pelo setup padrão, sem ações anteriores.

Configurações já concluídas e puladas nesta chamada · 0

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

| Nº | Cenário | Heurística | Algoritmo | Prof. | Rep. | Status | Tempo (s) | Nós | Folhas | Cortes | Pontuação |
|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | inicial | atual | minimax | 1 | 1 | concluido | 5.410687 | 14698 | 14697 | 0 | 4004 |
| 2 | inicial | atual | alfa_beta | 1 | 1 | concluido | 5.071385 | 14698 | 14697 | 0 | 4004 |
| 3 | inicial | atual | minimax | 2 | 1 | em_andamento |  |  |  |  |  |

## Jogadas escolhidas

- Execução 1 · Jogar Scottish Support em Strathclyde e convocar escoceses de Moray.
- Execução 2 · Jogar Scottish Support em Strathclyde e convocar escoceses de Moray.

## Tempos das execuções concluídas

- inicial, seed 42, atual, minimax, profundidade 1: n=1, média=5.410687 s, mínimo=5.410687 s, máximo=5.410687 s. Estado/código: a7d0177a0303/050e545b97b9.
- inicial, seed 42, atual, alfa_beta, profundidade 1: n=1, média=5.071385 s, mínimo=5.071385 s, máximo=5.071385 s. Estado/código: a7d0177a0303/050e545b97b9.

## Comparação e limites

Pares concluídos comparáveis entre Minimax e alfa-beta: 1.
Pares com divergência de nota ou jogada: 0.
Compare somente pares da mesma heurística, posição, código e profundidade.
Interrompido não significa derrota ou erro do algoritmo; não é tempo de conclusão.
Uma execução longa não estabelece o limite máximo viável. Ainda é necessário
definir o tempo aceitável para o usuário e analisar outras posições e seeds.

## Ambiente e rastreabilidade

- Código/Python/SO/CPU/CPUs lógicas: 050e545b97b97d8e18fa5f1959d9a28b916d140372ff0ce2bcf67ce18b9763b7 / 3.13.14 / Windows-11-10.0.26300-SP0 / Intel64 Family 6 Model 141 Stepping 1, GenuineIntel / 12

## Erros e interrupções

Nenhum erro ou interrupção registrado.

As posições são arquivadas em states/<estado_sha256>.json.
O hash do código identifica os fontes usados, inclusive alterações sem commit.
Não foram medidos consumo de memória, taxa de vitória ou treinamento.
