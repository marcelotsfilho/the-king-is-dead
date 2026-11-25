# Otimização da busca de jogadas

A busca usa a mesma versão da heurística do commit de referência `d25e2bd`. A primeira alteração troca a serialização seguida de restauração por uma cópia direta no executor. A segunda prioriza, nos nós internos do alfa-beta, a melhor resposta com carta encontrada em outro ramo no mesmo nível para o mesmo jogador. O passe continua sendo gerado primeiro. A raiz mantém a ordem original, preservando o desempate.

## Método

Foram medidas três versões em Windows 11 e Python 3.13.14, com `PYTHONHASHSEED=0` e sem renderização. Cada posição foi medida nas profundidades 1, 2 e 3, com três repetições por versão, alternando a ordem das versões e usando um limite de 12 s por decisão. O cenário reduzido também foi executado com Minimax sem poda. Três verificações adicionais em profundidade 2 usaram um limite de 45 s para obter a decisão completa em mais casos. As 225 tentativas incluem o status, o tempo, os totais de nós, folhas, cópias e cortes, a pontuação e a jogada completa. [Medições](medicoes.csv)

As aberturas foram geradas com as seeds 42, 53000 e 7. O meio de jogo inclui o turno 8 da seed 0 já arquivado e dois estados reproduzidos com `random.Random(seed)`. Para estes, em cada turno, `random() < 0.42` escolhe passar e os demais valores executam `GeradorJogadas.sortear_com_estado` com o mesmo gerador aleatório. A posição foi salva após 12 turnos na seed 7 e 22 turnos na seed 19. [Turno 8 da seed 0](../bateria_algoritmos_20261121_134131/states/seed0_turn8.json)

## Resultados

Nos casos com três conclusões, a tabela mostra a mediana. Quando houve uma única conclusão, a tabela indica `1/3`. `Limite` indica que todas as tentativas atingiram o limite de 12 s.

| Posição | Prof. | Código anterior | Cópia direta | Cópia direta e ordenação |
|---|---:|---:|---:|---:|
| Abertura 42 | 1 | 3,324 s | 1,284 s | 1,399 s |
| Abertura 42 | 2 | Limite | 8,523 s (1/3) | 8,291 s (1/3) |
| Abertura 42 | 3 | Limite | Limite | Limite |
| Abertura 53000 | 1 | 3,391 s | 1,341 s | 1,252 s |
| Abertura 53000 | 2 | 8,744 s (1/3) | 2,889 s | 3,761 s |
| Abertura 53000 | 3 | Limite | Limite | Limite |
| Abertura 7 | 1 | 3,356 s | 1,192 s | 1,200 s |
| Abertura 7 | 2 | Limite | Limite | Limite |
| Abertura 7 | 3 | Limite | Limite | Limite |
| Seed 0, turno 8 | 1 | 0,540 s | 0,262 s | 0,309 s |
| Seed 0, turno 8 | 2 | Limite | 10,504 s (1/3) | 2,461 s |
| Seed 0, turno 8 | 3 | Limite | Limite | Limite |
| Seed 7, turno 12 | 1 | 0,333 s | 0,180 s | 0,146 s |
| Seed 7, turno 12 | 2 | 1,922 s | 0,759 s | 0,882 s |
| Seed 7, turno 12 | 3 | Limite | Limite | Limite |
| Seed 19, turno 22 | 1 | 0,031 s | 0,011 s | 0,012 s |
| Seed 19, turno 22 | 2 | 0,521 s | 0,209 s | 0,225 s |
| Seed 19, turno 22 | 3 | 4,437 s | 1,391 s | 1,193 s |

As verificações em profundidade 2 com limite de 45 s mostraram os seguintes resultados, com uma tentativa por versão.

| Posição | Código anterior | Cópia direta | Cópia direta e ordenação |
|---|---:|---:|---:|
| Abertura 42 | 19,071 s | 9,519 s | 9,956 s |
| Abertura 7 | Limite de 45 s | 28,536 s | 16,705 s |
| Seed 0, turno 8 | 22,131 s | 10,633 s | 3,212 s |

Na seed 0, turno 8, a ordenação reduziu as cópias de 99.938 para 25.239 em profundidade 2. Na seed 19, turno 22, reduziu as cópias de 19.156 para 15.240 em profundidade 3. Na abertura 53000 em profundidade 2, as três versões visitaram a mesma quantidade de nós. A magnitude do ganho adicional da ordenação depende da posição.

## Correção e funcionamento

- Em todas as buscas concluídas na mesma posição e profundidade, as versões retornaram a mesma jogada e pontuação. O cenário reduzido também coincidiu entre Minimax e alfa-beta nas três profundidades.
- As versões produziram os mesmos 46.778 sucessores imediatos, na ordem original, somando as sete posições. Foram comparados os dados completos de cada jogada e do estado resultante.
- Os 351 testes automatizados passaram. Uma partida entre duas IAs rodou no loop do Pygame com vídeo virtual, usou profundidade 2 na primeira decisão e profundidade 1 nas seguintes. Terminou por coroação em 36 turnos e pôde ser salva e recarregada.

## Perfil após as mudanças

Na versão otimizada, a cópia representou 49,8% do tempo instrumentado em profundidade 2 na abertura 53000 e 44,8% em profundidade 3 no turno 22 da seed 19. A avaliação das folhas representou 30,8% e 35,4%, respectivamente.
