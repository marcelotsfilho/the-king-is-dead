import unittest

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao
from model.game_setup import ConfiguracaoJogo


class TesteConfiguracaoJogo(unittest.TestCase):

    def test_cria_uma_trilha_de_disputas(self):
        tabuleiro = Tabuleiro()
        configuracao = ConfiguracaoJogo()

        trilha = configuracao.criar_trilha_disputas(tabuleiro)

        self.assertIsInstance(trilha, TrilhaDisputas)

    def test_trilha_possui_todas_as_regioes(self):
        tabuleiro = Tabuleiro()
        configuracao = ConfiguracaoJogo()

        trilha = configuracao.criar_trilha_disputas(tabuleiro)
        cartas = trilha.obter_cartas()

        nomes_encontrados = []

        for carta in cartas:
            nomes_encontrados.append(carta.nome_regiao)

        nomes_esperados = tabuleiro.obter_nomes_das_regioes()

        self.assertEqual(len(nomes_encontrados), 8)
        self.assertEqual(set(nomes_encontrados), set(nomes_esperados))

    def test_cria_estado_com_dois_jogadores(self):
        configuracao = ConfiguracaoJogo(42)

        estado = configuracao.criar_estado_inicial(["Ana", "Bruno"])
        jogadores = estado.obter_jogadores()

        self.assertEqual(len(jogadores), 2)
        self.assertEqual(jogadores[0].nome, "Ana")
        self.assertEqual(jogadores[1].nome, "Bruno")

    def test_cada_regiao_comeca_com_quatro_seguidores(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        for regiao in estado.tabuleiro.obter_regioes().values():
            self.assertEqual(regiao.total_de_seguidores(), 4)

    def test_cada_jogador_comeca_com_dois_seguidores_na_corte(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        for jogador in estado.obter_jogadores():
            total_corte = 0

            for faccao in Faccao:
                total_corte += jogador.qtd_na_corte(faccao)

            self.assertEqual(total_corte, 2)

    def test_setup_conserva_dezesseis_seguidores_por_faccao(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        for faccao in Faccao:
            total = estado.reserva.quantidade(faccao)

            for regiao in estado.tabuleiro.obter_regioes().values():
                total += regiao.quantidade_de_seguidores(faccao)

            for jogador in estado.obter_jogadores():
                total += jogador.qtd_na_corte(faccao)

            self.assertEqual(total, 16)

    def test_regioes_iniciais_possuem_seguidores_da_faccao_correta(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        self.assertGreaterEqual(
            estado.tabuleiro.obter_regiao("Moray").quantidade_de_seguidores(
                Faccao.ESCOCESES
            ),
            2,
        )
        self.assertGreaterEqual(
            estado.tabuleiro.obter_regiao("Gwynedd").quantidade_de_seguidores(
                Faccao.GALESES
            ),
            2,
        )
        self.assertGreaterEqual(
            estado.tabuleiro.obter_regiao("Essex").quantidade_de_seguidores(
                Faccao.INGLESES
            ),
            2,
        )

    def test_mesma_semente_reproduz_o_setup(self):
        estado_1 = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        estado_2 = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        nomes_1 = []
        nomes_2 = []

        for carta in estado_1.trilha_disputas.obter_cartas():
            nomes_1.append(carta.nome_regiao)

        for carta in estado_2.trilha_disputas.obter_cartas():
            nomes_2.append(carta.nome_regiao)

        self.assertEqual(nomes_1, nomes_2)


if __name__ == "__main__":
    unittest.main()
