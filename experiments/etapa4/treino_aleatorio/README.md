# Q-learning com jogadas aleatórias contra a heurística

O modo `--jogadas-aleatorias-contra-heuristica` mantém a política heurística inicial como oponente em todas as partidas de treino. Em cada turno do Q-learning, o gerador sorteia o passe ou um tipo de carta e, para uma carta, sorteia também os parâmetros legais e a convocação. A tabela registra o tipo da ação executada e recebe `+1` por vitória, `−1` por derrota e `0` por empate. A pontuação heurística continua sendo usada para representar a posição e, na avaliação, para concretizar o tipo de ação escolhido pela tabela.

Em cada uma das três execuções, uma tabela vazia foi treinada por 5.000 partidas, alternando o lado do agente e quem começava. A exploração ficou em 100% do início ao fim. A validação reutilizou as mesmas 400 partidas com a tabela congelada, antes do treino e a cada 1.000 partidas. A seleção priorizou o maior número de vitórias na validação, depois o menor número de partidas de treino e a menor semente. As três execuções em paralelo, incluindo a validação, terminaram em cerca de 7 minutos e 43 segundos nesta máquina.

## Validação e seleção

| Semente de treino | Inicial | 1.000 | 2.000 | 3.000 | 4.000 | 5.000 |
|---|---:|---:|---:|---:|---:|---:|
| 650000 | 195 | 221 | 223 | 232 | 219 | 225 |
| 660000 | 195 | 277 | 234 | 261 | 227 | 246 |
| 670000 | 195 | **279** | 209 | 236 | 232 | 262 |

Os números são vitórias em 400 partidas. A tabela selecionada foi a da semente **670000 após 1.000 partidas**. No checkpoint escolhido, 98,23% dos turnos da validação passaram por estados já registrados. O desempenho variou entre sementes e checkpoints. [Tabela selecionada](tabela_selecionada.json) · [Dados de seleção](selecao.json)

## Avaliação reservada

Na avaliação reservada, cada política enfrentou a mesma heurística em 800 partidas, com 400 sementes distintas e troca de lados. O intervalo de confiança das diferenças foi calculado por reamostragem dos pares de partidas por semente.

| Política avaliada | Vitórias | Derrotas | Empates | Taxa de vitória |
|---|---:|---:|---:|---:|
| Nova tabela Q | 564 | 236 | 0 | **70,50%** |
| Tabela Q anterior | 506 | 293 | 1 | 63,25% |
| Sorteio de jogadas completas | 452 | 348 | 0 | 56,50% |
| Política heurística inicial | 393 | 393 | 14 | 49,13% |

A tabela selecionada ganhou **7,25 pontos percentuais** sobre a anterior (IC de 95% de 2,50 a 12,00 pontos) e **14,00 pontos** sobre o sorteio de jogadas (IC de 95% de 9,63 a 18,37 pontos). As tabelas foram avaliadas com a exploração desligada e sem busca de final. [Resumo da análise pareada](reservada_resumo.json)

## Verificações no jogo

A tabela selecionada carregou no controlador e executou uma jogada pelo fluxo normal do jogo. Os 362 testes automatizados passaram. Repetir as 1.000 partidas com a semente 670000 reproduziu todos os valores Q da tabela selecionada. Nas 35 posições táticas já armazenadas, a nova tabela encontrou uma jogada ótima em 22 posições, ante 23 com a tabela anterior. Com a busca de final ativada, ambas acertaram as 35. [Resultados por posição](avaliacao_tatica.csv)

## Reprodução do treino

Execute no PowerShell a partir da raiz do projeto com o ambiente virtual ativado.

```powershell
$saidaTreinoQL = 'experiments/reproducao_treino_aleatorio'
foreach ($sementeTreinoQL in 650000,660000,670000) {
    python main_q_learning.py treinar --jogadas-aleatorias-contra-heuristica --partidas 5000 --intervalo 1000 --validacao 400 --semente $sementeTreinoQL --semente-validacao 700000 --salvar-checkpoints --saida "$saidaTreinoQL/semente_$sementeTreinoQL"
}
python main_q_learning.py avaliar --partidas 800 --semente 710000 --adversarios politica_inicial --tabela "$saidaTreinoQL/semente_670000/checkpoints/01000.json" --saida "$saidaTreinoQL/reservada_tabela_selecionada.csv"
```
