import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game_state import EstadoJogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.player import Jogador
from model.supply import ReservaSeguidores


def criar_estado_manual(quantidade_reserva=0):
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(quantidade_reserva)
    return EstadoJogo(tabuleiro, trilha, jogadores, reserva)


class TesteGeradorJogadas(unittest.TestCase):
    def setUp(self):
        self.gerador = GeradorJogadas()
        self.executor = ExecutorJogada()

    def test_estado_sem_cartas_possui_apenas_passe(self):
        estado = criar_estado_manual()

        jogadas = self.gerador.gerar(estado)

        self.assertEqual(len(jogadas), 1)
        self.assertTrue(jogadas[0].eh_passe())

    def test_estado_finalizado_nao_possui_jogadas(self):
        estado = criar_estado_manual()
        estado.finalizado = True
        estado.fase_turno = FaseTurno.ENCERRADO

        self.assertEqual(self.gerador.gerar(estado), [])

    def test_gerador_nao_altera_estado_original(self):
        estado = criar_estado_manual(2)
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        estado.reserva.retirar(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        jogadas = self.gerador.gerar(estado)

        self.assertGreater(len(jogadas), 1)
        self.assertEqual(jogador.quantidade_cartas(), 1)
        self.assertEqual(estado.indice_jogador_atual, 0)
        self.assertEqual(
            estado.tabuleiro.obter_regiao("Strathclyde")
            .total_de_seguidores(),
            0,
        )

    def test_todas_as_jogadas_geradas_podem_ser_executadas(self):
        estado = criar_estado_manual(2)
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        estado.reserva.retirar(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        jogadas = self.gerador.gerar(estado)

        for jogada in jogadas:
            resultado = self.executor.executar(estado, jogada)
            self.assertIsNot(resultado, estado)

    def test_cartas_repetidas_nao_duplicam_as_jogadas(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        jogadas = self.gerador.gerar(estado)
        jogadas_reunir = []

        for jogada in jogadas:
            if jogada.tipo_carta == TipoCartaAcao.REUNIR:
                jogadas_reunir.append(jogada)

        self.assertEqual(len(jogadas_reunir), 1)

    def test_negociar_sem_efeito_nao_exige_disco_disponivel(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.NEGOCIAR))
        jogador.usar_disco_negociacao()
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        for posicao in range(2, 9):
            estado.trilha_disputas.obter_carta(posicao).virar_para_baixo()

        jogadas = self.gerador.gerar(estado)
        encontrou_negociar = False

        for jogada in jogadas:
            if jogada.tipo_carta == TipoCartaAcao.NEGOCIAR:
                encontrou_negociar = True

        self.assertTrue(encontrou_negociar)

    def test_gera_opcoes_para_todos_os_tipos_de_carta(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()

        for tipo_carta in TipoCartaAcao:
            jogador.adicionar_carta_mao(CartaAcao(tipo_carta))

        moray = estado.tabuleiro.obter_regiao("Moray")
        strathclyde = estado.tabuleiro.obter_regiao("Strathclyde")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        strathclyde.adicionar_seguidores(Faccao.GALESES, 2)

        jogadas = self.gerador.gerar(estado)
        tipos_encontrados = set()

        for jogada in jogadas:
            if jogada.eh_carta():
                tipos_encontrados.add(jogada.tipo_carta)

        self.assertEqual(tipos_encontrados, set(TipoCartaAcao))

    def test_rejeita_objeto_que_nao_seja_estado(self):
        with self.assertRaises(TypeError):
            self.gerador.gerar("estado")


if __name__ == "__main__":
    unittest.main()
