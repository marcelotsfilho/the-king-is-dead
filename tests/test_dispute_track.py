import unittest

from model.dispute_track import TrilhaDisputas


def obter_nomes_regioes():
    return [
        "Moray",
        "Strathclyde",
        "Northumbria",
        "Lancaster",
        "Gwynedd",
        "Warwick",
        "Essex",
        "Devon",
    ]


class TesteTrilhaDisputas(unittest.TestCase):
    """Verifica a ordem e as operações básicas da trilha de disputas."""

    def test_trilha_cria_oito_cartas_na_ordem_recebida(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())
        cartas = trilha.obter_cartas()

        self.assertEqual(len(cartas), 8)

        for indice in range(8):
            self.assertEqual(
                cartas[indice].nome_regiao,
                obter_nomes_regioes()[indice],
            )

    def test_lista_vazia_e_rejeitada(self):
        with self.assertRaises(ValueError):
            TrilhaDisputas([])

    def test_quantidade_diferente_de_oito_e_rejeitada(self):
        with self.assertRaises(ValueError):
            TrilhaDisputas(["Moray"])

    def test_nomes_repetidos_sao_rejeitados(self):
        nomes = ["Moray"] * 8

        with self.assertRaises(ValueError):
            TrilhaDisputas(nomes)

    def test_argumento_deve_ser_uma_lista(self):
        with self.assertRaises(ValueError):
            TrilhaDisputas("12345678")

    def test_obter_cartas_retorna_uma_copia(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        cartas_recebidas = trilha.obter_cartas()
        cartas_recebidas.clear()

        self.assertEqual(len(trilha.obter_cartas()), 8)

    def test_posicao_um_retorna_a_primeira_carta(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        carta = trilha.obter_carta(1)

        self.assertEqual(carta.nome_regiao, "Moray")

    def test_posicao_oito_retorna_a_ultima_carta(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        carta = trilha.obter_carta(8)

        self.assertEqual(carta.nome_regiao, "Devon")

    def test_posicoes_fora_de_um_a_oito_sao_rejeitadas(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        with self.assertRaises(ValueError):
            trilha.obter_carta(0)

        with self.assertRaises(ValueError):
            trilha.obter_carta(9)

    def test_posicao_nao_inteira_e_rejeitada(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        with self.assertRaises(ValueError):
            trilha.obter_carta("1")

    def test_proxima_carta_e_a_primeira_virada_para_cima(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())
        primeira_carta = trilha.obter_carta(1)
        primeira_carta.virar_para_baixo()

        proxima_carta = trilha.obter_proxima_carta()

        self.assertEqual(proxima_carta.nome_regiao, "Strathclyde")

    def test_sem_cartas_para_cima_retorna_none(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        for carta in trilha.obter_cartas():
            carta.virar_para_baixo()

        self.assertIsNone(trilha.obter_proxima_carta())

    def test_troca_cartas_entre_duas_posicoes(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        trilha.trocar_cartas(1, 8)

        self.assertEqual(trilha.obter_carta(1).nome_regiao, "Devon")
        self.assertEqual(trilha.obter_carta(8).nome_regiao, "Moray")

    def test_troca_rejeita_posicoes_invalidas(self):
        trilha = TrilhaDisputas(obter_nomes_regioes())

        with self.assertRaises(ValueError):
            trilha.trocar_cartas(0, 8)

        with self.assertRaises(ValueError):
            trilha.trocar_cartas(1, 9)


if __name__ == "__main__":
    unittest.main()
