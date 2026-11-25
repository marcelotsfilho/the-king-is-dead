import json
from os import replace
from pathlib import Path
from tempfile import NamedTemporaryFile

from model.enums import TipoJogador
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import restaurar_jogada, serializar_jogada
from model.match_settings import ConfiguracaoPartida
from model.state_tree import ArvoreEstados


_VERSAO_DA_ARVORE = 2


class SerializadorArvoreEstados:
    """Salva e restaura a árvore de estados em formato JSON."""

    def __init__(self):
        self._serializador_estado = SerializadorEstadoJogo()

    def serializar(self, arvore, configuracao_partida=None):
        """Transforma a árvore e, quando informada, a configuração em dados simples."""
        if not isinstance(arvore, ArvoreEstados):
            raise TypeError("O valor informado deve ser uma ArvoreEstados.")

        nos = arvore.obter_nos()
        dados_nos = []

        for indice in range(len(nos)):
            no = nos[indice]
            pai = no.obter_pai()
            indice_pai = self._obter_indice_no(pai, nos)
            jogada = no.obter_jogada_origem()
            dados_jogada = None

            if jogada is not None:
                dados_jogada = serializar_jogada(jogada)

            dados_nos.append(
                {
                    "indice": indice,
                    "indice_pai": indice_pai,
                    "estado": self._serializador_estado.serializar(
                        no.obter_estado()
                    ),
                    "jogada_origem": dados_jogada,
                    "expandido": no.esta_expandido(),
                    "jogada_voltada": no.representa_jogada_voltada(),
                    "avaliacao_heuristica": no.obter_avaliacao_heuristica(),
                }
            )

        indice_atual = self._obter_indice_no(
            arvore.obter_no_atual(),
            nos,
        )

        dados = {
            "versao": _VERSAO_DA_ARVORE,
            "indice_no_atual": indice_atual,
            "nos": dados_nos,
        }
        if configuracao_partida is not None:
            dados["configuracao_partida"] = self._serializar_configuracao(configuracao_partida)
        return dados

    def restaurar(self, dados):
        """Reconstrói a árvore a partir dos dados salvos."""
        self._validar_dados_principais(dados)
        dados_nos = dados["nos"]
        dados_raiz = dados_nos[0]
        self._validar_dados_raiz(dados_raiz)

        estado_raiz = self._serializador_estado.restaurar(
            dados_raiz["estado"]
        )
        arvore = ArvoreEstados(
            estado_raiz,
            avaliacao_heuristica=dados_raiz.get("avaliacao_heuristica"),
        )
        nos_restaurados = [arvore.obter_raiz()]

        if dados_raiz.get("expandido") is True:
            arvore.obter_raiz().marcar_como_expandido()

        for indice in range(1, len(dados_nos)):
            dados_no = dados_nos[indice]
            self._validar_dados_no(dados_no, indice, nos_restaurados)
            pai = nos_restaurados[dados_no["indice_pai"]]
            estado = self._serializador_estado.restaurar(
                dados_no["estado"]
            )
            jogada = restaurar_jogada(dados_no["jogada_origem"])
            novo_no = arvore.adicionar_estado(
                estado, jogada, pai,
                avaliacao_heuristica=dados_no.get("avaliacao_heuristica"),
            )

            if novo_no is None:
                raise ValueError("O arquivo possui um estado repetido.")

            if dados_no.get("expandido") is True:
                novo_no.marcar_como_expandido()

            if dados_no.get("jogada_voltada") is True:
                novo_no.marcar_como_jogada_voltada()

            nos_restaurados.append(novo_no)

        indice_atual = dados["indice_no_atual"]

        if not isinstance(indice_atual, int):
            raise ValueError("O índice do nó atual deve ser inteiro.")

        if indice_atual < 0 or indice_atual >= len(nos_restaurados):
            raise ValueError("O índice do nó atual está fora da árvore.")

        self._restaurar_caminho_atual(
            arvore,
            nos_restaurados[indice_atual],
        )
        return arvore

    def salvar(self, arvore, caminho, configuracao_partida=None):
        """Grava a árvore e a configuração juntas e substitui o arquivo salvo."""
        self._validar_caminho(caminho)
        dados = self.serializar(arvore, configuracao_partida)

        temporario = NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=Path(caminho).parent, delete=False
        )
        try:
            with temporario:
                json.dump(dados, temporario, ensure_ascii=False, indent=2)
            replace(temporario.name, caminho)
        finally:
            Path(temporario.name).unlink(missing_ok=True)

    def carregar(self, caminho):
        """Lê um arquivo JSON e reconstrói a árvore."""
        return self.restaurar(self._ler_dados(caminho))

    def carregar_partida(self, caminho):
        """Restaura a árvore e as escolhas dos jogadores para retomar a partida."""
        dados = self._ler_dados(caminho)
        arvore = self.restaurar(dados)
        if "configuracao_partida" not in dados:
            return arvore, ConfiguracaoPartida()
        return arvore, self._restaurar_configuracao(dados["configuracao_partida"])

    def _ler_dados(self, caminho):
        self._validar_caminho(caminho)
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except json.JSONDecodeError:
            raise ValueError("O arquivo não contém um JSON válido.")

    def _serializar_configuracao(self, configuracao):
        if not isinstance(configuracao, ConfiguracaoPartida):
            raise TypeError("A configuração deve ser uma ConfiguracaoPartida.")

        return {
            "jogadores": [
                {
                    "tipo": configuracao.obter_tipo_jogador(indice).name,
                    "profundidade": configuracao.obter_profundidade(indice),
                    "simulacoes_monte_carlo": configuracao.obter_simulacoes_monte_carlo(indice),
                    "limite_tempo_segundos": configuracao.obter_limite_tempo(indice),
                }
                for indice in range(2)
            ]
        }

    def _restaurar_configuracao(self, dados):
        if not isinstance(dados, dict):
            raise ValueError("A configuração da partida salva é inválida.")
        jogadores = dados.get("jogadores")
        if not isinstance(jogadores, list) or len(jogadores) != 2:
            raise ValueError("A configuração da partida deve conter dois jogadores.")

        configuracao = ConfiguracaoPartida()
        for indice, jogador in enumerate(jogadores):
            try:
                configuracao.definir_tipo_jogador(indice, TipoJogador[jogador["tipo"]])
                configuracao.definir_profundidade(indice, jogador["profundidade"])
                configuracao.definir_simulacoes_monte_carlo(
                    indice, jogador["simulacoes_monte_carlo"]
                )
                configuracao.definir_limite_tempo(indice, jogador.get("limite_tempo_segundos"))
            except (KeyError, TypeError, ValueError) as erro:
                raise ValueError(f"A configuração do Jogador {indice + 1} é inválida.") from erro
        return configuracao

    def _obter_indice_no(self, no_procurado, nos):
        if no_procurado is None:
            return None

        for indice in range(len(nos)):
            if nos[indice] is no_procurado:
                return indice

        raise ValueError("Um nó da árvore não foi encontrado no registro.")

    def _validar_dados_principais(self, dados):
        if not isinstance(dados, dict):
            raise TypeError("Os dados da árvore devem estar em um dicionário.")

        if isinstance(dados.get("versao"), bool) or dados.get("versao") not in (1, _VERSAO_DA_ARVORE):
            raise ValueError("A versão do arquivo da árvore não é suportada.")

        if not isinstance(dados.get("nos"), list) or not dados["nos"]:
            raise ValueError("O arquivo deve possuir ao menos o nó raiz.")

        if "indice_no_atual" not in dados:
            raise ValueError("O arquivo não informa qual é o nó atual.")

    def _validar_dados_raiz(self, dados_raiz):
        if not isinstance(dados_raiz, dict):
            raise ValueError("Os dados do nó raiz são inválidos.")

        if dados_raiz.get("indice") != 0:
            raise ValueError("O nó raiz deve possuir o índice zero.")

        if dados_raiz.get("indice_pai") is not None:
            raise ValueError("O nó raiz não pode possuir pai.")

        if dados_raiz.get("jogada_origem") is not None:
            raise ValueError("O nó raiz não pode possuir jogada de origem.")

        if not isinstance(dados_raiz.get("expandido"), bool):
            raise ValueError("A expansão do nó raiz deve ser verdadeira ou falsa.")

        jogada_voltada = dados_raiz.get("jogada_voltada", False)

        if not isinstance(jogada_voltada, bool):
            raise ValueError("A marca de jogada voltada deve ser booleana.")

        if jogada_voltada:
            raise ValueError("O nó raiz não pode representar uma jogada voltada.")

    def _validar_dados_no(self, dados_no, indice, nos_restaurados):
        if not isinstance(dados_no, dict):
            raise ValueError("Os dados de um nó são inválidos.")

        if dados_no.get("indice") != indice:
            raise ValueError("A ordem dos nós no arquivo é inválida.")

        indice_pai = dados_no.get("indice_pai")

        if not isinstance(indice_pai, int):
            raise ValueError("Todo nó filho deve informar o índice do pai.")

        if indice_pai < 0 or indice_pai >= len(nos_restaurados):
            raise ValueError("O pai de um nó ainda não foi carregado.")

        if dados_no.get("jogada_origem") is None:
            raise ValueError("Todo nó filho deve informar sua jogada.")

        if not isinstance(dados_no.get("expandido"), bool):
            raise ValueError("A expansão do nó deve ser verdadeira ou falsa.")

        jogada_voltada = dados_no.get("jogada_voltada", False)

        if not isinstance(jogada_voltada, bool):
            raise ValueError("A marca de jogada voltada deve ser booleana.")

    def _restaurar_caminho_atual(self, arvore, no_atual):
        caminho = []
        no_analisado = no_atual

        while not no_analisado.eh_raiz():
            caminho.insert(0, no_analisado)
            no_analisado = no_analisado.obter_pai()

        for no in caminho:
            arvore.avancar_para(no)

    def _validar_caminho(self, caminho):
        if not isinstance(caminho, str):
            raise TypeError("O caminho do arquivo deve ser um texto.")

        if not caminho.strip():
            raise ValueError("O caminho do arquivo deve ser preenchido.")
