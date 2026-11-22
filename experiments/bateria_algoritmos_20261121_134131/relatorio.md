# Bateria comparativa dos algoritmos

## Escopo e método

Foram executadas 40 partidas completas sem renderização Pygame: 20 de Monte Carlo com 100 simulações (MC100) e 20 com 300 (MC300), sempre contra Minimax de profundidade 1 sem poda. Em cada configuração, seeds 0–9 foram testadas duas vezes, alternando qual jogador começa e qual lado recebe o Monte Carlo. Os tempos de partida incluem as decisões dos dois agentes; os tempos de decisão foram registrados separadamente.

Também foram medidos Minimax 1, MC100, MC300 e MC1000 em três estados fixos: abertura seed 42, turno 8 de uma partida reproduzida com seed 0 e turno 16 dessa partida. O último estado já estava praticamente encerrado e serve apenas como referência de custo em posição terminal/quase terminal. Para comparar Minimax com alfa-beta, foi feita uma validação de profundidades 1–3 em um cenário sintético reduzido e uma comparação de profundidade 1 nos três estados fixos.

## Resultados das partidas

| Configuração | Partidas | Vitórias MC | Vitórias Minimax 1 | Tempo médio por decisão MC | Tempo médio por decisão Minimax | Duração média da partida | Mediana |
|---|---:|---:|---:|---:|---:|---:|---:|
| MC100 | 20 | 17 | 3 | 0,298 s | 0,570 s | 16,234 s | 15,321 s |
| MC300 | 20 | 18 | 2 | 1,249 s | 0,853 s | 37,837 s | 28,764 s |

O pareamento por seed reduz o efeito de começar primeiro: MC100 venceu as duas partidas em 8 seeds, dividiu as vitórias em 1 seed e perdeu as duas em 1 seed. MC300 venceu as duas em 8 seeds, dividiu em 2 seeds e não perdeu ambas em nenhuma seed. As vitórias por lado foram equilibradas: MC100 venceu 8 vezes como jogador 1 e 9 como jogador 2; MC300 venceu 9 vezes de cada lado.

Os resultados apontam uma vantagem consistente do Monte Carlo observado nesta amostra, mas são exploratórios: 10 seeds pareadas por configuração não bastam para concluir que ele será sempre superior. A configuração de 300 simulações teve custo bem maior e uma partida levou 96,7 s. MC100 foi mais rápido em média que Minimax 1 neste conjunto; ainda assim, a diferença varia conforme o estado.

## Tempos e nós em estados fixos

| Posição | Algoritmo | Tempo | Nós registrados | Folhas/simulações |
|---|---|---:|---:|---:|
| Abertura seed 42 | Minimax 1 | 4,521 s | 14.698 | 14.697 folhas |
| Abertura seed 42 | MC100 | 1,468 s | 3.443 | 100 simulações |
| Abertura seed 42 | MC300 | 4,215 s | 10.295 | 300 simulações |
| Abertura seed 42 | MC1000 | 11,022 s | 34.501 | 1.000 simulações |
| Turno 8 seed 0 | Minimax 1 | 0,831 s | 2.844 | 2.843 folhas |
| Turno 8 seed 0 | MC100 | 0,935 s | 2.617 | 100 simulações |
| Turno 8 seed 0 | MC300 | 2,249 s | 7.959 | 300 simulações |
| Turno 8 seed 0 | MC1000 | 6,858 s | 26.194 | 1.000 simulações |
| Turno 16 seed 0 (quase terminal) | Minimax 1 | 0,00027 s | 2 | 1 folha |
| Turno 16 seed 0 (quase terminal) | MC100 | 0,357 s | 1.852 | 100 simulações |
| Turno 16 seed 0 (quase terminal) | MC300 | 0,990 s | 5.548 | 300 simulações |
| Turno 16 seed 0 (quase terminal) | MC1000 | 3,613 s | 18.599 | 1.000 simulações |

O custo do Monte Carlo cresce aproximadamente com o número de simulações. MC1000 não foi submetido a partidas completas porque já consumiu 11 s em uma decisão de abertura. A amostra fixa é curta e o estado quase terminal não representa uma decisão típica do meio da partida.

## Minimax versus alfa-beta

No cenário sintético reduzido, Minimax e alfa-beta retornaram a mesma pontuação e jogada nas profundidades 1, 2 e 3. As podas reduziram os nós de 11 para 9 na profundidade 2 e de 34 para 28 na profundidade 3. Como o cenário é pequeno e ambos escolhem passar, isso valida a consistência básica, mas não compara desempenho/força no tabuleiro completo.

Nos três estados completos, a comparação foi apenas na profundidade 1. Os dois métodos retornaram a mesma jogada e pontuação e visitaram a mesma quantidade de nós (14.698 na abertura, 2.844 no turno 8 e 2 no estado quase terminal). Isso é esperado na profundidade 1: não há um nível interno de decisão onde a poda possa eliminar subárvores. Portanto, estes dados não permitem concluir se alfa-beta reduz o custo em profundidades maiores no jogo real.

## Checagens e limitações

- Reprodutibilidade do MC: duas execuções com o mesmo estado, seed 20261121 e 100 simulações retornaram a mesma jogada e pontuação; ambas executaram 100 simulações e preservaram o estado de entrada.
- Testes automatizados: 331 passaram e 1 falhou. A falha existente é `test_plano_padrao_possui_36_configuracoes`: o teste espera 36 experimentos, enquanto o plano padrão atual gera 8. Não foi introduzida alteração de código nesta bateria.
- Os tempos foram obtidos sem renderização Pygame e dependem da máquina/estado. Eles isolam o custo dos algoritmos; não incluem interface, espera de eventos ou atualização gráfica.
- A implementação testada é Monte Carlo por rollouts aleatórios, não MCTS/UCT. Em cada rollout, as ações subsequentes são aleatórias.

## Arquivos

- `partidas.csv`: resultado e tempos individuais das 40 partidas.
- `tempos_posicoes.json`: tempos, nós, folhas/simulações e jogada escolhida em cada estado fixo.
- `alfa_beta_depth1.json`: comparação de profundidade 1 nos três estados completos.
- `buscas_pequenas.json`: contagens e resultados Minimax/alfa-beta no cenário reduzido.
- `states/`: snapshots dos estados usados nos testes fixos.
