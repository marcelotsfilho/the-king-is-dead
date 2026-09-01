import unittest

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
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


if __name__ == "__main__":
    unittest.main()