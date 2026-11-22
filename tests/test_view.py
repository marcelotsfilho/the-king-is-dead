import unittest
from unittest.mock import patch

import pygame

from model.board import Tabuleiro
from view.game_view import VisaoJogo


class JanelaFalsa:
    def __init__(self, largura, altura):
        self._tamanho = (largura, altura)

    def get_size(self):
        return self._tamanho


class NoArvoreFalso:
    def __init__(self, quantidade_filhos):
        self._quantidade_filhos = quantidade_filhos

    def quantidade_filhos(self):
        return self._quantidade_filhos


class ArvoreFalsa:
    def __init__(self, quantidade_filhos):
        self._no_atual = NoArvoreFalso(quantidade_filhos)

    def obter_no_atual(self):
        return self._no_atual


class TesteVisaoResponsiva(unittest.TestCase):
    def test_identifica_pausa_da_ia_em_janela_reduzida(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(600, 515)
        visao.retangulo_pausar_ia = pygame.Rect(650, 35, 240, 45)
        self.assertTrue(visao.botao_pausar_ia_foi_clicado((385, 28)))
        self.assertFalse(visao.botao_pausar_ia_foi_clicado((0, 0)))

    def test_configuracao_identifica_iniciar_e_voltar_com_escala(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(600, 515)
        visao.retangulo_iniciar_partida = pygame.Rect(420, 650, 360, 70)
        visao.retangulo_voltar_menu = pygame.Rect(420, 750, 360, 70)
        self.assertEqual(visao.obter_acao_tela_configuracao((300, 342.5)), "iniciar")
        self.assertEqual(visao.obter_acao_tela_configuracao((300, 392.5)), "voltar")
        self.assertIsNone(visao.obter_acao_tela_configuracao((0, 0)))

    def test_configuracao_reconhece_jogador_e_controle_em_janela_reduzida(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(600, 515)
        for indice in (0, 1):
            controles = visao._obter_controles_configuracao(indice)
            for acao, retangulo in controles.items():
                posicao = (retangulo.centerx / 2, retangulo.centery / 2)
                self.assertEqual(visao.obter_acao_configuracao(posicao), (acao, indice))
        self.assertIsNone(visao.obter_acao_configuracao((0, 0)))

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

    def test_trilha_reconhece_as_oito_posicoes_em_janela_reduzida(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(800, 515)

        for indice in range(8):
            caixa = visao._retangulo_trilha(indice)
            clique = (100 + caixa.centerx / 2, caixa.centery / 2)
            with self.subTest(indice=indice):
                self.assertEqual(visao.obter_posicao_trilha_clicada(clique), indice + 1)
        self.assertIsNone(visao.obter_posicao_trilha_clicada((150, 250)))

    def test_paginacao_da_arvore_limita_sete_filhos(self):
        visao = VisaoJogo.__new__(VisaoJogo)

        self.assertEqual(
            visao.obter_quantidade_paginas_arvore(
                ArvoreFalsa(0)
            ),
            1,
        )
        self.assertEqual(
            visao.obter_quantidade_paginas_arvore(
                ArvoreFalsa(7)
            ),
            1,
        )
        self.assertEqual(
            visao.obter_quantidade_paginas_arvore(
                ArvoreFalsa(8)
            ),
            2,
        )

    def test_menu_identifica_novo_jogo_e_sair(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(1200, 1030)
        visao.retangulo_novo_jogo = pygame.Rect(420, 410, 360, 70)
        visao.retangulo_continuar_jogo = pygame.Rect(420, 510, 360, 70)
        visao.retangulo_sair = pygame.Rect(420, 610, 360, 70)

        novo = visao.obter_acao_menu_inicial((600, 445), False)
        sair = visao.obter_acao_menu_inicial((600, 645), False)

        self.assertEqual(novo, "novo_jogo")
        self.assertEqual(sair, "sair")

    def test_menu_so_permite_continuar_quando_existe_salvamento(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(1200, 1030)
        visao.retangulo_novo_jogo = pygame.Rect(420, 410, 360, 70)
        visao.retangulo_continuar_jogo = pygame.Rect(420, 510, 360, 70)
        visao.retangulo_sair = pygame.Rect(420, 610, 360, 70)

        sem_salvamento = visao.obter_acao_menu_inicial(
            (600, 545),
            False,
        )
        com_salvamento = visao.obter_acao_menu_inicial(
            (600, 545),
            True,
        )

        self.assertIsNone(sem_salvamento)
        self.assertEqual(com_salvamento, "continuar_jogo")

    def test_identifica_clique_no_botao_salvar(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(1200, 1030)
        visao.retangulo_botao_salvar = pygame.Rect(805, 925, 110, 45)

        clicou = visao.botao_salvar_foi_clicado((860, 947))

        self.assertTrue(clicou)

    def test_identifica_clique_no_botao_graphviz(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(1200, 1030)
        visao.retangulo_exportar_graphviz = pygame.Rect(
            800,
            45,
            210,
            45,
        )

        clicou = visao.botao_exportar_graphviz_foi_clicado(
            (900, 67)
        )

        self.assertTrue(clicou)

    def test_identifica_cliques_no_filtro_de_pagina(self):
        visao = VisaoJogo.__new__(VisaoJogo)
        visao.janela = JanelaFalsa(1200, 1030)
        visao.retangulo_campo_pagina = pygame.Rect(650, 940, 55, 50)
        visao.retangulo_ir_pagina = pygame.Rect(715, 940, 55, 50)

        clicou_campo = visao.campo_pagina_arvore_foi_clicado(
            (675, 965)
        )
        clicou_ir = visao.botao_ir_pagina_foi_clicado((740, 965))

        self.assertTrue(clicou_campo)
        self.assertTrue(clicou_ir)


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
        ponto_moray, ponto_strathclyde = self.visao._obter_pontos_da_fronteira(
            "Moray", "Strathclyde"
        )

        self.assertEqual(ponto_moray, (230, 165))
        self.assertEqual(ponto_strathclyde, (260, 165))

    def test_pontos_verticais_ficam_nas_bordas_das_regioes(self):
        ponto_northumbria, ponto_essex = self.visao._obter_pontos_da_fronteira(
            "Northumbria", "Essex"
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
