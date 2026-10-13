import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, TipoCartaAcao, TipoJogada
from model.game_state import EstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.player import Jogador
from model.state_node import NoEstado
from model.state_tree import ArvoreEstados
from model.supply import ReservaSeguidores


def criar_estado_manual():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(0)
    return EstadoJogo(tabuleiro, trilha, jogadores, reserva)


class TesteArvoreEstados(unittest.TestCase):
    def setUp(self):
        self.estado = criar_estado_manual()
        self.arvore = ArvoreEstados(self.estado)
        self.executor = ExecutorJogada()

    def _adicionar_passe(self, estado, pai=None):
        jogada = Jogada(TipoJogada.PASSE)
        novo_estado = self.executor.executar(estado, jogada)
        novo_no = self.arvore.adicionar_estado(novo_estado, jogada, pai)
        return novo_estado, novo_no

    def test_cria_arvore_com_raiz_atual_e_visitada(self):
        raiz = self.arvore.obter_raiz()

        self.assertIs(self.arvore.obter_no_atual(), raiz)
        self.assertTrue(raiz.eh_raiz())
        self.assertTrue(raiz.esta_visitado())
        self.assertEqual(self.arvore.quantidade_nos(), 1)
        self.assertTrue(self.arvore.possui_estado(self.estado))

    def test_adiciona_estado_como_filho_do_no_atual(self):
        novo_estado, novo_no = self._adicionar_passe(self.estado)
        raiz = self.arvore.obter_raiz()

        self.assertIsNotNone(novo_no)
        self.assertIs(novo_no.obter_pai(), raiz)
        self.assertEqual(raiz.quantidade_filhos(), 1)
        self.assertEqual(self.arvore.quantidade_nos(), 2)
        self.assertTrue(self.arvore.possui_estado(novo_estado))
        self.assertIs(self.arvore.obter_no_atual(), raiz)

    def test_expande_somente_o_no_atual(self):
        filhos = self.arvore.expandir_no_atual()

        self.assertEqual(len(filhos), 1)
        self.assertTrue(filhos[0].obter_jogada_origem().eh_passe())
        self.assertTrue(self.arvore.obter_raiz().esta_expandido())
        self.assertFalse(filhos[0].esta_expandido())
        self.assertEqual(self.arvore.quantidade_nos(), 2)

    def test_expansao_integra_passe_e_carta(self):
        estado = criar_estado_manual()
        estado.reserva.devolver(Faccao.ESCOCESES, 2)
        estado.reserva.retirar(Faccao.ESCOCESES)
        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        estado.obter_jogador_atual().adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        arvore = ArvoreEstados(estado)

        filhos = arvore.expandir_no_atual()
        possui_passe = False
        possui_carta = False

        for filho in filhos:
            jogada = filho.obter_jogada_origem()

            if jogada.eh_passe():
                possui_passe = True
            if jogada.eh_carta():
                possui_carta = True

        self.assertTrue(possui_passe)
        self.assertTrue(possui_carta)

    def test_nao_expande_o_mesmo_no_duas_vezes(self):
        primeiros_filhos = self.arvore.expandir_no_atual()
        quantidade_inicial = self.arvore.quantidade_nos()

        segundos_filhos = self.arvore.expandir_no_atual()

        self.assertEqual(segundos_filhos, primeiros_filhos)
        self.assertEqual(self.arvore.quantidade_nos(), quantidade_inicial)

    def test_registra_e_avanca_para_jogada_realizada(self):
        jogada = Jogada(TipoJogada.PASSE)
        novo_estado = self.executor.executar(self.estado, jogada)

        novo_no = self.arvore.registrar_jogada_realizada(
            jogada,
            novo_estado,
        )

        self.assertIs(self.arvore.obter_no_atual(), novo_no)
        self.assertEqual(novo_no.obter_nivel(), 1)
        self.assertEqual(self.arvore.quantidade_nos(), 2)

    def test_jogada_realizada_reutiliza_filho_ja_gerado(self):
        filho_gerado = self.arvore.expandir_no_atual()[0]
        jogada = filho_gerado.obter_jogada_origem()
        estado_resultante = filho_gerado.obter_estado()

        no_visitado = self.arvore.registrar_jogada_realizada(
            jogada,
            estado_resultante,
        )

        self.assertIs(no_visitado, filho_gerado)
        self.assertEqual(self.arvore.quantidade_nos(), 2)

    def test_expande_proximo_nivel_somente_depois_de_avancar(self):
        filhos_da_raiz = self.arvore.expandir_no_atual()
        primeiro_filho = filhos_da_raiz[0]

        self.assertEqual(primeiro_filho.quantidade_filhos(), 0)

        self.arvore.avancar_para(primeiro_filho)
        filhos_do_segundo_nivel = self.arvore.expandir_no_atual()

        self.assertTrue(primeiro_filho.esta_expandido())
        self.assertGreater(len(filhos_do_segundo_nivel), 0)

    def test_estado_atual_retornado_e_uma_copia(self):
        estado_recebido = self.arvore.obter_estado_atual()
        estado_recebido.passes_consecutivos = 99

        estado_preservado = self.arvore.obter_estado_atual()

        self.assertEqual(estado_preservado.passes_consecutivos, 0)

    def test_nao_adiciona_estado_repetido_em_outro_nivel(self):
        _, primeiro_filho = self._adicionar_passe(self.estado)
        jogada = Jogada(TipoJogada.PASSE)

        repetido = self.arvore.adicionar_estado(
            self.estado,
            jogada,
            primeiro_filho,
        )

        self.assertIsNone(repetido)
        self.assertEqual(self.arvore.quantidade_nos(), 2)
        self.assertEqual(primeiro_filho.quantidade_filhos(), 0)

    def test_avanca_e_volta_pelo_caminho_da_arvore(self):
        novo_estado, primeiro_filho = self._adicionar_passe(self.estado)
        self.arvore.avancar_para(primeiro_filho)
        _, segundo_filho = self._adicionar_passe(novo_estado)
        self.arvore.avancar_para(segundo_filho)

        caminho = self.arvore.obter_caminho_atual()
        self.assertEqual(
            caminho,
            [self.arvore.obter_raiz(), primeiro_filho, segundo_filho],
        )
        self.assertTrue(primeiro_filho.esta_visitado())
        self.assertTrue(segundo_filho.esta_visitado())

        self.assertTrue(self.arvore.voltar())
        self.assertIs(self.arvore.obter_no_atual(), primeiro_filho)
        self.assertFalse(segundo_filho.esta_visitado())
        self.assertTrue(primeiro_filho.esta_visitado())

    def test_nao_volta_quando_esta_na_raiz(self):
        self.assertFalse(self.arvore.voltar())
        self.assertIs(
            self.arvore.obter_no_atual(),
            self.arvore.obter_raiz(),
        )

    def test_lista_de_nos_nao_altera_registro_interno(self):
        nos = self.arvore.obter_nos()
        nos.clear()

        self.assertEqual(self.arvore.quantidade_nos(), 1)

    def test_rejeita_no_que_nao_pertence_a_arvore(self):
        outro_no = NoEstado(self.estado)
        jogada = Jogada(TipoJogada.PASSE)
        novo_estado = self.executor.executar(self.estado, jogada)

        with self.assertRaises(ValueError):
            self.arvore.adicionar_estado(novo_estado, jogada, outro_no)

        with self.assertRaises(ValueError):
            self.arvore.avancar_para(outro_no)

    def test_rejeita_avanco_que_nao_seja_para_filho_atual(self):
        novo_estado, primeiro_filho = self._adicionar_passe(self.estado)
        self.arvore.avancar_para(primeiro_filho)
        _, segundo_filho = self._adicionar_passe(novo_estado)
        self.arvore.voltar()

        with self.assertRaises(ValueError):
            self.arvore.avancar_para(segundo_filho)

    def test_rejeita_valores_invalidos(self):
        with self.assertRaises(TypeError):
            ArvoreEstados("estado")

        with self.assertRaises(TypeError):
            self.arvore.possui_estado("estado")

        with self.assertRaises(TypeError):
            self.arvore.adicionar_estado("estado", Jogada(TipoJogada.PASSE))

        with self.assertRaises(TypeError):
            self.arvore.adicionar_estado(self.estado, "jogada")

        with self.assertRaises(TypeError):
            self.arvore.avancar_para("nó")

        with self.assertRaises(TypeError):
            self.arvore.registrar_jogada_realizada(
                "jogada",
                self.estado,
            )

        with self.assertRaises(TypeError):
            self.arvore.registrar_jogada_realizada(
                Jogada(TipoJogada.PASSE),
                "estado",
            )


if __name__ == "__main__":
    unittest.main()
