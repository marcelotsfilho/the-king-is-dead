import os
import tempfile
import unittest
from threading import Event
from unittest.mock import Mock, patch

from controller.game_controller import ControladorJogo
from model.enums import Faccao, FaseTurno, TipoCartaAcao, TipoJogada, TipoJogador
from model.game import Jogo
from model.action_card import CartaAcao
from model.legal_move import Jogada
from model.state_tree_serializer import SerializadorArvoreEstados
from tests.test_controller import VisaoFalsa
from tests.test_minimax_agent import criar_estado


def criar_controlador_ia(tipo_um=TipoJogador.MINIMAX, tipo_dois=TipoJogador.HUMANO):
    controlador = ControladorJogo(Jogo(criar_estado()), VisaoFalsa())
    controlador.configuracao_partida.definir_tipo_jogador(0, tipo_um)
    controlador.configuracao_partida.definir_tipo_jogador(1, tipo_dois)
    return controlador


def preparar_busca(controlador):
    """Aguarda a chamada manual de run, mantendo o teste determinístico."""
    with patch("controller.game_controller.Thread.start"):
        controlador._atualizar_turno_ia()
    controlador._tarefa_ia.run()


class TesteTurnosIA(unittest.TestCase):
    def test_retomar_busca_em_andamento_mostra_calculo_e_tempo(self):
        controlador = criar_controlador_ia()
        with patch("controller.game_controller.Thread.start"):
            controlador._atualizar_turno_ia()
        with patch("controller.game_controller.perf_counter", return_value=controlador._inicio_busca_ia + 12):
            self.assertIn("12.0 s", controlador._obter_status_ia())
            self.assertIn("demorada", controlador._obter_status_ia())
            controlador._alternar_pausa_ia()
            self.assertIn("cálculo continua", controlador._obter_status_ia())
            controlador._alternar_pausa_ia()
            self.assertIn("calculando", controlador.instrucao)
            self.assertNotIn("Aguardando o próximo turno", controlador.instrucao)

    def test_resposta_pronta_informa_como_continuar(self):
        controlador = criar_controlador_ia()
        preparar_busca(controlador)
        controlador.ia_pausada = True
        self.assertIn("Jogada pronta", controlador._obter_status_ia())
        self.assertIn("RETOMAR IA", controlador._obter_status_ia())
        controlador.ia_pausada = False
        controlador.arvore_aberta = True
        self.assertIn("Feche a árvore", controlador._obter_status_ia())

    def test_falha_da_ia_tem_instrucao_de_recuperacao(self):
        controlador = criar_controlador_ia()
        with patch("controller.game_controller.AgenteMinimax", side_effect=RuntimeError("falha")):
            preparar_busca(controlador)
        controlador._atualizar_turno_ia()
        self.assertIn("preservada", controlador._obter_status_ia())
        self.assertIn("RETOMAR IA", controlador._obter_status_ia())
        self.assertIn("SALVAR", controlador._obter_status_ia())

    def test_thread_real_mantem_loop_livre_e_envia_resultado_pela_fila(self):
        controlador = criar_controlador_ia()
        iniciou = Event()
        liberar = Event()

        def escolher(estado, profundidade_maxima, usar_poda):
            iniciou.set()
            if not liberar.wait(timeout=2):
                raise RuntimeError("O teste não liberou a busca.")
            return Jogada(TipoJogada.PASSE)

        with patch("controller.game_controller.AgenteMinimax") as classe_agente:
            agente = classe_agente.return_value
            agente.escolher_jogada.side_effect = escolher
            agente.nos_visitados = 2
            agente.podas_realizadas = 0
            controlador._atualizar_turno_ia()
            try:
                self.assertTrue(iniciou.wait(timeout=1))
                controlador._atualizar_turno_ia()
                controlador._processar_clique("arvore")
                self.assertTrue(controlador.arvore_aberta)
                self.assertEqual(controlador.arvore.quantidade_nos(), 1)
            finally:
                liberar.set()
                controlador._tarefa_ia.join(timeout=2)
        self.assertFalse(controlador._tarefa_ia.is_alive())
        controlador._processar_clique("fechar_arvore")
        controlador._atualizar_turno_ia()
        self.assertEqual(controlador.arvore.quantidade_nos(), 2)

    def test_tipo_profundidade_e_flag_sao_entregues_ao_agente(self):
        for tipo, usar_poda in ((TipoJogador.MINIMAX, False), (TipoJogador.ALFA_BETA, True)):
            controlador = criar_controlador_ia(tipo)
            controlador.configuracao_partida.definir_profundidade(0, 3)
            agente = Mock()
            agente.escolher_jogada.return_value = Jogada(TipoJogada.PASSE)
            with patch("controller.game_controller.AgenteMinimax", return_value=agente):
                preparar_busca(controlador)
            self.assertEqual(controlador.jogo.estado.indice_jogador_atual, 0)
            self.assertEqual(controlador.arvore.quantidade_nos(), 1)
            parametros = agente.escolher_jogada.call_args
            self.assertIsNot(parametros.args[0], controlador.jogo.estado)
            self.assertEqual(parametros.kwargs, {"profundidade_maxima": 3, "usar_poda": usar_poda})
            controlador._atualizar_turno_ia()
            self.assertEqual(controlador.jogo.estado.indice_jogador_atual, 1)
            self.assertEqual(controlador.arvore.obter_no_atual().obter_nivel(), 1)
            self.assertGreaterEqual(controlador.ultima_decisao_ia["tempo_segundos"], 0)

    def test_carta_da_ia_inclui_convocacao_e_um_unico_no(self):
        estado = criar_estado()
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES)
        estado.obter_jogador_atual().adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
        controlador = ControladorJogo(Jogo(estado), VisaoFalsa())
        controlador.configuracao_partida.definir_tipo_jogador(0, TipoJogador.MINIMAX)
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=TipoCartaAcao.REUNIR,
            parametros={},
            nome_regiao_convocacao="Moray",
            faccao_convocacao=Faccao.ESCOCESES,
        )
        with patch("controller.game_controller.AgenteMinimax") as classe_agente:
            classe_agente.return_value.escolher_jogada.return_value = jogada
            preparar_busca(controlador)
        controlador._atualizar_turno_ia()
        self.assertEqual(controlador.jogo.estado.fase_turno, FaseTurno.ESCOLHER_ACAO)
        self.assertEqual(controlador.jogo.estado.indice_jogador_atual, 1)
        self.assertEqual(controlador.jogo.estado.obter_jogadores()[0].qtd_na_corte(Faccao.ESCOCESES), 1)
        self.assertEqual(controlador.arvore.quantidade_nos(), 2)

    def test_turno_humano_nao_inicia_ia_e_cliques_nao_jogam_pela_ia(self):
        controlador = criar_controlador_ia()
        controlador._processar_clique("passar")
        self.assertEqual(controlador.arvore.quantidade_nos(), 1)
        preparar_busca(controlador)
        controlador._atualizar_turno_ia()
        with patch("controller.game_controller.Thread") as thread:
            controlador._atualizar_turno_ia()
        thread.assert_not_called()
        controlador._processar_clique("passar")
        self.assertEqual(controlador.arvore.obter_no_atual().obter_nivel(), 2)

    def test_uma_unica_busca_pendente_sem_bloquear_atualizacoes(self):
        controlador = criar_controlador_ia()
        with patch("controller.game_controller.Thread.start") as iniciar:
            controlador._atualizar_turno_ia()
            for _ in range(5):
                controlador._atualizar_turno_ia()
            iniciar.assert_called_once()
        self.assertEqual(controlador.arvore.quantidade_nos(), 1)

    def test_pausa_e_arvore_aberta_adiam_aplicacao_do_resultado(self):
        for motivo in ("pausa", "arvore"):
            controlador = criar_controlador_ia()
            preparar_busca(controlador)
            if motivo == "pausa":
                controlador._processar_clique("pausar_ia")
            else:
                controlador._processar_clique("arvore")
            controlador._atualizar_turno_ia()
            self.assertEqual(controlador.arvore.quantidade_nos(), 1)
            if motivo == "pausa":
                controlador._processar_clique("pausar_ia")
            else:
                controlador._processar_clique("fechar_arvore")
            controlador._atualizar_turno_ia()
            self.assertEqual(controlador.arvore.quantidade_nos(), 2)

    def test_volta_descarta_resposta_antiga_e_pausa_ia(self):
        controlador = criar_controlador_ia(TipoJogador.HUMANO, TipoJogador.ALFA_BETA)
        controlador._processar_clique("passar")
        preparar_busca(controlador)
        controlador._processar_clique("voltar")
        controlador._atualizar_turno_ia()
        self.assertTrue(controlador.arvore.obter_no_atual().eh_raiz())
        self.assertTrue(controlador.ia_pausada)
        self.assertIsNone(controlador._tarefa_ia)

    def test_erro_na_busca_pausa_sem_alterar_jogo(self):
        controlador = criar_controlador_ia()
        with patch("controller.game_controller.AgenteMinimax", side_effect=RuntimeError("falha de teste")):
            preparar_busca(controlador)
        controlador._atualizar_turno_ia()
        self.assertTrue(controlador.ia_pausada)
        self.assertIn("falha de teste", controlador.instrucao)
        self.assertEqual(controlador.arvore.quantidade_nos(), 1)

    def test_ausencia_de_jogada_pausa_sem_alterar_jogo(self):
        controlador = criar_controlador_ia()
        with patch("controller.game_controller.AgenteMinimax") as classe_agente:
            classe_agente.return_value.escolher_jogada.return_value = None
            preparar_busca(controlador)
        controlador._atualizar_turno_ia()
        self.assertTrue(controlador.ia_pausada)
        self.assertEqual(controlador.arvore.quantidade_nos(), 1)

    def test_ia_contra_ia_termina_e_salva_partida_sem_cartas(self):
        controlador = criar_controlador_ia(TipoJogador.MINIMAX, TipoJogador.ALFA_BETA)
        with tempfile.TemporaryDirectory() as pasta:
            controlador.caminho_salvamento = os.path.join(pasta, "ia.json")
            # Sem cartas e seguidores, a terceira instabilidade vem após seis passes.
            for _ in range(6):
                preparar_busca(controlador)
                controlador._atualizar_turno_ia()
            self.assertTrue(controlador.jogo.estado.finalizado)
            self.assertEqual(controlador.arvore.obter_no_atual().obter_nivel(), 6)
            restaurada = SerializadorArvoreEstados().carregar(controlador.caminho_salvamento)
            self.assertTrue(restaurada.obter_estado_atual().finalizado)
            with patch("controller.game_controller.Thread") as thread:
                controlador._atualizar_turno_ia()
            thread.assert_not_called()

    def test_fechar_janela_nao_aplica_resposta_pronta(self):
        controlador = criar_controlador_ia()
        preparar_busca(controlador)
        controlador.executando = False
        controlador._atualizar_turno_ia()
        self.assertEqual(controlador.arvore.quantidade_nos(), 1)

    def test_registro_rejeitado_mantem_estado_e_arvore_sincronizados(self):
        controlador = criar_controlador_ia()
        preparar_busca(controlador)
        estado_anterior = controlador.jogo.estado
        with patch.object(controlador.arvore, "registrar_jogada_realizada", side_effect=ValueError("duplicado")):
            controlador._atualizar_turno_ia()
        self.assertIs(controlador.jogo.estado, estado_anterior)
        self.assertTrue(controlador.ia_pausada)
        controlador._validar_sincronia_inicial()


if __name__ == "__main__":
    unittest.main()
