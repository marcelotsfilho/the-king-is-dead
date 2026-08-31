import unittest

from model.enums import Faccao


class TesteFaccao(unittest.TestCase):
    """Verifica o contrato público das facções."""

    def test_jogo_possui_exatamente_tres_faccoes(self):
        self.assertEqual(
            set(Faccao),
            {Faccao.ESCOCESES, Faccao.GALESES, Faccao.INGLESES},
        )

    def test_cada_faccao_possui_valor_textual_estavel(self):
        self.assertEqual(Faccao.ESCOCESES.value, "escoceses")
        self.assertEqual(Faccao.GALESES.value, "galeses")
        self.assertEqual(Faccao.INGLESES.value, "ingleses")

    def test_faccao_pode_ser_recuperada_pelo_valor(self):
        self.assertIs(Faccao("escoceses"), Faccao.ESCOCESES)


if __name__ == "__main__":
    unittest.main()
