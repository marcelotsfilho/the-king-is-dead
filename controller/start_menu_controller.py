import os

import pygame


ACAO_NOVO_JOGO = "novo_jogo"
ACAO_CONTINUAR_JOGO = "continuar_jogo"
ACAO_SAIR = "sair"
QUADROS_POR_SEGUNDO = 60


class ControladorMenuInicial:
    """Controla as escolhas feitas na tela inicial."""

    def __init__(self, visao, caminho_salvamento):
        self.visao = visao
        self.caminho_salvamento = caminho_salvamento
        self.relogio = pygame.time.Clock()

    def existe_jogo_salvo(self):
        return os.path.isfile(self.caminho_salvamento)

    def executar(self, mensagem=""):
        """Exibe o menu até o jogador escolher uma opção."""
        while True:
            salvamento_disponivel = self.existe_jogo_salvo()
            self.visao.desenhar_menu_inicial(
                salvamento_disponivel,
                mensagem,
            )

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return ACAO_SAIR

                if (
                    evento.type == pygame.MOUSEBUTTONDOWN
                    and evento.button == 1
                ):
                    acao = self.visao.obter_acao_menu_inicial(
                        evento.pos,
                        salvamento_disponivel,
                    )

                    if acao is not None:
                        return acao

            self.relogio.tick(QUADROS_POR_SEGUNDO)
