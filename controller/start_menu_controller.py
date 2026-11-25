import os

import pygame

from model.enums import TipoJogador
from model.match_settings import (
    LIMITES_TEMPO_BUSCA,
    SIMULACOES_MONTE_CARLO_DISPONIVEIS,
    TIPOS_COM_LIMITE_DE_TEMPO,
    ConfiguracaoPartida,
)


ACAO_NOVO_JOGO = "novo_jogo"
ACAO_CONTINUAR_JOGO = "continuar_jogo"
ACAO_SAIR = "sair"
QUADROS_POR_SEGUNDO = 60


class ControladorMenuInicial:
    """Controla as escolhas feitas na tela inicial."""

    def __init__(self, visao, caminho_salvamento, configuracao_partida=None):
        self.visao = visao
        self.caminho_salvamento = caminho_salvamento
        if configuracao_partida is None:
            configuracao_partida = ConfiguracaoPartida()
        self.configuracao_partida = configuracao_partida
        self.relogio = pygame.time.Clock()

    def existe_jogo_salvo(self):
        return os.path.isfile(self.caminho_salvamento)

    def _alterar_configuracao(self, acao, indice, configuracao=None):
        """Altera somente a escolha do jogador indicado pelo clique."""
        if configuracao is None:
            configuracao = self.configuracao_partida

        if acao == "tipo":
            tipos = list(TipoJogador)
            tipo_atual = configuracao.obter_tipo_jogador(indice)
            proxima_posicao = tipos.index(tipo_atual) + 1
            if proxima_posicao == len(tipos):
                proxima_posicao = 0
            configuracao.definir_tipo_jogador(indice, tipos[proxima_posicao])
            return

        tipo = configuracao.obter_tipo_jogador(indice)
        if acao == "tempo":
            if tipo in TIPOS_COM_LIMITE_DE_TEMPO:
                posicao = LIMITES_TEMPO_BUSCA.index(configuracao.obter_limite_tempo(indice))
                proximo = (posicao + 1) % len(LIMITES_TEMPO_BUSCA)
                configuracao.definir_limite_tempo(indice, LIMITES_TEMPO_BUSCA[proximo])
            return

        if tipo in (TipoJogador.HUMANO, TipoJogador.Q_LEARNING):
            return

        if tipo == TipoJogador.MONTE_CARLO:
            opcoes = SIMULACOES_MONTE_CARLO_DISPONIVEIS
            atual = configuracao.obter_simulacoes_monte_carlo(indice)
            posicao = opcoes.index(atual)
            if acao == "aumentar" and posicao < len(opcoes) - 1:
                configuracao.definir_simulacoes_monte_carlo(indice, opcoes[posicao + 1])
            elif acao == "diminuir" and posicao > 0:
                configuracao.definir_simulacoes_monte_carlo(indice, opcoes[posicao - 1])
            return

        profundidade = configuracao.obter_profundidade(indice)
        if acao == "aumentar":
            configuracao.definir_profundidade(indice, profundidade + 1)
        elif acao == "diminuir" and profundidade > 1:
            configuracao.definir_profundidade(indice, profundidade - 1)

    def executar(self, mensagem=""):
        """Exibe o menu até o jogador escolher uma opção."""
        configuracao_em_edicao = None
        while True:
            salvamento_disponivel = self.existe_jogo_salvo()
            if configuracao_em_edicao is None:
                self.visao.desenhar_menu_inicial(
                    salvamento_disponivel, mensagem,
                )
            else:
                self.visao.desenhar_tela_configuracao(configuracao_em_edicao)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return ACAO_SAIR

                if (
                    evento.type == pygame.MOUSEBUTTONDOWN
                    and evento.button == 1
                ):
                    if configuracao_em_edicao is not None:
                        controle = self.visao.obter_acao_configuracao(evento.pos)
                        if controle is not None:
                            acao, indice = controle
                            self._alterar_configuracao(
                                acao, indice, configuracao_em_edicao
                            )
                            continue

                        acao = self.visao.obter_acao_tela_configuracao(evento.pos)
                        if acao == "voltar":
                            configuracao_em_edicao = None
                        elif acao == "iniciar":
                            for indice in range(2):
                                self.configuracao_partida.definir_tipo_jogador(
                                    indice,
                                    configuracao_em_edicao.obter_tipo_jogador(indice),
                                )
                                self.configuracao_partida.definir_profundidade(
                                    indice,
                                    configuracao_em_edicao.obter_profundidade(indice),
                                )
                                self.configuracao_partida.definir_simulacoes_monte_carlo(
                                    indice,
                                    configuracao_em_edicao.obter_simulacoes_monte_carlo(indice),
                                )
                                self.configuracao_partida.definir_limite_tempo(
                                    indice, configuracao_em_edicao.obter_limite_tempo(indice)
                                )
                            return ACAO_NOVO_JOGO
                        continue

                    acao = self.visao.obter_acao_menu_inicial(
                        evento.pos,
                        salvamento_disponivel,
                    )

                    if acao == ACAO_NOVO_JOGO:
                        configuracao_em_edicao = ConfiguracaoPartida()
                    elif acao is not None:
                        return acao

            self.relogio.tick(QUADROS_POR_SEGUNDO)
