import pygame


LARGURA_JANELA = 800
ALTURA_JANELA = 600
TITULO_JANELA = "The King is Dead"
COR_DE_FUNDO = (230, 217, 191)
QUADROS_POR_SEGUNDO = 60


def principal() -> None:
    """Inicializa e mantém a primeira janela do jogo aberta."""
    pygame.init()

    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption(TITULO_JANELA)
    relogio = pygame.time.Clock()

    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

        tela.fill(COR_DE_FUNDO)
        pygame.display.flip()
        relogio.tick(QUADROS_POR_SEGUNDO)

    pygame.quit()


if __name__ == "__main__":
    principal()
