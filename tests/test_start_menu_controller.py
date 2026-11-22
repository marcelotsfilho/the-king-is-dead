import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import pygame

from controller.start_menu_controller import ControladorMenuInicial
from model.enums import TipoJogador
from model.match_settings import ConfiguracaoPartida


class VisaoFalsa:
    pass


class TesteControladorMenuInicial(unittest.TestCase):
    def test_alterna_tipos_e_retorna_ao_humano(self):
        controlador = ControladorMenuInicial(VisaoFalsa(), "nao_existe.json")
        for tipo in (
            TipoJogador.MINIMAX,
            TipoJogador.ALFA_BETA,
            TipoJogador.MONTE_CARLO,
            TipoJogador.Q_LEARNING,
            TipoJogador.HUMANO,
        ):
            controlador._alterar_configuracao("tipo", 1)
            self.assertEqual(controlador.configuracao_partida.obter_tipo_jogador(1), tipo)
        self.assertEqual(controlador.configuracao_partida.obter_tipo_jogador(0), TipoJogador.HUMANO)

    def test_profundidade_desativada_para_humano_e_minimo_um_para_ia(self):
        controlador = ControladorMenuInicial(VisaoFalsa(), "nao_existe.json")
        configuracao = controlador.configuracao_partida
        controlador._alterar_configuracao("aumentar", 0)
        self.assertEqual(configuracao.obter_profundidade(0), 1)
        controlador._alterar_configuracao("tipo", 0)
        controlador._alterar_configuracao("diminuir", 0)
        self.assertEqual(configuracao.obter_profundidade(0), 1)
        controlador._alterar_configuracao("aumentar", 0)
        self.assertEqual(configuracao.obter_profundidade(0), 2)
        controlador._alterar_configuracao("tipo", 0)
        self.assertEqual(configuracao.obter_profundidade(0), 2)
        controlador._alterar_configuracao("diminuir", 0)
        self.assertEqual(configuracao.obter_profundidade(0), 1)

    def test_monte_carlo_permite_ajustar_simulacoes_nas_opcoes(self):
        controlador = ControladorMenuInicial(VisaoFalsa(), "nao_existe.json")
        configuracao = controlador.configuracao_partida
        for _ in range(3):
            controlador._alterar_configuracao("tipo", 0)
        controlador._alterar_configuracao("aumentar", 0)
        self.assertEqual(configuracao.obter_simulacoes_monte_carlo(0), 300)
        controlador._alterar_configuracao("aumentar", 0)
        self.assertEqual(configuracao.obter_simulacoes_monte_carlo(0), 1000)
        controlador._alterar_configuracao("diminuir", 0)
        self.assertEqual(configuracao.obter_simulacoes_monte_carlo(0), 300)

    def test_loop_recebe_selecao_e_preserva_configuracao_ao_iniciar(self):
        visao = Mock()
        visao.obter_acao_configuracao.side_effect = [("tipo", 0), ("aumentar", 0), None]
        visao.obter_acao_menu_inicial.return_value = "novo_jogo"
        visao.obter_acao_tela_configuracao.return_value = "iniciar"
        configuracao = ConfiguracaoPartida()
        controlador = ControladorMenuInicial(visao, "nao_existe.json", configuracao)
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        with patch("pygame.event.get", return_value=[clique] * 4):
            self.assertEqual(controlador.executar(), "novo_jogo")
        self.assertIs(controlador.configuracao_partida, configuracao)
        self.assertEqual(configuracao.obter_tipo_jogador(0), TipoJogador.MINIMAX)
        self.assertEqual(configuracao.obter_profundidade(0), 2)

    def test_loop_preserva_orcamento_monte_carlo_ao_iniciar(self):
        visao = Mock()
        visao.obter_acao_configuracao.side_effect = [
            ("tipo", 0), ("tipo", 0), ("tipo", 0), ("aumentar", 0), None,
        ]
        visao.obter_acao_menu_inicial.return_value = "novo_jogo"
        visao.obter_acao_tela_configuracao.return_value = "iniciar"
        configuracao = ConfiguracaoPartida()
        controlador = ControladorMenuInicial(visao, "nao_existe.json", configuracao)
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        with patch("pygame.event.get", return_value=[clique] * 6):
            self.assertEqual(controlador.executar(), "novo_jogo")
        self.assertEqual(configuracao.obter_tipo_jogador(0), TipoJogador.MONTE_CARLO)
        self.assertEqual(configuracao.obter_simulacoes_monte_carlo(0), 300)

    def test_voltar_descarta_edicao_e_continuar_nao_abre_configuracao(self):
        visao = Mock()
        visao.obter_acao_menu_inicial.side_effect = ["novo_jogo", "continuar_jogo"]
        visao.obter_acao_configuracao.side_effect = [("tipo", 0), None]
        visao.obter_acao_tela_configuracao.return_value = "voltar"
        configuracao = ConfiguracaoPartida()
        controlador = ControladorMenuInicial(visao, "salvo.json", configuracao)
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        with patch("pygame.event.get", return_value=[clique] * 4):
            with patch.object(controlador, "existe_jogo_salvo", return_value=True):
                self.assertEqual(controlador.executar(), "continuar_jogo")
        self.assertEqual(configuracao.obter_tipo_jogador(0), TipoJogador.HUMANO)
        self.assertEqual(configuracao.obter_profundidade(0), 1)

    def test_continuar_retorna_diretamente_sem_configuracao(self):
        visao = Mock()
        visao.obter_acao_menu_inicial.return_value = "continuar_jogo"
        controlador = ControladorMenuInicial(visao, "salvo.json")
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        with patch("pygame.event.get", return_value=[clique]):
            with patch.object(controlador, "existe_jogo_salvo", return_value=True):
                self.assertEqual(controlador.executar(), "continuar_jogo")
        visao.desenhar_tela_configuracao.assert_not_called()
        visao.obter_acao_configuracao.assert_not_called()

    def test_fechar_configuracao_sai_sem_confirmar_edicao(self):
        visao = Mock()
        visao.obter_acao_menu_inicial.return_value = "novo_jogo"
        visao.obter_acao_configuracao.return_value = ("tipo", 0)
        controlador = ControladorMenuInicial(visao, "salvo.json")
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        with patch("pygame.event.get", side_effect=[
            [clique], [clique], [pygame.event.Event(pygame.QUIT)]
        ]):
            self.assertEqual(controlador.executar(), "sair")
        self.assertEqual(
            controlador.configuracao_partida.obter_tipo_jogador(0), TipoJogador.HUMANO
        )
        visao.desenhar_tela_configuracao.assert_called()

    def test_fechar_janela_sai_do_menu(self):
        controlador = ControladorMenuInicial(Mock(), "nao_existe.json")
        with patch("pygame.event.get", return_value=[pygame.event.Event(pygame.QUIT)]):
            self.assertEqual(controlador.executar(), "sair")

    def test_informa_quando_existe_jogo_salvo(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "state_tree.json")

            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("{}")

            controlador = ControladorMenuInicial(
                VisaoFalsa(),
                caminho,
            )

            self.assertTrue(controlador.existe_jogo_salvo())

    def test_informa_quando_nao_existe_jogo_salvo(self):
        controlador = ControladorMenuInicial(
            VisaoFalsa(),
            "arquivo_inexistente.json",
        )

        self.assertFalse(controlador.existe_jogo_salvo())


if __name__ == "__main__":
    unittest.main()
