import pygame

from view.constants import (
    ALTURA_JANELA,
    COR_DE_FUNDO,
    LARGURA_JANELA,
    TITULO_JANELA,
)


class VisaoJogo:
    """Cria a janela e desenha o estado visual da aplicação."""

    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JANELA)

    def desenhar(self):
        """Desenha e apresenta um quadro da aplicação."""
        self.tela.fill(COR_DE_FUNDO)
        pygame.display.flip()
