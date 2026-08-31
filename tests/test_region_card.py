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


if __name__ == "__main__":
    unittest.main()
