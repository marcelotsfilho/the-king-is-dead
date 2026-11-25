import unittest
from random import Random
from unittest.mock import patch

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import serializar_jogada
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

    def test_geracao_com_estados_reusa_resultados_legais(self):
        estado = criar_estado_manual(2)
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        estado.reserva.retirar(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        pares = list(self.gerador.gerar_com_estados(estado))
        jogadas = self.gerador.gerar(estado)

        self.assertEqual(len(pares), len(jogadas))
        for (jogada_com_estado, _), jogada in zip(pares, jogadas):
            self.assertTrue(jogada_com_estado.possui_mesmos_dados(jogada))
        for jogada, estado_resultante in pares:
            esperado = self.executor.executar(estado, jogada)
            self.assertTrue(
                SerializadorEstadoJogo().possuem_mesmo_estado(
                    estado_resultante,
                    esperado,
                )
            )

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

    def test_prioriza_resposta_legal_sem_gerar_as_demais_jogadas_antes(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.APOIO_GALES))
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(Faccao.GALESES)
        jogadas = self.gerador.gerar(estado)
        preferida = jogadas[-1]

        with patch.object(Jogo, "jogar_carta", autospec=True, side_effect=Jogo.jogar_carta) as jogar:
            sucessores = self.gerador.gerar_com_estados(estado, prioridade=preferida)
            passe, _ = next(sucessores)
            self.assertTrue(passe.eh_passe())
            jogar.assert_not_called()
            primeira_carta, resultado = next(sucessores)
            self.assertTrue(primeira_carta.possui_mesmos_dados(preferida))
            jogar.assert_called_once()

        serializador = SerializadorEstadoJogo()
        esperado = self.executor.executar(estado, preferida)
        self.assertEqual(serializador.serializar(resultado), serializador.serializar(esperado))
        ordenadas = [passe, primeira_carta, *(jogada for jogada, _ in sucessores)]
        self.assertCountEqual(
            [serializar_jogada(jogada) for jogada in ordenadas],
            [serializar_jogada(jogada) for jogada in jogadas],
        )

    def test_convocacoes_reaproveitam_o_efeito_da_carta_em_estados_independentes(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        moray = estado.tabuleiro.obter_regiao("Moray")
        gwynedd = estado.tabuleiro.obter_regiao("Gwynedd")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        gwynedd.adicionar_seguidores(Faccao.GALESES)
        serializador = SerializadorEstadoJogo()
        original = serializador.serializar(estado)

        with patch.object(
            Jogo, "jogar_carta", autospec=True, side_effect=Jogo.jogar_carta
        ) as jogar:
            pares = list(self.gerador.gerar_com_estados(estado))
        self.assertEqual(len(pares), 3)
        jogar.assert_called_once()

        sorteada, resultado_sorteado = self.gerador.sortear_com_estado(
            estado, Random(0)
        )
        self.assertTrue(sorteada.eh_carta())
        pares.append((sorteada, resultado_sorteado))
        for jogada, resultado in pares:
            esperado = self.executor.executar(estado, jogada)
            self.assertEqual(
                serializador.serializar(resultado), serializador.serializar(esperado)
            )
        self.assertEqual(serializador.serializar(estado), original)

    def test_avaliacao_dos_sucessores_reusa_a_copia_apos_a_carta(self):
        estado = criar_estado_manual()
        estado.obter_jogador_atual().adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(Faccao.GALESES)
        serializar = SerializadorEstadoJogo().serializar
        antes = serializar(estado)
        esperados = [serializar(filho) for _, filho in self.gerador.gerar_com_estados(estado)]

        with patch.object(EstadoJogo, "copiar", autospec=True, side_effect=EstadoJogo.copiar) as copiar:
            obtidos = list(self.gerador.avaliar_sucessores(estado, serializar))

        self.assertEqual(obtidos, esperados)
        self.assertEqual(len(obtidos), 3)
        self.assertEqual(copiar.call_count, 2)
        self.assertEqual(serializar(estado), antes)

    def test_convocacao_temporaria_restaura_estado_se_a_avaliacao_falhar(self):
        estado = criar_estado_manual()
        estado.obter_jogador_atual().adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES)
        pendente = self.executor.executar_carta(estado, TipoCartaAcao.REUNIR, {})
        serializar = SerializadorEstadoJogo().serializar
        antes = serializar(pendente)

        def avaliar(filho):
            self.assertEqual(filho.fase_turno, FaseTurno.ESCOLHER_ACAO)
            raise RuntimeError("Falha simulada")

        with self.assertRaisesRegex(RuntimeError, "Falha simulada"):
            list(Jogo(pendente).avaliar_convocacoes([("Moray", Faccao.ESCOCESES)], avaliar))
        self.assertEqual(serializar(pendente), antes)

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
