import pygame


QUADROS_POR_SEGUNDO = 60


class ControladorJogo:
    """Coordena eventos, atualização e desenho da aplicação."""

    def __init__(self, visao):
        self.visao = visao
        self.relogio = pygame.time.Clock()
        self.executando = True

    def executar(self):
        """Mantém o loop principal ativo até o fechamento da janela."""
        while self.executando:
            self._processar_eventos()
            self.visao.desenhar()
            self.relogio.tick(QUADROS_POR_SEGUNDO)

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False
