import pygame

from model.enums import Faccao
from view.constants import (
    ALTURA_JANELA,
    ALTURA_REGIAO,
    CORES_FACCOES,
    COR_BORDA,
    COR_BOTAO,
    COR_BOTAO_DESATIVADO,
    COR_BRANCA,
    COR_DE_FUNDO,
    COR_INSTABILIDADE,
    COR_PAINEL,
    COR_TEXTO,
    LARGURA_REGIAO,
    LARGURA_JANELA,
    POSICOES_REGIOES,
    TITULO_JANELA,
)


class VisaoJogo:
    """Cria a janela e desenha o estado visual da aplicação."""

    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.fonte_titulo = pygame.font.Font(None, 38)
        self.fonte_normal = pygame.font.Font(None, 26)
        self.fonte_pequena = pygame.font.Font(None, 21)
        self.retangulo_botao_passar = pygame.Rect(965, 690, 200, 60)

    def desenhar(self, estado):
        """Desenha e apresenta um quadro da aplicação."""
        self.tela.fill(COR_DE_FUNDO)
        self._desenhar_titulo()
        self._desenhar_regioes(estado)
        self._desenhar_painel_lateral(estado)
        self._desenhar_trilha(estado)
        self._desenhar_mensagem(estado)
        self._desenhar_botao_passar(estado)
        pygame.display.flip()

    def botao_passar_foi_clicado(self, posicao, estado):
        """Informa se o clique ocorreu no botão Passar ativo."""
        return (
            not estado.finalizado
            and self.retangulo_botao_passar.collidepoint(posicao)
        )

    def _desenhar_titulo(self):
        texto = self.fonte_titulo.render(TITULO_JANELA, True, COR_TEXTO)
        self.tela.blit(texto, (40, 35))

    def _desenhar_regioes(self, estado):
        for nome in POSICOES_REGIOES:
            regiao = estado.tabuleiro.obter_regiao(nome)
            self._desenhar_regiao(regiao, POSICOES_REGIOES[nome])

    def _desenhar_regiao(self, regiao, posicao):
        retangulo = pygame.Rect(
            posicao[0],
            posicao[1],
            LARGURA_REGIAO,
            ALTURA_REGIAO,
        )
        pygame.draw.rect(self.tela, COR_PAINEL, retangulo)

        cor_borda = COR_BORDA

        if regiao.instavel:
            cor_borda = COR_INSTABILIDADE
        elif regiao.controlador is not None:
            cor_borda = CORES_FACCOES[regiao.controlador.value]

        pygame.draw.rect(self.tela, cor_borda, retangulo, 4)
        self._desenhar_texto(regiao.nome, posicao[0] + 10, posicao[1] + 8)

        deslocamento = 38

        for faccao in Faccao:
            quantidade = regiao.quantidade_de_seguidores(faccao)
            texto = faccao.value.capitalize() + ": " + str(quantidade)
            cor = CORES_FACCOES[faccao.value]
            self._desenhar_texto(
                texto,
                posicao[0] + 10,
                posicao[1] + deslocamento,
                cor,
                pequena=True,
            )
            deslocamento += 22

        if regiao.instavel:
            situacao = "INSTÁVEL"
        elif regiao.controlador is not None:
            situacao = "Controle: " + regiao.controlador.value
        else:
            situacao = "Em disputa"

        self._desenhar_texto(
            situacao,
            posicao[0] + 10,
            posicao[1] + 108,
            pequena=True,
        )

    def _desenhar_painel_lateral(self, estado):
        painel = pygame.Rect(930, 30, 240, 620)
        pygame.draw.rect(self.tela, COR_PAINEL, painel)
        pygame.draw.rect(self.tela, COR_BORDA, painel, 3)

        jogador_atual = estado.obter_jogador_atual()
        self._desenhar_texto("Turno", 955, 55)
        self._desenhar_texto(jogador_atual.nome, 955, 85)
        self._desenhar_texto(
            "Passes: " + str(estado.passes_consecutivos),
            955,
            115,
            pequena=True,
        )

        self._desenhar_texto("Reserva", 955, 160)
        altura = 190

        for faccao in Faccao:
            quantidade = estado.reserva.quantidade(faccao)
            texto = faccao.value.capitalize() + ": " + str(quantidade)
            self._desenhar_texto(
                texto,
                955,
                altura,
                CORES_FACCOES[faccao.value],
                pequena=True,
            )
            altura += 25

        altura = 290

        for jogador in estado.obter_jogadores():
            self._desenhar_texto("Corte de " + jogador.nome, 955, altura)
            altura += 28

            for faccao in Faccao:
                quantidade = jogador.qtd_na_corte(faccao)
                texto = faccao.value.capitalize() + ": " + str(quantidade)
                self._desenhar_texto(
                    texto,
                    965,
                    altura,
                    CORES_FACCOES[faccao.value],
                    pequena=True,
                )
                altura += 22

            altura += 18

        self._desenhar_texto(
            "Disputas: " + str(estado.disputas_resolvidas) + "/8",
            955,
            545,
            pequena=True,
        )
        self._desenhar_texto(
            "Instabilidades: " + str(estado.quantidade_instabilidades) + "/3",
            955,
            570,
            pequena=True,
        )

        if estado.finalizado:
            self._desenhar_texto("PARTIDA ENCERRADA", 955, 610, COR_BOTAO)

    def _desenhar_trilha(self, estado):
        self._desenhar_texto("Ordem das disputas", 40, 455)
        cartas = estado.trilha_disputas.obter_cartas()
        posicao_x = 40
        numero = 1

        for carta in cartas:
            retangulo = pygame.Rect(posicao_x, 490, 102, 62)

            if carta.virada_para_cima:
                cor_carta = COR_PAINEL
            else:
                cor_carta = (175, 170, 160)

            pygame.draw.rect(self.tela, cor_carta, retangulo)
            pygame.draw.rect(self.tela, COR_BORDA, retangulo, 2)
            self._desenhar_texto(
                str(numero) + ".",
                posicao_x + 5,
                497,
                pequena=True,
            )
            self._desenhar_texto(
                carta.nome_regiao,
                posicao_x + 5,
                523,
                pequena=True,
            )
            posicao_x += 110
            numero += 1

    def _desenhar_mensagem(self, estado):
        caixa = pygame.Rect(40, 585, 850, 165)
        pygame.draw.rect(self.tela, COR_PAINEL, caixa)
        pygame.draw.rect(self.tela, COR_BORDA, caixa, 2)
        self._desenhar_texto("Último acontecimento", 60, 605)
        self._desenhar_texto(
            estado.ultima_mensagem,
            60,
            645,
            pequena=True,
        )

        if estado.finalizado:
            motivo = "Motivo: " + estado.motivo_encerramento
            self._desenhar_texto(motivo, 60, 685, pequena=True)

    def _desenhar_botao_passar(self, estado):
        if estado.finalizado:
            cor = COR_BOTAO_DESATIVADO
        else:
            cor = COR_BOTAO

        pygame.draw.rect(self.tela, cor, self.retangulo_botao_passar)
        pygame.draw.rect(self.tela, COR_BORDA, self.retangulo_botao_passar, 2)
        texto = self.fonte_normal.render("PASSAR", True, COR_BRANCA)
        centro = texto.get_rect(center=self.retangulo_botao_passar.center)
        self.tela.blit(texto, centro)

    def _desenhar_texto(
        self,
        conteudo,
        posicao_x,
        posicao_y,
        cor=COR_TEXTO,
        pequena=False,
    ):
        if pequena:
            fonte = self.fonte_pequena
        else:
            fonte = self.fonte_normal

        texto = fonte.render(conteudo, True, cor)
        self.tela.blit(texto, (posicao_x, posicao_y))
