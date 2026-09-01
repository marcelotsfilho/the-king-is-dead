import unittest

from model.region_card import CartaRegiao


class TesteCartaRegiao(unittest.TestCase):
    """Verifica o estado inicial de uma carta de região."""

    def test_carta_armazena_nome_da_regiao(self):
        carta = CartaRegiao("Moray")

        self.assertEqual(carta.nome_regiao, "Moray")

    def test_carta_comeca_virada_para_cima_e_sem_disco(self):
        carta = CartaRegiao("Moray")

        self.assertTrue(carta.virada_para_cima)
        self.assertFalse(carta.possui_disco_negociacao)

    def test_nome_vazio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            CartaRegiao("   ")

    def test_carta_pode_ser_virada_para_baixo(self):
        carta = CartaRegiao("Moray")

        carta.virar_para_baixo()

        self.assertFalse(carta.virada_para_cima)

    def test_carta_pode_ser_virada_novamente_para_cima(self):
        carta = CartaRegiao("Moray")
        carta.virar_para_baixo()

        carta.virar_para_cima()

        self.assertTrue(carta.virada_para_cima)

    def test_carta_pode_receber_e_remover_disco_de_negociacao(self):
        carta = CartaRegiao("Moray")

        carta.colocar_disco_negociacao()
        self.assertTrue(carta.possui_disco_negociacao)

        carta.remover_disco_negociacao()
        self.assertFalse(carta.possui_disco_negociacao)

    def test_carta_virada_para_baixo_nao_recebe_disco(self):
        carta = CartaRegiao("Moray")
        carta.virar_para_baixo()

        with self.assertRaises(ValueError):
            carta.colocar_disco_negociacao()


if __name__ == "__main__":
    unittest.main()
