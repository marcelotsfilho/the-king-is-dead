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
- Pygame 2.6.1;
- Graphviz, usado somente para exportar a árvore completa.

No PowerShell:

```powershell
cd C:\Users\markt\Documents\GitHub\the-king-is-dead
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

No Windows, o programa Graphviz pode ser instalado com:

```powershell
winget install --id Graphviz.Graphviz --exact
```

Depois da instalação, feche e abra novamente o terminal para atualizar o
`PATH`. O jogo continua funcionando sem Graphviz; somente a criação do SVG
fica indisponível e o arquivo DOT ainda é gerado.

O ambiente virtual `.venv` isola a dependência do projeto das demais
instalações do computador.

## Como executar

Com o ambiente virtual ativado:

```powershell
python main.py
```

O jogo começa em uma tela inicial com três opções:

- **NOVO JOGO:** cria uma partida desde o estado inicial;
- **CONTINUAR JOGO:** carrega `saves/state_tree.json` e fica desativado quando
  não existe uma partida salva;
- **SAIR:** fecha a aplicação sem criar uma partida.

Se o arquivo salvo estiver inválido, o jogo volta ao menu e apresenta uma
mensagem de erro. Os nomes iniciais são `Jogador 1` e `Jogador 2`. A partida
acontece na mesma tela e o painel à direita informa de quem é o turno.

A janela calcula automaticamente um tamanho compatível com a resolução do
monitor. Ela também pode ser redimensionada manualmente: o conteúdo mantém a
proporção e os cliques continuam alinhados aos elementos exibidos.

Durante a partida, o botão **ÁRVORE** abre a representação visual do histórico.
O botão **VOLTAR** restaura o estado anterior quando não existe uma carta ou
convocação pendente.

Ao fechar o jogo, a árvore atual é gravada em
`saves/state_tree.json`. O mesmo arquivo também é salvo automaticamente
quando a partida termina. Durante a partida, o botão **SALVAR** permite gravar
manualmente o estado atual e apresenta uma confirmação no quadro de
instruções. Para continuar, use o botão **CONTINUAR JOGO**.

O argumento abaixo foi mantido como uma alternativa para carregar diretamente
pelo terminal, sem passar pelo menu:

```powershell
python main.py --carregar
```

O comando sem `--carregar` abre a tela inicial.

Para executar a demonstração textual da árvore de estados:

```powershell
python main_tree.py
```

A posição inicial possui muitas combinações completas. Por isso, a geração do
primeiro nível pode levar alguns segundos. A demonstração mostra vinte filhos
e informa quantos foram omitidos da impressão, mas todos permanecem registrados
na árvore.

## Segunda entrega — árvore de estados

Na segunda etapa, cada nó representa uma fotografia completa da partida depois
de uma jogada. Uma jogada de carta inclui seu efeito, a convocação obrigatória
e a troca do jogador atual. O passe também inclui suas consequências, como a
resolução automática de uma disputa depois de dois passes.

O fluxo implementado é:

```text
Estado do nó atual
        ↓
Gerador encontra jogadas completas possíveis
        ↓
Executor aplica cada jogada em uma cópia
        ↓
Comparador descarta estados já existentes
        ↓
Novos estados são ligados como filhos do nó atual
```

A árvore cresce sob demanda. Apenas o nó atual pode ser expandido. Portanto,
os filhos de uma jogada que ainda não foi escolhida não são gerados. Quando o
jogador avança para um filho, esse novo nó poderá ser expandido. Ao voltar, o
estado anterior é recuperado sem recalcular a partida.

Uma jogada feita na interface é registrada imediatamente, mesmo que as demais
opções daquele nível ainda não tenham sido geradas. Se o nível já tiver sido
expandido, a árvore encontra e reutiliza o filho correspondente em vez de criar
outro nó.

### Visualização no Pygame

O botão **ÁRVORE** mostra duas áreas:

- **Caminho percorrido:** estados realmente visitados desde a raiz. O nó azul é
  o estado atual e os nós verdes são seus antecessores;
- **Próximas jogadas:** filhos já conhecidos do estado atual, limitados a sete
  por página.

O botão **GERAR OPÇÕES** calcula todas as jogadas completas possíveis somente
para o estado atual. Essa ação não é automática porque o início da partida pode
produzir milhares de combinações e levar alguns segundos. Os botões
**ANTERIOR** e **PRÓXIMA** percorrem as páginas sem tentar desenhar todos os nós
ao mesmo tempo.

Os marcadores da apresentação textual significam:

- `[ATUAL]`: posição atual da partida;
- `[CAMINHO]`: estado que faz parte do caminho entre a raiz e o nó atual;
- `[NÃO VISITADO]`: alternativa gerada, mas não escolhida.

### Visualização completa pelo Graphviz

Na tela da árvore, o botão **ABRIR GRAPHVIZ** exporta todos os estados que já
foram registrados naquele momento. A exportação gera:

- `saves/state_tree.dot`: descrição textual entendida pelo Graphviz;
- `saves/state_tree.svg`: diagrama vetorial que pode ser ampliado sem perder
  qualidade e é aberto no navegador padrão.

O nó atual aparece em azul, o caminho visitado em verde e as alternativas não
visitadas em cinza. Cada caixa informa índice, nível, jogada de origem e se as
opções daquele nó já foram geradas. As setas representam a relação entre pai e
filho.

A exportação é manual porque árvores com milhares de estados podem demorar e
produzir um SVG muito grande. Assim, uma jogada comum continua rápida. Depois
de qualquer jogada, basta abrir a tela **ÁRVORE** e solicitar uma nova
exportação para obter a versão completa e atualizada.

### Salvar e carregar a árvore

A árvore é salva em JSON porque o projeto já representa estados e jogadas por
dicionários, listas, textos e números. Esse formato é legível, faz parte da
biblioteca padrão do Python e não exige outra dependência.

```python
from model.state_tree_serializer import SerializadorArvoreEstados

serializador = SerializadorArvoreEstados()
serializador.salvar(arvore, "arvore_da_partida.json")

arvore_carregada = serializador.carregar("arvore_da_partida.json")
```

O arquivo guarda os estados, as jogadas, a relação entre pais e filhos, quais
nós já foram expandidos e qual era o nó atual. A marcação do caminho visitado é
reconstruída no carregamento.

No fluxo normal não é necessário chamar esses métodos manualmente. O Controller
salva `saves/state_tree.json` ao encerrar a aplicação ou concluir a partida, e
o botão **CONTINUAR JOGO** restaura a árvore e usa uma cópia do nó atual como
estado do jogo. Durante a leitura, o menu apresenta a mensagem de carregamento.

O salvamento manual ou automático acontece desta forma:

1. o `ControladorJogo` solicita o salvamento quando o jogador clica em
   **SALVAR**, fecha a janela ou finaliza a partida;
2. `SerializadorArvoreEstados` transforma cada nó, estado e jogada em
   dicionários e listas;
3. esses dados são escritos em `saves/state_tree.json`;
4. também são guardados o pai de cada nó, o nó atual e a informação de quais
   nós já foram expandidos.

O carregamento faz o caminho inverso:

1. o menu verifica se o arquivo existe antes de habilitar **CONTINUAR JOGO**;
2. `SerializadorArvoreEstados` lê e valida o JSON;
3. os estados e as jogadas são reconstruídos;
4. as relações entre pais e filhos são refeitas;
5. a árvore avança até o nó que era o atual no momento do salvamento;
6. o `Jogo` recebe uma cópia desse estado e a partida continua no Pygame.

Uma seleção incompleta de carta não é salva como jogada. A árvore registra
somente passes completos ou ações que já incluam a convocação obrigatória.

### Alterações finais da segunda entrega e seus motivos

- `model/state_tree.py` recebeu `registrar_jogada_realizada()` para centralizar
  a procura ou criação do filho correspondente. O Controller não precisa
  repetir regras de comparação;
- `controller/game_controller.py` passou a guardar a árvore, formar uma
  `Jogada` somente depois que carta e convocação foram concluídas, restaurar o
  estado ao voltar e solicitar salvamento. Assim, uma escolha parcial nunca
  vira nó;
- o mesmo Controller passou a combinar o nome, `descricao` e próximo passo da
  carta selecionada. Isso cria a legenda solicitada sem repetir o texto das
  cartas na View;
- o botão **SALVAR** passou a solicitar a gravação imediatamente e informar o
  resultado no quadro de instruções. O salvamento automático foi mantido como
  proteção;
- `view/game_view.py` recebeu a tela paginada e os botões da árvore. A View
  continua apenas desenhando e identificando cliques, sem validar regras;
- `main.py` passou a iniciar uma árvore nova ou carregar o JSON existente e
  entrega a mesma árvore ao Controller;
- a tela inicial passou a oferecer novo jogo, continuação e saída. A opção de
  continuar só aceita um arquivo existente e erros de leitura são apresentados
  no próprio menu;
- `view/state_tree_graphviz_view.py` passou a transformar todos os nós
  registrados em DOT e solicitar ao Graphviz a criação do SVG. Essa View não
  altera estados nem repete regras do jogo;
- `.gitignore` passou a ignorar `saves/` porque os arquivos dessa pasta são
  resultados de partidas locais, não código-fonte;
- os testes de `main.py`, Controller, árvore e View passaram a verificar
  carregamento, registro, volta, salvamento, abertura da tela e paginação.

## Como jogar pela interface

No começo do turno, o jogador possui duas alternativas:

1. clicar em uma carta de ação da própria mão; ou
2. clicar em **PASSAR**.

Dois passes consecutivos resolvem a próxima região indicada pela trilha. Uma
carta jogada interrompe a sequência de passes.

Depois de executar uma carta de ação, o mesmo jogador é obrigado a convocar um
seguidor do tabuleiro para sua corte. Para isso, deve clicar primeiro na região
e depois no botão da facção desejada. Somente então o turno passa ao adversário.

Ao clicar em uma carta, a área **O que fazer agora** apresenta três informações:

1. o nome da carta selecionada;
2. uma explicação curta do seu efeito;
3. o próximo clique necessário para continuar a jogada.

Foi escolhida uma ajuda textual em vez de imagens porque as descrições já fazem
parte de `CartaAcao`. Assim, a interface reutiliza o Model, não exige arquivos
externos e evita que a explicação visual fique diferente da regra implementada.

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
│   ├── game_controller.py
│   └── start_menu_controller.py
├── model/
│   ├── action_card.py
│   ├── board.py
│   ├── dispute_track.py
│   ├── enums.py
│   ├── game.py
│   ├── game_setup.py
│   ├── game_state.py
│   ├── game_state_serializer.py
│   ├── legal_move.py
│   ├── legal_move_executor.py
│   ├── legal_move_generator.py
│   ├── player.py
│   ├── region.py
│   ├── region_card.py
│   ├── state_node.py
│   ├── state_tree.py
│   ├── state_tree_serializer.py
│   └── supply.py
├── tests/
├── view/
│   ├── constants.py
│   ├── game_view.py
│   ├── state_tree_graphviz_view.py
│   └── state_tree_view.py
├── main.py
├── main_tree.py
├── saves/                 # criado durante a execução
├── README.md
└── requirements.txt
```

## Responsabilidade de cada arquivo e método

### `main.py`

- `_preparar_arvore(argumentos, serializador)`: carrega
  `saves/state_tree.json` quando existe `--carregar`; caso contrário, cria um
  novo estado e sua raiz;
- `_escolher_arvore_pelo_menu(...)`: repete a tela inicial até criar, carregar
  ou sair; se o JSON for inválido, mantém o menu aberto com uma mensagem;
- `principal()`: prepara a pasta de salvamento, inicializa Pygame, Model, View,
  menu, árvore e Controller, executa a aplicação e encerra o Pygame.

### `main_tree.py`

- `principal()`: cria um estado inicial reproduzível, expande somente a raiz e
  apresenta uma amostra da árvore no terminal.

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
- `copiar(estado)`: combina as duas operações para futuras simulações;
- `obter_identificador(estado)`: gera um texto estável com os dados relevantes;
- `possuem_mesmo_estado(primeiro, segundo)`: verifica se dois estados possuem
  as mesmas informações capazes de influenciar a partida;
- `_obter_dados_relevantes()`: retira da comparação apenas dados de interface.

A comparação ignora apenas `ultima_mensagem`, pois ela serve para orientar a
interface e não modifica as próximas jogadas. A última ação continua fazendo
parte da comparação porque algumas cartas não podem desfazer imediatamente a
ação do adversário.

### `model/legal_move.py`

- `Jogada`: representa um passe ou uma carta completa com efeito e convocação;
- `obter_parametros()`: devolve uma cópia das escolhas da carta;
- `eh_passe()` e `eh_carta()`: identificam a natureza da jogada;
- `possui_mesmos_dados()`: compara todas as escolhas de duas jogadas;
- `descrever()`: produz um resumo para apresentação;
- `_descrever_efeito()`: detalha destinos, trocas ou ausência de efeito;
- `serializar_jogada()`: converte passe ou carta para dados simples;
- `restaurar_jogada()`: reconstrói uma jogada salva;
- `_serializar_parametros()` e `_restaurar_parametros()`: convertem as facções
  presentes nos parâmetros sem perder seus tipos.

### `model/legal_move_executor.py`

- `ExecutorJogada.executar(estado, jogada)`: copia o estado, aplica uma jogada
  completa e devolve o resultado sem modificar a partida original;
- `_obter_carta_do_jogador()`: encontra na cópia a carta indicada pela jogada.

Esse executor será compartilhado pela árvore e pela futura IA. Um passe inclui
suas consequências automáticas; uma carta inclui efeito, convocação e troca de
jogador.

### `model/legal_move_generator.py`

- `GeradorJogadas.gerar(estado)`: encontra todas as jogadas completas que o
  jogador atual pode realizar sem modificar o estado recebido;
- os métodos `_gerar_parametros_*()`: enumeram as escolhas de cada tipo de
  carta;
- `_simular_carta()`: aplica temporariamente apenas o efeito da carta para
  descobrir quais seguidores poderão ser convocados;
- `_adicionar_se_valida()`: utiliza o executor como verificação final antes de
  incluir uma jogada no resultado.

O gerador não substitui as regras de `Jogo`. Ele cria combinações possíveis e
reutiliza o executor para descartar aquelas que forem rejeitadas pelo model.
Cartas repetidas do mesmo tipo, como as duas Assemble, são processadas uma única
vez porque produzem as mesmas escolhas.

Como uma única carta pode gerar muitas combinações, a futura árvore deverá ser
expandida sob demanda: somente os filhos do estado que está sendo analisado
serão criados, sem antecipar os netos de jogadas que ainda não aconteceram.

### `model/state_node.py`

- `NoEstado.__init__()`: copia e protege um estado, além de guardar pai e
  jogada de origem;
- `obter_estado()`: devolve uma cópia para proteger o histórico armazenado;
- `obter_identificador()`: devolve a chave estável usada contra repetições;
- `obter_jogada_origem()`: informa qual jogada criou o nó;
- `obter_pai()`: permite voltar ao estado anterior;
- `obter_filhos()` e `quantidade_filhos()`: consultam o próximo nível sem
  expor a lista interna;
- `adicionar_filho()`: liga um novo estado ao nó e evita filhos repetidos;
- `eh_raiz()`, `eh_folha()` e `obter_nivel()`: descrevem a posição do nó;
- `marcar_como_visitado()`, `desmarcar_como_visitado()` e `esta_visitado()`:
  controlam a marcação usada para mostrar o caminho percorrido pelo jogador;
- `marcar_como_expandido()` e `esta_expandido()`: impedem que os mesmos filhos
  sejam gerados novamente.

O nó raiz não possui pai nem jogada de origem. Todos os outros nós possuem um
pai e a jogada completa responsável pela criação de seu estado.

### `model/state_tree.py`

- `ArvoreEstados.__init__()`: cria a raiz, marca o caminho inicial e prepara o
  registro global dos estados;
- `obter_raiz()` e `obter_no_atual()`: consultam os pontos principal e atual;
- `adicionar_estado()`: liga um novo estado a um pai somente quando seu
  identificador ainda não estiver na árvore;
- `expandir_no_atual()`: usa gerador e executor para criar somente o próximo
  nível da posição atual;
- `registrar_jogada_realizada()`: procura o estado resultante entre os filhos,
  cria o filho quando necessário e avança o caminho atual;
- `avancar_para()`: permite avançar apenas para um filho do nó atual;
- `voltar()`: retorna ao pai e atualiza a marcação do caminho percorrido;
- `obter_caminho_atual()`: lista os nós desde a raiz até a posição atual;
- `possui_estado()`: consulta se um estado equivalente já foi registrado;
- `obter_estado_atual()`: entrega uma cópia protegida da posição atual;
- `obter_nos()` e `quantidade_nos()`: consultam o registro global;
- `_validar_no_da_arvore()`: impede navegação ou inserção com nós externos.

A raiz começa marcada como visitada. Ao avançar, o novo nó também é marcado;
ao voltar, o nó abandonado é desmarcado. Dessa maneira, a apresentação poderá
destacar visualmente o caminho atual sem confundir isso com o registro global
de estados, que permanece guardado na árvore.

### `model/state_tree_serializer.py`

- `__init__()`: prepara o serializador já usado pelos estados individuais;
- `serializar(arvore)`: converte todos os nós em dados simples;
- `restaurar(dados)`: recria nós, pais, filhos, expansão e caminho atual;
- `salvar(arvore, caminho)`: grava um arquivo JSON em UTF-8;
- `carregar(caminho)`: lê o JSON e devolve uma `ArvoreEstados` funcional;
- `_obter_indice_no()`: troca referências entre objetos por índices simples;
- `_validar_dados_principais()`: verifica versão, lista e nó atual;
- `_validar_dados_raiz()`: confirma que a raiz não possui pai nem jogada;
- `_validar_dados_no()`: verifica índice, pai, expansão e jogada dos filhos;
- `_restaurar_caminho_atual()`: percorre novamente o caminho salvo;
- `_validar_caminho()`: exige um caminho de arquivo preenchido.

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

- `__init__(...)`: recebe jogo, View, árvore e dados de salvamento, além de
  iniciar as seleções;
- `_validar_sincronia_inicial()`: impede iniciar o Controller com jogo e árvore
  representando estados diferentes;
- `_mostrar_ajuda_da_carta()`: monta a legenda com nome, efeito e próximo passo
  usando a descrição já armazenada na carta;
- `_registrar_jogada_realizada()`: envia ao Model somente uma jogada completa;
- `_salvar_arvore()`: grava o JSON sem encerrar o jogo caso ocorra um erro de
  arquivo;
- `_processar_clique()`: também reconhece o botão **SALVAR** e apresenta a
  confirmação sem alterar o turno ou as seleções do jogador;
- `executar()`: mantém o loop de eventos e desenho em 60 quadros por segundo;
- `_processar_eventos()` e `_processar_clique()`: encaminham cliques;
- métodos `_processar_...`: montam, passo a passo, os parâmetros de cada ação;
- `_tentar_jogar_carta()`: chama o Model e transforma erros em instruções;
- `_atualizar_instrucao_da_carta()`: explica a próxima seleção;
- `_pode_voltar_jogada()` e `_voltar_jogada()`: validam a volta e substituem o
  estado do jogo pela cópia protegida do nó pai;
- `_processar_clique_da_arvore()`: fecha a tela, muda páginas ou solicita a
  expansão do nó atual e também inicia a exportação pelo Graphviz;
- `_limpar_selecao()`: cancela dados temporários;
- `_obter_selecao()`: entrega à View somente o necessário para destacar itens;
- `_desenhar_quadro()`: envia estado, seleção e informações da árvore à View.

### `controller/start_menu_controller.py`

- `existe_jogo_salvo()`: verifica se `state_tree.json` está disponível;
- `executar(mensagem)`: mantém o menu ativo, trata fechamento e clique e
  devolve uma das três escolhas para `main.py`;
- as constantes `ACAO_NOVO_JOGO`, `ACAO_CONTINUAR_JOGO` e `ACAO_SAIR` evitam
  usar textos visuais como decisões do programa.

### `view/constants.py`

Centraliza cores, tamanhos e posições. Isso mantém detalhes visuais fora do
Model e facilita mudar o layout sem alterar regras. `LARGURA_JANELA` e
`ALTURA_JANELA` representam a área lógica do desenho, não uma resolução que o
monitor seja obrigado a utilizar. `ROTAS_FRONTEIRAS` guarda apenas desvios
visuais para as ligações longas não atravessarem as caixas das regiões; ela
não define quais regiões são vizinhas.

### `view/game_view.py`

- `desenhar_menu_inicial(...)`: apresenta novo jogo, continuar e sair, além de
  mensagens de carregamento ou erro;
- `obter_acao_menu_inicial(...)`: identifica a opção clicada e bloqueia a
  continuação quando não existe salvamento;
- `desenhar(...)`: redesenha a partida e, quando solicitado, sobrepõe a tela da
  árvore;
- métodos `botao_...foi_clicado()` e `obter_...clicada()`: identificam áreas,
  incluindo o botão de salvamento manual;
- `obter_quantidade_paginas_arvore()`: calcula quantas páginas de sete filhos
  serão necessárias;
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
  mensagens, controles, caminho da árvore e filhos paginados;
- `_obter_retangulo_carta()`: calcula a área de cada carta;
- `_quebrar_texto()` e métodos de texto: mantêm os textos dentro das áreas.

O prefixo `_` indica um detalhe interno da classe ou do arquivo. É uma
convenção de Python: o código continua acessível, mas outras classes devem usar
preferencialmente os métodos públicos.

### `view/state_tree_view.py`

- `formatar(arvore, limite_filhos)`: transforma a árvore em texto indentado;
- `mostrar(...)`: imprime o texto no terminal;
- `_adicionar_no()`: percorre pais e filhos respeitando seus níveis;
- `_obter_marcador()`: diferencia nó atual, caminho e alternativas;
- `_obter_descricao()`: mostra `Estado inicial` ou a jogada de origem;
- `_validar_limite()`: protege o limite opcional usado em árvores largas.

### `view/state_tree_graphviz_view.py`

- `gerar_dot(arvore)`: percorre todos os nós uma vez e monta a descrição
  completa do grafo;
- `exportar(arvore, caminho_svg, abrir)`: salva o DOT, executa o Graphviz,
  cria o SVG e pode abri-lo no navegador;
- `_localizar_dot()`: procura o executável no `PATH` e nas pastas comuns do
  Windows;
- `_criar_rotulo(...)`: resume índice, nível, jogada e expansão de cada nó;
- `_escapar_texto(...)`: protege aspas e barras para produzir DOT válido;
- `_validar_caminho(...)`: rejeita destinos vazios ou de tipo incorreto.

## Testes automatizados

Execute:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

A pasta `tests` verifica unidades pequenas e independentes. O arquivo
`test_actions.py` cobre o ciclo das cartas, execuções parciais, jogadas
inválidas, convocação e restrições contra desfazer a ação adversária.
`test_game.py` cobre turnos, disputas, fim, desempates e uma partida completa
por passes. Os arquivos `test_state_...` cobrem nós, expansão controlada,
navegação, apresentação e persistência da árvore. Os demais arquivos acompanham
uma classe do Model. `test_controller.py` também garante que passe e carta
completa atualizem a árvore, que voltar restaure o jogo, que o arquivo possa ser
carregado e que a ajuda da carta apresente efeito e próximo passo.
`test_main.py` cobre a escolha entre uma partida nova e uma árvore salva.
`test_view.py` verifica a paginação da apresentação gráfica.

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
- A árvore não altera estados existentes: executor e nós trabalham com cópias.
- Um identificador textual permite comparar estados sem depender da identidade
  dos objetos em memória. A mensagem da interface não participa da comparação.
- O registro global da árvore impede repetição no mesmo nível e em níveis
  diferentes; a marcação de visitado possui somente finalidade de navegação e
  apresentação.
- A expansão sob demanda evita gerar netos de jogadas ainda não escolhidas.
- JSON foi escolhido para persistência por ser legível, simples e nativo do
  Python. O campo de versão permite rejeitar formatos incompatíveis no futuro.
- Os testes usam uma semente aleatória ou estados montados manualmente para que
  o resultado seja previsível e repetível.
