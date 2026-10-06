import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao, TipoJogada
from model.game_state import EstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.player import Jogador
from model.supply import ReservaSeguidores


def criar_estado_manual(quantidade_reserva=3):
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(quantidade_reserva)
    return EstadoJogo(tabuleiro, trilha, jogadores, reserva)


class TesteExecutorJogada(unittest.TestCase):
    def setUp(self):
        self.executor = ExecutorJogada()

    def test_executa_passe_sem_alterar_estado_original(self):
        estado = criar_estado_manual()
        jogada = Jogada(TipoJogada.PASSE)

        resultado = self.executor.executar(estado, jogada)

        self.assertEqual(estado.passes_consecutivos, 0)
        self.assertEqual(estado.indice_jogador_atual, 0)
        self.assertEqual(resultado.passes_consecutivos, 1)
        self.assertEqual(resultado.indice_jogador_atual, 1)

    def test_segundo_passe_resolve_disputa_apenas_na_copia(self):
        estado = criar_estado_manual()
        estado.passes_consecutivos = 1
        moray = estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES, 2)
        jogada = Jogada(TipoJogada.PASSE)

        resultado = self.executor.executar(estado, jogada)

        moray_resultado = resultado.tabuleiro.obter_regiao("Moray")
        self.assertFalse(moray.esta_resolvida())
        self.assertTrue(moray_resultado.esta_resolvida())
        self.assertTrue(estado.trilha_disputas.obter_carta(1).virada_para_cima)
        self.assertFalse(
            resultado.trilha_disputas.obter_carta(1).virada_para_cima
        )

    def test_executa_carta_e_convocacao_como_uma_jogada(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        carta = CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        jogador.adicionar_carta_mao(carta)
        estado.reserva.retirar(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_ESCOCES,
            parametros={"regiao": "Strathclyde"},
            nome_regiao_convocacao="Strathclyde",
            faccao_convocacao=Faccao.ESCOCESES,
        )

        resultado = self.executor.executar(estado, jogada)

        jogador_resultado = resultado.obter_jogadores()[0]
        strathclyde = resultado.tabuleiro.obter_regiao("Strathclyde")
        self.assertEqual(jogador.quantidade_cartas(), 1)
        self.assertEqual(jogador_resultado.quantidade_cartas(), 0)
        self.assertEqual(len(jogador_resultado.obter_descarte_mao()), 1)
        self.assertEqual(
            jogador_resultado.qtd_na_corte(Faccao.ESCOCESES),
            1,
        )
        self.assertEqual(
            strathclyde.quantidade_de_seguidores(Faccao.ESCOCESES),
            1,
        )
        self.assertEqual(resultado.indice_jogador_atual, 1)
        self.assertEqual(resultado.fase_turno, FaseTurno.ESCOLHER_ACAO)

    def test_jogada_invalida_nao_altera_estado_original(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_ESCOCES,
            parametros={"regiao": "Devon"},
            nome_regiao_convocacao="Moray",
            faccao_convocacao=Faccao.ESCOCESES,
        )

        with self.assertRaises(ValueError):
            self.executor.executar(estado, jogada)

        self.assertEqual(jogador.quantidade_cartas(), 1)
        self.assertEqual(estado.indice_jogador_atual, 0)
        self.assertEqual(
            estado.tabuleiro.obter_regiao("Devon").total_de_seguidores(),
            0,
        )

    def test_rejeita_carta_que_nao_esta_na_mao(self):
        estado = criar_estado_manual()
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.REUNIR,
            parametros={},
            nome_regiao_convocacao="Moray",
            faccao_convocacao=Faccao.ESCOCESES,
        )

        with self.assertRaises(ValueError):
            self.executor.executar(estado, jogada)

    def test_rejeita_objeto_que_nao_seja_jogada(self):
        estado = criar_estado_manual()

        with self.assertRaises(TypeError):
            self.executor.executar(estado, "passar")


if __name__ == "__main__":
    unittest.main()
