import json
import random

from model.game_state import EstadoJogo
from model.legal_move import serializar_jogada
from model.legal_move_generator import GeradorJogadas
from model.state_evaluator import AvaliadorEstado


_SIMULACOES_PADRAO = 100
_LIMITE_TURNOS_SIMULACAO = 40


class AgenteMonteCarlo:
    """Escolhe uma jogada pela média de partidas aleatórias simuladas."""

    def __init__(self, indice_jogador, semente=None):
        if (
            isinstance(indice_jogador, bool)
            or not isinstance(indice_jogador, int)
        ):
            raise TypeError("O índice do jogador deve ser inteiro.")
        if indice_jogador not in (0, 1):
            raise ValueError("O índice do jogador deve ser 0 ou 1.")

        self._indice_jogador = indice_jogador
        self._aleatorio = random.Random(semente)
        self._gerador = GeradorJogadas()
        self._avaliador = AvaliadorEstado(indice_jogador)
        self._limpar_estatisticas()

    def _limpar_estatisticas(self):
        self.nos_visitados = 0
        self.folhas_avaliadas = 0
        self.podas_realizadas = 0
        self.ultima_pontuacao = None
        self.simulacoes_realizadas = 0

    def _validar_entrada(self, estado, quantidade_simulacoes):
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser um EstadoJogo.")
        if (
            isinstance(quantidade_simulacoes, bool)
            or not isinstance(quantidade_simulacoes, int)
        ):
            raise TypeError("A quantidade de simulações deve ser inteira.")
        if quantidade_simulacoes < 1:
            raise ValueError("A quantidade de simulações deve ser positiva.")
        if (
            not estado.finalizado
            and estado.indice_jogador_atual != self._indice_jogador
        ):
            raise ValueError("A escolha deve acontecer no turno da IA.")

    def _simular_partida(self, estado):
        estado_atual = estado
        jogada_inicial = None

        for _ in range(_LIMITE_TURNOS_SIMULACAO):
            resultado = self._gerador.sortear_com_estado(
                estado_atual, self._aleatorio
            )
            if resultado is None:
                break
            jogada, estado_atual = resultado
            self.nos_visitados += 1
            if jogada_inicial is None:
                jogada_inicial = jogada

        if estado_atual.finalizado:
            vencedor = estado_atual.vencedor
            if vencedor is None:
                pontuacao = 0
            elif vencedor is estado_atual.obter_jogadores()[self._indice_jogador]:
                pontuacao = 1
            else:
                pontuacao = -1
        else:
            pontuacao = self._avaliador.avaliar(estado_atual)
            pontuacao = max(-100000, min(100000, pontuacao)) / 100000

        self.folhas_avaliadas += 1
        return jogada_inicial, pontuacao

    def escolher_jogada(
        self,
        estado,
        profundidade_maxima=1,
        usar_poda=True,
        quantidade_simulacoes=_SIMULACOES_PADRAO,
    ):
        """Retorna a primeira ação com maior média nas simulações."""
        self._validar_entrada(estado, quantidade_simulacoes)
        self._limpar_estatisticas()
        resultados = {}

        for _ in range(quantidade_simulacoes):
            jogada, pontuacao = self._simular_partida(estado)
            if jogada is None:
                continue
            chave = json.dumps(
                serializar_jogada(jogada),
                sort_keys=True,
            )
            if chave not in resultados:
                resultados[chave] = [jogada, 0.0, 0]
            resultados[chave][1] += pontuacao
            resultados[chave][2] += 1
            self.simulacoes_realizadas += 1

        if not resultados:
            self.ultima_pontuacao = self._avaliador.avaliar(estado)
            return None

        melhor = max(
            resultados.values(),
            key=lambda resultado: resultado[1] / resultado[2],
        )
        self.ultima_pontuacao = melhor[1] / melhor[2]
        return melhor[0]
