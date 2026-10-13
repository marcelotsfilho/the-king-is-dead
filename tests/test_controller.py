import os
import tempfile
import unittest

from controller.game_controller import ControladorJogo
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.state_tree_serializer import SerializadorArvoreEstados


class VisaoFalsa:
    """Substitui a janela para testar o Controller sem interação manual."""

    def desenhar(self, *argumentos):
        pass

    def botao_cancelar_foi_clicado(self, posicao):
        return posicao == "cancelar"

    def botao_sem_efeito_foi_clicado(self, posicao):
        return posicao == "sem_efeito"

    def botao_passar_foi_clicado(self, posicao, estado):
        return posicao == "passar"

    def botao_arvore_foi_clicado(self, posicao):
        return posicao == "arvore"

    def botao_salvar_foi_clicado(self, posicao):
        return posicao == "salvar"

    def botao_voltar_jogada_foi_clicado(self, posicao):
        return posicao == "voltar"

    def botao_fechar_arvore_foi_clicado(self, posicao):
        return posicao == "fechar_arvore"

    def botao_exportar_graphviz_foi_clicado(self, posicao):
        return posicao == "graphviz"

    def botao_gerar_opcoes_foi_clicado(self, posicao):
        return posicao == "gerar_opcoes"

    def botao_pagina_anterior_foi_clicado(self, posicao):
        return posicao == "pagina_anterior"

    def botao_proxima_pagina_foi_clicado(self, posicao):
        return posicao == "proxima_pagina"

    def obter_quantidade_paginas_arvore(self, arvore):
        return 1

    def obter_indice_carta_clicada(self, posicao, estado):
        if isinstance(posicao, int):
            return posicao
        return None

    def obter_nome_regiao_clicada(self, posicao):
        nomes = [
            "Moray",
            "Strathclyde",
            "Northumbria",
            "Lancaster",
            "Gwynedd",
            "Warwick",
            "Essex",
            "Devon",
        ]
        if posicao in nomes:
            return posicao
        return None

    def obter_posicao_trilha_clicada(self, posicao):
        if isinstance(posicao, tuple) and posicao[0] == "trilha":
            return posicao[1]
        return None

    def obter_faccao_clicada(self, posicao):
        if isinstance(posicao, Faccao):
            return posicao
        return None


def criar_controlador(caminho_salvamento=None):
    estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
    return ControladorJogo(
        Jogo(estado),
        VisaoFalsa(),
        caminho_salvamento=caminho_salvamento,
    )


class TesteControladorJogo(unittest.TestCase):
    def test_clique_na_carta_mostra_efeito_e_proximo_passo(self):
        controlador = criar_controlador()
        carta = (
            controlador.jogo.estado
            .obter_jogador_atual()
            .obter_mao()[0]
        )

        controlador._processar_clique(0)

        self.assertIn("Carta: " + carta.nome, controlador.instrucao)
        self.assertIn(carta.descricao, controlador.instrucao)
        self.assertIn("Próximo passo:", controlador.instrucao)

    def test_clique_em_passar_chama_o_model_e_alterna_jogador(self):
        controlador = criar_controlador()

        controlador._processar_clique("passar")

        atual = controlador.jogo.estado.obter_jogador_atual()
        self.assertEqual(atual.nome, "Bruno")
        self.assertEqual(
            controlador.arvore.obter_no_atual().obter_nivel(),
            1,
        )
        self.assertTrue(
            controlador.arvore.obter_no_atual()
            .obter_jogada_origem()
            .eh_passe()
        )

    def test_fluxo_de_assemble_chega_a_convocacao(self):
        controlador = criar_controlador()
        mao = controlador.jogo.estado.obter_jogador_atual().obter_mao()
        indice_assemble = None

        for indice in range(len(mao)):
            if mao[indice].tipo == TipoCartaAcao.REUNIR:
                indice_assemble = indice
                break

        controlador._processar_clique(indice_assemble)
        controlador._processar_clique("Moray")
        controlador._processar_clique("Gwynedd")
        controlador._processar_clique("Essex")

        self.assertEqual(
            controlador.jogo.estado.fase_turno,
            FaseTurno.CONVOCAR_SEGUIDOR,
        )

        regiao_escolhida = None
        faccao_escolhida = None
        tabuleiro = controlador.jogo.estado.tabuleiro

        for nome in tabuleiro.obter_nomes_das_regioes():
            regiao = tabuleiro.obter_regiao(nome)
            for faccao in Faccao:
                if regiao.quantidade_de_seguidores(faccao) > 0:
                    regiao_escolhida = nome
                    faccao_escolhida = faccao
                    break
            if regiao_escolhida is not None:
                break

        controlador._processar_clique(regiao_escolhida)
        controlador._processar_clique(faccao_escolhida)

        self.assertEqual(
            controlador.jogo.estado.fase_turno,
            FaseTurno.ESCOLHER_ACAO,
        )
        self.assertEqual(
            controlador.jogo.estado.obter_jogador_atual().nome,
            "Bruno",
        )
        no_atual = controlador.arvore.obter_no_atual()
        self.assertEqual(no_atual.obter_nivel(), 1)
        self.assertTrue(no_atual.obter_jogada_origem().eh_carta())

    def test_cancelar_limpa_uma_carta_selecionada(self):
        controlador = criar_controlador()

        controlador._processar_clique(0)
        controlador._processar_clique("cancelar")

        self.assertIsNone(controlador.carta_selecionada)

    def test_voltar_jogada_restaura_estado_anterior(self):
        controlador = criar_controlador()
        controlador._processar_clique("passar")

        controlador._processar_clique("voltar")

        jogador_atual = controlador.jogo.estado.obter_jogador_atual()
        self.assertEqual(jogador_atual.nome, "Ana")
        self.assertTrue(
            controlador.arvore.obter_no_atual().eh_raiz()
        )
        self.assertEqual(
            controlador.instrucao,
            "A última jogada foi desfeita.",
        )

    def test_abre_e_fecha_visualizacao_da_arvore(self):
        controlador = criar_controlador()

        controlador._processar_clique("arvore")
        self.assertTrue(controlador.arvore_aberta)

        controlador._processar_clique("fechar_arvore")
        self.assertFalse(controlador.arvore_aberta)

    def test_botao_graphviz_exporta_a_arvore_completa(self):
        class VisualizadorGraphvizFalso:
            def __init__(self):
                self.arvore = None

            def exportar(self, arvore, caminho):
                self.arvore = arvore
                return caminho

        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "arvore.json")
            controlador = criar_controlador(caminho)
            visualizador = VisualizadorGraphvizFalso()
            controlador.visualizador_graphviz = visualizador

            controlador._processar_clique("arvore")
            controlador._processar_clique("graphviz")

        self.assertIs(visualizador.arvore, controlador.arvore)
        self.assertIn("Árvore aberta em", controlador.mensagem_arvore)

    def test_salva_arvore_para_carregamento_posterior(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "arvore.json")
            controlador = criar_controlador(caminho)
            controlador._processar_clique("passar")

            salvou = controlador._salvar_arvore()
            restaurada = SerializadorArvoreEstados().carregar(
                caminho
            )

        self.assertTrue(salvou)
        self.assertEqual(restaurada.quantidade_nos(), 2)
        self.assertEqual(
            restaurada.obter_no_atual().obter_nivel(),
            1,
        )

    def test_botao_salvar_grava_partida_e_mostra_confirmacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "arvore.json")
            controlador = criar_controlador(caminho)

            controlador._processar_clique("salvar")

            restaurada = SerializadorArvoreEstados().carregar(
                caminho
            )

        self.assertEqual(restaurada.quantidade_nos(), 1)
        self.assertEqual(
            controlador.instrucao,
            "Partida salva com sucesso.",
        )

    def test_fim_da_partida_salva_arvore_automaticamente(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "arvore_final.json")
            controlador = criar_controlador(caminho)

            for _ in range(16):
                if controlador.jogo.estado.finalizado:
                    break

                controlador._processar_clique("passar")

            restaurada = SerializadorArvoreEstados().carregar(
                caminho
            )

        self.assertTrue(controlador.jogo.estado.finalizado)
        self.assertTrue(
            restaurada.obter_estado_atual().finalizado
        )


if __name__ == "__main__":
    unittest.main()
