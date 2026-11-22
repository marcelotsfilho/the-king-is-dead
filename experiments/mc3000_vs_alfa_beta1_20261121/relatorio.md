# Monte Carlo 3.000 contra Minimax com alfa-beta

## Protocolo

20 partidas completas, sem renderização Pygame, com seeds 0–19. Monte Carlo usou 3.000 rollouts por decisão; o adversário usou Minimax profundidade 1 com alfa-beta ativado. O lado de cada algoritmo e o jogador inicial foram equilibrados: cada lado começou 10 partidas, e cada algoritmo jogou 10 vezes como jogador 1 e 10 como jogador 2. Uma seed corresponde a uma partida (não é um par de partidas com lados invertidos).

As decisões e a duração das partidas foram medidas com `perf_counter`. A partida foi executada pelo modelo do jogo, fora do Pygame, para separar o algoritmo da interface. CSV grava uma linha por partida.

## Resultado

| Métrica | Monte Carlo 3.000 | Minimax 1 + alfa-beta |
|---|---:|---:|
| Vitórias | 9/20 | 11/20 |
| Média de tempo por decisão | 13,398 s | 0,952 s |
| Mediana da média por partida | 13,148 s | 0,894 s |
| Maior decisão observada | 38,007 s | 7,032 s |
| Nós/estados visitados por partida (média) | 985.884 | 63.970 |
| Simulações/folhas por partida (média) | 54.450 simulações | 63.952 folhas |

A duração das partidas foi de **261,7 s em média** (4 min 22 s), mediana 245,6 s, mínima 203,6 s e máxima 349,1 s. As partidas tiveram 30–42 jogadas completas. Foram concluídas 363 decisões de Monte Carlo e 373 decisões Minimax. O total foi de 1.089.000 rollouts.

Por jogador inicial, o Monte Carlo venceu 5 das 10 partidas em que começou; quando alfa-beta começou, MC venceu 4 das 10. No lado 1, MC venceu 7/10; no lado 2, venceu 2/10. A diferença observada por lado merece investigação em uma bateria pareada adicional, apesar de a quantidade de jogos por lado e por jogador inicial estar equilibrada.

## O que os tempos mostram

Na abertura seed 42, uma decisão MC3000 levou **30,281 s**, com 102.976 estados visitados e 3.000 simulações. No torneio, decisões iniciais chegaram a 38,007 s. A média de todas as decisões foi menor (13,398 s), porque o espaço de ações diminui em fases mais avançadas. Portanto, o orçamento atinge a faixa de 30–60 s na abertura, mas não representa uma espera constante por jogada.

## Sobre alfa-beta

Alfa-beta está ligado em todas as decisões do adversário, mas o Minimax usou profundidade 1. Nessa profundidade não há camada interna para cortar; foram registrados **zero cortes em todas as 20 partidas**. Assim, o torneio mede MC3000 contra Minimax 1 e confirma a execução da opção alfa-beta, mas não mede economia de busca da poda em jogo completo.

A validação disponível em cenário reduzido verificou decisões iguais entre Minimax simples e alfa-beta e registrou cortes reais: profundidade 2, 11 → 9 nós (2 cortes); profundidade 3, 34 → 28 nós (4 cortes). Os resultados estão em `../bateria_algoritmos_20261121_134131/buscas_pequenas.json`. Uma comparação em profundidade 2 no tabuleiro completo não foi repetida: o jogo já havia mostrado buscas de milhares de segundos nessa profundidade.

## Conclusão

MC3000 atende ao limite de 30–60 s no estado inicial medido e terminou todas as partidas; o custo médio por decisão ao longo da partida foi 13,4 s. Porém, nesta bateria, MC venceu 9/20 contra Minimax 1 com alfa-beta. Isso não indica que mais simulações tornam a estratégia mais forte: só compara uma amostra pequena e um adversário de profundidade 1. Os resultados também mostram possível efeito do lado do jogador, que deve ser testado com seeds pareadas trocando os lados.

A interface agora permite escolher 100, 300, 1.000, 3.000 e 5.000 simulações. O valor padrão permanece 100; 5.000 não foi medido e pode exceder um minuto. Para aproximar 30 s na abertura, a opção testada é 3.000.

## Testes automatizados

A suíte executou 335 testes: **334 aprovados e 1 falha preexistente** em `test_plano_padrao_possui_36_configuracoes`, que espera 36 itens enquanto o plano padrão atual gera 8. Os 32 testes direcionados a configuração, menu e execução da IA passaram.

## Arquivos

- `partidas.csv`: resultados e tempos por seed.
- `../../torneio_mc_alfa_beta.py`: harness reproduzível; suporta retomada, registrando e pulando seeds concluídas.
- `../bateria_algoritmos_20261121_134131/buscas_pequenas.json`: validação de Minimax/alfa-beta com cortes em profundidades 2 e 3 no cenário reduzido.
- `../bateria_algoritmos_20261121_134131/tempos_posicoes.json`: benchmark anterior dos budgets MC em estados fixos.
