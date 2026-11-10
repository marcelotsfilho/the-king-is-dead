import unittest

from model.enums import TipoJogador
from model.match_settings import ConfiguracaoPartida


class TesteConfiguracaoPartida(unittest.TestCase):
    def test_padrao_humano_e_profundidade_um(self):
        configuracao = ConfiguracaoPartida()
        for indice in (0, 1):
            self.assertEqual(configuracao.obter_tipo_jogador(indice), TipoJogador.HUMANO)
            self.assertEqual(configuracao.obter_profundidade(indice), 1)

    def test_aceita_todas_as_combinacoes_com_profundidades_independentes(self):
        configuracao = ConfiguracaoPartida()
        for tipo_um in TipoJogador:
            for tipo_dois in TipoJogador:
                configuracao.definir_tipo_jogador(0, tipo_um)
                configuracao.definir_tipo_jogador(1, tipo_dois)
                configuracao.definir_profundidade(0, 2)
                configuracao.definir_profundidade(1, 4)
                self.assertEqual(configuracao.obter_tipo_jogador(0), tipo_um)
                self.assertEqual(configuracao.obter_tipo_jogador(1), tipo_dois)
                self.assertEqual(configuracao.obter_profundidade(0), 2)
                self.assertEqual(configuracao.obter_profundidade(1), 4)

    def test_configuracoes_de_partidas_sao_independentes(self):
        primeira = ConfiguracaoPartida()
        segunda = ConfiguracaoPartida()
        primeira.definir_tipo_jogador(0, TipoJogador.MINIMAX)
        primeira.definir_profundidade(0, 3)
        self.assertEqual(segunda.obter_tipo_jogador(0), TipoJogador.HUMANO)
        self.assertEqual(segunda.obter_profundidade(0), 1)

    def test_rejeita_configuracao_invalida(self):
        configuracao = ConfiguracaoPartida()
        for indice in (-1, 2):
            with self.assertRaises(ValueError):
                configuracao.obter_tipo_jogador(indice)
        for indice in (True, "0"):
            with self.assertRaises(TypeError):
                configuracao.obter_profundidade(indice)
        for profundidade in (0, -1):
            with self.assertRaises(ValueError):
                configuracao.definir_profundidade(0, profundidade)
        for profundidade in (True, 1.5, "2"):
            with self.assertRaises(TypeError):
                configuracao.definir_profundidade(0, profundidade)
        with self.assertRaises(TypeError):
            configuracao.definir_tipo_jogador(0, "Minimax")


if __name__ == "__main__":
    unittest.main()
