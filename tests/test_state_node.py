import unittest

from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, TipoJogada
from model.game_state import EstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.player import Jogador
from model.state_node import NoEstado
from model.supply import ReservaSeguidores
from model.state_evaluator import AvaliadorEstado, VERSAO_HEURISTICA


def criar_estado_manual():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(0)
    return EstadoJogo(tabuleiro, trilha, jogadores, reserva)


class TesteNoEstado(unittest.TestCase):
    def test_nota_estatica_tem_perspectiva_versao_e_copia_protegida(self):
        estado = criar_estado_manual()
        no = NoEstado(estado)
        avaliacao = no.obter_avaliacao_heuristica()
        self.assertEqual(avaliacao["valor"], AvaliadorEstado(0).avaliar(estado, 0))
        self.assertEqual(avaliacao["indice_jogador"], 0)
        self.assertEqual(avaliacao["versao"], VERSAO_HEURISTICA)
        avaliacao["valor"] = 9999
        self.assertNotEqual(no.obter_avaliacao_heuristica()["valor"], 9999)

    def test_mudar_perspectiva_nao_muda_identificador_do_estado(self):
        estado = criar_estado_manual()
        estado.obter_jogadores()[0].adicionar_seguidor_na_corte(Faccao.ESCOCESES)
        no = NoEstado(estado)
        identificador = no.obter_identificador()
        nota_jogador_um = no.obter_avaliacao_heuristica()["valor"]
        no.calcular_avaliacao_heuristica(1)
        self.assertEqual(no.obter_avaliacao_heuristica()["valor"], -nota_jogador_um)
        self.assertEqual(no.obter_identificador(), identificador)

    def test_rejeita_notas_invalidas_sem_alterar_a_nota_anterior(self):
        no = NoEstado(criar_estado_manual())
        antes = no.obter_avaliacao_heuristica()
        for campo, valor in (
            ("valor", True), ("valor", "10"), ("valor", float("nan")),
            ("valor", float("inf")), ("indice_jogador", 2),
            ("indice_jogador", True), ("versao", "1"), ("versao", 0),
        ):
            dados = antes.copy()
            dados[campo] = valor
            with self.assertRaises(ValueError):
                no.definir_avaliacao_heuristica(dados)
            self.assertEqual(no.obter_avaliacao_heuristica(), antes)

    def test_cria_no_raiz(self):
        estado = criar_estado_manual()

        raiz = NoEstado(estado)

        self.assertTrue(raiz.eh_raiz())
        self.assertTrue(raiz.eh_folha())
        self.assertEqual(raiz.obter_nivel(), 0)
        self.assertEqual(raiz.quantidade_filhos(), 0)
        self.assertIsNone(raiz.obter_pai())
        self.assertIsNone(raiz.obter_jogada_origem())
        self.assertFalse(raiz.esta_visitado())
        self.assertFalse(raiz.representa_jogada_voltada())
        self.assertFalse(raiz.esta_expandido())

    def test_no_protege_estado_armazenado(self):
        estado = criar_estado_manual()
        raiz = NoEstado(estado)
        identificador_inicial = raiz.obter_identificador()

        estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        copia_recebida = raiz.obter_estado()
        copia_recebida.tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(
            Faccao.GALESES
        )

        estado_preservado = raiz.obter_estado()
        self.assertEqual(
            estado_preservado.tabuleiro.obter_regiao("Moray")
            .total_de_seguidores(),
            0,
        )
        self.assertEqual(
            estado_preservado.tabuleiro.obter_regiao("Gwynedd")
            .total_de_seguidores(),
            0,
        )
        self.assertEqual(raiz.obter_identificador(), identificador_inicial)

    def test_adiciona_no_filho(self):
        estado = criar_estado_manual()
        raiz = NoEstado(estado)
        jogada = Jogada(TipoJogada.PASSE)
        estado_filho = ExecutorJogada().executar(estado, jogada)
        filho = NoEstado(estado_filho, jogada, raiz)

        adicionado = raiz.adicionar_filho(filho)

        self.assertTrue(adicionado)
        self.assertFalse(raiz.eh_folha())
        self.assertTrue(filho.eh_folha())
        self.assertFalse(filho.eh_raiz())
        self.assertEqual(filho.obter_nivel(), 1)
        self.assertIs(filho.obter_pai(), raiz)
        self.assertIs(filho.obter_jogada_origem(), jogada)

    def test_lista_de_filhos_nao_pode_ser_alterada_por_fora(self):
        estado = criar_estado_manual()
        raiz = NoEstado(estado)

        filhos_recebidos = raiz.obter_filhos()
        filhos_recebidos.append("filho falso")

        self.assertEqual(raiz.quantidade_filhos(), 0)

    def test_nao_adiciona_estado_repetido_entre_os_filhos(self):
        estado = criar_estado_manual()
        raiz = NoEstado(estado)
        jogada = Jogada(TipoJogada.PASSE)
        estado_filho = ExecutorJogada().executar(estado, jogada)
        primeiro_filho = NoEstado(estado_filho, jogada, raiz)
        segundo_filho = NoEstado(estado_filho, jogada, raiz)

        self.assertTrue(raiz.adicionar_filho(primeiro_filho))
        self.assertFalse(raiz.adicionar_filho(segundo_filho))
        self.assertEqual(raiz.quantidade_filhos(), 1)

    def test_marca_e_desmarca_no_visitado(self):
        raiz = NoEstado(criar_estado_manual())

        raiz.marcar_como_visitado()
        self.assertTrue(raiz.esta_visitado())

        raiz.desmarcar_como_visitado()
        self.assertFalse(raiz.esta_visitado())

    def test_marca_no_como_expandido(self):
        raiz = NoEstado(criar_estado_manual())

        raiz.marcar_como_expandido()

        self.assertTrue(raiz.esta_expandido())

    def test_marca_jogada_voltada_e_limpa_ao_visitar_novamente(self):
        raiz = NoEstado(criar_estado_manual())

        raiz.marcar_como_jogada_voltada()

        self.assertFalse(raiz.esta_visitado())
        self.assertTrue(raiz.representa_jogada_voltada())

        raiz.marcar_como_visitado()

        self.assertTrue(raiz.esta_visitado())
        self.assertFalse(raiz.representa_jogada_voltada())

    def test_rejeita_configuracoes_invalidas(self):
        estado = criar_estado_manual()
        raiz = NoEstado(estado)
        jogada = Jogada(TipoJogada.PASSE)

        with self.assertRaises(TypeError):
            NoEstado("estado")

        with self.assertRaises(TypeError):
            NoEstado(estado, pai="pai")

        with self.assertRaises(TypeError):
            NoEstado(estado, jogada_origem="jogada")

        with self.assertRaises(ValueError):
            NoEstado(estado, jogada_origem=jogada)

        with self.assertRaises(ValueError):
            NoEstado(estado, pai=raiz)

    def test_rejeita_filho_com_outro_pai(self):
        estado = criar_estado_manual()
        primeira_raiz = NoEstado(estado)
        segunda_raiz = NoEstado(estado)
        jogada = Jogada(TipoJogada.PASSE)
        estado_filho = ExecutorJogada().executar(estado, jogada)
        filho = NoEstado(estado_filho, jogada, primeira_raiz)

        with self.assertRaises(TypeError):
            primeira_raiz.adicionar_filho("filho")

        with self.assertRaises(ValueError):
            segunda_raiz.adicionar_filho(filho)


if __name__ == "__main__":
    unittest.main()
