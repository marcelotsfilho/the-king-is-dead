import unittest
from unittest.mock import Mock

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.minimax_agent import AgenteMinimax
from model.player import Jogador
from model.state_evaluator import AvaliadorEstado
from model.supply import ReservaSeguidores


def criar_estado(indice_jogador=0):
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    estado = EstadoJogo(tabuleiro, trilha, jogadores, ReservaSeguidores(0))
    estado.indice_jogador_atual = indice_jogador
    return estado


def preparar_arvore_controlada(agente, notas):
    """Isola a busca para conferir decisões e cortes com valores conhecidos."""
    estados = {
        "raiz": criar_estado(0),
        "A": criar_estado(1),
        "B": criar_estado(1),
        "A1": criar_estado(0),
        "A2": criar_estado(0),
        "B1": criar_estado(0),
        "B2": criar_estado(0),
    }
    filhos = {
        "raiz": ["A", "B"],
        "A": ["A1", "A2"],
        "B": ["B1", "B2"],
    }

    for nome in estados:
        estados[nome].nome_teste = nome

    agente._gerador = Mock()
    agente._gerador.gerar.side_effect = (
        lambda estado: filhos.get(estado.nome_teste, [])
    )
    agente._executor = Mock()
    agente._executor.executar.side_effect = (
        lambda estado, jogada: estados[jogada]
    )
    agente._avaliador = Mock()
    agente._avaliador.avaliar.side_effect = (
        lambda estado, profundidade: notas[estado.nome_teste]
    )
    return estados


class TesteAgenteMinimax(unittest.TestCase):
    def test_antecipacao_considera_a_melhor_resposta_do_adversario(self):
        agente = AgenteMinimax(0)
        estados = preparar_arvore_controlada(
            agente,
            {"A": 8, "B": 5, "A1": 1, "A2": 2, "B1": 4, "B2": 6},
        )

        self.assertEqual(agente.escolher_jogada(estados["raiz"], 1), "A")
        self.assertEqual(agente.escolher_jogada(estados["raiz"], 2), "B")
        self.assertEqual(agente.ultima_pontuacao, 4)

    def test_poda_mantem_resultado_e_reduz_nos_visitados(self):
        agente = AgenteMinimax(0)
        estados = preparar_arvore_controlada(
            agente,
            {"A1": 3, "A2": 5, "B1": 2, "B2": 9},
        )

        sem_poda = agente.escolher_jogada(estados["raiz"], 2, False)
        nota_sem_poda = agente.ultima_pontuacao
        nos_sem_poda = agente.nos_visitados
        self.assertEqual(agente.podas_realizadas, 0)

        com_poda = agente.escolher_jogada(estados["raiz"], 2, True)

        self.assertEqual(sem_poda, "A")
        self.assertEqual(com_poda, sem_poda)
        self.assertEqual(agente.ultima_pontuacao, nota_sem_poda)
        self.assertLess(agente.nos_visitados, nos_sem_poda)
        self.assertGreater(agente.podas_realizadas, 0)
        self.assertEqual(agente.folhas_avaliadas, 3)

    def test_empate_mantem_primeira_jogada(self):
        agente = AgenteMinimax(0)
        estados = preparar_arvore_controlada(agente, {"A": 5, "B": 5})

        for usar_poda in (False, True):
            self.assertEqual(
                agente.escolher_jogada(estados["raiz"], 1, usar_poda), "A"
            )

    def test_nao_gera_filhos_de_estado_final(self):
        estado = criar_estado()
        estado.finalizado = True
        estado.vencedor = estado.obter_jogadores()[0]
        agente = AgenteMinimax(0)
        agente._gerador = Mock()

        self.assertIsNone(agente.escolher_jogada(estado, 3))
        agente._gerador.gerar.assert_not_called()
        self.assertEqual(agente.ultima_pontuacao, 1000000)

    def test_prefere_vitoria_rapida_e_adia_derrota_inevitavel(self):
        for indice_vencedor, escolha_esperada in ((0, "A"), (1, "B")):
            for usar_poda in (False, True):
                agente = AgenteMinimax(0)
                estados = preparar_arvore_controlada(agente, {})
                agente._avaliador = AvaliadorEstado(0)

                for nome in ("A", "B1", "B2"):
                    estado = estados[nome]
                    estado.finalizado = True
                    estado.vencedor = estado.obter_jogadores()[indice_vencedor]

                escolha = agente.escolher_jogada(
                    estados["raiz"], 2, usar_poda
                )

                self.assertEqual(escolha, escolha_esperada)

    def test_sem_jogadas_avalia_o_estado(self):
        agente = AgenteMinimax(0)
        agente._gerador = Mock()
        agente._gerador.gerar.return_value = []
        agente._avaliador = Mock()
        agente._avaliador.avaliar.return_value = 12

        self.assertIsNone(agente.escolher_jogada(criar_estado()))
        self.assertEqual(agente.ultima_pontuacao, 12)

    def test_convocacao_pendente_nao_inicia_busca(self):
        estado = criar_estado()
        estado.fase_turno = FaseTurno.CONVOCAR_SEGUIDOR
        agente = AgenteMinimax(0)

        self.assertIsNone(agente.escolher_jogada(estado))
        self.assertEqual(agente.nos_visitados, 0)

    def test_rejeita_configuracoes_invalidas(self):
        agente = AgenteMinimax(0)
        estado = criar_estado()

        for profundidade in (0, -1):
            with self.assertRaises(ValueError):
                agente.escolher_jogada(estado, profundidade)

        for profundidade in (True, "2", 1.5):
            with self.assertRaises(TypeError):
                agente.escolher_jogada(estado, profundidade)

        with self.assertRaises(TypeError):
            agente.escolher_jogada(None)

        with self.assertRaises(TypeError):
            agente.escolher_jogada(estado, usar_poda="sim")

        with self.assertRaises(ValueError):
            agente.escolher_jogada(criar_estado(1))

    def test_jogo_real_produz_jogada_legal_e_preserva_estado(self):
        for indice_ia in (0, 1):
            estado = criar_estado(indice_ia)
            estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
                Faccao.ESCOCESES
            )
            estado.tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(
                Faccao.GALESES
            )
            for jogador in estado.obter_jogadores():
                jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))

            serializador = SerializadorEstadoJogo()
            dados_antes = serializador.serializar(estado)
            agente = AgenteMinimax(indice_ia)
            sem_poda = agente.escolher_jogada(estado, 2, False)
            nota_sem_poda = agente.ultima_pontuacao
            com_poda = agente.escolher_jogada(estado, 2, True)

            self.assertTrue(sem_poda.possui_mesmos_dados(com_poda))
            self.assertEqual(nota_sem_poda, agente.ultima_pontuacao)
            jogadas_validas = GeradorJogadas().gerar(estado)
            self.assertTrue(any(
                com_poda.possui_mesmos_dados(jogada)
                for jogada in jogadas_validas
            ))
            ExecutorJogada().executar(estado, com_poda)
            self.assertEqual(serializador.serializar(estado), dados_antes)


if __name__ == "__main__":
    unittest.main()
