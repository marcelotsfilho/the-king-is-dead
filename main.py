import pygame

from controller.game_controller import ControladorJogo
from view.game_view import VisaoJogo


def principal() -> None:
    """Monta as camadas MVC e inicia a aplicação."""
    pygame.init()

    visao = VisaoJogo()
    controlador = ControladorJogo(visao)
    controlador.executar()

    pygame.quit()


if __name__ == "__main__":
    principal()
