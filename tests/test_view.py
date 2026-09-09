import unittest
from unittest.mock import patch

from model.board import Tabuleiro
from view.game_view import VisaoJogo


class JanelaFalsa:
    def __init__(self, largura, altura):
        self._tamanho = (largura, altura)

    def get_size(self):
        return self._tamanho


class TesteVisaoResponsiva(unittest.TestCase):
    def test_tamanho_inicial_cabe_em_monitor_full_hd(self):
        visao = VisaoJogo.__new__(VisaoJogo)

        with patch("pygame.display.get_desktop_sizes", return_value=[(1920, 1080)]):
            largura, altura = visao._calcular_tamanho_inicial_da_janela()

        self.assertLessEqual(largura, 1728)
        self.assertLessEqual(altura, 918)
        self.assertAlmostEqual(largura / altura, 1200 / 1030, places=2)

    def test_converte_clique_de_uma_janela_reduzida(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(600, 515)

        posicao_logica = visao._converter_para_posicao_logica((525, 353))

        self.assertEqual(posicao_logica, (1050, 706))

    def test_converte_clique_quando_existem_margens_laterais(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(800, 515)

        posicao_logica = visao._converter_para_posicao_logica((625, 353))

        self.assertEqual(posicao_logica, (1050, 706))

    def test_clique_na_margem_nao_atinge_o_jogo(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(800, 515)

        posicao_logica = visao._converter_para_posicao_logica((50, 200))

        self.assertEqual(posicao_logica, (-1, -1))


class TesteFronteirasDaVisao(unittest.TestCase):
    def setUp(self):
        self.visao = VisaoJogo.__new__(VisaoJogo)
        self.tabuleiro = Tabuleiro()

    def test_cada_fronteira_e_obtida_uma_unica_vez(self):
        fronteiras = self.visao._obter_fronteiras_sem_repeticao(
            self.tabuleiro
        )

        self.assertEqual(len(fronteiras), 14)

        identificadores = []
        for origem, destino in fronteiras:
            identificadores.append(frozenset([origem, destino]))

        self.assertEqual(len(identificadores), len(set(identificadores)))

    def test_pontos_horizontais_ficam_nas_bordas_das_regioes(self):
        ponto_moray = self.visao._calcular_ponto_na_borda(
            "Moray", "Strathclyde"
        )
        ponto_strathclyde = self.visao._calcular_ponto_na_borda(
            "Strathclyde", "Moray"
        )

        self.assertEqual(ponto_moray, (230, 165))
        self.assertEqual(ponto_strathclyde, (260, 165))

    def test_pontos_verticais_ficam_nas_bordas_das_regioes(self):
        ponto_northumbria = self.visao._calcular_ponto_na_borda(
            "Northumbria", "Essex"
        )
        ponto_essex = self.visao._calcular_ponto_na_borda(
            "Essex", "Northumbria"
        )

        self.assertEqual(ponto_northumbria, (575, 230))
        self.assertEqual(ponto_essex, (575, 280))

    def test_fronteira_longa_desvia_da_regiao_intermediaria(self):
        pontos = self.visao._obter_pontos_da_fronteira(
            "Moray", "Northumbria"
        )

        self.assertEqual(pontos[0], (135, 100))
        self.assertEqual(pontos[1], (135, 82))
        self.assertEqual(pontos[-2], (575, 82))
        self.assertEqual(pontos[-1], (575, 100))


if __name__ == "__main__":
    unittest.main()
