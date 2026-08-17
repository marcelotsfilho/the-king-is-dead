import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "The King is Dead"
BACKGROUND_COLOR = (30, 35, 45)
FRAMES_PER_SECOND = 60


def main() -> None:
    """Inicializa e mantém a primeira janela do jogo aberta."""
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        clock.tick(FRAMES_PER_SECOND)

    pygame.quit()


if __name__ == "__main__":
    main()
