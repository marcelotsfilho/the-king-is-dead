import unittest

from model.game_setup import ConfiguracaoJogo
from model.enums import Faccao
from model.state_evaluator import AvaliadorEstado


def criar_estado():
    return ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])


class TesteAvaliadorEstado(unittest.TestCase):
    def test_rejeita_indice_de_jogador_invalido(self):
        with self.assertRaises(TypeError):
            AvaliadorEstado("0")

        with self.assertRaises(ValueError):
            AvaliadorEstado(2)

    def test_rejeita_estado_invalido(self):
        avaliador = AvaliadorEstado(0)

        with self.assertRaises(TypeError):
            avaliador.avaliar(None)

    def test_rejeita_profundidade_invalida(self):
        avaliador = AvaliadorEstado(0)
        estado = criar_estado()

        with self.assertRaises(ValueError):
            avaliador.avaliar(estado, -1)

        with self.assertRaises(TypeError):
            avaliador.avaliar(estado, "1")

    def test_vitoria_da_ia_vale_mais_quando_acontece_mais_cedo(self):
        estado = criar_estado()
        jogadores = estado.obter_jogadores()
        estado.finalizado = True
        estado.vencedor = jogadores[0]
        avaliador = AvaliadorEstado(0)

        pontuacao_cedo = avaliador.avaliar(estado, 2)
        pontuacao_tarde = avaliador.avaliar(estado, 5)

        self.assertGreater(pontuacao_cedo, pontuacao_tarde)
        self.assertGreater(pontuacao_cedo, 0)

    def test_derrota_da_ia_vale_mais_quando_acontece_mais_tarde(self):
        estado = criar_estado()
        jogadores = estado.obter_jogadores()
        estado.finalizado = True
        estado.vencedor = jogadores[1]
        avaliador = AvaliadorEstado(0)

        pontuacao_cedo = avaliador.avaliar(estado, 2)
        pontuacao_tarde = avaliador.avaliar(estado, 5)

        self.assertGreater(pontuacao_tarde, pontuacao_cedo)
        self.assertLess(pontuacao_tarde, 0)

    def test_empate_final_tem_pontuacao_zero(self):
        estado = criar_estado()
        estado.finalizado = True

        self.assertEqual(AvaliadorEstado(0).avaliar(estado), 0)

    def test_vantagem_na_corte_favorece_a_ia(self):
        estado = criar_estado()
        jogadores = estado.obter_jogadores()
        jogadores[0].adicionar_seguidor_na_corte(Faccao.ESCOCESES)
        jogadores[0].adicionar_seguidor_na_corte(Faccao.ESCOCESES)

        pontuacao = AvaliadorEstado(0).avaliar(estado)

        self.assertGreater(pontuacao, 0)

    def test_dois_conjuntos_a_mais_favorecem_a_ia_na_invasao(self):
        estado = criar_estado()
        jogadores = estado.obter_jogadores()

        for _ in range(3):
            for faccao in Faccao:
                jogadores[0].adicionar_seguidor_na_corte(faccao)

        for regiao in list(estado.tabuleiro.obter_regioes().values())[:2]:
            regiao.marcar_como_instavel()

        pontuacao = AvaliadorEstado(0).avaliar(estado)

        self.assertGreater(pontuacao, 0)


if __name__ == "__main__":
    unittest.main()
