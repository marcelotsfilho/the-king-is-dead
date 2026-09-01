import unittest

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


def criar_jogo_manual():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(0)
    estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)
    return Jogo(estado)


class TesteJogo(unittest.TestCase):
    """Verifica turnos, passes, disputas e encerramento."""

    def test_um_passe_alterna_o_jogador(self):
        jogo = criar_jogo_manual()

        jogo.passar()

        self.assertEqual(jogo.estado.passes_consecutivos, 1)
        self.assertEqual(jogo.estado.obter_jogador_atual().nome, "Bruno")

    def test_dois_passes_resolvem_a_proxima_disputa(self):
        jogo = criar_jogo_manual()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES, 3)
        moray.adicionar_seguidores(Faccao.GALESES)

        jogo.passar()
        jogo.passar()

        self.assertEqual(jogo.estado.disputas_resolvidas, 1)
        self.assertEqual(jogo.estado.passes_consecutivos, 0)
        self.assertEqual(moray.controlador, Faccao.ESCOCESES)
        self.assertFalse(jogo.estado.trilha_disputas.obter_carta(1).virada_para_cima)

    def test_seguidores_da_regiao_resolvida_voltam_para_reserva(self):
        jogo = criar_jogo_manual()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES, 3)
        moray.adicionar_seguidores(Faccao.INGLESES)

        jogo.resolver_proxima_disputa()

        self.assertEqual(moray.total_de_seguidores(), 0)
        self.assertEqual(jogo.estado.reserva.quantidade(Faccao.ESCOCESES), 3)
        self.assertEqual(jogo.estado.reserva.quantidade(Faccao.INGLESES), 1)

    def test_empate_marca_regiao_como_instavel(self):
        jogo = criar_jogo_manual()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES, 2)
        moray.adicionar_seguidores(Faccao.GALESES, 2)

        jogo.resolver_proxima_disputa()

        self.assertTrue(moray.instavel)
        self.assertEqual(jogo.estado.quantidade_instabilidades, 1)

    def test_regiao_vazia_fica_instavel(self):
        jogo = criar_jogo_manual()

        jogo.resolver_proxima_disputa()

        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        self.assertTrue(moray.instavel)

    def test_terceira_instabilidade_encerra_por_invasao(self):
        jogo = criar_jogo_manual()

        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()

        self.assertTrue(jogo.estado.finalizado)
        self.assertEqual(jogo.estado.motivo_encerramento, "Invasão francesa")

    def test_invasao_e_vencida_por_mais_conjuntos_na_corte(self):
        jogo = criar_jogo_manual()
        jogador_1 = jogo.estado.obter_jogadores()[0]

        for faccao in Faccao:
            jogador_1.adicionar_seguidor_na_corte(faccao)

        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()

        self.assertIs(jogo.estado.vencedor, jogador_1)

    def test_oitava_disputa_encerra_por_coroacao(self):
        jogo = criar_jogo_manual()

        for regiao in jogo.estado.tabuleiro.obter_regioes().values():
            regiao.adicionar_seguidores(Faccao.ESCOCESES)

        jogador_1 = jogo.estado.obter_jogadores()[0]
        jogador_1.adicionar_seguidor_na_corte(Faccao.ESCOCESES)

        for _ in range(8):
            jogo.resolver_proxima_disputa()

        self.assertTrue(jogo.estado.finalizado)
        self.assertEqual(jogo.estado.motivo_encerramento, "Coroação")
        self.assertEqual(jogo.estado.faccao_vencedora, Faccao.ESCOCESES)
        self.assertIs(jogo.estado.vencedor, jogador_1)

    def test_nao_permite_passar_depois_do_encerramento(self):
        jogo = criar_jogo_manual()

        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()
        jogo.resolver_proxima_disputa()

        with self.assertRaises(ValueError):
            jogo.passar()

    def test_partida_completa_pode_ser_jogada_apenas_passando(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        jogo = Jogo(estado)
        quantidade_passes = 0

        while not estado.finalizado:
            jogo.passar()
            quantidade_passes += 1

            if quantidade_passes > 16:
                self.fail("A partida não foi encerrada após oito disputas.")

        self.assertIn(
            estado.motivo_encerramento,
            ["Invasão francesa", "Coroação"],
        )

        for faccao in Faccao:
            total = estado.reserva.quantidade(faccao)

            for regiao in estado.tabuleiro.obter_regioes().values():
                total += regiao.quantidade_de_seguidores(faccao)

            for jogador in estado.obter_jogadores():
                total += jogador.qtd_na_corte(faccao)

            self.assertEqual(total, 16)


if __name__ == "__main__":
    unittest.main()
