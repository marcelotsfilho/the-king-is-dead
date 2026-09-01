import random

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao
from model.game_state import EstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


class ConfiguracaoJogo:
    """Prepara automaticamente o estado inicial para dois jogadores."""

    def __init__(self, semente=None):
        self._gerador_aleatorio = random.Random(semente)

    def criar_trilha_disputas(self, tabuleiro):
        nomes_regioes = tabuleiro.obter_nomes_das_regioes()
        self._gerador_aleatorio.shuffle(nomes_regioes)
        trilha = TrilhaDisputas(nomes_regioes)
        return trilha

    def criar_estado_inicial(self, nomes_jogadores):
        """Cria tabuleiro, jogadores, reserva e trilha prontos para jogar."""
        self._validar_nomes_jogadores(nomes_jogadores)

        tabuleiro = Tabuleiro()
        trilha = self.criar_trilha_disputas(tabuleiro)
        jogadores = []

        for nome in nomes_jogadores:
            jogadores.append(Jogador(nome))

        reserva = ReservaSeguidores(16)

        self._colocar_seguidores_das_regioes_iniciais(tabuleiro, reserva)
        self._distribuir_seguidores_para_as_cortes(jogadores, reserva)
        self._completar_seguidores_das_regioes(tabuleiro, reserva)

        return EstadoJogo(tabuleiro, trilha, jogadores, reserva)

    def _colocar_seguidores_das_regioes_iniciais(self, tabuleiro, reserva):
        iniciais = {
            "Moray": Faccao.ESCOCESES,
            "Gwynedd": Faccao.GALESES,
            "Essex": Faccao.INGLESES,
        }

        for nome_regiao in iniciais:
            faccao = iniciais[nome_regiao]
            reserva.retirar(faccao, 2)
            tabuleiro.obter_regiao(nome_regiao).adicionar_seguidores(faccao, 2)

    def _distribuir_seguidores_para_as_cortes(self, jogadores, reserva):
        for jogador in jogadores:
            for _ in range(2):
                faccao = self._sortear_faccao_disponivel(reserva)
                reserva.retirar(faccao)
                jogador.adicionar_seguidor_na_corte(faccao)

    def _completar_seguidores_das_regioes(self, tabuleiro, reserva):
        for nome_regiao in tabuleiro.obter_nomes_das_regioes():
            regiao = tabuleiro.obter_regiao(nome_regiao)

            while regiao.total_de_seguidores() < 4:
                faccao = self._sortear_faccao_disponivel(reserva)
                reserva.retirar(faccao)
                regiao.adicionar_seguidores(faccao)

    def _sortear_faccao_disponivel(self, reserva):
        opcoes = []

        for faccao in Faccao:
            quantidade = reserva.quantidade(faccao)

            for _ in range(quantidade):
                opcoes.append(faccao)

        return self._gerador_aleatorio.choice(opcoes)

    def _validar_nomes_jogadores(self, nomes_jogadores):
        if not isinstance(nomes_jogadores, list):
            raise ValueError("Os nomes dos jogadores devem estar em uma lista.")

        if len(nomes_jogadores) != 2:
            raise ValueError("A partida deve possuir exatamente dois jogadores.")
