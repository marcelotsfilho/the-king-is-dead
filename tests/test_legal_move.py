import unittest

from model.enums import Faccao, TipoCartaAcao, TipoJogada
from model.legal_move import Jogada


class TesteJogada(unittest.TestCase):
    def test_cria_jogada_de_passe(self):
        jogada = Jogada(TipoJogada.PASSE)

        self.assertTrue(jogada.eh_passe())
        self.assertFalse(jogada.eh_carta())
        self.assertIsNone(jogada.tipo_carta)
        self.assertEqual(jogada.obter_parametros(), {})
        self.assertIsNone(jogada.nome_regiao_convocacao)
        self.assertIsNone(jogada.faccao_convocacao)

    def test_passe_nao_aceita_dados_de_carta(self):
        with self.assertRaises(ValueError):
            Jogada(
                TipoJogada.PASSE,
                tipo_carta=TipoCartaAcao.REUNIR,
            )

    def test_cria_jogada_completa_de_carta(self):
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_ESCOCES,
            parametros={"regiao": "Northumbria"},
            nome_regiao_convocacao="Moray",
            faccao_convocacao=Faccao.ESCOCESES,
        )

        self.assertTrue(jogada.eh_carta())
        self.assertFalse(jogada.eh_passe())
        self.assertEqual(jogada.tipo_carta, TipoCartaAcao.APOIO_ESCOCES)
        self.assertEqual(
            jogada.obter_parametros(),
            {"regiao": "Northumbria"},
        )
        self.assertEqual(jogada.nome_regiao_convocacao, "Moray")
        self.assertEqual(jogada.faccao_convocacao, Faccao.ESCOCESES)

    def test_parametros_da_jogada_sao_copiados(self):
        parametros = {
            "destinos": {
                Faccao.ESCOCESES: "Moray",
                Faccao.GALESES: "Gwynedd",
                Faccao.INGLESES: "Essex",
            }
        }
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.REUNIR,
            parametros=parametros,
            nome_regiao_convocacao="Moray",
            faccao_convocacao=Faccao.ESCOCESES,
        )

        parametros["destinos"][Faccao.ESCOCESES] = "Devon"
        parametros_da_jogada = jogada.obter_parametros()
        parametros_da_jogada["destinos"][Faccao.GALESES] = "Warwick"

        parametros_preservados = jogada.obter_parametros()
        self.assertEqual(
            parametros_preservados["destinos"][Faccao.ESCOCESES],
            "Moray",
        )
        self.assertEqual(
            parametros_preservados["destinos"][Faccao.GALESES],
            "Gwynedd",
        )

    def test_carta_exige_tipo_de_carta_valido(self):
        with self.assertRaises(TypeError):
            Jogada(
                TipoJogada.CARTA,
                tipo_carta="Assemble",
                nome_regiao_convocacao="Moray",
                faccao_convocacao=Faccao.ESCOCESES,
            )

    def test_carta_exige_parametros_em_dicionario(self):
        with self.assertRaises(TypeError):
            Jogada(
                TipoJogada.CARTA,
                tipo_carta=TipoCartaAcao.REUNIR,
                parametros=[],
                nome_regiao_convocacao="Moray",
                faccao_convocacao=Faccao.ESCOCESES,
            )

    def test_carta_exige_convocacao_completa(self):
        with self.assertRaises(TypeError):
            Jogada(
                TipoJogada.CARTA,
                tipo_carta=TipoCartaAcao.REUNIR,
                parametros={},
                nome_regiao_convocacao=None,
                faccao_convocacao=Faccao.ESCOCESES,
            )

        with self.assertRaises(TypeError):
            Jogada(
                TipoJogada.CARTA,
                tipo_carta=TipoCartaAcao.REUNIR,
                parametros={},
                nome_regiao_convocacao="Moray",
                faccao_convocacao=None,
            )

    def test_compara_todas_as_escolhas_da_jogada(self):
        primeira = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_GALES,
            parametros={"regiao": "Warwick"},
            nome_regiao_convocacao="Gwynedd",
            faccao_convocacao=Faccao.GALESES,
        )
        segunda = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_GALES,
            parametros={"regiao": "Warwick"},
            nome_regiao_convocacao="Gwynedd",
            faccao_convocacao=Faccao.GALESES,
        )
        diferente = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.APOIO_GALES,
            parametros={"regiao": "Devon"},
            nome_regiao_convocacao="Gwynedd",
            faccao_convocacao=Faccao.GALESES,
        )

        self.assertTrue(primeira.possui_mesmos_dados(segunda))
        self.assertFalse(primeira.possui_mesmos_dados(diferente))

    def test_descreve_passe_e_carta(self):
        passe = Jogada(TipoJogada.PASSE)
        carta = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.NEGOCIAR,
            parametros={
                "posicao_a": 1,
                "posicao_b": 2,
                "posicao_disco": 1,
            },
            nome_regiao_convocacao="Essex",
            faccao_convocacao=Faccao.INGLESES,
        )

        self.assertEqual(passe.descrever(), "Passar.")
        self.assertEqual(
            carta.descrever(),
            "Jogar Negotiate e convocar ingleses de Essex.",
        )


if __name__ == "__main__":
    unittest.main()
