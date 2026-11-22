# Evolução do Q-learning e guia da apresentação

A versão jogável combina a tabela Q selecionada após 500 partidas com uma busca tática para finais pequenos. A busca corrigiu os três erros que motivaram a revisão e escolheu uma jogada ótima nas 24 posições inéditas da bateria. Nas partidas completas contra a política inicial, a porcentagem de vitórias permaneceu em 62% com a mesma tabela.

## O que mudou

A auditoria registrou, para cada jogada legal, sua presença na amostra, a pontuação imediata, o valor Q associado ao tipo de ação e o desfecho alcançável. Nos três erros, ela mostrou dois problemas distintos. [Auditoria por jogada](auditoria.csv)

| Posição | O que o agente fazia | O que a busca de final corrigiu |
|---|---|---|
| Semente 55127 | Passava. A convocação vencedora depois de Negotiate ficou fora da amostra. | Jogou Negotiate e convocou a facção que permitia vencer. |
| Semente 55179 | Jogava Assemble com parâmetros que levavam à derrota. As cinco combinações vencedoras ficaram fora da amostra. | Encontrou uma combinação de distribuição e convocação que levava à vitória. |
| Semente 60577 | Gastava English Support. A avaliação imediata deu 6.720 à carta e −640 ao passe, com valor Q zero para os dois. | Passou, guardou a carta e a usou na disputa seguinte para vencer. |

O **Model** consulta a tabela para escolher entre passar e usar um tipo de carta, com uma jogada legal concreta por tipo. Quando restam até duas disputas e até duas cartas no total, e o jogador da vez tem carta, a busca compara o resultado até o fim da partida considerando a melhor resposta adversária. Ela usa poda alfa-beta e visita até 800 nós. Se precisar de mais nós para concluir, aplica a jogada original da tabela. Quando duas ações têm o mesmo melhor desfecho, a preferência original é preservada. [Agente Q-learning](../../../model/q_learning_agent.py) · [Busca de final](../../../model/endgame_search.py)

O **Controller** carrega a tabela uma vez por partida e executa a decisão pela thread de IA já usada no jogo. A mensagem de turno indica quando a busca ajustou ou confirmou uma jogada. A **View** continua lendo o estado e mostrando o resultado. [Controlador](../../../controller/game_controller.py)

## Resultados da evolução

As duas versões usaram exatamente a mesma tabela, com exploração desligada. Em posições táticas, o acerto significa escolher uma jogada cujo melhor desfecho, considerando a resposta adversária, iguala o resultado ótimo verificado por uma busca exaustiva independente. As 24 posições inéditas foram extraídas de partidas aleatórias e tinham duas disputas restantes e mãos de tamanhos `(1, 0)`, `(1, 1)` ou `(2, 0)`. Cada grupo teve oito posições em que o desfecho dependia da jogada. [Dados táticos e estados salvos](avaliacao_tatica/)

| Amostra | Q-learning | Q-learning com busca de final | Alfa-beta 3 |
|---|---:|---:|---:|
| 11 posições de regressão | 8/11 | **11/11** | 10/11 |
| 24 posições inéditas | 15/24 | **24/24** | 22/24 |

| Adversário nas partidas completas | Q-learning | Q-learning com busca de final | Mudanças no resultado de uma partida |
|---|---:|---:|---:|
| Política inicial, 100 sementes pareadas | 124/200 | 124/200 | 0 |
| Alfa-beta 1, quatro sementes pareadas | 4/8 | 4/8 | 0 |

A busca ajustou duas decisões contra a política inicial e nenhuma contra alfa-beta nesse conjunto. O ganho observado aparece nas escolhas dos finais pequenos. A bateria de oito partidas contra alfa-beta usa sementes diferentes das 16 partidas do estudo de treino. [Partidas contra a política inicial](partidas_politica_inicial/partidas.csv) · [Partidas contra alfa-beta](partidas_alfa_beta/partidas.csv)

Nas 24 posições finais inéditas, 95% das decisões da versão atual foram concluídas em até **34,4 ms**. A mais longa levou **88,3 ms**. Nas partidas completas, o percentil 95 foi de **8,1 ms** contra a política inicial e **6,8 ms** contra alfa-beta. Os tempos são da tomada de decisão do agente na máquina medida, sem incluir desenho da interface ou decisões do adversário. [Resumo e tempos](resumo.json)

## O que você precisa saber para apresentar

> O Q-learning aprendeu por partidas simuladas a escolher entre passar e usar uma carta. Salvamos a tabela treinada para a apresentação. Nos finais pequenos, o agente também verifica, pelas regras do jogo, se outra jogada consegue um desfecho melhor.

### 1. Regras e objetivo do agente

Em *The King is Dead*, cada turno permite passar ou usar uma carta, executar seu efeito e convocar um seguidor para a corte. Dois passes consecutivos resolvem a próxima disputa. A partida termina por coroação ou invasão. Guardar uma carta pode ser decisivo porque ela permite reagir em uma disputa futura. No caso de demonstração, usar English Support cedo perde, e passar primeiro permite vencer com a mesma carta depois.

### 2. Como o Q-learning funciona aqui

- **Estado** é um resumo da posição, com fase das disputas, sequência de passes, risco de invasão, vantagem na corte e tamanho da mão.
- **Ação** na tabela é passar ou usar um tipo de carta disponível. O gerador monta as jogadas legais completas, incluindo a região e a facção convocada.
- **Recompensa** é `+1` por vitória, `−1` por derrota e `0` por empate. Durante o treino, o agente explora e atualiza valores Q. Na apresentação, ele lê o arquivo e usa a tabela congelada, com exploração desligada.
- **Minimax** simula ações e respostas. A **poda alfa-beta** elimina ramos que já não podem mudar a decisão da mesma busca. **Monte Carlo** estima o resultado com partidas simuladas. A busca de final do agente atual usa o princípio do Minimax e vai até o resultado do jogo dentro de um limite de nós.

### 3. Como explicar os números sem confundir as baterias

| Número | O que ele mede |
|---|---|
| 1.200 partidas | Rodada inicial. A tabela escolhida após 900 partidas teve 39 vitórias em 80 jogos reservados. |
| 9.000 partidas | Três execuções independentes de 3.000 partidas para verificar se a melhora se repetia. Cada execução começou com uma tabela vazia. |
| 500 partidas | Ponto em que foi salva a tabela selecionada. Duas execuções sustentaram a meta de 55% nos pontos de 500, 1.000 e 1.500. As partidas até 1.500 foram necessárias para verificar a estabilidade. |
| 124 de 200 vitórias | Desempenho da tabela de 500 partidas contra a política inicial em partidas inéditas. Nas mesmas condições, a tabela anterior obteve 96 de 200. |
| 15/24 → 24/24 | Efeito da busca tática na escolha da jogada ótima em posições inéditas, mantendo a mesma tabela. |

O gráfico tem partidas de treino no eixo horizontal. O painel de cima mostra vitórias por bloco de 500 partidas. O painel de baixo mostra vitórias em 200 partidas de validação a cada checkpoint. Para defender a quantidade de treino, mostre o checkpoint de 500, a confirmação em 1.500 e o resultado reservado de 124 de 200. [Gráfico da execução selecionada](../bateria_3000/semente_30000/aprendizado.png) · [Metodologia do treino](../bateria_3000/README.md)

### 4. Roteiro da demonstração

1. Em cerca de 30 segundos, explique por que passar com uma carta na mão pode ser a melhor jogada.
2. Mostre o gráfico e diga quantas partidas compõem a tabela usada no jogo. Expresse 500 como resultado deste protocolo e 1.500 como ponto da confirmação de estabilidade.
3. No jogo, escolha **Novo Jogo**, configure um lado como **Q-learning** e o outro como **Minimax com alfa-beta**, em profundidade 1. Mostre que a partida inicia com a tabela já carregada quando chega o turno do agente.
4. Mostre o antes e depois da semente 60577 no terminal. A política Q sozinha gasta English Support e perde. A versão jogável passa, guarda a carta e vence. Termine com a comparação de posições inéditas e o resultado das partidas completas.

Abra o PowerShell na raiz do projeto e use os comandos abaixo.

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m experiments.q_learning_evolution demonstrar experiments/etapa4/bateria_3000/taticas/guardar_carta_60577.json
```

### Perguntas que podem aparecer

- **“Vocês treinaram o Q-learning contra Minimax?”** O treino alternou entre um adversário aleatório e a política inicial. Minimax simples e alfa-beta foram adversários de avaliação. A busca de final da versão atual é executada durante a decisão em finais pequenos.
- **“A busca de final é o que a tabela aprendeu?”** A tabela foi treinada por recompensa. A busca verifica as consequências pelas regras do jogo durante os finais. A comparação entre as duas versões mantém a tabela igual para medir o efeito da busca.
- **“Por que usar profundidade 1 na demonstração?”** Ela permite jogar a partir da abertura com custo prático. No piloto em profundidade 2, as duas partidas completas atingiram 60 segundos. Profundidade 3 foi útil em posições finais pequenas, que têm menos ações possíveis.
- **“Passar mais foi o objetivo?”** A recompensa é vencer. Nas posições táticas, verificamos se passar ou usar a carta produz o melhor desfecho naquela posição.

## Reprodução da bateria de evolução

```powershell
$saidaEvolucaoQL = 'experiments/reproducao_evolucao_q'
python -m experiments.q_learning_evolution auditoria $saidaEvolucaoQL
python -m experiments.q_learning_evolution posicoes "$saidaEvolucaoQL/avaliacao_tatica" --por-grupo 8 --semente 174000
python -m experiments.q_learning_evolution confrontos "$saidaEvolucaoQL/partidas_politica_inicial" --partidas 200 --semente 205000
python -m experiments.q_learning_evolution confrontos "$saidaEvolucaoQL/partidas_alfa_beta" --partidas 8 --semente 206000 --adversario alfa_beta
python -m experiments.q_learning_evolution resumo $saidaEvolucaoQL
```
