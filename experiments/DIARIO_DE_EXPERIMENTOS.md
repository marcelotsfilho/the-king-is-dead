# Diário automático de experimentos

Este arquivo é gerado pelo executor. Os dados completos estão em results.csv.

## Cenário e protocolo

Cenário: inicial; seed: 42; bateria: ambas; profundidades: [1, 2]; repetições: 1; algoritmos: ['minimax', 'alfa_beta']. Plano desta invocação: 8 decisões. Estado: a7d0177a0303d829f91846d0fcc9b0d90549b72b1c595f23a5c596f6699f4496. Estado inicial completo criado pelo setup padrão, sem ações anteriores.

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
| [1](execucoes/execucao-0001.md) | inicial | atual | minimax | 1 | 1 | concluido | 4.002835 | 14698 | 0 |
| [2](execucoes/execucao-0002.md) | inicial | atual | alfa_beta | 1 | 1 | concluido | 3.647179 | 14698 | 0 |
| [3](execucoes/execucao-0003.md) | inicial | atual | minimax | 1 | 2 | concluido | 3.610492 | 14698 | 0 |
| [4](execucoes/execucao-0004.md) | inicial | atual | alfa_beta | 1 | 2 | concluido | 3.683581 | 14698 | 0 |
| [5](execucoes/execucao-0005.md) | inicial | atual | minimax | 1 | 3 | concluido | 3.540789 | 14698 | 0 |
| [6](execucoes/execucao-0006.md) | inicial | atual | alfa_beta | 1 | 3 | concluido | 3.503588 | 14698 | 0 |
| [7](execucoes/execucao-0007.md) | inicial | atual | minimax | 2 | 1 | interrompido |  |  |  |
| [8](execucoes/execucao-0008.md) | inicial | atual | minimax | 1 | 1 | concluido | 4.548892 | 14698 | 0 |
| [9](execucoes/execucao-0009.md) | inicial | atual | alfa_beta | 1 | 1 | concluido | 4.389157 | 14698 | 0 |
| [10](execucoes/execucao-0010.md) | inicial | atual | minimax | 2 | 1 | interrompido | 1167.067241 | 3595587 | 0 |
| [11](execucoes/execucao-0011.md) | inicial | atual | minimax | 1 | 1 | concluido | 4.365406 | 14698 | 0 |
| [12](execucoes/execucao-0012.md) | inicial | atual | alfa_beta | 1 | 1 | concluido | 4.042438 | 14698 | 0 |
| [13](execucoes/execucao-0013.md) | inicial | atual | minimax | 2 | 1 | interrompido | 16.390585 | 46666 | 0 |
| [14](execucoes/execucao-0014.md) | inicial | atual | minimax | 1 | 1 | concluido | 4.366225 | 14698 | 0 |
| [15](execucoes/execucao-0015.md) | inicial | atual | alfa_beta | 1 | 1 | interrompido | 1.957911 | 1 | 0 |

## Tempos das execuções concluídas

- inicial, seed 42, atual, minimax, profundidade 1: n=3, média=3.718039 s, mínimo=3.540789 s, máximo=4.002835 s. Estado/código: a7d0177a0303/6c6f08a78e49.
- inicial, seed 42, atual, alfa_beta, profundidade 1: n=3, média=3.611449 s, mínimo=3.503588 s, máximo=3.683581 s. Estado/código: a7d0177a0303/6c6f08a78e49.
- inicial, seed 42, atual, minimax, profundidade 1: n=1, média=4.548892 s, mínimo=4.548892 s, máximo=4.548892 s. Estado/código: a7d0177a0303/b6506cc07490.
- inicial, seed 42, atual, alfa_beta, profundidade 1: n=1, média=4.389157 s, mínimo=4.389157 s, máximo=4.389157 s. Estado/código: a7d0177a0303/b6506cc07490.
- inicial, seed 42, atual, minimax, profundidade 1: n=2, média=4.365816 s, mínimo=4.365406 s, máximo=4.366225 s. Estado/código: a7d0177a0303/ee295a114f63.
- inicial, seed 42, atual, alfa_beta, profundidade 1: n=1, média=4.042438 s, mínimo=4.042438 s, máximo=4.042438 s. Estado/código: a7d0177a0303/ee295a114f63.

## Comparação e limites

Pares concluídos comparáveis entre Minimax e alfa-beta: 5.
Pares com divergência de nota ou jogada: 0.
Compare somente pares da mesma heurística, posição, código e profundidade.
Interrompido não significa derrota ou erro do algoritmo; não é tempo de conclusão.
Uma execução longa não estabelece o limite máximo viável. Ainda é necessário
definir o tempo aceitável para o usuário e analisar outras posições e seeds.

## Ambiente e rastreabilidade

- Código/Python/SO/CPU/CPUs lógicas: 6c6f08a78e49bebe7498342e43e1c433bbd5e421e96fae788446edf206714d1e / 3.13.14 / Windows-11-10.0.26300-SP0 / Intel64 Family 6 Model 141 Stepping 1, GenuineIntel / 12
- Código/Python/SO/CPU/CPUs lógicas: b6506cc07490578945f7ee53be1bc188c700acebb0f3fd6bcbdc747caa0730f2 / 3.13.14 / Windows-11-10.0.26300-SP0 / Intel64 Family 6 Model 141 Stepping 1, GenuineIntel / 12
- Código/Python/SO/CPU/CPUs lógicas: ee295a114f631666ce942f4b33400e6d52e4cb8297424cd9bfacef34917abb82 / 3.13.14 / Windows-11-10.0.26300-SP0 / Intel64 Family 6 Model 141 Stepping 1, GenuineIntel / 12

## Erros e interrupções

- Execução 7: Execução anterior terminou sem registrar o resultado; tempo desconhecido.
- Execução 10: Interrupção solicitada pelo usuário (Ctrl+C).
- Execução 13: Interrupção solicitada pelo usuário (Ctrl+C).
- Execução 15: Interrupção solicitada pelo usuário (Ctrl+C).

As posições são arquivadas em states/<estado_sha256>.json.
O hash do código identifica os fontes usados, inclusive alterações sem commit.
Não foram medidos consumo de memória, taxa de vitória ou treinamento.
