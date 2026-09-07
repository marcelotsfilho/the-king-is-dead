import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
