import unittest

from model.board import Tabuleiro
from model.region import Regiao


class TesteTabuleiro(unittest.TestCase):
    """Verifica as regiões e as fronteiras do tabuleiro."""

    def setUp(self) -> None:
        self.tabuleiro = Tabuleiro()

    def test_tabuleiro_possui_as_oito_regioes(self) -> None:
        nomes_esperados = {
            "Moray",
            "Strathclyde",
            "Northumbria",
            "Lancaster",
            "Gwynedd",
            "Warwick",
            "Essex",
            "Devon",
        }

        self.assertEqual(set(self.tabuleiro.nomes_das_regioes), nomes_esperados)
        self.assertEqual(len(self.tabuleiro.regioes), 8)

    def test_cada_nome_corresponde_a_uma_regiao(self) -> None:
        for nome in self.tabuleiro.nomes_das_regioes:
            regiao = self.tabuleiro.obter_regiao(nome)

            self.assertIsInstance(regiao, Regiao)
            self.assertEqual(regiao.nome, nome)

    def test_adjacencias_correspondem_ao_mapa(self) -> None:
        adjacencias_esperadas = {
            "Moray": {"Strathclyde", "Northumbria"},
            "Strathclyde": {"Moray", "Northumbria", "Lancaster"},
            "Northumbria": {
                "Moray",
                "Strathclyde",
                "Lancaster",
                "Warwick",
                "Essex",
            },
            "Lancaster": {"Strathclyde", "Northumbria", "Gwynedd", "Warwick"},
            "Gwynedd": {"Lancaster", "Warwick", "Devon"},
            "Warwick": {"Northumbria", "Lancaster", "Gwynedd", "Essex", "Devon"},
            "Essex": {"Northumbria", "Warwick", "Devon"},
            "Devon": {"Gwynedd", "Warwick", "Essex"},
        }

        for nome, adjacentes in adjacencias_esperadas.items():
            self.assertEqual(
                self.tabuleiro.regioes_adjacentes(nome),
                frozenset(adjacentes),
            )

    def test_adjacencia_e_bidirecional(self) -> None:
        for origem in self.tabuleiro.nomes_das_regioes:
            for destino in self.tabuleiro.regioes_adjacentes(origem):
                self.assertTrue(self.tabuleiro.sao_adjacentes(destino, origem))

    def test_regiao_nao_e_adjacente_a_si_mesma(self) -> None:
        for nome in self.tabuleiro.nomes_das_regioes:
            self.assertFalse(self.tabuleiro.sao_adjacentes(nome, nome))

    def test_nome_desconhecido_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ValueError, "Região desconhecida"):
            self.tabuleiro.obter_regiao("Região inexistente")


if __name__ == "__main__":
    unittest.main()
