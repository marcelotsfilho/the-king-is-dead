from model.enums import FaseTurno
from model.game_state import EstadoJogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.state_evaluator import AvaliadorEstado


class AgenteMinimax:
    """Escolhe jogadas com antecipação e poda alfa-beta opcional."""

    def __init__(self, indice_jogador_ia, avaliador=None):
        self._avaliador = AvaliadorEstado(indice_jogador_ia)
        if avaliador is not None:
            if not callable(getattr(avaliador, "avaliar", None)):
                raise TypeError("O avaliador deve possuir o método avaliar.")
            self._avaliador = avaliador
        self._indice_jogador_ia = indice_jogador_ia
        self._gerador = GeradorJogadas()
        self._executor = ExecutorJogada()
        self._limpar_estatisticas()

    def _limpar_estatisticas(self):
        self.nos_visitados = 0
        self.folhas_avaliadas = 0
        self.podas_realizadas = 0
        self.ultima_pontuacao = None

    def _validar_entrada(self, estado, profundidade_maxima, usar_poda):
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser um EstadoJogo.")

        if (
            isinstance(profundidade_maxima, bool)
            or not isinstance(profundidade_maxima, int)
        ):
            raise TypeError("A profundidade máxima deve ser um inteiro.")

        if profundidade_maxima < 1:
            raise ValueError("A profundidade máxima deve ser pelo menos 1.")

        if not isinstance(usar_poda, bool):
            raise TypeError("A opção de poda deve ser True ou False.")

        if not estado.finalizado:
            if estado.indice_jogador_atual != self._indice_jogador_ia:
                raise ValueError("A escolha deve acontecer no turno da IA.")

    def _avaliar_folha(self, estado, profundidade):
        self.folhas_avaliadas += 1
        return self._avaliador.avaliar(estado, profundidade)

    def _buscar(
        self,
        estado,
        profundidade,
        profundidade_maxima,
        alfa,
        beta,
        usar_poda,
    ):
        self.nos_visitados += 1

        if estado.finalizado or profundidade == profundidade_maxima:
            return self._avaliar_folha(estado, profundidade), None

        maximizar = estado.indice_jogador_atual == self._indice_jogador_ia
        melhor_pontuacao = float("inf")

        if maximizar:
            melhor_pontuacao = float("-inf")

        melhor_jogada = None

        encontrou_jogada = False

        for jogada, novo_estado in self._gerador.gerar_com_estados(estado):
            encontrou_jogada = True
            pontuacao, jogada_seguinte = self._buscar(
                novo_estado,
                profundidade + 1,
                profundidade_maxima,
                alfa,
                beta,
                usar_poda,
            )

            # avalia melhor jogada no turno da IA e pior no turno do adversário
            if maximizar:
                if pontuacao > melhor_pontuacao:
                    melhor_pontuacao = pontuacao
                    melhor_jogada = jogada
            else:
                if pontuacao < melhor_pontuacao:
                    melhor_pontuacao = pontuacao
                    melhor_jogada = jogada

            # avalia jogada e evita explorar ramos desnecessários com poda alfa-beta
            if usar_poda:
                if maximizar:
                    alfa = max(alfa, melhor_pontuacao)
                else:
                    beta = min(beta, melhor_pontuacao)

                if beta <= alfa:
                    self.podas_realizadas += 1
                    break

        if not encontrou_jogada:
            return self._avaliar_folha(estado, profundidade), None

        return melhor_pontuacao, melhor_jogada

    def escolher_jogada(self, estado, profundidade_maxima=1, usar_poda=True):
        """Retorna a melhor jogada; empates mantêm a primeira encontrada."""
        self._validar_entrada(estado, profundidade_maxima, usar_poda)
        self._limpar_estatisticas()

        if (
            not estado.finalizado
            and estado.fase_turno != FaseTurno.ESCOLHER_ACAO
        ):
            return None

        pontuacao, jogada = self._buscar(
            estado,
            0,
            profundidade_maxima,
            float("-inf"),
            float("inf"),
            usar_poda,
        )
        self.ultima_pontuacao = pontuacao
        return jogada
