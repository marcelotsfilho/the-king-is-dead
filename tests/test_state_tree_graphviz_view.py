import os
from unittest.mock import patch
import tempfile
import unittest

from model.enums import TipoJogada
from model.game_setup import ConfiguracaoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.state_tree import ArvoreEstados
from view.state_tree_graphviz_view import VisaoArvoreGraphviz


def criar_arvore_com_passe():
    estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
    arvore = ArvoreEstados(estado)
    jogada = Jogada(TipoJogada.PASSE)
    novo_estado = ExecutorJogada().executar(estado, jogada)
    arvore.registrar_jogada_realizada(jogada, novo_estado)
    return arvore


class TesteVisaoArvoreGraphviz(unittest.TestCase):
    def test_dot_possui_todos_os_nos_e_a_ligacao(self):
        arvore = criar_arvore_com_passe()

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        self.assertIn("n0 [", conteudo)
        self.assertIn("n1 [", conteudo)
        self.assertIn("n0 -> n1;", conteudo)
        self.assertIn("Passar.", conteudo)

    def test_estado_atual_recebe_destaque_azul(self):
        arvore = criar_arvore_com_passe()

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        linha_atual = ""

        for linha in conteudo.splitlines():
            if linha.strip().startswith("n1 ["):
                linha_atual = linha

        self.assertIn("#9ec5f8", linha_atual)
        self.assertIn('penwidth="3"', linha_atual)

    def test_sem_graphviz_salva_dot_e_exibe_erro_explicativo(self):
        arvore = criar_arvore_com_passe()

        with tempfile.TemporaryDirectory() as pasta:
            caminho_svg = os.path.join(pasta, "arvore.svg")
            caminho_dot = os.path.join(pasta, "arvore.dot")

            with patch.object(
                VisaoArvoreGraphviz,
                "_localizar_dot",
                return_value=None,
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Graphviz não foi encontrado",
                ):
                    VisaoArvoreGraphviz().exportar(
                        arvore,
                        caminho_svg,
                        abrir=False,
                    )

            self.assertTrue(os.path.isfile(caminho_dot))


if __name__ == "__main__":
    unittest.main()
