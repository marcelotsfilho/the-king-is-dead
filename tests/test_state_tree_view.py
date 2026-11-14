import unittest

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.game_state import EstadoJogo
from model.player import Jogador
from model.state_tree import ArvoreEstados
from model.supply import ReservaSeguidores
from view.state_tree_view import VisaoArvoreEstados


def criar_arvore_com_tres_niveis():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    estado = EstadoJogo(
        tabuleiro,
        trilha,
        jogadores,
        ReservaSeguidores(0),
    )
    arvore = ArvoreEstados(estado)
    primeiro_filho = arvore.expandir_no_atual()[0]
    arvore.avancar_para(primeiro_filho)
    segundo_filho = arvore.expandir_no_atual()[0]
    arvore.avancar_para(segundo_filho)
    return arvore


class TesteVisaoArvoreEstados(unittest.TestCase):
    def setUp(self):
        self.visao = VisaoArvoreEstados()

    def test_formata_arvore_com_niveis_e_marcadores(self):
        arvore = criar_arvore_com_tres_niveis()

        texto = self.visao.formatar(arvore)

        self.assertIn("ÁRVORE DE ESTADOS", texto)
        self.assertIn("Total de nós: 3", texto)
        self.assertIn("Nível atual: 2", texto)
        self.assertIn("[CAMINHO] Nível 0 - Estado inicial", texto)
        self.assertIn("[CAMINHO] Nível 1 - Passar.", texto)
        self.assertIn("[ATUAL] Nível 2 - Passar.", texto)
        self.assertIn("H(J1, v1):", texto)

    def test_mostra_quais_nos_estao_expandidos(self):
        arvore = criar_arvore_com_tres_niveis()

        texto = self.visao.formatar(arvore)

        self.assertIn("Estado inicial (expandido)", texto)
        self.assertIn("[ATUAL] Nível 2 - Passar. (não expandido)", texto)

    def test_limite_omite_filhos_excedentes(self):
        arvore = criar_arvore_com_tres_niveis()
        arvore.voltar()
        arvore.voltar()
        raiz = arvore.obter_raiz()

        for quantidade in [3, 4, 5]:
            outro_estado = arvore.obter_estado_atual()
            outro_estado.passes_consecutivos = quantidade
            jogada = raiz.obter_filhos()[0].obter_jogada_origem()
            arvore.adicionar_estado(outro_estado, jogada, raiz)

        texto = self.visao.formatar(arvore, limite_filhos=2)

        self.assertIn("... 2 filho(s) omitido(s)", texto)

    def test_rejeita_valores_invalidos(self):
        arvore = criar_arvore_com_tres_niveis()

        with self.assertRaises(TypeError):
            self.visao.formatar("árvore")

        with self.assertRaises(TypeError):
            self.visao.formatar(arvore, limite_filhos="dois")

        with self.assertRaises(ValueError):
            self.visao.formatar(arvore, limite_filhos=0)


if __name__ == "__main__":
    unittest.main()
