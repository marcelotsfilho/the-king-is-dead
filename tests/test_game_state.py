import unittest

from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.board import Tabuleiro
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


class TesteEstadoJogo(unittest.TestCase):
    """Verifica a estrutura que reúne o estado atual da partida."""

    def test_estado_armazena_tabuleiro_trilha_e_jogadores(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)
        jogadores = [Jogador("Jogador 1"), Jogador("Jogador 2")]

        estado = EstadoJogo(tabuleiro, trilha, jogadores)

        self.assertIs(estado.tabuleiro, tabuleiro)
        self.assertIs(estado.trilha_disputas, trilha)
        self.assertEqual(estado.obter_jogadores(), jogadores)

    def test_primeiro_jogador_comeca_como_jogador_atual(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)
        jogador_1 = Jogador("Jogador 1")
        jogador_2 = Jogador("Jogador 2")

        estado = EstadoJogo(tabuleiro, trilha, [jogador_1, jogador_2])

        self.assertEqual(estado.indice_jogador_atual, 0)
        self.assertIs(estado.obter_jogador_atual(), jogador_1)

    def test_estado_comeca_sem_passes_e_nao_finalizado(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)
        jogadores = [Jogador("Jogador 1"), Jogador("Jogador 2")]

        estado = EstadoJogo(tabuleiro, trilha, jogadores)

        self.assertEqual(estado.passes_consecutivos, 0)
        self.assertFalse(estado.finalizado)

    def test_estado_comeca_na_fase_de_escolher_acao(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])

        self.assertEqual(estado.fase_turno, FaseTurno.ESCOLHER_ACAO)
        self.assertIsNone(estado.carta_em_execucao)
        self.assertIsNone(estado.ultima_acao)
        self.assertIsNone(estado.vencedor)
        self.assertIsNone(estado.motivo_encerramento)

    def test_copia_direta_isola_convocacao_pendente_e_referencia_a_carta(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        jogador = estado.obter_jogador_atual()
        primeira, segunda = [
            carta for carta in jogador.obter_mao() if carta.tipo == TipoCartaAcao.REUNIR
        ]
        jogador.usar_carta(primeira)
        destinos = {faccao: "Moray" for faccao in Faccao}
        Jogo(estado).jogar_carta(segunda, {"destinos": destinos})

        serializador = SerializadorEstadoJogo()
        antes = serializador.serializar(estado)
        copia = estado.copiar()
        irmao = estado.copiar()
        self.assertEqual(serializador.serializar(copia), antes)
        jogador_da_copia = copia.obter_jogador_atual()
        self.assertIs(copia.ultima_acao["jogador"], jogador_da_copia)
        self.assertIs(copia.ultimo_jogador_que_agiu, jogador_da_copia)
        self.assertIs(copia.carta_em_execucao, jogador_da_copia.obter_descarte_mao()[-1])
        self.assertIsNot(copia.carta_em_execucao, estado.carta_em_execucao)

        Jogo(copia).convocar_seguidor("Moray", Faccao.ESCOCESES)
        copia.ultima_acao["detalhes"]["destinos"].clear()
        copia.trilha_disputas.obter_carta(1).virar_para_baixo()
        copia.reserva.devolver(Faccao.GALESES)
        self.assertEqual(serializador.serializar(estado), antes)
        self.assertEqual(serializador.serializar(irmao), antes)

    def test_jogadores_devem_ser_informados_em_uma_lista(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)

        with self.assertRaises(ValueError):
            EstadoJogo(tabuleiro, trilha, "Jogador 1 e Jogador 2")

    def test_estado_rejeita_apenas_um_jogador(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)

        with self.assertRaises(ValueError):
            EstadoJogo(tabuleiro, trilha, [Jogador("Jogador 1")])

    def test_estado_rejeita_mais_de_dois_jogadores(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)
        jogadores = [
            Jogador("Jogador 1"),
            Jogador("Jogador 2"),
            Jogador("Jogador 3"),
        ]

        with self.assertRaises(ValueError):
            EstadoJogo(tabuleiro, trilha, jogadores)

    def test_obter_jogadores_retorna_uma_copia(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo().criar_trilha_disputas(tabuleiro)
        jogadores = [Jogador("Jogador 1"), Jogador("Jogador 2")]
        estado = EstadoJogo(tabuleiro, trilha, jogadores)

        jogadores_recebidos = estado.obter_jogadores()
        jogadores_recebidos.clear()

        self.assertEqual(len(estado.obter_jogadores()), 2)

    def test_avancar_jogador_alterna_e_retorna_ao_primeiro(self):
        tabuleiro = Tabuleiro()
        trilha = ConfiguracaoJogo(42).criar_trilha_disputas(tabuleiro)
        jogadores = [Jogador("Jogador 1"), Jogador("Jogador 2")]
        reserva = ReservaSeguidores(16)
        estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)

        estado.avancar_jogador()
        self.assertIs(estado.obter_jogador_atual(), jogadores[1])

        estado.avancar_jogador()
        self.assertIs(estado.obter_jogador_atual(), jogadores[0])


if __name__ == "__main__":
    unittest.main()
