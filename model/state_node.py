from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada


class NoEstado:
    """Representa um estado dentro da árvore de jogadas."""

    def __init__(self, estado, jogada_origem=None, pai=None):
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O nó deve receber uma instância de EstadoJogo.")

        if pai is not None and not isinstance(pai, NoEstado):
            raise TypeError("O pai deve ser outro NoEstado ou None.")

        if jogada_origem is not None and not isinstance(jogada_origem, Jogada):
            raise TypeError("A jogada de origem deve ser uma Jogada ou None.")

        if pai is None and jogada_origem is not None:
            raise ValueError("O nó raiz não pode possuir uma jogada de origem.")

        if pai is not None and jogada_origem is None:
            raise ValueError("Um nó filho deve possuir uma jogada de origem.")

        self._serializador = SerializadorEstadoJogo()
        self._estado = self._serializador.copiar(estado)
        self._identificador = self._serializador.obter_identificador(
            self._estado
        )
        self._jogada_origem = jogada_origem
        self._pai = pai
        self._filhos = []
        self._visitado = False
        self._jogada_voltada = False
        self._expandido = False

    def obter_estado(self):
        """Retorna uma cópia do estado armazenado no nó."""
        return self._serializador.copiar(self._estado)

    def obter_identificador(self):
        """Retorna o identificador usado para detectar estados repetidos."""
        return self._identificador

    def obter_jogada_origem(self):
        """Retorna a jogada que gerou este nó."""
        return self._jogada_origem

    def obter_pai(self):
        """Retorna o nó anterior ou None quando este nó for a raiz."""
        return self._pai

    def obter_filhos(self):
        """Retorna uma cópia da lista de filhos."""
        return self._filhos.copy()

    def adicionar_filho(self, filho):
        """Adiciona um filho quando ele pertence ao nó e ainda não existe."""
        if not isinstance(filho, NoEstado):
            raise TypeError("O filho deve ser uma instância de NoEstado.")

        if filho.obter_pai() is not self:
            raise ValueError("O nó informado não possui este nó como pai.")

        for filho_existente in self._filhos:
            if (
                filho_existente.obter_identificador()
                == filho.obter_identificador()
            ):
                return False

        self._filhos.append(filho)
        return True

    def quantidade_filhos(self):
        """Retorna quantos filhos foram ligados ao nó."""
        return len(self._filhos)

    def eh_raiz(self):
        """Informa se o nó representa o começo da árvore."""
        return self._pai is None

    def eh_folha(self):
        """Informa se o nó ainda não possui filhos."""
        return len(self._filhos) == 0

    def obter_nivel(self):
        """Conta quantas ligações separam o nó da raiz."""
        nivel = 0
        no_atual = self._pai

        while no_atual is not None:
            nivel += 1
            no_atual = no_atual.obter_pai()

        return nivel

    def marcar_como_visitado(self):
        """Indica que este estado faz parte do caminho percorrido."""
        self._visitado = True
        self._jogada_voltada = False

    def desmarcar_como_visitado(self):
        """Remove a marcação para permitir a volta de uma jogada."""
        self._visitado = False

    def esta_visitado(self):
        """Informa se o nó está marcado como visitado."""
        return self._visitado

    def marcar_como_jogada_voltada(self):
        """Indica que o jogador visitou o nó e depois voltou."""
        self._visitado = False
        self._jogada_voltada = True

    def representa_jogada_voltada(self):
        """Informa se o nó representa uma jogada que foi voltada."""
        return self._jogada_voltada

    def marcar_como_expandido(self):
        """Registra que as próximas jogadas do nó já foram geradas."""
        self._expandido = True

    def esta_expandido(self):
        """Informa se os filhos possíveis do nó já foram gerados."""
        return self._expandido
