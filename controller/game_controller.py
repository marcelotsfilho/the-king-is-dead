import pygame


QUADROS_POR_SEGUNDO = 60


class ControladorJogo:
    """Coordena eventos, atualização e desenho da aplicação."""

    def __init__(self, jogo, visao):
        self.jogo = jogo
        self.visao = visao
        self.relogio = pygame.time.Clock()
        self.executando = True

    def executar(self):
        """Mantém o loop principal ativo até o fechamento da janela."""
        while self.executando:
            self._processar_eventos()
            self.visao.desenhar(self.jogo.estado)
            self.relogio.tick(QUADROS_POR_SEGUNDO)

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clicou_em_passar = self.visao.botao_passar_foi_clicado(
                    evento.pos,
                    self.jogo.estado,
                )

                if clicou_em_passar:
                    self.jogo.passar()
