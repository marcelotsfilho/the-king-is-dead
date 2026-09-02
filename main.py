import pygame

from controller.game_controller import ControladorJogo
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from view.game_view import VisaoJogo


def principal():
    """Monta as camadas MVC e inicia a aplicação."""
    pygame.init()

    configuracao = ConfiguracaoJogo()
    estado = configuracao.criar_estado_inicial(["Jogador 1", "Jogador 2"])
    jogo = Jogo(estado)
    visao = VisaoJogo()
    controlador = ControladorJogo(jogo, visao)
    controlador.executar()

    pygame.quit()


if __name__ == "__main__":
    principal()
