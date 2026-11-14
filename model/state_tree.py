from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.state_node import NoEstado


class ArvoreEstados:
    """Organiza os estados conhecidos e o caminho atual da partida."""

    def __init__(self, estado_inicial, avaliacao_heuristica=None):
        if not isinstance(estado_inicial, EstadoJogo):
            raise TypeError("A árvore deve receber um EstadoJogo inicial.")

        self._serializador = SerializadorEstadoJogo()
        self._executor = ExecutorJogada()
        self._gerador = GeradorJogadas()
        self._raiz = NoEstado(estado_inicial, avaliacao_heuristica=avaliacao_heuristica)
        self._no_atual = self._raiz
        self._nos_por_identificador = {
            self._raiz.obter_identificador(): self._raiz
        }
        self._raiz.marcar_como_visitado()

    def obter_raiz(self):
        """Retorna o primeiro nó da árvore."""
        return self._raiz

    def obter_no_atual(self):
        """Retorna o nó correspondente à posição atual da partida."""
        return self._no_atual

    def obter_nos(self):
        """Retorna uma lista com todos os nós registrados."""
        return list(self._nos_por_identificador.values())

    def quantidade_nos(self):
        """Retorna a quantidade total de estados presentes na árvore."""
        return len(self._nos_por_identificador)

    def possui_estado(self, estado):
        """Informa se um estado equivalente já está registrado."""
        identificador = self._serializador.obter_identificador(estado)
        return identificador in self._nos_por_identificador

    def obter_estado_atual(self):
        """Retorna uma cópia do estado correspondente ao nó atual."""
        return self._no_atual.obter_estado()

    def adicionar_estado(self, estado, jogada, pai=None, avaliacao_heuristica=None):
        """Cria um filho se o estado ainda não existir na árvore."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O novo nó deve receber um EstadoJogo.")

        if not isinstance(jogada, Jogada):
            raise TypeError("O novo nó deve possuir uma Jogada de origem.")

        if pai is None:
            pai = self._no_atual

        self._validar_no_da_arvore(pai)
        identificador = self._serializador.obter_identificador(estado)

        if identificador in self._nos_por_identificador:
            return None

        novo_no = NoEstado(estado, jogada, pai, avaliacao_heuristica)
        pai.adicionar_filho(novo_no)
        self._nos_por_identificador[identificador] = novo_no
        return novo_no

    def expandir_no_atual(self):
        """Gera somente os filhos do nó que representa a jogada atual."""
        if self._no_atual.esta_expandido():
            return self._no_atual.obter_filhos()

        estado_atual = self._no_atual.obter_estado()
        jogadas = self._gerador.gerar(estado_atual)

        for jogada in jogadas:
            novo_estado = self._executor.executar(estado_atual, jogada)
            self.adicionar_estado(
                novo_estado,
                jogada,
                self._no_atual,
            )

        self._no_atual.marcar_como_expandido()
        return self._no_atual.obter_filhos()

    def registrar_jogada_realizada(self, jogada, estado_resultante):
        """Registra e visita o estado produzido por uma jogada real."""
        if not isinstance(jogada, Jogada):
            raise TypeError("A jogada realizada deve ser uma Jogada.")

        if not isinstance(estado_resultante, EstadoJogo):
            raise TypeError("O resultado deve ser um EstadoJogo.")

        identificador = self._serializador.obter_identificador(
            estado_resultante
        )
        no_destino = None

        for filho in self._no_atual.obter_filhos():
            if filho.obter_identificador() == identificador:
                no_destino = filho
                break

        if no_destino is None:
            no_destino = self.adicionar_estado(
                estado_resultante,
                jogada,
                self._no_atual,
            )

        if no_destino is None:
            raise ValueError(
                "O estado resultante já existe em outro ponto da árvore."
            )

        self.avancar_para(no_destino)
        return no_destino

    def avancar_para(self, no_destino):
        """Avança uma jogada quando o destino for filho do nó atual."""
        self._validar_no_da_arvore(no_destino)

        if no_destino.obter_pai() is not self._no_atual:
            raise ValueError("O destino não é filho do nó atual.")

        self._no_atual = no_destino
        self._no_atual.marcar_como_visitado()

    def voltar(self):
        """Volta uma jogada e informa se a operação foi realizada."""
        if self._no_atual.eh_raiz():
            return False

        no_anterior = self._no_atual
        self._no_atual = no_anterior.obter_pai()
        no_anterior.marcar_como_jogada_voltada()
        return True

    def obter_caminho_atual(self):
        """Retorna os nós visitados desde a raiz até o nó atual."""
        caminho = []
        no_analisado = self._no_atual

        while no_analisado is not None:
            caminho.insert(0, no_analisado)
            no_analisado = no_analisado.obter_pai()

        return caminho

    def _validar_no_da_arvore(self, no):
        if not isinstance(no, NoEstado):
            raise TypeError("O valor informado deve ser um NoEstado.")

        identificador = no.obter_identificador()
        no_registrado = self._nos_por_identificador.get(identificador)

        if no_registrado is not no:
            raise ValueError("O nó informado não pertence a esta árvore.")
