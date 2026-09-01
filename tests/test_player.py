import unittest

from model.enums import Faccao
from model.player import Jogador


class TesteJogador(unittest.TestCase):
    """Verifica os dados e as operações básicas de um jogador."""

    def test_jogador_armazena_nome_sem_espacos_externos(self):
        jogador = Jogador("  Jogador 1  ")

        self.assertEqual(jogador.nome, "Jogador 1")

    def test_nome_vazio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            Jogador("   ")

    def test_jogador_comeca_com_mao_e_descarte_vazios(self):
        jogador = Jogador("Jogador 1")

        self.assertEqual(jogador.obter_mao(), [])
        self.assertEqual(jogador.obter_descarte_mao(), [])

    def test_jogador_recebe_uma_carta(self):
        jogador = Jogador("Jogador 1")

        jogador.adicionar_carta_mao("Assemble")

        self.assertEqual(jogador.obter_mao(), ["Assemble"])

    def test_carta_usada_sai_da_mao_e_vai_para_o_descarte(self):
        jogador = Jogador("Jogador 1")
        jogador.adicionar_carta_mao("Assemble")

        jogador.usar_carta("Assemble")

        self.assertEqual(jogador.obter_mao(), [])
        self.assertEqual(jogador.obter_descarte_mao(), ["Assemble"])

    def test_carta_que_nao_esta_na_mao_nao_pode_ser_usada(self):
        jogador = Jogador("Jogador 1")

        with self.assertRaises(ValueError):
            jogador.usar_carta("Assemble")

    def test_obter_mao_retorna_uma_copia(self):
        jogador = Jogador("Jogador 1")
        jogador.adicionar_carta_mao("Assemble")

        mao_recebida = jogador.obter_mao()
        mao_recebida.clear()

        self.assertEqual(jogador.obter_mao(), ["Assemble"])

    def test_obter_descarte_retorna_uma_copia(self):
        jogador = Jogador("Jogador 1")
        jogador.adicionar_carta_mao("Assemble")
        jogador.usar_carta("Assemble")

        descarte_recebido = jogador.obter_descarte_mao()
        descarte_recebido.clear()

        self.assertEqual(jogador.obter_descarte_mao(), ["Assemble"])

    def test_corte_comeca_sem_seguidores(self):
        jogador = Jogador("Jogador 1")

        for faccao in Faccao:
            self.assertEqual(jogador.qtd_na_corte(faccao), 0)

    def test_adiciona_e_remove_seguidor_da_corte(self):
        jogador = Jogador("Jogador 1")

        jogador.adicionar_seguidor_na_corte(Faccao.ESCOCESES)
        jogador.remover_seguidor_da_corte(Faccao.ESCOCESES)

        self.assertEqual(jogador.qtd_na_corte(Faccao.ESCOCESES), 0)

    def test_nao_remove_seguidor_inexistente_da_corte(self):
        jogador = Jogador("Jogador 1")

        with self.assertRaises(ValueError):
            jogador.remover_seguidor_da_corte(Faccao.GALESES)

    def test_obter_corte_retorna_uma_copia(self):
        jogador = Jogador("Jogador 1")

        corte_recebida = jogador.obter_corte()
        corte_recebida[Faccao.INGLESES] = 5

        self.assertEqual(jogador.qtd_na_corte(Faccao.INGLESES), 0)

    def test_disco_de_negociacao_comeca_disponivel(self):
        jogador = Jogador("Jogador 1")

        self.assertTrue(jogador.disco_negociacao_disponivel)

    def test_disco_de_negociacao_so_pode_ser_usado_uma_vez(self):
        jogador = Jogador("Jogador 1")

        jogador.usar_disco_negociacao()

        self.assertFalse(jogador.disco_negociacao_disponivel)

        with self.assertRaises(ValueError):
            jogador.usar_disco_negociacao()


if __name__ == "__main__":
    unittest.main()
