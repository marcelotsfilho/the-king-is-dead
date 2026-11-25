from math import isfinite
from time import perf_counter

from model.enums import FaseTurno
from model.game_state import EstadoJogo
from model.legal_move import Jogada
from model.legal_move_generator import GeradorJogadas
from model.state_evaluator import AvaliadorEstado


class _LimiteDeTempo(Exception):
    pass


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
        self._limpar_estatisticas()

    def _limpar_estatisticas(self):
        self.nos_visitados = 0
        self.folhas_avaliadas = 0
        self.podas_realizadas = 0
        self.ultima_pontuacao = None
        self.profundidade_concluida = 0
        self.tempo_esgotado = False
        self._respostas = {}
        self._prazo = None
        self._melhor_parcial = (None, None)

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
        if self._prazo is not None and perf_counter() >= self._prazo:
            raise _LimiteDeTempo
        self.folhas_avaliadas += 1
        return self._avaliador.avaliar(estado, profundidade)

    def _avaliar_ultimo_nivel(self, estado, profundidade, maximizar):
        def avaliar(filho):
            self.nos_visitados += 1
            return self._avaliar_folha(filho, profundidade + 1)

        escolher_pontuacao = max if maximizar else min
        sucessores = self._gerador.avaliar_sucessores(estado, avaliar)
        pontuacao = escolher_pontuacao(sucessores, default=None)
        if pontuacao is None:
            pontuacao = self._avaliar_folha(estado, profundidade)
        return pontuacao, None

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

        if self._prazo is not None and perf_counter() >= self._prazo:
            raise _LimiteDeTempo

        maximizar = estado.indice_jogador_atual == self._indice_jogador_ia
        # Só o avaliador padrão lê a posição temporária e devolve uma nota.
        if (
            not usar_poda
            and 0 < profundidade == profundidade_maxima - 1
            and type(self._avaliador) is AvaliadorEstado
        ):
            return self._avaliar_ultimo_nivel(estado, profundidade, maximizar)

        melhor_pontuacao = None
        melhor_jogada = None

        chave_ordem = None
        prioridade = None
        # A raiz mantém a ordem original para preservar o desempate.
        if usar_poda and profundidade > 0:
            chave_ordem = (profundidade, estado.indice_jogador_atual)
            prioridade = self._respostas.get(chave_ordem)
        if prioridade is None:
            sucessores = self._gerador.gerar_com_estados(estado)
        else:
            sucessores = self._gerador.gerar_com_estados(
                estado, prioridade=prioridade
            )

        for jogada, novo_estado in sucessores:
            pontuacao, _ = self._buscar(
                novo_estado,
                profundidade + 1,
                profundidade_maxima,
                alfa,
                beta,
                usar_poda,
            )

            if (
                melhor_pontuacao is None
                or (maximizar and pontuacao > melhor_pontuacao)
                or (not maximizar and pontuacao < melhor_pontuacao)
            ):
                melhor_pontuacao = pontuacao
                melhor_jogada = jogada
                if self._prazo is not None and profundidade == 0 and profundidade_maxima == 1:
                    self._melhor_parcial = pontuacao, jogada

            if usar_poda:
                if maximizar:
                    alfa = max(alfa, melhor_pontuacao)
                else:
                    beta = min(beta, melhor_pontuacao)

                if beta <= alfa:
                    self.podas_realizadas += 1
                    break

        if melhor_pontuacao is None:
            return self._avaliar_folha(estado, profundidade), None

        if (
            chave_ordem is not None
            and isinstance(melhor_jogada, Jogada)
            and melhor_jogada.eh_carta()
        ):
            # Uma resposta boa costuma ser útil em outros ramos do mesmo nível.
            self._respostas[chave_ordem] = melhor_jogada

        return melhor_pontuacao, melhor_jogada

    def escolher_jogada(
        self, estado, profundidade_maxima=1, usar_poda=True, *, limite_segundos=None
    ):
        """Escolhe em profundidade fixa ou aprofunda a busca dentro do prazo."""
        self._validar_entrada(estado, profundidade_maxima, usar_poda)
        if limite_segundos is not None:
            if isinstance(limite_segundos, bool) or not isinstance(limite_segundos, (int, float)):
                raise TypeError("O limite de tempo deve ser numérico.")
            if not isfinite(limite_segundos) or limite_segundos <= 0:
                raise ValueError("O limite de tempo deve ser positivo e finito.")
        self._limpar_estatisticas()

        if (
            not estado.finalizado
            and estado.fase_turno != FaseTurno.ESCOLHER_ACAO
        ):
            return None

        if limite_segundos is not None:
            return self._escolher_com_prazo(estado, profundidade_maxima, usar_poda, limite_segundos)

        self.ultima_pontuacao, jogada = self._buscar_na_raiz(estado, profundidade_maxima, usar_poda)
        self.profundidade_concluida = profundidade_maxima
        return jogada

    def _buscar_na_raiz(self, estado, profundidade, usar_poda):
        return self._buscar(
            estado,
            0,
            profundidade,
            float("-inf"),
            float("inf"),
            usar_poda,
        )

    def _escolher_com_prazo(self, estado, profundidade_maxima, usar_poda, limite_segundos):
        melhor_jogada = None
        self._prazo = perf_counter() + limite_segundos
        try:
            for profundidade in range(1, profundidade_maxima + 1):
                self._respostas.clear()
                pontuacao, jogada = self._buscar_na_raiz(estado, profundidade, usar_poda)
                self.ultima_pontuacao = pontuacao
                melhor_jogada = jogada
                self.profundidade_concluida = profundidade
                if jogada is None:
                    break
        except _LimiteDeTempo:
            self.tempo_esgotado = True
        finally:
            self._prazo = None

        if self.profundidade_concluida or not self.tempo_esgotado:
            return melhor_jogada
        self.ultima_pontuacao, jogada = self._melhor_parcial
        if jogada is not None:
            return jogada
        # Um passe é o primeiro sucessor legal e serve de saída se o prazo for imediato.
        primeiro, _ = next(iter(self._gerador.gerar_com_estados(estado)), (None, None))
        return primeiro
