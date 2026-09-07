import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


def criar_jogo_para_acoes(quantidade_reserva=10):
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    reserva = ReservaSeguidores(quantidade_reserva)
    estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)
    return Jogo(estado)


def entregar_carta(jogo, tipo):
    carta = CartaAcao(tipo)
    jogo.estado.obter_jogador_atual().adicionar_carta_mao(carta)
    return carta


class TesteFluxoDasAcoes(unittest.TestCase):
    def test_carta_usada_vai_para_descarte_e_exige_convocacao(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.REUNIR)

        jogo.jogar_carta(
            carta,
            {
                "destinos": {
                    Faccao.ESCOCESES: "Moray",
                    Faccao.GALESES: "Gwynedd",
                    Faccao.INGLESES: "Essex",
                }
            },
        )

        jogador = jogo.estado.obter_jogador_atual()
        self.assertFalse(jogador.possui_carta(carta))
        self.assertIn(carta, jogador.obter_descarte_mao())
        self.assertEqual(jogo.estado.fase_turno, FaseTurno.CONVOCAR_SEGUIDOR)

    def test_nao_permite_passar_antes_da_convocacao(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        jogo.estado.trilha_disputas.obter_carta(2).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(3).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(4).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(5).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(6).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(7).virar_para_baixo()
        jogo.estado.trilha_disputas.obter_carta(8).virar_para_baixo()

        jogo.jogar_carta(carta)

        with self.assertRaises(ValueError):
            jogo.passar()

    def test_convocacao_move_seguidor_para_corte_e_avanca_turno(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        for posicao in range(2, 9):
            jogo.estado.trilha_disputas.obter_carta(posicao).virar_para_baixo()

        jogo.jogar_carta(carta)
        jogo.convocar_seguidor("Moray", Faccao.ESCOCESES)

        ana = jogo.estado.obter_jogadores()[0]
        self.assertEqual(moray.quantidade_de_seguidores(Faccao.ESCOCESES), 0)
        self.assertEqual(ana.qtd_na_corte(Faccao.ESCOCESES), 1)
        self.assertEqual(jogo.estado.obter_jogador_atual().nome, "Bruno")
        self.assertEqual(jogo.estado.fase_turno, FaseTurno.ESCOLHER_ACAO)

    def test_rejeita_carta_que_nao_pertence_ao_jogador(self):
        jogo = criar_jogo_para_acoes()
        carta = CartaAcao(TipoCartaAcao.REUNIR)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(carta)

    def test_jogada_cancela_passes_consecutivos(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.passes_consecutivos = 1
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        for posicao in range(2, 9):
            jogo.estado.trilha_disputas.obter_carta(posicao).virar_para_baixo()

        jogo.jogar_carta(carta)

        self.assertEqual(jogo.estado.passes_consecutivos, 0)

    def test_acao_e_convocacao_conservam_dezesseis_por_faccao(self):
        estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
        jogo = Jogo(estado)
        jogador = estado.obter_jogador_atual()
        carta = None

        for carta_da_mao in jogador.obter_mao():
            if carta_da_mao.tipo == TipoCartaAcao.APOIO_ESCOCES:
                carta = carta_da_mao
                break

        regiao_apoio = jogo.obter_regioes_validas_para_apoio(carta.tipo)[0]
        jogo.jogar_carta(carta, {"regiao": regiao_apoio})

        regiao_convocacao = None
        faccao_convocada = None
        for nome in estado.tabuleiro.obter_nomes_das_regioes():
            regiao = estado.tabuleiro.obter_regiao(nome)
            for faccao in Faccao:
                if regiao.quantidade_de_seguidores(faccao) > 0:
                    regiao_convocacao = nome
                    faccao_convocada = faccao
                    break
            if regiao_convocacao is not None:
                break

        jogo.convocar_seguidor(regiao_convocacao, faccao_convocada)

        for faccao in Faccao:
            total = estado.reserva.quantidade(faccao)
            for regiao in estado.tabuleiro.obter_regioes().values():
                total += regiao.quantidade_de_seguidores(faccao)
            for participante in estado.obter_jogadores():
                total += participante.qtd_na_corte(faccao)
            self.assertEqual(total, 16)


class TesteAssemble(unittest.TestCase):
    def test_coloca_um_seguidor_de_cada_faccao(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.REUNIR)

        jogo.jogar_carta(
            carta,
            {
                "destinos": {
                    Faccao.ESCOCESES: "Moray",
                    Faccao.GALESES: "Moray",
                    Faccao.INGLESES: "Essex",
                }
            },
        )

        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        self.assertEqual(moray.quantidade_de_seguidores(Faccao.ESCOCESES), 1)
        self.assertEqual(moray.quantidade_de_seguidores(Faccao.GALESES), 1)
        self.assertEqual(
            jogo.estado.tabuleiro.obter_regiao("Essex").quantidade_de_seguidores(
                Faccao.INGLESES
            ),
            1,
        )

    def test_ignora_faccao_ausente_da_reserva(self):
        jogo = criar_jogo_para_acoes(1)
        jogo.estado.reserva.retirar(Faccao.GALESES)
        carta = entregar_carta(jogo, TipoCartaAcao.REUNIR)

        jogo.jogar_carta(
            carta,
            {
                "destinos": {
                    Faccao.ESCOCESES: "Moray",
                    Faccao.INGLESES: "Essex",
                }
            },
        )

        self.assertEqual(
            jogo.estado.tabuleiro.obter_regiao("Moray").quantidade_de_seguidores(
                Faccao.ESCOCESES
            ),
            1,
        )
        self.assertEqual(
            jogo.estado.tabuleiro.obter_regiao("Gwynedd").quantidade_de_seguidores(
                Faccao.GALESES
            ),
            0,
        )

    def test_rejeita_regiao_ja_resolvida(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").definir_controlador(
            Faccao.ESCOCESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.REUNIR)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta,
                {
                    "destinos": {
                        Faccao.ESCOCESES: "Moray",
                        Faccao.GALESES: "Gwynedd",
                        Faccao.INGLESES: "Essex",
                    }
                },
            )


class TesteSupport(unittest.TestCase):
    def test_apoio_coloca_dois_em_regiao_vizinha_da_origem(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.APOIO_ESCOCES)

        jogo.jogar_carta(carta, {"regiao": "Strathclyde"})

        regiao = jogo.estado.tabuleiro.obter_regiao("Strathclyde")
        self.assertEqual(regiao.quantidade_de_seguidores(Faccao.ESCOCESES), 2)

    def test_apoio_coloca_apenas_o_que_restou_na_reserva(self):
        jogo = criar_jogo_para_acoes(1)
        carta = entregar_carta(jogo, TipoCartaAcao.APOIO_GALES)

        jogo.jogar_carta(carta, {"regiao": "Lancaster"})

        regiao = jogo.estado.tabuleiro.obter_regiao("Lancaster")
        self.assertEqual(regiao.quantidade_de_seguidores(Faccao.GALESES), 1)

    def test_apoio_pode_partir_de_regiao_controlada(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").marcar_como_instavel()
        jogo.estado.tabuleiro.obter_regiao("Warwick").definir_controlador(
            Faccao.ESCOCESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.APOIO_ESCOCES)

        jogo.jogar_carta(carta, {"regiao": "Devon"})

        self.assertEqual(
            jogo.estado.tabuleiro.obter_regiao("Devon").quantidade_de_seguidores(
                Faccao.ESCOCESES
            ),
            2,
        )

    def test_apoio_rejeita_regiao_sem_fronteira_valida(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.APOIO_ESCOCES)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(carta, {"regiao": "Devon"})


class TesteNegotiate(unittest.TestCase):
    def test_troca_cartas_coloca_disco_e_consumo_o_recurso(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        nome_primeira = jogo.estado.trilha_disputas.obter_carta(1).nome_regiao
        nome_segunda = jogo.estado.trilha_disputas.obter_carta(2).nome_regiao
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )

        jogo.jogar_carta(
            carta,
            {"posicao_a": 1, "posicao_b": 2, "posicao_disco": 1},
        )

        trilha = jogo.estado.trilha_disputas
        self.assertEqual(trilha.obter_carta(1).nome_regiao, nome_segunda)
        self.assertEqual(trilha.obter_carta(2).nome_regiao, nome_primeira)
        self.assertTrue(trilha.obter_carta(2).possui_disco_negociacao)
        self.assertFalse(
            jogo.estado.obter_jogador_atual().disco_negociacao_disponivel
        )

    def test_nao_permite_trocar_carta_virada_para_baixo(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        jogo.estado.trilha_disputas.obter_carta(1).virar_para_baixo()

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta,
                {"posicao_a": 1, "posicao_b": 2, "posicao_disco": 1},
            )

    def test_sem_duas_cartas_validas_a_acao_nao_tem_efeito(self):
        jogo = criar_jogo_para_acoes()
        carta = entregar_carta(jogo, TipoCartaAcao.NEGOCIAR)
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        for posicao in range(2, 9):
            jogo.estado.trilha_disputas.obter_carta(posicao).virar_para_baixo()

        jogo.jogar_carta(carta)

        detalhes = jogo.estado.historico_acoes[-1]["detalhes"]
        self.assertTrue(detalhes["sem_efeito"])


class TesteManoeuvre(unittest.TestCase):
    def test_troca_um_seguidor_entre_duas_regioes(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogo.estado.tabuleiro.obter_regiao("Devon").adicionar_seguidores(
            Faccao.GALESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.MANOBRAR)

        jogo.jogar_carta(
            carta,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Devon",
                "faccao_b": Faccao.GALESES,
            },
        )

        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        devon = jogo.estado.tabuleiro.obter_regiao("Devon")
        self.assertEqual(moray.quantidade_de_seguidores(Faccao.GALESES), 1)
        self.assertEqual(devon.quantidade_de_seguidores(Faccao.ESCOCESES), 1)

    def test_manobra_nao_exige_adjacencia(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        devon = jogo.estado.tabuleiro.obter_regiao("Devon")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        devon.adicionar_seguidores(Faccao.GALESES)
        carta = entregar_carta(jogo, TipoCartaAcao.MANOBRAR)

        jogo.jogar_carta(
            carta,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Devon",
                "faccao_b": Faccao.GALESES,
            },
        )

        self.assertEqual(devon.quantidade_de_seguidores(Faccao.ESCOCESES), 1)

    def test_sem_duas_regioes_ocupadas_a_acao_nao_tem_efeito(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        carta = entregar_carta(jogo, TipoCartaAcao.MANOBRAR)

        jogo.jogar_carta(carta)

        self.assertTrue(
            jogo.estado.historico_acoes[-1]["detalhes"]["sem_efeito"]
        )

    def test_adversario_nao_pode_desfazer_a_manobra_imediatamente(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        devon = jogo.estado.tabuleiro.obter_regiao("Devon")
        lancaster = jogo.estado.tabuleiro.obter_regiao("Lancaster")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        devon.adicionar_seguidores(Faccao.GALESES)
        lancaster.adicionar_seguidores(Faccao.INGLESES)
        carta_ana = entregar_carta(jogo, TipoCartaAcao.MANOBRAR)
        bruno = jogo.estado.obter_jogadores()[1]
        carta_bruno = CartaAcao(TipoCartaAcao.MANOBRAR)
        bruno.adicionar_carta_mao(carta_bruno)

        jogo.jogar_carta(
            carta_ana,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Devon",
                "faccao_b": Faccao.GALESES,
            },
        )
        jogo.convocar_seguidor("Lancaster", Faccao.INGLESES)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta_bruno,
                {
                    "regiao_a": "Moray",
                    "faccao_a": Faccao.GALESES,
                    "regiao_b": "Devon",
                    "faccao_b": Faccao.ESCOCESES,
                },
            )


class TesteOutmanoeuvre(unittest.TestCase):
    def test_troca_um_seguidor_por_dois_em_regiao_adjacente(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        strathclyde = jogo.estado.tabuleiro.obter_regiao("Strathclyde")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        strathclyde.adicionar_seguidores(Faccao.GALESES, 2)
        carta = entregar_carta(jogo, TipoCartaAcao.SUPERAR_MANOBRA)

        jogo.jogar_carta(
            carta,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Strathclyde",
                "faccao_b": Faccao.GALESES,
            },
        )

        self.assertEqual(moray.quantidade_de_seguidores(Faccao.GALESES), 2)
        self.assertEqual(
            strathclyde.quantidade_de_seguidores(Faccao.ESCOCESES), 1
        )

    def test_exige_uma_troca_completa_quando_ela_existe(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        strathclyde = jogo.estado.tabuleiro.obter_regiao("Strathclyde")
        northumbria = jogo.estado.tabuleiro.obter_regiao("Northumbria")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        strathclyde.adicionar_seguidores(Faccao.GALESES, 2)
        northumbria.adicionar_seguidores(Faccao.INGLESES)
        carta = entregar_carta(jogo, TipoCartaAcao.SUPERAR_MANOBRA)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta,
                {
                    "regiao_a": "Moray",
                    "faccao_a": Faccao.ESCOCESES,
                    "regiao_b": "Northumbria",
                    "faccao_b": Faccao.INGLESES,
                },
            )

    def test_faz_troca_parcial_quando_nao_existe_par_completo(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        strathclyde = jogo.estado.tabuleiro.obter_regiao("Strathclyde")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        strathclyde.adicionar_seguidores(Faccao.GALESES)
        carta = entregar_carta(jogo, TipoCartaAcao.SUPERAR_MANOBRA)

        jogo.jogar_carta(
            carta,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Strathclyde",
                "faccao_b": Faccao.GALESES,
            },
        )

        self.assertEqual(moray.quantidade_de_seguidores(Faccao.GALESES), 1)
        self.assertEqual(
            strathclyde.quantidade_de_seguidores(Faccao.ESCOCESES), 1
        )

    def test_rejeita_regioes_nao_adjacentes(self):
        jogo = criar_jogo_para_acoes()
        jogo.estado.tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogo.estado.tabuleiro.obter_regiao("Devon").adicionar_seguidores(
            Faccao.GALESES, 2
        )
        jogo.estado.tabuleiro.obter_regiao("Lancaster").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogo.estado.tabuleiro.obter_regiao("Warwick").adicionar_seguidores(
            Faccao.INGLESES, 2
        )
        carta = entregar_carta(jogo, TipoCartaAcao.SUPERAR_MANOBRA)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta,
                {
                    "regiao_a": "Moray",
                    "faccao_a": Faccao.ESCOCESES,
                    "regiao_b": "Devon",
                    "faccao_b": Faccao.GALESES,
                },
            )

    def test_adversario_nao_pode_desfazer_outmanoeuvre_imediatamente(self):
        jogo = criar_jogo_para_acoes()
        moray = jogo.estado.tabuleiro.obter_regiao("Moray")
        strathclyde = jogo.estado.tabuleiro.obter_regiao("Strathclyde")
        lancaster = jogo.estado.tabuleiro.obter_regiao("Lancaster")
        moray.adicionar_seguidores(Faccao.ESCOCESES)
        strathclyde.adicionar_seguidores(Faccao.GALESES, 2)
        lancaster.adicionar_seguidores(Faccao.INGLESES)
        carta_ana = entregar_carta(jogo, TipoCartaAcao.SUPERAR_MANOBRA)
        bruno = jogo.estado.obter_jogadores()[1]
        carta_bruno = CartaAcao(TipoCartaAcao.SUPERAR_MANOBRA)
        bruno.adicionar_carta_mao(carta_bruno)

        jogo.jogar_carta(
            carta_ana,
            {
                "regiao_a": "Moray",
                "faccao_a": Faccao.ESCOCESES,
                "regiao_b": "Strathclyde",
                "faccao_b": Faccao.GALESES,
            },
        )
        jogo.convocar_seguidor("Lancaster", Faccao.INGLESES)

        with self.assertRaises(ValueError):
            jogo.jogar_carta(
                carta_bruno,
                {
                    "regiao_a": "Strathclyde",
                    "faccao_a": Faccao.ESCOCESES,
                    "regiao_b": "Moray",
                    "faccao_b": Faccao.GALESES,
                },
            )


if __name__ == "__main__":
    unittest.main()
