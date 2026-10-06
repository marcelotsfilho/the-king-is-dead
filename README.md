# The King is Dead — modo básico para dois jogadores

Projeto acadêmico em Python e Pygame inspirado em **The King is Dead: Second
Edition**. Esta versão permite jogar uma partida local completa com duas
pessoas, incluindo as oito cartas de ação de cada jogador, disputas de poder,
invasão francesa, coroação e critérios de desempate.

O código usa nomes de pastas e arquivos em inglês. Classes, métodos, variáveis,
mensagens e esta documentação foram escritos em pt-BR para facilitar o estudo e
a apresentação do projeto.

As regras foram implementadas a partir do
[livro oficial de regras](https://www.ospreypublishing.com/media/3yxddtqg/tkid2_rulebook.pdf).

## Instalação

Requisitos:

- Python 3.13;
- Pygame 2.6.1.

No PowerShell:

```powershell
cd C:\Users\markt\Documents\GitHub\the-king-is-dead
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

O ambiente virtual `.venv` isola a dependência do projeto das demais
instalações do computador.

## Como executar

Com o ambiente virtual ativado:

```powershell
python main.py
```

Os nomes iniciais são `Jogador 1` e `Jogador 2`. A partida acontece na mesma
tela e o painel à direita informa de quem é o turno.

A janela calcula automaticamente um tamanho compatível com a resolução do
monitor. Ela também pode ser redimensionada manualmente: o conteúdo mantém a
proporção e os cliques continuam alinhados aos elementos exibidos.

## Como jogar pela interface

No começo do turno, o jogador possui duas alternativas:

1. clicar em uma carta de ação da própria mão; ou
2. clicar em **PASSAR**.

Dois passes consecutivos resolvem a próxima região indicada pela trilha. Uma
carta jogada interrompe a sequência de passes.

Depois de executar uma carta de ação, o mesmo jogador é obrigado a convocar um
seguidor do tabuleiro para sua corte. Para isso, deve clicar primeiro na região
e depois no botão da facção desejada. Somente então o turno passa ao adversário.

Os botões auxiliares são:

- **CANCELAR:** apaga uma seleção ainda não executada;
- **SEM EFEITO:** tenta usar a carta sem executar seu efeito. Isso só é aceito
  quando a regra realmente não permite uma execução completa ou parcial;
- botões **ESCOCESES**, **GALESES** e **INGLESES:** escolhem a facção em uma
  troca ou convocação.

### Assemble

Adiciona um seguidor de cada facção disponível na reserva. Depois de selecionar
a carta, clique em uma região para os Escoceses, outra para os Galeses e outra
para os Ingleses, seguindo a instrução mostrada na tela. As regiões podem ser
iguais. Uma facção sem peças na reserva é ignorada.

### Scottish, Welsh e English Support

Adiciona até dois seguidores da facção indicada em uma única região válida.
Clique na carta e depois na região. A região precisa fazer fronteira com uma
região já controlada pela facção. Enquanto a região natal da facção ainda não
foi resolvida, também são válidas suas vizinhas:

- Escoceses: Moray;
- Galeses: Gwynedd;
- Ingleses: Essex.

### Negotiate

Troca duas cartas ainda ativas na trilha de disputas e coloca o disco de
negociação em uma delas. Clique na primeira posição, na segunda e, por fim, em
uma das duas para escolher onde ficará o disco. Cartas resolvidas ou que já
possuem disco não podem ser escolhidas. Cada jogador usa seu disco uma vez.

### Manoeuvre

Troca um seguidor de uma região por um seguidor de outra região. As regiões não
precisam ser vizinhas. A sequência de cliques é:

1. primeira região;
2. facção que sairá dela;
3. segunda região;
4. facção que sairá da segunda região.

É permitido trocar seguidores da mesma facção. Um jogador não pode desfazer
imediatamente a última Manoeuvre do adversário.

### Outmanoeuvre

Usa a mesma sequência de cliques da Manoeuvre, mas troca um seguidor da primeira
região por dois seguidores da mesma facção na segunda. As regiões devem ser
vizinhas. Se nenhuma troca de um por dois existir no tabuleiro, deve ser feita
uma troca parcial de um por um, quando possível. Também não é permitido desfazer
imediatamente a Outmanoeuvre adversária.

## Disputas e fim da partida

Depois de dois passes consecutivos, a primeira carta ativa da trilha é
resolvida:

- a facção com maioria única controla a região;
- empate na maior quantidade, inclusive uma região vazia, gera instabilidade;
- todos os seguidores dessa região voltam para a reserva;
- a carta da trilha é virada para baixo e a região não pode mais ser alterada.

A partida termina de duas formas:

- **Invasão francesa:** ocorre na terceira instabilidade. Vence quem tiver mais
  conjuntos completos na corte, sendo cada conjunto formado por um seguidor de
  cada facção. Em empate, vence quem jogou a carta de ação mais recentemente;
- **Coroação:** ocorre depois da oitava disputa. As facções são ordenadas pelo
  número de regiões controladas; empates entre facções usam a vitória regional
  mais recente. Compara-se primeiro a quantidade da facção mais poderosa na
  corte de cada jogador e depois a segunda mais poderosa. Persistindo o empate,
  vence quem esvaziou sua mão primeiro.

## Arquitetura MVC

```text
Clique do usuário
      ↓
Controller interpreta a seleção
      ↓
Model valida a regra e altera EstadoJogo
      ↓
View lê o estado e redesenha a tela
```

- **Model:** contém os dados e todas as regras. Não conhece o Pygame.
- **View:** apenas desenha e identifica áreas clicadas. Não decide se uma
  jogada é válida.
- **Controller:** mantém a seleção temporária do usuário e chama operações do
  Model.

Essa separação permite testar as regras sem abrir a janela e evita misturar
cálculos do jogo com coordenadas da interface.

## Estrutura do projeto

```text
the-king-is-dead/
├── controller/
│   └── game_controller.py
├── model/
│   ├── action_card.py
│   ├── board.py
│   ├── dispute_track.py
│   ├── enums.py
│   ├── game.py
│   ├── game_setup.py
│   ├── game_state.py
│   ├── player.py
│   ├── region.py
│   ├── region_card.py
│   └── supply.py
├── tests/
├── view/
│   ├── constants.py
│   └── game_view.py
├── main.py
├── README.md
└── requirements.txt
```

## Responsabilidade de cada arquivo e método

### `main.py`

- `principal()`: inicializa o Pygame, cria Model, View e Controller, executa a
  aplicação e encerra o Pygame ao fechar a janela.

### `model/enums.py`

- `Faccao`: fornece identidades fixas para Escoceses, Galeses e Ingleses;
- `TipoCartaAcao`: identifica os sete efeitos das oito cartas;
- `TipoJogada`: distingue passe e uso completo de carta;
- `FaseTurno`: impede ações fora de ordem com as fases `ESCOLHER_ACAO`,
  `CONVOCAR_SEGUIDOR` e `ENCERRADO`.

### `model/action_card.py`

- `CartaAcao.__init__(tipo)`: valida o tipo e guarda nome e descrição;
- `criar_conjunto_padrao()`: cria as oito cartas independentes de um jogador,
  com duas Assemble e uma de cada outro tipo;
- `eh_carta_de_apoio(tipo)`: identifica as três cartas Support;
- `obter_dados_da_carta_de_apoio(tipo)`: informa sua facção e região inicial.

### `model/region.py`

- `Regiao.__init__(nome)`: cria uma região sem seguidores;
- `obter_seguidores()`: retorna uma cópia das quantidades;
- `quantidade_de_seguidores(faccao)`: consulta uma facção;
- `adicionar_seguidores(...)` e `remover_seguidores(...)`: alteram quantidades
  sem aceitar valores inválidos ou regiões resolvidas;
- `remover_todos_os_seguidores()`: esvazia a região e informa o que saiu;
- `total_de_seguidores()`: soma as três facções;
- `definir_controlador(faccao)`: registra uma vitória regional;
- `marcar_como_instavel()`: resolve a região sem controlador;
- `esta_resolvida()`: informa se a região já saiu do jogo;
- métodos iniciados por `_validar`: protegem as regras internas da classe.

### `model/board.py`

- `Tabuleiro.__init__()`: cria as oito regiões e o grafo de fronteiras;
- `obter_regioes()` e `obter_nomes_das_regioes()`: consultam o catálogo;
- `obter_regiao(nome)`: encontra o objeto de uma região;
- `regioes_adjacentes(nome)`: retorna suas vizinhas;
- `sao_adjacentes(a, b)`: verifica uma fronteira;
- `quantidade_instabilidades()`: calcula o total pelas próprias regiões;
- `_validar_nome()` e `_validar_grafo()`: detectam dados desconhecidos ou um
  grafo inconsistente.

### `model/region_card.py`

- `CartaRegiao.__init__(nome_regiao)`: cria uma disputa ativa e sem disco;
- `virar_para_baixo()` e `virar_para_cima()`: alteram o estado da carta;
- `colocar_disco_negociacao()` e `remover_disco_negociacao()`: controlam o
  marcador usado por Negotiate.

### `model/dispute_track.py`

- `TrilhaDisputas.__init__(nomes_regioes)`: exige oito nomes únicos;
- `obter_cartas()`: retorna uma cópia da lista;
- `obter_carta(posicao)`: consulta posições numeradas de 1 a 8;
- `obter_proxima_carta()`: encontra a próxima disputa ativa;
- `quantidade_resolvida()`: conta cartas viradas;
- `trocar_cartas(a, b)`: executa a mudança de ordem de Negotiate.

### `model/player.py`

- `Jogador.__init__(nome)`: cria mão, descarte, corte e disco;
- `obter_mao()` e `obter_descarte_mao()`: retornam cópias das cartas;
- `adicionar_carta_mao(carta)`: entrega uma carta;
- `possui_carta(carta)`: confirma que a carta pode ser usada;
- `quantidade_cartas()`: informa o tamanho da mão;
- `usar_carta(carta)`: move a carta para o descarte;
- `obter_corte()` e `qtd_na_corte(faccao)`: consultam a corte;
- `adicionar_seguidor_na_corte()` e `remover_seguidor_da_corte()`: alteram a
  corte sem permitir contagem negativa;
- `usar_disco_negociacao()`: consome o disco de uso único.

### `model/supply.py`

- `ReservaSeguidores.__init__(quantidade_por_faccao)`: cria a reserva;
- `obter_quantidades()`, `quantidade(faccao)` e `total()`: fazem consultas;
- `retirar(...)` e `devolver(...)`: movimentam peças;
- `_validar_quantidade()`: exige um inteiro positivo.

### `model/game_state.py`

- `EstadoJogo.__init__(...)`: reúne tabuleiro, trilha, jogadores e reserva e
  inicia turno, última ação, fase e resultado;
- `obter_jogadores()`: retorna uma cópia da lista;
- `obter_jogador_atual()`: informa de quem é o turno;
- `avancar_jogador()`: alterna entre os dois jogadores.

O estado também guarda `ultima_acao`, `ultimo_jogador_que_agiu`,
`ordem_jogadores_sem_cartas`, `fase_turno`, passes e informações do vencedor.
As quantidades de disputas e instabilidades são calculadas diretamente pela
trilha e pelo tabuleiro, evitando guardar a mesma informação duas vezes.

### `model/game_state_serializer.py`

- `serializar(estado)`: cria uma fotografia composta por dados simples;
- `restaurar(dados)`: reconstrói um `EstadoJogo` independente;
- `copiar(estado)`: combina as duas operações para futuras simulações.

### `model/legal_move.py`

- `Jogada`: representa um passe ou uma carta completa com efeito e convocação;
- `obter_parametros()`: devolve uma cópia das escolhas da carta;
- `eh_passe()` e `eh_carta()`: identificam a natureza da jogada;
- `possui_mesmos_dados()`: compara todas as escolhas de duas jogadas;
- `descrever()`: produz um resumo para apresentação.

### `model/game_setup.py`

- `ConfiguracaoJogo.__init__(semente)`: cria um gerador aleatório que pode ser
  reproduzido nos testes;
- `criar_trilha_disputas(tabuleiro)`: embaralha as regiões;
- `criar_estado_inicial(nomes_jogadores)`: monta uma partida completa;
- `_entregar_cartas_ao_jogador()`: entrega o conjunto padrão;
- `_colocar_seguidores_das_regioes_iniciais()`: prepara Moray, Gwynedd e Essex;
- `_distribuir_seguidores_para_as_cortes()`: sorteia duas peças por jogador;
- `_completar_seguidores_das_regioes()`: deixa quatro peças em cada região;
- `_sortear_faccao_disponivel()`: sorteia sem ultrapassar a reserva;
- `_validar_nomes_jogadores()`: exige exatamente dois nomes.

### `model/game.py`

Métodos públicos, chamados pelo Controller:

- `passar()`: registra o passe e, no segundo passe, resolve uma disputa;
- `jogar_carta(carta, parametros)`: valida a carta, encaminha ao efeito correto,
  descarta a carta e muda a fase para convocação;
- `convocar_seguidor(regiao, faccao)`: move uma peça do tabuleiro para a corte e
  encerra o turno;
- `resolver_proxima_disputa()`: calcula maioria, controle ou instabilidade,
  devolve peças à reserva e verifica o fim;
- `obter_regioes_validas_para_apoio(tipo)`: calcula destinos de Support.

Métodos internos que dividem as regras em etapas menores:

- `_executar_assemble()`, `_executar_apoio()`, `_executar_negociar()`,
  `_executar_manobra()` e `_executar_superar_manobra()`: implementam os efeitos;
- `_obter_dados_de_troca()`: valida a seleção comum às duas trocas;
- `_obter_posicoes_validas_para_negociar()`: filtra cartas disponíveis;
- métodos `_existe_...`: descobrem se uma execução total ou parcial é possível;
- métodos `_validar_...nao_desfaz_acao()`: protegem a restrição de repetição;
- `_registrar_carta_jogada()`: atualiza mão, última ação, passes e fase;
- `_validar_carta_do_jogador()`, `_validar_convocacao_possivel()`,
  `_validar_fase()` e `_validar_partida_em_andamento()`: bloqueiam comandos
  inválidos;
- `_determinar_faccao_controladora()`: encontra uma maioria única;
- `_devolver_seguidores_para_reserva()`: conserva as peças;
- métodos `_finalizar_...` e `_determinar_vencedor_...`: implementam invasão,
  coroação e desempates;
- métodos `_ordenar_...`, `_quantidade_...` e `_indice_...`: fazem os cálculos
  auxiliares de pontuação.

### `controller/game_controller.py`

- `__init__(jogo, visao)`: recebe as outras camadas e inicia seleções;
- `executar()`: mantém o loop de eventos e desenho em 60 quadros por segundo;
- `_processar_eventos()` e `_processar_clique()`: encaminham cliques;
- métodos `_processar_...`: montam, passo a passo, os parâmetros de cada ação;
- `_tentar_jogar_carta()`: chama o Model e transforma erros em instruções;
- `_atualizar_instrucao_da_carta()`: explica a próxima seleção;
- `_limpar_selecao()`: cancela dados temporários;
- `_obter_selecao()`: entrega à View somente o necessário para destacar itens.

### `view/constants.py`

Centraliza cores, tamanhos e posições. Isso mantém detalhes visuais fora do
Model e facilita mudar o layout sem alterar regras. `LARGURA_JANELA` e
`ALTURA_JANELA` representam a área lógica do desenho, não uma resolução que o
monitor seja obrigado a utilizar. `ROTAS_FRONTEIRAS` guarda apenas desvios
visuais para as ligações longas não atravessarem as caixas das regiões; ela
não define quais regiões são vizinhas.

### `view/game_view.py`

- `desenhar(...)`: redesenha a tela completa;
- métodos `botao_...foi_clicado()` e `obter_...clicada()`: identificam áreas;
- `_calcular_tamanho_inicial_da_janela()`: escolhe um tamanho que caiba no
  monitor;
- `_calcular_escala_e_deslocamento()`: mantém proporção e centralização;
- `_apresentar_tela_redimensionada()`: adapta o desenho à janela real;
- `_converter_para_posicao_logica()`: mantém os cliques corretos após a escala;
- `_desenhar_fronteiras()`: consulta o grafo do `Tabuleiro` e desenha cada
  fronteira como uma seta dupla;
- `_obter_fronteiras_sem_repeticao()`: evita desenhar duas vezes uma ligação
  bidirecional;
- `_obter_pontos_da_fronteira()`: aplica os desvios puramente visuais das
  ligações mais longas;
- métodos `_desenhar_...`: desenham título, regiões, trilha, painel, mão,
  mensagens e controles;
- `_obter_retangulo_carta()`: calcula a área de cada carta;
- `_quebrar_texto()` e métodos de texto: mantêm os textos dentro das áreas.

O prefixo `_` indica um detalhe interno da classe ou do arquivo. É uma
convenção de Python: o código continua acessível, mas outras classes devem usar
preferencialmente os métodos públicos.

## Testes automatizados

Execute:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

A pasta `tests` verifica unidades pequenas e independentes. O arquivo
`test_actions.py` cobre o ciclo das cartas, execuções parciais, jogadas
inválidas, convocação e restrições contra desfazer a ação adversária.
`test_game.py` cobre turnos, disputas, fim, desempates e uma partida completa
por passes. Os demais arquivos acompanham uma classe do Model.

## Decisões de implementação para explicar na apresentação

- O tabuleiro é um **grafo**: cada região é um ponto e cada fronteira é uma
  ligação. As setas duplas da interface representam essas ligações
  bidirecionais. A trilha é separada porque representa ordem, não geografia.
- `Enum` evita comparar textos digitados livremente e reduz erros de escrita.
- O `EstadoJogo` reúne a fotografia da partida; o `Jogo` contém as regras que
  alteram essa fotografia.
- Os métodos retornam cópias de listas e dicionários para evitar que outra
  classe altere dados internos sem validação.
- A fase do turno funciona como uma pequena máquina de estados e impede passar
  ou jogar outra carta antes da convocação obrigatória.
- O histórico existe porque algumas regras dependem do passado: última ação,
  última vitória de facção e primeiro jogador que esvaziou a mão.
- Os testes usam uma semente aleatória ou estados montados manualmente para que
  o resultado seja previsível e repetível.
