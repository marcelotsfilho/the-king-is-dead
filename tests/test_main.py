import os
import tempfile
import unittest
from unittest.mock import patch

import main
from model.enums import TipoJogada, TipoJogador
from model.game_setup import ConfiguracaoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.state_tree import ArvoreEstados
from model.state_tree_serializer import SerializadorArvoreEstados


class VisaoMenuFalsa:
    def __init__(self):
        self.mensagens = []

    def desenhar_menu_inicial(
        self, salvamento_disponivel, mensagem, configuracao_partida=None
    ):
        self.mensagens.append(mensagem)


class ControladorMenuFalso:
    def __init__(self, acoes):
        self.acoes = acoes
        self.mensagens = []

    def executar(self, mensagem=""):
        self.mensagens.append(mensagem)
        return self.acoes.pop(0)


class TesteInicializacaoPrincipal(unittest.TestCase):
    def test_principal_entrega_as_escolhas_do_menu_ao_controller(self):
        def escolher_no_menu(mensagem=""):
            configuracao = criar_menu.call_args.args[2]
            configuracao.definir_tipo_jogador(0, TipoJogador.MINIMAX)
            configuracao.definir_tipo_jogador(1, TipoJogador.ALFA_BETA)
            configuracao.definir_profundidade(0, 2)
            configuracao.definir_profundidade(1, 3)
            return "novo_jogo"

        with patch("main.VisaoJogo"):
            with patch("main.ControladorMenuInicial") as criar_menu:
                criar_menu.return_value.executar.side_effect = escolher_no_menu
                with patch("main.ControladorJogo") as criar_controlador:
                    with patch("main.sys.argv", ["main.py"]):
                        main.principal()

        configuracao = criar_controlador.call_args.kwargs["configuracao_partida"]
        self.assertEqual(configuracao.obter_tipo_jogador(0), TipoJogador.MINIMAX)
        self.assertEqual(configuracao.obter_tipo_jogador(1), TipoJogador.ALFA_BETA)
        self.assertEqual(configuracao.obter_profundidade(0), 2)
        self.assertEqual(configuracao.obter_profundidade(1), 3)
        criar_controlador.return_value.executar.assert_called_once()

    def test_sem_argumento_cria_nova_arvore(self):
        serializador = SerializadorArvoreEstados()

        arvore = main._preparar_arvore([], serializador)

        self.assertTrue(arvore.obter_no_atual().eh_raiz())
        self.assertEqual(arvore.quantidade_nos(), 1)

    def test_argumento_carregar_restaura_arvore_salva(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(
            ["Ana", "Bruno"]
        )
        arvore = ArvoreEstados(estado)
        jogada = Jogada(TipoJogada.PASSE)
        novo_estado = ExecutorJogada().executar(estado, jogada)
        arvore.registrar_jogada_realizada(jogada, novo_estado)
        serializador = SerializadorArvoreEstados()

        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "state_tree.json")
            serializador.salvar(arvore, caminho)

            with patch("main._CAMINHO_DA_ARVORE", caminho):
                carregada = main._preparar_arvore(
                    ["--carregar"],
                    serializador,
                )

        self.assertEqual(
            carregada.obter_no_atual().obter_nivel(),
            1,
        )
        self.assertEqual(carregada.quantidade_nos(), 2)

    def test_menu_novo_jogo_cria_arvore_inicial(self):
        menu = ControladorMenuFalso(["novo_jogo"])

        with patch("main.ControladorMenuInicial", return_value=menu):
            arvore = main._escolher_arvore_pelo_menu(
                VisaoMenuFalsa(),
                SerializadorArvoreEstados(),
            )

        self.assertEqual(arvore.quantidade_nos(), 1)
        self.assertTrue(arvore.obter_no_atual().eh_raiz())

    def test_menu_sair_nao_cria_partida(self):
        menu = ControladorMenuFalso(["sair"])

        with patch("main.ControladorMenuInicial", return_value=menu):
            arvore = main._escolher_arvore_pelo_menu(
                VisaoMenuFalsa(),
                SerializadorArvoreEstados(),
            )

        self.assertIsNone(arvore)

    def test_menu_continuar_carrega_a_arvore_salva(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(
            ["Ana", "Bruno"]
        )
        arvore = ArvoreEstados(estado)
        serializador = SerializadorArvoreEstados()
        menu = ControladorMenuFalso(["continuar_jogo"])
        visao = VisaoMenuFalsa()

        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "state_tree.json")
            serializador.salvar(arvore, caminho)

            with patch("main._CAMINHO_DA_ARVORE", caminho):
                with patch(
                    "main.ControladorMenuInicial",
                    return_value=menu,
                ):
                    carregada = main._escolher_arvore_pelo_menu(
                        visao,
                        serializador,
                    )

        self.assertEqual(carregada.quantidade_nos(), 1)
        self.assertIn("Carregando", visao.mensagens[0])

    def test_arquivo_invalido_volta_ao_menu_com_mensagem(self):
        menu = ControladorMenuFalso(
            ["continuar_jogo", "novo_jogo"]
        )
        visao = VisaoMenuFalsa()

        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "state_tree.json")

            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("{}")

            with patch("main._CAMINHO_DA_ARVORE", caminho):
                with patch(
                    "main.ControladorMenuInicial",
                    return_value=menu,
                ):
                    arvore = main._escolher_arvore_pelo_menu(
                        visao,
                        SerializadorArvoreEstados(),
                    )

        self.assertEqual(arvore.quantidade_nos(), 1)
        self.assertIn("Não foi possível carregar", menu.mensagens[1])


if __name__ == "__main__":
    unittest.main()
