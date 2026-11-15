import unittest
from unittest.mock import patch

from model.game_setup import ConfiguracaoJogo
from model.enums import Faccao
from model.game import Jogo
from model.state_evaluator import AvaliadorEstado
from model.game_state_serializer import SerializadorEstadoJogo
from tests.test_minimax_agent import criar_estado as criar_estado_manual


def criar_estado():
    return ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])


class TesteAvaliadorEstado(unittest.TestCase):
    def test_avaliacao_nao_gera_nem_executa_jogadas(self):
        estado = criar_estado()
        with patch("model.legal_move_generator.GeradorJogadas.gerar") as gerar:
            with patch("model.legal_move_executor.ExecutorJogada.executar") as executar:
                AvaliadorEstado(0).avaliar(estado)
        gerar.assert_not_called()
        executar.assert_not_called()

    def test_perspectivas_opostas_e_estado_preservado(self):
        estado = criar_estado()
        estado.obter_jogadores()[0].adicionar_seguidor_na_corte(Faccao.ESCOCESES)
        serializador = SerializadorEstadoJogo()
        antes = serializador.serializar(estado)
        self.assertEqual(AvaliadorEstado(0).avaliar(estado), -AvaliadorEstado(1).avaliar(estado))
        self.assertEqual(serializador.serializar(estado), antes)

    def test_primeira_faccao_tem_prioridade_sobre_segunda_nos_cortes(self):
        estado = criar_estado_manual()
        jogadores = estado.obter_jogadores()
        jogadores[0].adicionar_seguidor_na_corte(Faccao.ESCOCESES)
        for _ in range(16):
            jogadores[1].adicionar_seguidor_na_corte(Faccao.GALESES)
        nota = AvaliadorEstado(0)._pontuar_cortes(estado, list(Faccao))
        self.assertGreater(nota, 0)

    def test_proxima_disputa_tem_mais_peso_na_projecao(self):
        estado = criar_estado_manual()
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES, 2)
        estado.tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(Faccao.GALESES, 2)
        avaliador = AvaliadorEstado(0)
        self.assertEqual(avaliador._obter_faccoes_projetadas(estado, list(Faccao))[0], Faccao.ESCOCESES)
        estado.trilha_disputas.trocar_cartas(1, 5)
        self.assertEqual(avaliador._obter_faccoes_projetadas(estado, list(Faccao))[0], Faccao.GALESES)

    def test_empate_regional_e_passe_aumentam_peso_da_invasao(self):
        estado = criar_estado_manual()
        for faccao in Faccao:
            estado.obter_jogadores()[0].adicionar_seguidor_na_corte(faccao)
        estado.tabuleiro.obter_regiao("Essex").marcar_como_instavel()
        estado.tabuleiro.obter_regiao("Devon").marcar_como_instavel()
        regiao = estado.tabuleiro.obter_regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES)
        avaliador = AvaliadorEstado(0)
        maioria = avaliador._avaliar_invasao(estado)
        regiao.adicionar_seguidores(Faccao.GALESES)
        empate = avaliador._avaliar_invasao(estado)
        estado.passes_consecutivos = 1
        apos_passe = avaliador._avaliar_invasao(estado)
        self.assertGreater(empate, maioria)
        self.assertGreater(apos_passe, empate)

    def test_empate_de_conjuntos_considera_ultima_carta(self):
        estado = criar_estado_manual()
        estado.ultimo_jogador_que_agiu = estado.obter_jogadores()[0]
        self.assertGreater(AvaliadorEstado(0)._avaliar_invasao(estado), 0)
        self.assertLess(AvaliadorEstado(1)._avaliar_invasao(estado), 0)

    def test_cartas_restantes_favorecem_quem_preservou_mais_opcoes(self):
        estado = criar_estado()
        jogador_2 = estado.obter_jogadores()[1]
        jogador_2.usar_carta(jogador_2.obter_mao()[0])

        nota_jogador_1 = AvaliadorEstado(0)._avaliar_cartas_restantes(estado)
        nota_jogador_2 = AvaliadorEstado(1)._avaliar_cartas_restantes(estado)

        self.assertGreater(nota_jogador_1, 0)
        self.assertEqual(nota_jogador_1, -nota_jogador_2)

    def test_valor_das_cartas_diminui_com_disputas_resolvidas(self):
        estado = criar_estado()
        jogador_2 = estado.obter_jogadores()[1]
        jogador_2.usar_carta(jogador_2.obter_mao()[0])
        avaliador = AvaliadorEstado(0)
        valor_inicial = avaliador._avaliar_cartas_restantes(estado)

        Jogo(estado).resolver_proxima_disputa()

        valor_reduzido = avaliador._avaliar_cartas_restantes(estado)
        self.assertGreater(valor_inicial, valor_reduzido)
        self.assertGreater(valor_reduzido, 0)
        self.assertEqual(
            valor_reduzido,
            -AvaliadorEstado(1)._avaliar_cartas_restantes(estado),
        )

    def test_ultimas_cartas_valem_mais_que_cartas_abundantes(self):
        estado_abundante = criar_estado()
        jogador_2 = estado_abundante.obter_jogadores()[1]
        jogador_2.usar_carta(jogador_2.obter_mao()[0])
        valor_oitava = AvaliadorEstado(0)._avaliar_cartas_restantes(
            estado_abundante
        )

        estado_escasso = criar_estado()
        jogadores = estado_escasso.obter_jogadores()
        for _ in range(7):
            jogadores[0].usar_carta(jogadores[0].obter_mao()[0])
        for _ in range(8):
            jogadores[1].usar_carta(jogadores[1].obter_mao()[0])
        valor_ultima = AvaliadorEstado(0)._avaliar_cartas_restantes(
            estado_escasso
        )

        self.assertGreater(valor_ultima, valor_oitava)

    def test_estimativa_fica_abaixo_do_valor_terminal(self):
        estado = criar_estado_manual()
        for _ in range(200):
            for faccao in Faccao:
                estado.obter_jogadores()[0].adicionar_seguidor_na_corte(faccao)
        self.assertLessEqual(abs(AvaliadorEstado(0).avaliar(estado)), 100000)
        estado.finalizado = True
        estado.vencedor = estado.obter_jogadores()[0]
        self.assertGreater(AvaliadorEstado(0).avaliar(estado, 10), 100000)

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
