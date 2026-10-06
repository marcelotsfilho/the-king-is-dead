import json
import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


def criar_estado_manual():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(5)
    return EstadoJogo(tabuleiro, trilha, jogadores, reserva)


class TesteSerializadorEstadoJogo(unittest.TestCase):
    def setUp(self):
        self.serializador = SerializadorEstadoJogo()

    def test_estado_inicial_pode_ser_serializado_e_restaurado(self):
        estado = ConfiguracaoJogo(semente=10).criar_estado_inicial(
            ["Ana", "Bruno"]
        )

        dados = self.serializador.serializar(estado)
        restaurado = self.serializador.restaurar(dados)

        self.assertEqual(dados, self.serializador.serializar(restaurado))

    def test_dados_serializados_possuem_apenas_valores_simples(self):
        estado = ConfiguracaoJogo(semente=10).criar_estado_inicial(
            ["Ana", "Bruno"]
        )

        dados = self.serializador.serializar(estado)

        texto_json = json.dumps(dados, ensure_ascii=False)
        self.assertIn('"jogadores"', texto_json)
        self.assertNotIn("disputas_resolvidas", dados)
        self.assertNotIn("quantidade_instabilidades", dados)

    def test_copia_nao_compartilha_objetos_com_estado_original(self):
        estado = ConfiguracaoJogo(semente=10).criar_estado_inicial(
            ["Ana", "Bruno"]
        )

        copia = self.serializador.copiar(estado)
        Jogo(copia).passar()

        self.assertEqual(estado.passes_consecutivos, 0)
        self.assertEqual(copia.passes_consecutivos, 1)
        self.assertEqual(estado.indice_jogador_atual, 0)
        self.assertEqual(copia.indice_jogador_atual, 1)

    def test_restaura_carta_em_execucao_e_ultima_acao_de_manobra(self):
        estado = criar_estado_manual()
        jogo = Jogo(estado)
        moray = estado.tabuleiro.obter_regiao("Moray")
        devon = estado.tabuleiro.obter_regiao("Devon")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        devon.adicionar_seguidores(Faccao.GALESES)
        carta = CartaAcao(TipoCartaAcao.MANOBRAR)
        estado.obter_jogador_atual().adicionar_carta_mao(carta)

        jogo.jogar_carta(
            carta,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Devon",
                "faccao_b": Faccao.GALESES,
            },
        )
        restaurado = self.serializador.copiar(estado)

        self.assertEqual(restaurado.fase_turno, FaseTurno.CONVOCAR_SEGUIDOR)
        self.assertEqual(
            restaurado.carta_em_execucao.tipo,
            TipoCartaAcao.MANOBRAR,
        )
        detalhes = restaurado.ultima_acao["detalhes"]
        self.assertEqual(detalhes["faccao_a"], Faccao.ESCOCESES)
        self.assertEqual(detalhes["faccao_b"], Faccao.GALESES)

        Jogo(restaurado).convocar_seguidor("Moray", Faccao.GALESES)
        self.assertEqual(restaurado.fase_turno, FaseTurno.ESCOLHER_ACAO)

    def test_restaura_regiao_resolvida_e_carta_da_trilha(self):
        estado = criar_estado_manual()
        moray = estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES, 2)
        moray.adicionar_seguidores(Faccao.GALESES)
        primeira_carta = estado.trilha_disputas.obter_carta(1)
        primeira_carta.colocar_disco_negociacao()

        Jogo(estado).resolver_proxima_disputa()
        restaurado = self.serializador.copiar(estado)
        moray_restaurada = restaurado.tabuleiro.obter_regiao("Moray")
        carta_restaurada = restaurado.trilha_disputas.obter_carta(1)

        self.assertEqual(moray_restaurada.controlador, Faccao.ESCOCESES)
        self.assertFalse(carta_restaurada.virada_para_cima)
        self.assertTrue(carta_restaurada.possui_disco_negociacao)
        self.assertEqual(
            self.serializador.serializar(estado),
            self.serializador.serializar(restaurado),
        )

    def test_restaura_referencias_de_jogadores_e_resultado_final(self):
        estado = criar_estado_manual()
        jogadores = estado.obter_jogadores()
        estado.ultimo_jogador_que_agiu = jogadores[1]
        estado.ordem_jogadores_sem_cartas = [jogadores[1], jogadores[0]]
        estado.historico_vitorias_faccoes = [
            Faccao.GALESES,
            Faccao.ESCOCESES,
        ]
        estado.fase_turno = FaseTurno.ENCERRADO
        estado.finalizado = True
        estado.vencedor = jogadores[0]
        estado.faccao_vencedora = Faccao.GALESES
        estado.motivo_encerramento = "Coroação"

        restaurado = self.serializador.copiar(estado)
        jogadores_restaurados = restaurado.obter_jogadores()

        self.assertIs(
            restaurado.ultimo_jogador_que_agiu,
            jogadores_restaurados[1],
        )
        self.assertIs(
            restaurado.ordem_jogadores_sem_cartas[0],
            jogadores_restaurados[1],
        )
        self.assertIs(restaurado.vencedor, jogadores_restaurados[0])
        self.assertEqual(restaurado.faccao_vencedora, Faccao.GALESES)
        self.assertEqual(restaurado.fase_turno, FaseTurno.ENCERRADO)

    def test_restaura_destinos_de_assemble_com_chaves_de_faccao(self):
        estado = criar_estado_manual()
        jogador = estado.obter_jogador_atual()
        estado.ultima_acao = {
            "jogador": jogador,
            "tipo": TipoCartaAcao.REUNIR,
            "detalhes": {
                "destinos": {
                    Faccao.ESCOCESES: "Moray",
                    Faccao.GALESES: "Gwynedd",
                    Faccao.INGLESES: "Essex",
                }
            },
            "convocacao": {
                "regiao": "Moray",
                "faccao": Faccao.ESCOCESES,
            },
        }

        restaurado = self.serializador.copiar(estado)
        acao = restaurado.ultima_acao

        self.assertEqual(
            acao["detalhes"]["destinos"][Faccao.GALESES],
            "Gwynedd",
        )
        self.assertEqual(acao["convocacao"]["faccao"], Faccao.ESCOCESES)

    def test_rejeita_versao_desconhecida(self):
        estado = ConfiguracaoJogo(semente=10).criar_estado_inicial(
            ["Ana", "Bruno"]
        )
        dados = self.serializador.serializar(estado)
        dados["versao"] = 999

        with self.assertRaises(ValueError):
            self.serializador.restaurar(dados)


if __name__ == "__main__":
    unittest.main()
