# Q-learning — três execuções de 3.000 partidas

## Treino e seleção

Cada execução começou com a tabela vazia. Foram usadas 3.000 partidas por execução, 9.000 no total, com metade contra a política inicial e metade contra a política aleatória. Foram mantidos os parâmetros da primeira bateria (`α=0,12`, `γ=0,97`, `ε` de `0,90` a `0,10`) e a mesma representação de estados e ações. As três curvas foram avaliadas a cada 500 partidas de treino, com a tabela congelada, nas mesmas 200 partidas de validação. Os pareamentos usaram 100 sementes, duas partidas por semente, com inversão de lados e alternância de quem começa no conjunto.

A meta era atingir 55% de vitórias ou mais em três avaliações consecutivas em pelo menos duas das três execuções. A escolha priorizou o primeiro checkpoint de uma sequência sustentada e, em caso de empate, a maior taxa de vitória nesse checkpoint. A tabela foi escolhida antes de abrir a amostra reservada.

| Semente de treino | 0 | 500 | 1.000 | 1.500 | 2.000 | 2.500 | 3.000 | Primeiro ponto sustentado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20000 | 99 | 105 | 106 | 110 | 116 | 109 | 101 | — |
| 30000 | 99 | **126** | **115** | **113** | 118 | 123 | 108 | 500 |
| 40000 | 99 | **112** | **113** | **115** | 120 | 113 | 134 | 500 |

Os valores são vitórias em 200 partidas por ponto. As duas séries em negrito cumpriram a meta entre 500 e 1.500 partidas. A tabela escolhida foi a de **500 partidas da semente 30000**, com 63% de vitórias naquele checkpoint. A sequência foi confirmada após os checkpoints de 1.000 e 1.500 partidas. A maior taxa isolada da bateria foi 67%, após 3.000 partidas da semente 40000.

## Confirmação em partidas inéditas

| Tabela, contra a política inicial | Vitórias | Derrotas | Empates | Taxa de vitória | IC de 95% | Primeiro passe com cartas |
|---|---:|---:|---:|---:|---:|---:|
| Selecionada após 500 partidas | 124 | 75 | 1 | **62%** | 55,5% a 68,5% | 183 de 200 |
| Anterior, selecionada após 900 partidas | 96 | 104 | 0 | 48% | 41,5% a 54,5% | 170 de 200 |

As duas tabelas foram avaliadas nas mesmas 200 partidas reservadas, sem exploração ou atualização. A diferença pareada de **14 pontos percentuais** teve intervalo de 95% de **5 a 23 pontos percentuais**. Os intervalos foram calculados com 10.000 reamostragens dos pares agrupados por semente. Neste protocolo, 500 partidas foram suficientes para o checkpoint selecionado, com confirmação de estabilidade em 1.500 e confirmação de desempenho na amostra reservada.

## Profundidade do Minimax

Na primeira decisão da semente 53000, Minimax e alfa-beta em profundidade 1 visitaram 13.598 nós e levaram cerca de 2 segundos. Em profundidade 2, o Minimax sem poda atingiu o limite de 30 segundos. Alfa-beta concluiu em 6,07 segundos, visitou 40.791 nós e realizou 13.596 cortes. Em todos os casos concluídos, a escolha foi passar. Esses tempos descrevem uma abertura e a carga da máquina durante a bateria.

Em oito finais extraídos de partidas reais, com seis disputas resolvidas e uma ou duas cartas em cada mão, foi possível repetir os confrontos em ambas as profundidades. Cada grupo de 16 partidas usou os dois lados da mesma posição. A tabela treinada e a política inicial venceram **4 de 16** em cada combinação de adversário e profundidade, sem empates. Na profundidade 2, para cada política, Minimax visitou 15.619 nós e alfa-beta visitou 2.617, realizando 623 cortes. O aumento da profundidade teve custo mensurável e manteve os resultados nestes finais.

Desde a abertura, a tabela treinada venceu **14 de 16** partidas contra alfa-beta em profundidade 1. A política inicial venceu **9 de 16** nas mesmas condições. O primeiro passe ocorreu com cartas na mão em 15 de 16 partidas da tabela treinada e 16 de 16 da política inicial. Nas duas tentativas de partida completa contra alfa-beta em profundidade 2, na semente 53010 com troca de lados, o limite de 60 segundos por partida foi atingido. As duas contagens ficaram fora das taxas de vitória.

O treino manteve adversários baratos para isolar o efeito de repetir a experiência. Os confrontos com Minimax medem o desempenho da tabela já treinada. Medir o efeito de usar Minimax no treino exigiria comparar dois treinos com as mesmas sementes e o mesmo orçamento, alterando o adversário de treino entre eles.

## Passar, jogar ou guardar uma carta

Foram selecionadas 11 posições de partidas aleatórias com uma ou duas disputas por resolver, um passe já registrado, uma carta na mão do jogador da vez e nenhuma na mão do adversário. Uma busca exaustiva verificou o melhor resultado alcançável com cada escolha. As duas faixas de busca, de 30.000 sementes no total, encontraram três casos em que só era possível vencer passando naquele momento e usando a carta mais tarde.

| Posição | Q-learning treinado | Política inicial | Minimax 1 | Alfa-beta 2 | Alfa-beta 3 |
|---|---:|---:|---:|---:|---:|
| Passar vence imediatamente | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Jogar uma carta é necessário para vencer | 2/4 | 2/4 | 2/4 | 2/4 | 3/4 |
| Passar agora e usar a carta mais tarde | 2/3 | 2/3 | 2/3 | 2/3 | 3/3 |
| **Total de vitórias** | **8/11** | **8/11** | **8/11** | **8/11** | **10/11** |

A tabela treinada melhorou a taxa de vitória em partidas completas, mas igualou a política inicial nas posições táticas selecionadas. A profundidade 3 encontrou duas vitórias adicionais nesses finais. Esse resultado aponta uma forma de usar a busca mais profunda em posições pequenas, com desfechos verificáveis, para investigar treinamento tático em outra bateria.

## Dados e reprodução

| Dados | Arquivos |
|---|---|
| Partidas por execução, validação, tabelas por checkpoint e curvas | [20000](semente_20000/), [30000](semente_30000/), [40000](semente_40000/) |
| Seleção antes da confirmação | [Regra e resultados da seleção](selecao.json) · [Tabela escolhida](tabela_selecionada.json) |
| Partidas reservadas e intervalos | [Tabela escolhida](reservada_tabela_selecionada.csv) · [Tabela anterior](reservada_tabela_anterior.csv) · [Resumo](reservada_resumo.json) |
| Partidas com Minimax e alfa-beta em profundidades 1 e 2 | [Finais e estados salvos](finais/) · [Custo da abertura](custo_abertura/tempos.csv) |
| Partidas pareadas desde a abertura em profundidade 1 | [Tabela treinada](minimax_1_treinada.csv) · [Política inicial](minimax_1_inicial.csv) |
| Piloto desde a abertura em profundidade 2 com prazo por partida | [Piloto alfa-beta](minimax_2_abertura.csv) |
| Posições táticas e sequências de jogadas | [Posições e decisões](taticas/) |

Com o ambiente virtual ativado, os comandos refazem a bateria em uma pasta nova. A tabela anterior usada no controle está no diretório da primeira rodada.

```powershell
$saidaBateriaQL = 'experiments/reproducao_bateria_3000'
foreach ($sementeTreinoQL in 20000,30000,40000) {
    python main_q_learning.py treinar --partidas 3000 --intervalo 500 --validacao 200 --semente $sementeTreinoQL --semente-validacao 51000 --salvar-checkpoints --saida "$saidaBateriaQL/semente_$sementeTreinoQL"
    python -m experiments.q_learning_chart --pasta "$saidaBateriaQL/semente_$sementeTreinoQL" --bloco 500
}
python -m experiments.q_learning_selection $saidaBateriaQL
$tabelaBateriaQL = "$saidaBateriaQL/tabela_selecionada.json"
python main_q_learning.py avaliar --tabela $tabelaBateriaQL --partidas 200 --semente 52000 --adversarios politica_inicial --saida "$saidaBateriaQL/reservada_tabela_selecionada.csv"
python main_q_learning.py avaliar --tabela experiments/etapa4/tabela_q.json --partidas 200 --semente 52000 --adversarios politica_inicial --saida "$saidaBateriaQL/reservada_tabela_anterior.csv"
python -m experiments.q_learning_selection $saidaBateriaQL --comparar-reservada
python main_q_learning.py avaliar --tabela $tabelaBateriaQL --partidas 16 --profundidade 1 --semente 53010 --adversarios alfa_beta --saida "$saidaBateriaQL/minimax_1_treinada.csv"
python main_q_learning.py avaliar --politica-inicial --partidas 16 --profundidade 1 --semente 53010 --adversarios alfa_beta --saida "$saidaBateriaQL/minimax_1_inicial.csv"
python -m experiments.q_learning_depth abertura "$saidaBateriaQL/custo_abertura" --semente 53000 --limite 30
python -m experiments.q_learning_depth finais "$saidaBateriaQL/finais" $tabelaBateriaQL --semente 54000 --posicoes 8
python -m experiments.q_learning_depth partidas "$saidaBateriaQL/minimax_2_abertura.csv" $tabelaBateriaQL --semente 53010 --limite 60
python -m experiments.q_learning_tactics gerar "$saidaBateriaQL/taticas" --semente 55000 --quantidade 4 --tentativas 20000
python -m experiments.q_learning_tactics gerar "$saidaBateriaQL/taticas" --semente 75000 --quantidade 4 --tentativas 10000 --continuar
python -m experiments.q_learning_tactics avaliar "$saidaBateriaQL/taticas" $tabelaBateriaQL
```
