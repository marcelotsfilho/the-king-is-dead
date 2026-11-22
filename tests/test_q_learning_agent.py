import tempfile
import unittest
from pathlib import Path

from experiments.q_learning_evolution import _ler_estado, _PASTA_HISTORICA
from experiments.q_learning_scenarios import criar_posicao, desfecho
from experiments.q_learning_tactics import _continuar
from model.endgame_search import BuscaFinal
from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.q_learning_agent import CAMINHO_TABELA_Q_JOGO, AgenteQLearning, TabelaQ


class TesteQLearning(unittest.TestCase):
    def test_atualizacao_usa_apenas_acoes_legais_e_ignora_futuro_no_terminal(self):
        tabela = TabelaQ()
        tabela.atualizar("seguinte", "PASSE", 1, None, 1, 0.9)
        tabela.atualizar("seguinte", "APOIO_INGLES", 0.4, None, 1, 0.9)

        proximas = "seguinte", {"APOIO_INGLES": None}
        tabela.atualizar("atual", "PASSE", 0, proximas, 0.5, 0.9)
        self.assertAlmostEqual(tabela.consultar("atual", "PASSE"), 0.18)
        tabela.atualizar("atual", "PASSE", -1, None, 1, 0.9)
        self.assertAlmostEqual(tabela.consultar("atual", "PASSE"), -1)

    def test_aprende_preferencias_opostas_e_recarrega_decisoes_sem_treinar(self):
        tabela = TabelaQ()
        agente = AgenteQLearning(tabela)
        for estado, escolher_passe in ((criar_posicao(True), True), (criar_posicao(False), False)):
            chave, opcoes = agente.preparar_turno(estado)
            acao = "PASSE" if escolher_passe else "APOIO_INGLES"
            self.assertIn(acao, opcoes)
            tabela.atualizar(chave, acao, 1, None, 0.5, 0.9)

        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "tabela.json"
            tabela.salvar(caminho, {"partidas_treinadas": 2})
            carregada = TabelaQ.carregar(caminho)
            agente = AgenteQLearning(carregada)
            for escolher_passe in (True, False):
                estado = criar_posicao(escolher_passe)
                jogada = agente.escolher_jogada(estado)
                self.assertEqual(jogada.eh_passe(), escolher_passe)
                self.assertEqual(desfecho(estado, jogada), "vitoria")
                self.assertEqual(estado.obter_jogador_atual().quantidade_cartas(), 1)
            self.assertEqual(carregada.valores, tabela.valores)
            self.assertEqual(carregada.metadados["partidas_treinadas"], 2)

    def test_busca_final_corrige_as_tres_decisoes_da_auditoria(self):
        tabela = TabelaQ.carregar(CAMINHO_TABELA_Q_JOGO)
        agente = AgenteQLearning(tabela, analisar_finais=True)
        serializador = SerializadorEstadoJogo()
        for arquivo, escolha in (("carta_necessaria_55127.json", "NEGOCIAR"),
                                 ("carta_necessaria_55179.json", "REUNIR"),
                                 ("guardar_carta_60577.json", "PASSE")):
            with self.subTest(arquivo=arquivo):
                estado = _ler_estado(_PASTA_HISTORICA / arquivo)
                antes = serializador.serializar(estado)
                acao, _, _ = agente.decidir_turno(estado, agente.preparar_turno(estado))
                self.assertEqual(acao, escolha)
                self.assertTrue(agente.busca_final_concluida)
                self.assertTrue(agente.busca_final_alterou)
                lado = estado.indice_jogador_atual
                resultado, _ = _continuar(estado, lado, agente.escolher_jogada)
                self.assertEqual(resultado, 1)
                self.assertEqual(serializador.serializar(estado), antes)

    def test_busca_interrompida_preserva_a_jogada_original(self):
        estado = _ler_estado(_PASTA_HISTORICA / "guardar_carta_60577.json")
        agente = AgenteQLearning(TabelaQ.carregar(CAMINHO_TABELA_Q_JOGO))
        _, jogada, seguinte = agente.escolher_opcao(agente.preparar_turno(estado))
        busca = BuscaFinal(limite_nos=1)

        self.assertEqual(busca.melhorar(estado, jogada, seguinte), (jogada, seguinte))
        self.assertEqual(busca.nos_visitados, 1)
        self.assertFalse(busca.concluida)

    def test_abertura_usa_a_politica_q_sem_busca_de_final(self):
        estado = ConfiguracaoJogo(40).criar_estado_inicial(["Ana", "Bruno"])
        tabela = TabelaQ.carregar(CAMINHO_TABELA_Q_JOGO)
        original = AgenteQLearning(tabela)
        hibrido = AgenteQLearning(tabela, analisar_finais=True)

        self.assertTrue(hibrido.escolher_jogada(estado).possui_mesmos_dados(original.escolher_jogada(estado)))
        self.assertEqual(hibrido.nos_busca_final, 0)
