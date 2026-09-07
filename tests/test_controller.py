import unittest

from controller.game_controller import ControladorJogo
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo


class VisaoFalsa:
    """Substitui a janela para testar o Controller sem interação manual."""

    def botao_cancelar_foi_clicado(self, posicao):
        return posicao == "cancelar"

    def botao_sem_efeito_foi_clicado(self, posicao):
        return posicao == "sem_efeito"

    def botao_passar_foi_clicado(self, posicao, estado):
        return posicao == "passar"

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


def criar_controlador():
    estado = ConfiguracaoJogo(42).criar_estado_inicial(["Ana", "Bruno"])
    return ControladorJogo(Jogo(estado), VisaoFalsa())


class TesteControladorJogo(unittest.TestCase):
    def test_clique_em_passar_chama_o_model_e_alterna_jogador(self):
        controlador = criar_controlador()

        controlador._processar_clique("passar")

        atual = controlador.jogo.estado.obter_jogador_atual()
        self.assertEqual(atual.nome, "Bruno")

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

    def test_cancelar_limpa_uma_carta_selecionada(self):
        controlador = criar_controlador()

        controlador._processar_clique(0)
        controlador._processar_clique("cancelar")

        self.assertIsNone(controlador.carta_selecionada)


if __name__ == "__main__":
    unittest.main()
