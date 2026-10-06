import unittest

from model.action_card import (
    CartaAcao,
    criar_conjunto_padrao,
    eh_carta_de_apoio,
    obter_dados_da_carta_de_apoio,
)
from model.enums import Faccao, TipoCartaAcao


class TesteCartaAcao(unittest.TestCase):
    """Verifica as cartas de ação do modo básico."""

    def test_modo_basico_possui_sete_tipos_de_acao(self):
        self.assertEqual(len(TipoCartaAcao), 7)

    def test_carta_armazena_tipo_nome_e_descricao(self):
        carta = CartaAcao(TipoCartaAcao.REUNIR)

        self.assertEqual(carta.tipo, TipoCartaAcao.REUNIR)
        self.assertEqual(carta.nome, "Assemble")
        self.assertTrue(carta.descricao)

    def test_tipo_invalido_e_rejeitado(self):
        with self.assertRaises(TypeError):
            CartaAcao("Assemble")

    def test_conjunto_padrao_possui_oito_cartas(self):
        cartas = criar_conjunto_padrao()

        self.assertEqual(len(cartas), 8)

    def test_conjunto_padrao_possui_duas_cartas_assemble(self):
        cartas = criar_conjunto_padrao()
        quantidade_assemble = 0

        for carta in cartas:
            if carta.tipo == TipoCartaAcao.REUNIR:
                quantidade_assemble += 1

        self.assertEqual(quantidade_assemble, 2)

    def test_demais_acoes_aparecem_uma_vez(self):
        cartas = criar_conjunto_padrao()
        tipos_unicos = [
            TipoCartaAcao.APOIO_ESCOCES,
            TipoCartaAcao.APOIO_GALES,
            TipoCartaAcao.APOIO_INGLES,
            TipoCartaAcao.NEGOCIAR,
            TipoCartaAcao.MANOBRAR,
            TipoCartaAcao.SUPERAR_MANOBRA,
        ]

        for tipo in tipos_unicos:
            quantidade = 0

            for carta in cartas:
                if carta.tipo == tipo:
                    quantidade += 1

            self.assertEqual(quantidade, 1)

    def test_cada_conjunto_possui_novas_cartas(self):
        conjunto_1 = criar_conjunto_padrao()
        conjunto_2 = criar_conjunto_padrao()

        for indice in range(8):
            self.assertIsNot(conjunto_1[indice], conjunto_2[indice])

    def test_identifica_as_tres_cartas_de_apoio(self):
        self.assertTrue(eh_carta_de_apoio(TipoCartaAcao.APOIO_ESCOCES))
        self.assertTrue(eh_carta_de_apoio(TipoCartaAcao.APOIO_GALES))
        self.assertTrue(eh_carta_de_apoio(TipoCartaAcao.APOIO_INGLES))
        self.assertFalse(eh_carta_de_apoio(TipoCartaAcao.REUNIR))

    def test_obtem_faccao_e_regiao_inicial_do_apoio(self):
        faccao, regiao = obter_dados_da_carta_de_apoio(
            TipoCartaAcao.APOIO_ESCOCES
        )

        self.assertEqual(faccao, Faccao.ESCOCESES)
        self.assertEqual(regiao, "Moray")


if __name__ == "__main__":
    unittest.main()
