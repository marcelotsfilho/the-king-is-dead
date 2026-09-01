import unittest

from model.board import Tabuleiro
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
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
        self.assertIsNone(estado.vencedor)
        self.assertIsNone(estado.motivo_encerramento)

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
