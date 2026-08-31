import unittest

from model.board import Tabuleiro
from model.region import Regiao


class TesteTabuleiro(unittest.TestCase):
    """Verifica as regiões e as fronteiras do tabuleiro."""

    def test_tabuleiro_possui_as_oito_regioes(self):
        tabuleiro = Tabuleiro()
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

        self.assertEqual(set(tabuleiro.obter_nomes_das_regioes()), nomes_esperados)
        self.assertEqual(len(tabuleiro.obter_regioes()), 8)

    def test_cada_nome_corresponde_a_uma_regiao(self):
        tabuleiro = Tabuleiro()
        for nome in tabuleiro.obter_nomes_das_regioes():
            regiao = tabuleiro.obter_regiao(nome)

            self.assertIsInstance(regiao, Regiao)
            self.assertEqual(regiao.nome, nome)

    def test_adjacencias_correspondem_ao_mapa(self):
        tabuleiro = Tabuleiro()
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
                tabuleiro.regioes_adjacentes(nome),
                adjacentes,
            )

    def test_adjacencia_e_bidirecional(self):
        tabuleiro = Tabuleiro()
        for origem in tabuleiro.obter_nomes_das_regioes():
            for destino in tabuleiro.regioes_adjacentes(origem):
                self.assertTrue(tabuleiro.sao_adjacentes(destino, origem))

    def test_regiao_nao_e_adjacente_a_si_mesma(self):
        tabuleiro = Tabuleiro()
        for nome in tabuleiro.obter_nomes_das_regioes():
            self.assertFalse(tabuleiro.sao_adjacentes(nome, nome))

    def test_nome_desconhecido_e_rejeitado(self):
        tabuleiro = Tabuleiro()
        with self.assertRaisesRegex(ValueError, "Região desconhecida"):
            tabuleiro.obter_regiao("Região inexistente")


if __name__ == "__main__":
    unittest.main()
