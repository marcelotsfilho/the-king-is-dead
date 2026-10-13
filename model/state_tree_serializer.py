import json

from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import restaurar_jogada, serializar_jogada
from model.state_tree import ArvoreEstados


_VERSAO_DA_ARVORE = 1


class SerializadorArvoreEstados:
    """Salva e restaura a árvore de estados em formato JSON."""

    def __init__(self):
        self._serializador_estado = SerializadorEstadoJogo()

    def serializar(self, arvore):
        """Transforma a árvore completa em dados simples."""
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
                }
            )

        indice_atual = self._obter_indice_no(
            arvore.obter_no_atual(),
            nos,
        )

        return {
            "versao": _VERSAO_DA_ARVORE,
            "indice_no_atual": indice_atual,
            "nos": dados_nos,
        }

    def restaurar(self, dados):
        """Reconstrói a árvore a partir dos dados salvos."""
        self._validar_dados_principais(dados)
        dados_nos = dados["nos"]
        dados_raiz = dados_nos[0]
        self._validar_dados_raiz(dados_raiz)

        estado_raiz = self._serializador_estado.restaurar(
            dados_raiz["estado"]
        )
        arvore = ArvoreEstados(estado_raiz)
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
            novo_no = arvore.adicionar_estado(estado, jogada, pai)

            if novo_no is None:
                raise ValueError("O arquivo possui um estado repetido.")

            if dados_no.get("expandido") is True:
                novo_no.marcar_como_expandido()

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

    def salvar(self, arvore, caminho):
        """Escreve a árvore em um arquivo JSON."""
        self._validar_caminho(caminho)
        dados = self.serializar(arvore)

        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    def carregar(self, caminho):
        """Lê um arquivo JSON e reconstrói a árvore."""
        self._validar_caminho(caminho)

        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError:
            raise ValueError("O arquivo não contém um JSON válido.")

        return self.restaurar(dados)

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

        if dados.get("versao") != _VERSAO_DA_ARVORE:
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
