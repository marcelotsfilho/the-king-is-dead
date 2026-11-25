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
- Graphviz, usado somente para exportar a visualização do caminho atual.

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

Ao clicar em **NOVO JOGO**, uma segunda tela mostra os painéis **Jogador 1** e
**Jogador 2**, que permitem configurar
cada lado independentemente. Clique no tipo para alternar entre **Humano**,
**Minimax**, **Minimax com alfa-beta**, **Monte Carlo** e **Q-learning**. Use
`+` e `-` para ajustar a antecipação do Minimax (mínimo de uma jogada completa)
ou a quantidade de simulações do Monte Carlo. O Q-learning carrega a tabela
treinada ao calcular seu primeiro turno.

Para **Minimax** e **Minimax com alfa-beta**, clique em **Tempo por jogada**
para alternar entre **Sem limite**, **5 s**, **10 s**, **20 s**, **30 s** e **60 s**.
**Sem limite** faz a busca em profundidade fixa. Com um prazo, a IA aprofunda
a busca de 1 até o máximo escolhido e usa a melhor jogada da última
profundidade concluída. Se o prazo acabar antes da primeira profundidade, ela
usa a melhor jogada já avaliada ou passa se ainda estiver no início da busca.
O resultado mostra a profundidade alcançada e avisa quando o limite é atingido.

Clique em **INICIAR PARTIDA** para confirmar. **VOLTAR AO MENU** descarta a
edição e retorna à tela inicial, sem criar uma partida ou alterar o salvamento.
As escolhas confirmadas são entregues ao `ControladorJogo` ao iniciar o novo
jogo. Nos turnos configurados como IA, o Controller escolhe e aplica a jogada
automaticamente, respeitando o algoritmo e a profundidade de cada lado. É
possível jogar humano contra IA e colocar os algoritmos para jogarem entre si.

Durante um turno automático, cliques nas cartas, regiões e no botão Passar não
executam jogadas humanas. Salvar, abrir a árvore e voltar continuam disponíveis.
**PAUSAR IA** suspende a aplicação da próxima jogada; **RETOMAR IA** libera a
continuação. Ao abrir a árvore, nenhum resultado da IA é aplicado até fechá-la.
Ao voltar uma jogada, a IA é pausada para permitir analisar a posição restaurada.

O tempo da última decisão, algoritmo, profundidade, nós visitados e cortes
aparecem no rodapé, inclusive depois do fim da partida. Enquanto calcula, o
quadro de instruções identifica o jogador, algoritmo e profundidade usados.

O padrão para uma nova partida é Humano contra Humano, com profundidade 1
para cada jogador. O salvamento guarda o tipo de cada jogador, a profundidade,
o limite de tempo e a quantidade de simulações do Monte Carlo. **CONTINUAR JOGO** e
`--carregar` retomam o turno salvo com essas escolhas. Em salvamentos antigos
que guardavam apenas a árvore, a partida abre como Humano contra Humano.

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

## Etapa 4 — Q-learning

- [x] Implementar o agente e selecionar Q-learning no menu pelo fluxo MVC.
- [x] Treinar por partidas completas e medir o desempenho em checkpoints com a tabela congelada.
- [x] Registrar a quantidade treinada, verificar o critério de bom treino e guardar os dados para o relatório final.
- [x] Gerar o gráfico de partidas jogadas e vitórias do Q-learning.
- [x] Salvar a tabela treinada e carregar o arquivo para jogar sem repetir o treino.
- [x] Confrontar a mesma tabela com Minimax simples e Minimax com poda alfa-beta.
- [x] Testar posições em que passar favorece o jogador ou causa derrota. Registrar as cartas na mão no primeiro passe e a taxa de vitória nas partidas completas com os agentes avaliados.
- [ ] Montar o `.zip` de entrega quando o relatório final estiver incorporado.

Para demonstrar, selecione **Q-learning** em um dos lados e **Minimax** ou
**Minimax com alfa-beta** no outro. No primeiro turno do Q-learning, o jogo
carrega a tabela selecionada após 1.000 partidas com jogadas aleatórias contra
a heurística. O agente também verifica as decisões nos finais pequenos.
[Tabela ativa](experiments/etapa4/treino_aleatorio/tabela_selecionada.json) ·
[Treino e validação](experiments/etapa4/treino_aleatorio/README.md) ·
[Experimentos anteriores](experiments/etapa4/README.md)

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
ao mesmo tempo. Para acessar diretamente uma página, clique no campo **PÁG.**,
digite o número desejado e pressione **ENTER** ou o botão **IR**. O Controller
recusa números menores que um ou maiores que a quantidade de páginas.

Os marcadores da apresentação textual significam:

- `[ATUAL]`: posição atual da partida;
- `[CAMINHO]`: estado que faz parte do caminho entre a raiz e o nó atual;
- `[NÃO VISITADO]`: alternativa gerada, mas não escolhida.

### Visualização otimizada pelo Graphviz

Na tela da árvore, o botão **ABRIR GRAPHVIZ** exporta o caminho entre a raiz e
o nó atual, os filhos diretos do nó atual e os nós de jogadas voltadas.
Alternativas nunca visitadas de níveis anteriores são omitidas para reduzir o
arquivo e deixar o diagrama mais legível. A exportação gera:

- `saves/state_tree.dot`: descrição textual entendida pelo Graphviz;
- `saves/state_tree.svg`: diagrama vetorial que pode ser ampliado sem perder
  qualidade e é aberto no navegador padrão.

O nó atual aparece em azul, o caminho visitado em verde e as alternativas não
visitadas em cinza claro. Quando o jogador usa **VOLTAR**, o nó abandonado
recebe o texto `Jogada voltada`, uma borda mais forte e um cinza mais escuro.
Cada caixa também informa índice, nível, jogada de origem e se as opções daquele
nó já foram geradas. As setas representam a relação entre pai e filho. A
configuração `ranksep="1.0"` aumenta a distância vertical entre os níveis,
evitando que caixas e setas de níveis consecutivos fiquem muito próximas.

A exportação é manual para não interferir em uma jogada comum. Depois de uma
jogada ou de uma volta, basta abrir a tela **ÁRVORE** e solicitar outra
exportação para obter a versão atualizada do caminho e das próximas opções.

### Salvar e carregar a árvore

Cada nó agora guarda uma **avaliação heurística estática**, calculada quando o
nó é criado. Novos nós usam o jogador 1 como referência fixa, independentemente
de quem está no turno. Na legenda `H(J1, v3): +4004`, `J1` é a perspectiva e
`v1` é a versão da fórmula. Um valor positivo favorece o jogador indicado;
zero é uma estimativa neutra, não uma avaliação ausente.

O JSON de cada nó inclui, por exemplo:

```json
"avaliacao_heuristica": {
  "valor": 4004,
  "indice_jogador": 0,
  "versao": 1
}
```

A nota usa `AvaliadorEstado.avaliar(estado, profundidade=0)`: ela pertence à
posição. O valor retornado pelo Minimax é diferente, pois depende da busca,
de seu limite e da distância até uma vitória ou derrota. Não é salvo nesse
campo. Avaliações são metadados do nó e não entram na comparação de estados.

O formato da árvore passou para a versão 2, mantendo leitura da versão 1.
Notas da versão atual são restauradas sem recalcular. Arquivos sem esse campo
ou com `null` recebem uma avaliação atual durante o carregamento. Se a versão
da fórmula for diferente, o nó recalcula a nota preservando a perspectiva.
Metadados incompletos, valores não numéricos, NaN/infinito e índices inválidos
são rejeitados; a mensagem de erro do carregamento já é apresentada no menu.

`VERSAO_HEURISTICA`, em `model/state_evaluator.py`, deve ser incrementada quando
a fórmula ou seus pesos mudarem. A versão do formato JSON é independente da
versão da heurística. As notas atualizadas em memória serão gravadas no próximo
salvamento, sem reescrever o arquivo só por abri-lo.

Pygame, terminal e Graphviz mostram a mesma legenda. Ela não representa a
probabilidade de vitória. O Minimax continua avaliando suas folhas pela própria
perspectiva e profundidade: nesta etapa, não reutiliza essas notas como uma
tabela de resultados da busca. Também não há notas fictícias para ramos
podados; somente os nós efetivamente existentes no histórico são serializados.

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
reconstruída no carregamento. A configuração da partida, quando informada,
fica no campo `configuracao_partida` e pode ser lida com `carregar_partida()`.

No fluxo normal não é necessário chamar esses métodos manualmente. O Controller
salva `saves/state_tree.json` ao encerrar a aplicação ou concluir a partida, e
o botão **CONTINUAR JOGO** restaura a árvore, a configuração e o turno do nó
atual. Durante a leitura, o menu apresenta a mensagem de carregamento.

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
- `view/state_tree_graphviz_view.py` transforma o caminho atual e seus filhos
  diretos em DOT e solicita ao Graphviz a criação do SVG. Ramos antigos não
  visitados são omitidos, e a View não altera estados nem repete regras;
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
│   ├── minimax_agent.py
│   ├── match_settings.py
│   ├── state_evaluator.py
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

- `_criar_arvore_inicial()`: cria a árvore de um novo jogo pela `SEMENTE_JOGO`;
- `_escolher_partida_pelo_menu(...)`: retorna a árvore e a configuração
  escolhida ou salva, e informa erros de carregamento na tela inicial;
- `principal()`: prepara a pasta de salvamento, inicializa Pygame, Model, View,
  menu, árvore e Controller, executa a aplicação e encerra o Pygame.

### `main_tree.py`

- `principal()`: cria um estado inicial reproduzível, expande somente a raiz e
  apresenta uma amostra da árvore no terminal, usando a mesma `SEMENTE_JOGO`
  definida em `main.py`.

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
- `obter_lideranca()`: informa a facção líder e sua vantagem, usadas na
  resolução das disputas e na avaliação heurística;
- `definir_controlador(faccao)`: registra uma vitória regional;
- `marcar_como_instavel()`: resolve a região sem controlador;
- `esta_resolvida()`: informa se a região já saiu do jogo;
- métodos iniciados por `_validar`: protegem as regras internas da classe.

### `model/board.py`

- `Tabuleiro.__init__()`: cria as oito regiões e o grafo de fronteiras;
- `obter_regioes()` e `obter_nomes_das_regioes()`: consultam o catálogo;
- `obter_regiao(nome)`: encontra o objeto de uma região;
- `obter_regioes_com_seguidores()`: lista as regiões em disputa com peças;
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
- `obter_posicoes_negociaveis()`: lista as posições abertas sem disco;
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
- `retirar(...)` e `devolver(...)`: movimentam peças com a mesma validação de
  quantidade positiva usada pelas regiões.

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
- `ExecutorJogada.executar_carta(estado, tipo_carta, parametros)`: aplica o
  efeito em uma cópia e deixa a convocação pendente;
- `ExecutorJogada.executar_convocacao(estado, regiao, faccao)`: conclui uma
  convocação pendente em uma cópia;
- `_obter_carta_do_jogador()`: encontra na cópia a carta indicada pela jogada.

Um passe inclui suas consequências automáticas. A execução completa de uma
carta inclui efeito, convocação e troca de jogador.

### `model/legal_move_generator.py`

- `GeradorJogadas.gerar(estado)`: encontra todas as jogadas completas que o
  jogador atual pode realizar sem modificar o estado recebido;
- `gerar_com_estados(estado)`: gera sob demanda pares de jogada e estado
  resultante. Cada conjunto de parâmetros aplica o efeito da carta uma vez.
  Cada convocação possível usa sua própria cópia do estado intermediário.
- `sortear_com_estado(estado, aleatorio)`: usa a mesma execução de cartas e
  convocações para amostrar uma jogada nos rollouts de Monte Carlo.

O gerador usa as regras de `Jogo` para validar os efeitos das cartas e concluir
cada convocação. Cartas repetidas do mesmo tipo, como as duas Assemble, são
processadas uma vez. Em Outmanoeuvre, as regiões de destino de cada origem são
percorridas em ordem alfabética, inclusive quando há empate na busca.

### `model/match_settings.py`

`ConfiguracaoPartida` guarda as escolhas de controle dos dois jogadores.
Ela é diferente de `ConfiguracaoJogo`, que distribui cartas e seguidores e
prepara o tabuleiro. As escolhas de controle não modificam regras ou estados.

- `__init__()`: inicia os dois lados como humanos e profundidades em 1;
- `_validar_indice(indice)`: aceita somente os índices inteiros 0 e 1;
- `obter_tipo_jogador(indice)`: retorna o `TipoJogador` daquele lado;
- `obter_profundidade(indice)`: retorna sua antecipação configurada;
- `definir_tipo_jogador(indice, tipo)`: altera o tipo, validando o enum;
- `definir_profundidade(indice, profundidade)`: aceita um inteiro a partir de 1.

O enum `TipoJogador`, em `model/enums.py`, identifica Humano, Minimax e Minimax
com alfa-beta. O objeto de configuração é compartilhado por `main.py`, menu e
Controller da partida, evitando cópias divergentes das escolhas.

### `model/state_evaluator.py`

- `AvaliadorEstado(indice_jogador_ia)`: identifica qual dos dois jogadores será
  maximizado pelo Minimax;
- `avaliar(estado, profundidade)`: retorna uma pontuação positiva quando o
  estado favorece a IA e negativa quando favorece o adversário;
- estados finais recebem prioridade absoluta. Vitória vale um valor muito alto
  e diminui conforme a profundidade, enquanto derrota recebe valor negativo e
  fica menos ruim quando é adiada;
- estados não finais combinam cortes, poder atual e projetado das facções e
  risco de invasão. A heurística lê o estado sem gerar nem executar jogadas;
- `_avaliar_cartas_restantes(estado)`: compara o potencial das mãos. A última
  carta vale inicialmente 4500 pontos; cada carta adicional vale 150 pontos a
  menos que a anterior, representando a menor urgência de uma mão abundante.
  Cada disputa resolvida reduz em 100 pontos o valor de todas as cartas. Assim,
  a IA preserva opções escassas sem tratar toda carta como igualmente valiosa;
- `_pontuar_cortes(estado, faccoes)`: usa diferença da primeira facção com peso
  1000 e da segunda com peso 20. Com até 16 seguidores por facção, a segunda
  não supera uma vantagem unitária na primeira dentro dessa ordenação. No
  empate, considera quem esvaziou a mão primeiro, conforme a regra existente;
- `_obter_faccoes_projetadas(...)`: atribui 4 pontos a cada região controlada,
  até 2 a uma liderança pendente pela margem sobre a segunda facção e mais 1
  se for a próxima disputa. Empates de poder projetado mantêm a ordem atual;
- `_avaliar_coroacao(estado)`: combina três vezes a nota dos cortes na ordem
  atual com uma vez a nota na ordem projetada. A previsão tem peso menor;
- `_avaliar_invasao(estado)`: pondera a diferença de conjuntos por 20, 100 ou
  600 para zero, uma ou duas instabilidades. Dobra o peso se a próxima região
  estiver empatada/vazia, e novamente se já houver um passe. Empates de conjuntos
  consideram o último jogador que usou carta. Esses valores estimam risco,
  sem afirmar que a invasão ocorrerá;
- avaliações intermediárias ficam limitadas entre -100000 e 100000, abaixo
  dos resultados finais do jogo;
- foram removidas a enumeração exata de mobilidade e a simulação de ameaças em
  cada folha: elas repetiam a expansão e tornavam a primeira decisão inviável.
  O Minimax continua explorando todas as jogadas até a profundidade configurada.

### `model/minimax_agent.py`

`AgenteMinimax` escolhe uma jogada completa usando antecipação. No turno da IA,
busca a maior pontuação; no turno do adversário, considera a menor pontuação,
representando a melhor resposta dele contra a IA.

```python
from model.minimax_agent import AgenteMinimax

PROFUNDIDADE_ANTECIPACAO = 2
USAR_PODA_ALFA_BETA = True

agente = AgenteMinimax(indice_jogador_ia=0)
jogada = agente.escolher_jogada(
    estado,
    profundidade_maxima=PROFUNDIDADE_ANTECIPACAO,
    usar_poda=USAR_PODA_ALFA_BETA,
)

if jogada is not None:
    print(jogada.descrever())

print(agente.ultima_pontuacao)
print(agente.nos_visitados)
print(agente.folhas_avaliadas)
print(agente.podas_realizadas)
```

A profundidade é um parâmetro inteiro, a partir de 1, e pode ser alterada em
cada chamada. O valor padrão é 1, pois o jogo pode gerar milhares de combinações:

- profundidade 1: avalia o resultado das jogadas da IA;
- profundidade 2: inclui as respostas do adversário;
- profundidade 3: inclui mais uma jogada da IA.

O limite conta transições de jogadas completas desde o estado recebido (raiz
da busca em profundidade zero), independentemente do nível no histórico salvo.
A heurística agora avalia estaticamente as folhas, sem simular um nível extra.

Para executar Minimax simples, use `usar_poda=False`. Com `True`, o mesmo
algoritmo atualiza alfa (melhor limite do maximizador) e beta (melhor limite do
minimizador). Quando `beta <= alfa`, os irmãos restantes daquele ramo não
precisam ser avaliados. A poda preserva a decisão e a pontuação da busca com
a mesma profundidade e ordem de jogadas. Em empate, mantém a primeira opção.

Responsabilidades dos métodos:

- `__init__(indice_jogador_ia)`: prepara o avaliador e o gerador;
- `_limpar_estatisticas()`: zera os contadores antes de cada busca;
- `_validar_entrada(...)`: valida estado, profundidade, opção de poda e turno;
- `_avaliar_folha(estado, profundidade)`: conta uma avaliação e chama a
  heurística ao atingir o limite, um estado final ou uma posição sem jogadas;
- `_buscar(...)`: percorre recursivamente as opções, escolhe máximo ou mínimo
  conforme o jogador e aplica os cortes quando habilitados;
- `escolher_jogada(...)`: devolve a jogada escolhida e publica os contadores
  da busca. Retorna `None` para partidas finalizadas ou sem jogadas completas,
  incluindo uma convocação pendente. Uma chamada fora do turno da IA é rejeitada.

O gerador simula cada jogada em cópias. O Controller executa a busca em uma
cópia do estado e registra somente o resultado escolhido em `ArvoreEstados`.

O gerador produz os estados filhos sob demanda. Um corte alfa-beta interrompe
a geração dos estados irmãos restantes. O custo também inclui a avaliação
heurística das folhas, e a busca pode demorar em posições com muitas opções.

### Monte Carlo

O menu de configuração permite ajustar o orçamento do Monte Carlo com os
botões `-` e `+`: 100, 300, 1.000, 3.000 ou 5.000 simulações por decisão.
O valor inicial continua em 100. A duração depende do estado: na abertura,
3.000 simulações levaram cerca de 30 segundos nesta máquina; posições mais
avançadas podem levar menos. A interface mostra o número de simulações durante
a busca. Esta implementação usa rollouts aleatórios, não MCTS/UCT.

### `model/state_node.py`

- `calcular_avaliacao_heuristica(indice_jogador=0)`: calcula a nota estática
  sobre o estado protegido e guarda valor, jogador e versão;
- `definir_avaliacao_heuristica(avaliacao)`: valida os dados de uma nota salva
  e recalcula somente quando a versão é diferente;
- `obter_avaliacao_heuristica()`: retorna uma cópia dos metadados, protegendo
  o valor interno;
- `__init__(..., avaliacao_heuristica=None)`: aceita uma nota salva válida
  para evitar recálculo no carregamento; sem nota, avalia o novo estado.

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
- `marcar_como_jogada_voltada()` e `representa_jogada_voltada()`: diferenciam
  um nó nunca escolhido de outro que foi visitado e depois abandonado;
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
- `expandir_no_atual()`: usa os pares de jogada e estado do gerador para
  criar somente o próximo nível da posição atual;
- `registrar_jogada_realizada()`: consulta o registro pelo identificador do
  estado, cria o filho quando necessário e avança o caminho atual;
- `avancar_para()`: permite avançar apenas para um filho do nó atual;
- `voltar()`: retorna ao pai e atualiza a marcação do caminho percorrido;
- `obter_caminho_atual()`: lista os nós desde a raiz até a posição atual;
- `possui_estado()`: consulta se um estado equivalente já foi registrado;
- `obter_estado_atual()`: entrega uma cópia protegida da posição atual;
- `obter_nos()` e `quantidade_nos()`: consultam o registro global;
- `_validar_no_da_arvore()`: impede navegação ou inserção com nós externos.

A raiz começa marcada como visitada. Ao avançar, o novo nó também é marcado e
qualquer marca anterior de volta é removida. Ao voltar, o nó abandonado recebe
a marca de jogada voltada. Dessa maneira, a apresentação diferencia caminho
atual, alternativa nunca visitada e estado que já foi percorrido e abandonado.

Após desfazer uma jogada, uma alternativa pode levar a uma posição já
registrada em outro ramo. A árvore tem um único pai por nó e rejeita esse
registro. O controlador mantém o turno no ponto anterior à tentativa.

### `model/state_tree_serializer.py`

`serializar()` inclui `avaliacao_heuristica` em cada nó. `restaurar()` entrega
essa nota aos construtores de `ArvoreEstados` e `NoEstado`, evitando calcular
um valor para depois sobrescrevê-lo. A criação da raiz e `adicionar_estado()`
aceitam a nota como argumento opcional; os demais fluxos continuam calculando
a avaliação automaticamente na criação do nó.

- `__init__()`: prepara o serializador já usado pelos estados individuais;
- `serializar(arvore, configuracao_partida=None)` converte a árvore e, quando
  informada, a configuração da partida em dados simples;
- `restaurar(dados)`: recria nós, pais, filhos, expansão, voltas e caminho
  atual; arquivos anteriores sem a nova marca continuam aceitos;
- `salvar(arvore, caminho, configuracao_partida=None)` substitui o JSON depois
  de gravar a árvore e a configuração completa em UTF-8;
- `carregar(caminho)`: lê o JSON e devolve uma `ArvoreEstados` funcional;
- `carregar_partida(caminho)` devolve a árvore e a configuração da partida;
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
- `obter_regioes_validas_para_apoio(tipo)`: calcula destinos de Support;
- `obter_trocas_superar_manobra()`: encontra pares adjacentes elegíveis e a
  quantidade de seguidores exigida no destino;
- `obter_quantidade_conjuntos(jogador)` e `obter_faccoes_por_poder()`:
  calculam os valores usados no encerramento e na avaliação heurística.

Métodos internos que dividem as regras em etapas menores:

- `_executar_assemble()`, `_executar_apoio()`, `_executar_negociar()`,
  `_executar_manobra()` e `_executar_superar_manobra()`: implementam os efeitos;
- `_obter_dados_de_troca()`: valida a seleção comum às duas trocas;
- métodos `_validar_...nao_desfaz_acao()`: protegem a restrição de repetição;
- `_registrar_carta_jogada()`: atualiza mão, última ação, passes e fase;
- `_validar_carta_do_jogador()`, `_validar_convocacao_possivel()`,
  `_validar_fase()` e `_validar_partida_em_andamento()`: bloqueiam comandos
  inválidos;
- `_devolver_seguidores_para_reserva()`: conserva as peças;
- métodos `_finalizar_...` e `_determinar_vencedor_...`: implementam invasão,
  coroação e desempates.

### `controller/game_controller.py`

Execução dos turnos da IA:

- `_possui_ia()` e `_turno_da_ia()`: consultam a configuração da sessão;
- `_alternar_pausa_ia()`: suspende ou libera a aplicação de jogadas automáticas;
- `_calcular_jogada_ia(...)`: executa a busca na thread, aplica a jogada na
  cópia pelo `ExecutorJogada` e devolve resultado ou erro pela fila;
- `_iniciar_busca_ia()`: copia a posição atual, informa o cálculo na tela e
  inicia uma única thread;
- `_receber_jogada_ia()`: recebe a resposta, confere se o estado ainda é o da
  busca, registra a jogada e só então atualiza o jogo. Respostas antigas são
  descartadas; erros pausam a IA sem alterar a posição;
- `_obter_resumo_ia()`: formata as estatísticas da última decisão;
- `_obter_status_ia()`: mostra cálculo com tempo decorrido, pausa com cálculo
  ainda ativo, resposta pronta aguardando retomada/fechamento da árvore e
  descarte de cálculo antigo. Após 10 segundos explica que muitas opções
  podem demorar; isso é um aviso, não um limite de tempo ou porcentagem fictícia;
- `_atualizar_turno_ia()`: consulta a fila ou inicia a busca no turno correto,
  sem aguardar o cálculo dentro do loop da janela.

`Thread` e `Queue` são recursos da biblioteca padrão. A thread trabalha em uma
cópia e não acessa o Pygame nem altera a árvore. Apenas o loop principal aplica
o resultado. Isso permite processar eventos e desenhar enquanto a busca ocorre,
mas não torna a busca mais rápida. O tempo medido com `perf_counter()` inclui
a criação do agente, busca e execução final sobre a cópia; não inclui a cópia
inicial feita pelo Controller, o desenho, o salvamento nem a espera em pausa.

A pausa não interrompe um cálculo já iniciado: sua resposta fica aguardando na
fila. Há no máximo uma tarefa de cálculo por Controller. Ao voltar, a resposta
antiga é descartada quando chegar; uma nova busca aguarda a anterior terminar.
Ao fechar, a thread é daemon e não impede a saída; somente as jogadas já
confirmadas são salvas. O custo de posições grandes ainda exige experimentos
de viabilidade antes de recomendar profundidades maiores.

Erros de cálculo, ausência de jogada e falhas ao registrar preservam a posição,
pausam a IA e orientam a retomar/tentar novamente ou salvar. Não há um passe
automático de fallback: a mensagem não deve esconder uma falha da busca.

### Medição inicial após a otimização da heurística

Experimento com seed 42, estado inicial completo, execução direta no ambiente
local desta verificação (sem o desenho do Pygame). São medições pontuais, não
uma média de partidas nem uma garantia de tempo em outros computadores.

| Medição | Resultado |
|---|---:|
| Avaliação estática do estado inicial, média de 1000 chamadas | 0,082 ms |
| Primeira decisão Minimax, profundidade 1 | 5,782 s |
| Primeira decisão alfa-beta, profundidade 1 | 5,685 s |
| Primeira jogada pelo Controller, com thread e aplicação no jogo | 5,309 s |
| Folhas avaliadas em cada primeira decisão | 14697 |
| Nós visitados em cada primeira decisão | 14698 |

Os dois algoritmos escolheram a mesma jogada. Em profundidade 1 não houve
cortes; a pequena diferença de tempo não comprova vantagem da poda nesse nível.
Na verificação do Controller, o nó foi registrado e o turno passou ao jogador 2.
Antes da alteração, uma única folha medida após o passe inicial levou 4,567 s,
pois gerava e simulava novamente as respostas. Não foi medida uma busca
completa com a heurística antiga. Os estados das duas medições isoladas são
diferentes; a medida relevante de viabilidade agora é a decisão completa acima.
Profundidades maiores e partidas completas ainda precisam de experimentos.

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
- `_ir_para_pagina_digitada()`: valida o número informado no filtro e troca
  diretamente a página de filhos;
- `_processar_tecla_da_arvore()`: recebe números, BACKSPACE, ESC e ENTER no
  campo de página;
- `_limpar_selecao()`: cancela dados temporários;
- `_obter_selecao()`: entrega à View somente o necessário para destacar itens;
- `_desenhar_quadro()`: envia estado, seleção e informações da árvore à View.

`_registrar_jogada_realizada(jogada, estado_resultante)` atualiza o jogo
depois que a árvore aceita a transição. Passes, convocações e jogadas da IA
entregam um estado calculado em uma cópia, preservando o turno se o registro
falhar.

### `controller/start_menu_controller.py`

- `__init__(..., configuracao_partida)`: recebe as escolhas da sessão; quando
  omitidas, cria os padrões;
- `_alterar_configuracao(acao, indice, configuracao)`: alterna tipos ou ajusta a profundidade
  do jogador indicado, bloqueando alterações para humanos e valores abaixo de 1;
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

- `desenhar_menu_inicial(...)`: apresenta somente novo jogo, continuar e sair,
  além de mensagens de carregamento ou erro;
- `desenhar_tela_configuracao(configuracao_partida)`: apresenta a página de
  configuração exclusiva do novo jogo, com iniciar partida e voltar ao menu;
- `obter_acao_tela_configuracao(posicao)`: identifica iniciar ou voltar,
  respeitando a escala da janela;
- `_obter_controles_configuracao(indice)`: define áreas usadas tanto no desenho
  quanto na identificação dos cliques, evitando coordenadas duplicadas;
- `_desenhar_configuracao_jogadores(configuracao)`: desenha os dois painéis e
  desativa visualmente os ajustes de profundidade dos humanos;
- `obter_acao_configuracao(posicao)`: converte a posição redimensionada e retorna
  a ação e o índice do jogador, ou `None` quando nenhum controle foi clicado;
- `obter_acao_menu_inicial(...)`: identifica a opção clicada e bloqueia a
  continuação quando não existe salvamento;
- `desenhar(...)`: redesenha a partida e, quando solicitado, sobrepõe a tela da
  árvore;
- `botao_pausar_ia_foi_clicado(posicao)`: identifica o controle de pausa usando
  as mesmas coordenadas lógicas do desenho. `desenhar(...)` também recebe
  presença de IA, pausa e resumo da última decisão para exibição;
- métodos `botao_...foi_clicado()` e `obter_...clicada()`: identificam áreas,
  incluindo o botão de salvamento manual;
- `obter_quantidade_paginas_arvore()`: calcula quantas páginas de sete filhos
  serão necessárias;
- `campo_pagina_arvore_foi_clicado()` e `botao_ir_pagina_foi_clicado()`:
  identificam os controles usados para escolher diretamente uma página;
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

- `formatar_avaliacao_heuristica(no)`: formata a nota, perspectiva e versão.
  É reutilizada pelas três Views da árvore para evitar legendas divergentes.

- `formatar(arvore, limite_filhos)`: transforma a árvore em texto indentado;
- `mostrar(...)`: imprime o texto no terminal;
- `_adicionar_no()`: percorre pais e filhos respeitando seus níveis;
- `_obter_marcador()`: diferencia nó atual, caminho e alternativas;
- `_obter_descricao()`: mostra `Estado inicial` ou a jogada de origem;
- `_validar_limite()`: protege o limite opcional usado em árvores largas.

### `view/state_tree_graphviz_view.py`

- `gerar_dot(arvore)`: monta o DOT com o caminho atual e os filhos diretos do
  nó atual, mantendo a numeração original dos nós;
- `exportar(arvore, caminho_svg, abrir)`: salva o DOT, executa o Graphviz,
  cria o SVG e pode abri-lo no navegador;
- `_obter_nos_visiveis(arvore)`: mantém o caminho, os filhos atuais e as
  jogadas voltadas, omitindo alternativas que nunca foram visitadas;
- `_organizar_jogadas_voltadas(linhas, arvore, indices)`: coloca uma escolha
  voltada ao lado da nova escolha feita a partir do mesmo nó, mesmo depois de
  o jogo avançar novamente. O agrupamento de mesmo nível e a ligação invisível
  servem apenas para orientar o Graphviz;
- `_localizar_dot()`: procura o executável no `PATH` e nas pastas comuns do
  Windows;
- `_criar_rotulo(...)`: resume índice, nível, jogada, expansão e informa quando
  a jogada foi voltada;
- `_escapar_texto(...)`: protege aspas e barras para produzir DOT válido;
- `_validar_caminho(...)`: rejeita destinos vazios ou de tipo incorreto.

## Testes automatizados

Os testes unitários continuam separados dos experimentos de desempenho. Para
as baterias da terceira entrega, use o executor abaixo.

### Executor de experimentos pelo terminal

Na pasta do projeto, no PowerShell:

```powershell
$env:PYTHONHASHSEED = "0"
.\.venv\Scripts\python.exe main_experiments.py
```

Esse comando executa o plano combinado: heurísticas atual e inicial, Minimax
com e sem alfa-beta, profundidades 1 e 2, uma repetição, seed 123 e cenário
inicial completo. São **8 decisões de jogada**, sequenciais e sem limite
automático de duração. As buscas com a heurística antiga podem demorar horas
ou mais. Para reproduzir o plano histórico de 36 decisões, use
`--profundidades 1 2 3 --repeticoes 3 --seed 42`.
Você inicia e acompanha localmente; não há chamadas a serviços de IA ou APIs.

`PYTHONHASHSEED=0` mantém o identificador do ambiente usado pelo executor ao
retomar uma bateria. A opção `--seed` define a posição inicial do jogo.
O CSV também registra a identificação dessa ordem, separando medições feitas
em sessões incompatíveis. Não rode duas instâncias na mesma pasta de saída.

Os arquivos são gerados automaticamente:

- `experiments/results.csv`: todas as tentativas, com status, tempos, contadores,
  notas, jogadas, configuração e ambiente. Usa UTF-8 e separador `;`;
- `experiments/DIARIO_DE_EXPERIMENTOS_<data_e_hora_UTC>.md`: um diário por
  chamada do executor, com cenário, protocolo, resultados, jogadas, tempos,
  comparação dos pares, erros e limitações;
- `experiments/states/<hash>.json`: posição exata usada em cada experimento.

O terminal informa o caminho do novo diário. O executor atualiza esse arquivo
conforme as buscas da bateria começam, terminam ou são interrompidas. Cada
chamada de `main_experiments.py`, inclusive com `--retomar`, cria seu próprio
diário. Em uma retomada, o diário informa quantos testes já concluídos foram
pulados. O CSV reúne o histórico completo e os diários anteriores ficam
disponíveis para consulta.

Para **interromper**, pressione `Ctrl+C` uma vez e aguarde o salvamento. A
tentativa fica com o status `interrompido`. A seção **Resultados parciais dos
testes interrompidos** mostra o tempo decorrido, os nós visitados, as folhas
avaliadas e os cortes até a interrupção. As médias usam apenas testes
concluídos. Para retomar, use o comando abaixo.

```powershell
$env:PYTHONHASHSEED = "0"
.\.venv\Scripts\python.exe main_experiments.py --retomar
```

Use os mesmos argumentos da execução anterior. `--retomar` pula somente testes
concluídos com mesmo código, posição, heurística, profundidade, repetição e
ambiente. Erros e interrupções são tentados novamente. Fechar abruptamente o
terminal pode deixar uma linha em andamento no diário daquela bateria. Na
próxima abertura, o CSV registra a interrupção sem tempo conhecido. A
configuração interrompida é reiniciada do começo.

Para executar as baterias separadamente (18 decisões em cada comando):

```powershell
.\.venv\Scripts\python.exe main_experiments.py --bateria atual --retomar
.\.venv\Scripts\python.exe main_experiments.py --bateria inicial --retomar
```

Para um teste inicial curto, com apenas a heurística atual e profundidade 1:

```powershell
.\.venv\Scripts\python.exe main_experiments.py --bateria atual --profundidades 1 --repeticoes 1
```

Outras opções:

```powershell
# Apenas prepara CSV e diário, sem iniciar buscas:
.\.venv\Scripts\python.exe main_experiments.py --preparar

# Outra seed, preservando os registros anteriores:
.\.venv\Scripts\python.exe main_experiments.py --seed 7 --retomar

# Estado atual de uma árvore salva, útil para posições de meio/fim da partida:
.\.venv\Scripts\python.exe main_experiments.py --cenario salvo --arvore saves/state_tree.json --retomar

# Cenário sintético pequeno de validação, em saída separada:
.\.venv\Scripts\python.exe main_experiments.py --cenario reduzido --saida experiments/validation
```

No cenário `salvo`, o JSON deve conter uma partida em andamento, sem convocação
pendente. A seed é registrada como não aplicável: o cenário é identificado pela
posição arquivada e seu hash. O cenário `reduzido` tem reserva vazia, dois
seguidores no tabuleiro e uma Assemble por jogador; não representa a dificuldade
do início de uma partida real.

O tempo mede exclusivamente a chamada de escolha da jogada, sem Pygame,
preparação, I/O ou geração dos relatórios. Os contadores são do Minimax; não
contabilizam a expansão extra feita internamente pela heurística histórica.
Somente tentativas concluídas entram nas médias. O diário agrupa por estado,
código e ambiente; não mistura as duas heurísticas como se fossem equivalentes.
Uma diferença entre elas pode ser estratégica, pois seus pesos também mudaram.

Arquivos e métodos novos:

- `main_experiments.py`: `criar_argumentos()` define as flags;
  `inteiro_positivo()` valida profundidades/repetições; `principal()` valida a
  combinação de cenário e arquivo e inicia a bateria. Saída 0 indica conclusão,
  1 indica erro e 130 indica interrupção;
- `experiments/runner.py`: `criar_cenario()` prepara a posição;
  `identificar_codigo()` calcula o hash dos fontes; `arquivar_estado()` salva
  o snapshot; `montar_plano()` cria as combinações; `criar_registro()` reúne
  configuração/ambiente; `chave_execucao()` identifica testes para retomada;
  `executar_decisao()` mede e trata falhas/interrupções;
  `executar_bateria()` coordena o plano e a gravação;
- `experiments/report.py`: `carregar_resultados()` lê o histórico;
  `salvar_relatorios()` grava o CSV acumulado e o diário da bateria atual por
  arquivos temporários;
  `gerar_diario()` produz tabelas, estatísticas e comparações;
- `experiments/legacy_evaluator.py`: `AvaliadorInicial.avaliar()` reconstrói a
  fórmula anterior à otimização: ameaças somadas por resultado terminal,
  conjuntos com pesos 20/100/1000, cortes 100/10, margem regional vezes 3 e
  mobilidade exata com peso 2. Essa versão é experimental e não muda o Pygame;
- `AgenteMinimax(..., avaliador=None)` aceita um avaliador opcional, permitindo
  comparar fórmulas usando a mesma busca. O padrão continua a heurística atual.

Foi executada apenas a validação curta em `experiments/validation`: 36 decisões
concluídas no cenário reduzido, 18 pares sem divergência entre os algoritmos.
Isso valida o executor e os relatórios, não estabelece limites para o tabuleiro
completo. A bateria longa não foi iniciada automaticamente.

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
