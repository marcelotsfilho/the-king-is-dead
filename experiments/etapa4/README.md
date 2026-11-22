# Registro experimental da etapa 4

O [relatório de evolução e guia de apresentação](evolucao/README.md) descreve a versão jogável atual e o efeito da busca de finais com a mesma tabela Q.

A [bateria de três execuções de 3.000 partidas](bateria_3000/README.md) contém a confirmação em partidas reservadas, as novas posições de passe e a comparação com Minimax em profundidades maiores. Abaixo está o registro da primeira rodada, de 1.200 partidas.

## Treino e escolha da tabela

O agente aprende valores para **passar** e **usar cada tipo de carta**. A chave do estado resume o progresso das disputas, os passes consecutivos, o risco imediato de invasão, a vantagem na corte, o tamanho da mão e se o passe tem a melhor avaliação imediata. Para cada tipo de carta, o agente compara até duas jogadas legais completas e usa a mais bem avaliada como candidata. Na última disputa, compara todas as jogadas legais. A heurística também desempata valores Q iguais e permite jogar em estados ainda desconhecidos.

Foram executadas **1.200 partidas de treino**, metade contra uma política aleatória e metade contra a política inicial do agente (tabela vazia, com os mesmos critérios para montar e avaliar as jogadas). Foram usadas recompensas finais de `+1`, `−1` e `0`, taxa de aprendizado `0,12`, desconto `0,97` e exploração reduzida de `0,90` a `0,10`. Cada transição vai de uma decisão do agente à sua próxima decisão ou ao fim da partida. Nas avaliações, a exploração e a atualização da tabela ficam desligadas.

A cada 100 partidas, a tabela foi avaliada nas mesmas 80 partidas contra a política inicial, com sementes diferentes das de treino. O critério de bom treino exigia pelo menos 55% de vitórias, 5 pontos percentuais acima dos 50% iniciais, em três avaliações consecutivas. **Nenhum checkpoint cumpriu esse critério.** O melhor ponto foi após **900 partidas**, com **47 de 80 vitórias (58,75%)**, e foi selecionado para a demonstração. Nas 80 partidas reservadas, com sementes novas, a tabela de 900 partidas venceu **39 de 80 (48,75%)**. A melhora observada na seleção não se confirmou nessa amostra reservada.

| Partidas de treino | 0 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1.000 | 1.100 | 1.200 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Vitórias na validação (de 80) | 40 | 42 | 45 | 43 | 41 | 44 | 40 | 40 | 42 | 47 | 43 | 44 | 41 |

## Quando passar ou jogar uma carta

As posições controladas começam com uma carta disponível, sete disputas resolvidas e um passe do adversário já registrado. O arquivo `posicoes/posicoes.csv` registra a escolha de cada agente, os desfechos ao executar todas as jogadas legais e os parâmetros completos de cada jogada.

| Posição | Desfecho do passe | Decisão da tabela treinada | Decisão da política inicial | Minimax / alfa-beta | Monte Carlo 3.000 |
|---|---|---|---|---|---|
| Passe favorável | Vitória imediata | Passou e venceu | Passou e venceu | Passaram e venceram | Jogou carta e venceu |
| Carta necessária | Derrota imediata | Usou English Support, convocou inglês e venceu | Fez a mesma jogada e venceu | Fizeram a mesma jogada e venceram | Fez a mesma jogada e venceu |

Os dois casos confirmam decisões adequadas nessas posições. A política inicial também as acertou. Nas partidas reservadas, a tabela treinada fez seu primeiro passe com cartas na mão em **68 de 80** partidas. A política inicial adversária passou com cartas no primeiro passe em **80 de 80** nessas mesmas partidas. A métrica deve ser lida junto com o desfecho de cada jogo, pois passar com cartas também pode ser desfavorável em uma posição específica.

A referência histórica está no [diagnóstico do Monte Carlo 3.000 contra alfa-beta](../diagnostico_passes_mc3000_20261122/relatorio.md). Naquelas 10 partidas, o Monte Carlo esgotou a mão antes do primeiro passe em todos os jogos. As sementes e os confrontos desse diagnóstico são diferentes dos usados para a tabela Q.

## Confrontos com a tabela congelada

| Adversário | Profundidade | Partidas | Vitórias | Derrotas | Empates | Vitórias (%) | Primeiro passe do Q-learning com cartas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Minimax | 1 | 8 | 7 | 1 | 0 | 87,5% | 7 de 8 |
| Minimax com alfa-beta | 1 | 8 | 7 | 1 | 0 | 87,5% | 7 de 8 |
| Minimax contra a política inicial (controle) | 1 | 8 | 3 | 5 | 0 | 37,5% | 8 de 8 |

Os dois confrontos usaram as mesmas quatro sementes reservadas, cada uma disputada duas vezes, invertendo o lado da tabela. Quem começa também foi balanceado no conjunto. Todas as partidas foram concluídas. As variantes repetiram as escolhas e os resultados nessa configuração. Com profundidade 1, a busca ainda não chega a um nível de decisão em que a poda possa reduzir o trabalho. Os resultados descrevem esta bateria curta nessa profundidade.

O controle repetiu as oito partidas contra o Minimax simples com a tabela vazia. A tabela treinada ganhou quatro partidas que a política inicial perdeu e manteve o mesmo desfecho nas outras quatro. Os ganhos nessa bateria apareceram junto com uma redução de 8 para 7 partidas com cartas no primeiro passe.

## Arquivos e reprodução

| Arquivo | Dados |
|---|---|
| [treino.csv](treino.csv) | 1.200 partidas com semente, adversário, exploração, resultado e cartas restantes no primeiro passe de cada lado |
| [validacao.csv](validacao.csv) | 1.040 partidas com a exploração desligada, incluindo a política inicial e os 12 checkpoints |
| [avaliacao_reservada.csv](avaliacao_reservada.csv) | 80 partidas com a tabela escolhida e sementes reservadas |
| [confrontos.csv](confrontos.csv) | 16 partidas contra as duas variantes do Minimax |
| [confronto_politica_inicial.csv](confronto_politica_inicial.csv) | Oito partidas de controle contra o Minimax, com a tabela Q vazia |
| [posicoes/posicoes.csv](posicoes/posicoes.csv) | Decisões das IAs e resultados de todas as jogadas legais nas duas posições, com estados salvos em JSON na mesma pasta |
| [tabela_q.json](tabela_q.json) | Tabela selecionada e parâmetros de treino |
| [aprendizado.png](aprendizado.png) | Partidas jogadas × vitórias por bloco de 100, com validação no painel inferior |

No PowerShell, com o ambiente virtual ativado, os comandos abaixo refazem as amostras em uma pasta nova. O tempo de execução pode variar.

```powershell
$saidaEtapa4 = 'experiments/reproducao_etapa4'
python main_q_learning.py treinar --partidas 1200 --intervalo 100 --validacao 80 --semente 10000 --saida $saidaEtapa4
python main_q_learning.py avaliar --tabela "$saidaEtapa4/tabela_q.json" --partidas 8 --profundidade 1 --semente 90000 --saida "$saidaEtapa4/confrontos.csv"
python main_q_learning.py avaliar --politica-inicial --partidas 8 --profundidade 1 --semente 90000 --adversarios minimax --saida "$saidaEtapa4/confronto_politica_inicial.csv"
python main_q_learning.py avaliar --tabela "$saidaEtapa4/tabela_q.json" --partidas 80 --semente 91000 --adversarios politica_inicial --saida "$saidaEtapa4/avaliacao_reservada.csv"
python -m experiments.q_learning_scenarios --tabela "$saidaEtapa4/tabela_q.json" --saida "$saidaEtapa4/posicoes"
python -m experiments.q_learning_chart --pasta $saidaEtapa4 --bloco 100
```
