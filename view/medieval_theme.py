from functools import lru_cache
from pathlib import Path

import pygame


FUNDO = (23, 32, 36)
TINTA = (50, 35, 23)
MARFIM = (248, 232, 195)
OURO = (232, 184, 99)
OURO_ESCURO = (138, 103, 57)

_PALETAS = {
    "vinho": ((132, 48, 37), (66, 22, 20), OURO),
    "couro": ((109, 70, 44), (56, 33, 24), OURO),
    "ardosia": ((65, 79, 82), (26, 37, 41), (171, 153, 118)),
    "inativo": ((63, 66, 64), (39, 43, 42), (138, 131, 109)),
    "escoceses": ((34, 96, 155), (16, 51, 87), OURO),
    "galeses": ((157, 49, 44), (84, 21, 23), OURO),
    "ingleses": ((157, 100, 21), (93, 55, 12), OURO),
}

_ASSETS = Path(__file__).with_name("assets")


class TemaMedieval:
    """Mantém as superfícies decorativas reutilizáveis entre quadros."""

    def __init__(self):
        self.arte = {
            nome: pygame.image.load(str(_ASSETS / f"{nome}.jpg")).convert()
            for nome in ("ambiente", "mapa", "pergaminho")
            if (_ASSETS / f"{nome}.jpg").is_file()
        }
        # Os caches pertencem à instância, para liberar as superfícies ao fechar a visão.
        self.ajustar_arte = lru_cache(maxsize=16)(self._ajustar_arte)
        self.placa = lru_cache(maxsize=48)(self._placa)
        self.relevo = lru_cache(maxsize=64)(self._relevo)

    def _ajustar_arte(self, nome, tamanho):
        imagem = self.arte.get("ambiente" if nome == "ardosia" else nome)
        if imagem is None:
            superficie = pygame.Surface(tamanho)
            cor = {
                "ambiente": FUNDO,
                "ardosia": FUNDO,
                "mapa": (53, 76, 69),
                "pergaminho": (237, 211, 160),
            }
            superficie.fill(cor[nome])
            return superficie
        if nome == "ardosia":
            largura, altura = imagem.get_size()
            imagem = imagem.subsurface((largura // 7, altura * 3 // 8,
                                         largura * 5 // 7, altura * 2 // 5))
        return pygame.transform.smoothscale(imagem, tamanho)

    def _placa(self, tamanho, tonalidade=None, escurecer=False, irregular=False):
        largura, altura = tamanho
        placa = self.ajustar_arte("pergaminho", tamanho).copy()
        if tonalidade is not None:
            tinta = pygame.Surface(tamanho, pygame.SRCALPHA)
            tinta.fill((*tonalidade, 54))
            placa.blit(tinta, (0, 0))
        if escurecer:
            sombra = pygame.Surface(tamanho, pygame.SRCALPHA)
            sombra.fill((50, 49, 46, 75))
            placa.blit(sombra, (0, 0))

        mascara = pygame.Surface(tamanho, pygame.SRCALPHA)
        if irregular:
            contorno = (
                (8, 10), (23, 5), (43, 7), (63, 1), (90, 4), (115, 2),
                (132, 7), (158, 4), (largura - 12, 11), (largura - 4, 23),
                (largura - 6, 40), (largura - 1, 60), (largura - 5, 81),
                (largura - 3, 101), (largura - 11, altura - 10),
                (largura - 30, altura - 4), (largura - 54, altura - 6),
                (106, altura - 1), (81, altura - 4), (54, altura - 2),
                (32, altura - 7), (15, altura - 6), (5, altura - 19),
                (7, 92), (2, 74), (5, 55), (1, 34),
            )
            pygame.draw.polygon(mascara, (255, 255, 255), contorno)
        else:
            pygame.draw.rect(mascara, (255, 255, 255), mascara.get_rect(), border_radius=9)
        mascara.blit(placa, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if irregular:
            pygame.draw.lines(mascara, MARFIM, True, contorno, 3)
        return mascara

    def _relevo(self, tamanho, estilo, realce):
        largura, altura = tamanho
        claro, escuro, borda = _PALETAS[estilo]
        if realce:
            claro = tuple(min(255, canal + 28) for canal in claro)
            escuro = tuple(min(255, canal + 17) for canal in escuro)
            borda = MARFIM
        faixa = pygame.Surface((1, altura))
        for y in range(altura):
            proporcao = y / max(1, altura - 1)
            cor = tuple(round(a + (b - a) * proporcao) for a, b in zip(claro, escuro))
            faixa.set_at((0, y), cor)
        superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
        caixa = superficie.get_rect()
        raio = min(14, altura // 4)
        pygame.draw.rect(superficie, (255, 255, 255), caixa, border_radius=raio)
        superficie.blit(pygame.transform.scale(faixa, (largura, altura)), (0, 0),
                        special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(superficie, borda, caixa, 2, border_radius=raio)
        pygame.draw.rect(superficie, claro, caixa.inflate(-8, -8), 1, border_radius=raio - 2)
        return superficie
