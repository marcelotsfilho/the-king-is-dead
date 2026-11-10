import os
from unittest.mock import patch
import tempfile
import unittest

from model.enums import TipoJogada
from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
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

    def test_dot_aumenta_distancia_entre_os_niveis(self):
        arvore = criar_arvore_com_passe()

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        self.assertIn('ranksep="1.0"', conteudo)

    def test_dot_omite_alternativas_antigas_nao_visitadas(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        arvore = ArvoreEstados(estado)
        jogada = Jogada(TipoJogada.PASSE)
        copiador = SerializadorEstadoJogo()

        estado_visitado = ExecutorJogada().executar(estado, jogada)
        no_visitado = arvore.adicionar_estado(estado_visitado, jogada)

        estado_omitido = copiador.copiar(estado)
        estado_omitido.passes_consecutivos = 1
        arvore.adicionar_estado(estado_omitido, jogada)

        arvore.avancar_para(no_visitado)
        estado_proxima_opcao = copiador.copiar(estado_visitado)
        estado_proxima_opcao.passes_consecutivos = 2
        arvore.adicionar_estado(estado_proxima_opcao, jogada)

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        self.assertIn("n0 [", conteudo)
        self.assertIn("n1 [", conteudo)
        self.assertNotIn("n2 [", conteudo)
        self.assertIn("n3 [", conteudo)
        self.assertIn("n0 -> n1;", conteudo)
        self.assertNotIn("n0 -> n2;", conteudo)
        self.assertIn("n1 -> n3;", conteudo)

    def test_estado_atual_recebe_destaque_azul(self):
        arvore = criar_arvore_com_passe()

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        linha_atual = ""

        for linha in conteudo.splitlines():
            if linha.strip().startswith("n1 ["):
                linha_atual = linha

        self.assertIn("#9ec5f8", linha_atual)
        self.assertIn('penwidth="3"', linha_atual)

    def test_jogada_voltada_recebe_rotulo_e_cor_cinza(self):
        arvore = criar_arvore_com_passe()
        arvore.voltar()

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)
        linha_voltada = ""

        for linha in conteudo.splitlines():
            if linha.strip().startswith("n1 ["):
                linha_voltada = linha

        self.assertIn("Jogada voltada", linha_voltada)
        self.assertIn("#a8a8a8", linha_voltada)
        self.assertIn('penwidth="2"', linha_voltada)

    def test_mantem_jogadas_voltadas_de_niveis_anteriores(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        arvore = ArvoreEstados(estado)
        jogada = Jogada(TipoJogada.PASSE)

        primeiro_estado = ExecutorJogada().executar(estado, jogada)
        primeiro_no = arvore.registrar_jogada_realizada(
            jogada,
            primeiro_estado,
        )
        segundo_estado = ExecutorJogada().executar(
            primeiro_estado,
            jogada,
        )
        arvore.registrar_jogada_realizada(jogada, segundo_estado)

        arvore.voltar()
        arvore.voltar()
        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        self.assertTrue(primeiro_no.representa_jogada_voltada())
        self.assertIn("n1 [", conteudo)
        self.assertIn("n2 [", conteudo)
        self.assertEqual(conteudo.count("Jogada voltada"), 2)

    def test_mantem_volta_ao_lado_da_nova_escolha_e_seus_filhos(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        arvore = ArvoreEstados(estado)
        jogada = Jogada(TipoJogada.PASSE)
        copiador = SerializadorEstadoJogo()

        estado_anterior = copiador.copiar(estado)
        estado_anterior.passes_consecutivos = 1
        no_anterior = arvore.adicionar_estado(estado_anterior, jogada)
        arvore.avancar_para(no_anterior)

        escolha_antiga = copiador.copiar(estado_anterior)
        escolha_antiga.passes_consecutivos = 2
        no_antigo = arvore.adicionar_estado(escolha_antiga, jogada)
        arvore.avancar_para(no_antigo)
        arvore.voltar()

        nova_escolha = copiador.copiar(estado_anterior)
        nova_escolha.indice_jogador_atual = 1
        no_novo = arvore.adicionar_estado(nova_escolha, jogada)
        arvore.avancar_para(no_novo)

        estado_filho = copiador.copiar(nova_escolha)
        estado_filho.passes_consecutivos = 3
        no_filho = arvore.adicionar_estado(estado_filho, jogada)
        arvore.avancar_para(no_filho)

        conteudo = VisaoArvoreGraphviz().gerar_dot(arvore)

        self.assertTrue(no_antigo.representa_jogada_voltada())
        self.assertIn("n2 [", conteudo)
        self.assertIn("n3 [", conteudo)
        self.assertIn("n4 [", conteudo)
        self.assertIn("n1 -> n2;", conteudo)
        self.assertIn("n1 -> n3;", conteudo)
        self.assertIn("n3 -> n4;", conteudo)
        self.assertIn("{ rank=same; n2; n3; }", conteudo)
        self.assertIn(
            'n2 -> n3 [style="invis", weight="100"];',
            conteudo,
        )

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
