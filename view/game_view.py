import pygame
from model.action_card import eh_carta_de_apoio, obter_dados_da_carta_de_apoio
from model.enums import Faccao, FaseTurno, TipoCartaAcao, TipoJogador
from model.match_settings import (
    SIMULACOES_MONTE_CARLO_DISPONIVEIS,
    TIPOS_COM_LIMITE_DE_TEMPO,
)
from view.constants import (
    ALTURA_CARTA_ACAO,
    ALTURA_JANELA,
    ALTURA_REGIAO,
    CORES_FACCOES,
    COR_FRONTEIRA,
    ESPACO_ENTRE_CARTAS,
    LARGURA_CARTA_ACAO,
    LARGURA_JANELA,
    LARGURA_REGIAO,
    POSICAO_X_MAO,
    POSICAO_Y_MAO,
    POSICOES_REGIOES,
    ROTAS_FRONTEIRAS,
    TITULO_JANELA,
)
from view.medieval_theme import FUNDO, MARFIM, OURO, OURO_ESCURO, TINTA, TemaMedieval
from view.state_tree_view import formatar_avaliacao_heuristica


_FILHOS_POR_PAGINA_ARVORE = 7
_ACAO_NOVO_JOGO = "novo_jogo"
_ACAO_CONTINUAR_JOGO = "continuar_jogo"
_ACAO_SAIR = "sair"
_MARCAS_FACCOES = {
    Faccao.ESCOCESES: "✕",
    Faccao.GALESES: "⚜",
    Faccao.INGLESES: "♛",
}
_SIMBOLOS_CARTAS = {
    TipoCartaAcao.NEGOCIAR: "⇄",
    TipoCartaAcao.MANOBRAR: "♞",
    TipoCartaAcao.SUPERAR_MANOBRA: "↟",
    TipoCartaAcao.REUNIR: "♜",
}
_MAPA = pygame.Rect(14, 68, 895, 386)


class VisaoJogo:
    """Desenha a partida e identifica em qual elemento ocorreu um clique."""

    def __init__(self):
        tamanho_janela = self._calcular_tamanho_inicial_da_janela()
        self.janela = pygame.display.set_mode(tamanho_janela, pygame.RESIZABLE)
        self.tela = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.tema = TemaMedieval()
        serifada = "georgia,dejavuserif,liberationserif"
        self.fonte_titulo = pygame.font.SysFont(serifada, 36, bold=True)
        self.fonte_titulo_menu = pygame.font.SysFont(serifada, 72, bold=True)
        self.fonte_normal = pygame.font.SysFont(serifada, 24, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial,dejavusans,liberationsans", 17)
        self.fonte_legenda = pygame.font.SysFont(serifada, 23, italic=True)
        self.fonte_rotulo = pygame.font.SysFont(serifada, 19, bold=True)
        self.fonte_botao_menu = pygame.font.SysFont(serifada, 29, bold=True)
        self.fonte_simbolo = pygame.font.SysFont("segoeuisymbol,dejavusans", 33)
        self.retangulo_novo_jogo = pygame.Rect(327, 465, 546, 83)
        self.retangulo_continuar_jogo = pygame.Rect(327, 575, 546, 83)
        self.retangulo_sair = pygame.Rect(327, 685, 546, 83)
        self.retangulo_iniciar_partida = pygame.Rect(345, 730, 510, 76)
        self.retangulo_voltar_menu = pygame.Rect(345, 824, 510, 64)
        self.retangulo_pausar_ia = pygame.Rect(922, 567, 262, 43)
        self.retangulo_botao_passar = pygame.Rect(922, 620, 262, 56)
        self.retangulo_botao_cancelar = pygame.Rect(922, 686, 125, 45)
        self.retangulo_botao_sem_efeito = pygame.Rect(1055, 686, 129, 45)
        self.retangulo_botao_salvar = pygame.Rect(746, 929, 137, 52)
        self.retangulo_botao_arvore = pygame.Rect(894, 929, 137, 52)
        self.retangulo_botao_voltar_jogada = pygame.Rect(1042, 929, 137, 52)
        self.retangulo_fechar_arvore = pygame.Rect(1043, 85, 137, 51)
        self.retangulo_exportar_graphviz = pygame.Rect(798, 85, 230, 51)
        self.retangulo_gerar_opcoes = pygame.Rect(21, 948, 237, 57)
        self.retangulo_campo_pagina = pygame.Rect(666, 951, 70, 51)
        self.retangulo_ir_pagina = pygame.Rect(745, 951, 56, 51)
        self.retangulo_pagina_anterior = pygame.Rect(813, 951, 170, 51)
        self.retangulo_proxima_pagina = pygame.Rect(995, 951, 184, 51)
        self.retangulos_faccoes = {
            Faccao.ESCOCESES: pygame.Rect(21, 929, 205, 52),
            Faccao.GALESES: pygame.Rect(237, 929, 205, 52),
            Faccao.INGLESES: pygame.Rect(453, 929, 205, 52),
        }

    def _calcular_tamanho_inicial_da_janela(self):
        """Calcula uma janela que caiba no monitor sem deformar o jogo."""
        tamanhos_disponiveis = pygame.display.get_desktop_sizes()

        if not tamanhos_disponiveis:
            return (LARGURA_JANELA, ALTURA_JANELA)

        largura_monitor, altura_monitor = tamanhos_disponiveis[0]
        largura_disponivel = int(largura_monitor * 0.90)
        altura_disponivel = int(altura_monitor * 0.85)
        escala_largura = largura_disponivel / LARGURA_JANELA
        escala_altura = altura_disponivel / ALTURA_JANELA
        escala = min(escala_largura, escala_altura, 1)

        largura = int(LARGURA_JANELA * escala)
        altura = int(ALTURA_JANELA * escala)
        return (largura, altura)

    def _calcular_escala_e_deslocamento(self):
        """Mantém a proporção e centraliza o jogo quando a janela muda."""
        largura_real, altura_real = self.janela.get_size()
        escala_largura = largura_real / LARGURA_JANELA
        escala_altura = altura_real / ALTURA_JANELA
        escala = min(escala_largura, escala_altura)

        largura_desenhada = int(LARGURA_JANELA * escala)
        altura_desenhada = int(ALTURA_JANELA * escala)
        deslocamento_x = (largura_real - largura_desenhada) // 2
        deslocamento_y = (altura_real - altura_desenhada) // 2

        return (
            escala,
            largura_desenhada,
            altura_desenhada,
            deslocamento_x,
            deslocamento_y,
        )

    def _apresentar_tela_redimensionada(self):
        """Reduz ou amplia o desenho lógico para o tamanho real da janela."""
        dados = self._calcular_escala_e_deslocamento()
        _, largura, altura, deslocamento_x, deslocamento_y = dados
        tela_redimensionada = pygame.transform.smoothscale(
            self.tela,
            (largura, altura),
        )

        self.janela.fill(FUNDO)
        self.janela.blit(tela_redimensionada, (deslocamento_x, deslocamento_y))

    def _converter_para_posicao_logica(self, posicao):
        """Converte o clique da janela real para as coordenadas do desenho."""
        dados = self._calcular_escala_e_deslocamento()
        escala, largura, altura, deslocamento_x, deslocamento_y = dados
        posicao_x, posicao_y = posicao

        dentro_horizontal = deslocamento_x <= posicao_x < deslocamento_x + largura
        dentro_vertical = deslocamento_y <= posicao_y < deslocamento_y + altura

        if not dentro_horizontal or not dentro_vertical:
            return (-1, -1)

        posicao_logica_x = int((posicao_x - deslocamento_x) / escala)
        posicao_logica_y = int((posicao_y - deslocamento_y) / escala)
        return (posicao_logica_x, posicao_logica_y)

    def botao_passar_foi_clicado(self, posicao, estado):
        """Informa se o clique ocorreu no botão Passar ativo."""
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return (
            not estado.finalizado
            and estado.fase_turno == FaseTurno.ESCOLHER_ACAO
            and self.retangulo_botao_passar.collidepoint(posicao_logica)
        )

    def botao_cancelar_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_botao_cancelar.collidepoint(posicao_logica)

    def botao_sem_efeito_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_botao_sem_efeito.collidepoint(posicao_logica)

    def botao_arvore_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_botao_arvore.collidepoint(posicao_logica)

    def botao_pausar_ia_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_pausar_ia.collidepoint(posicao_logica)

    def botao_salvar_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_botao_salvar.collidepoint(posicao_logica)

    def botao_voltar_jogada_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_botao_voltar_jogada.collidepoint(
            posicao_logica
        )

    def botao_fechar_arvore_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_fechar_arvore.collidepoint(posicao_logica)

    def botao_exportar_graphviz_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_exportar_graphviz.collidepoint(
            posicao_logica
        )

    def botao_gerar_opcoes_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_gerar_opcoes.collidepoint(posicao_logica)

    def botao_pagina_anterior_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_pagina_anterior.collidepoint(
            posicao_logica
        )

    def botao_proxima_pagina_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_proxima_pagina.collidepoint(
            posicao_logica
        )

    def campo_pagina_arvore_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_campo_pagina.collidepoint(posicao_logica)

    def botao_ir_pagina_foi_clicado(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        return self.retangulo_ir_pagina.collidepoint(posicao_logica)

    def _obter_controles_configuracao(self, indice):
        """Compartilha as mesmas áreas entre desenho e leitura dos cliques."""
        posicao_x = 101 + indice * 544
        return {
            "tipo": pygame.Rect(posicao_x, 338, 454, 64),
            "diminuir": pygame.Rect(posicao_x + 43, 473, 66, 51),
            "aumentar": pygame.Rect(posicao_x + 345, 473, 66, 51),
            "tempo": pygame.Rect(posicao_x + 43, 550, 368, 52),
        }

    def obter_acao_configuracao(self, posicao):
        """Retorna o controle e o índice do jogador selecionados."""
        posicao_logica = self._converter_para_posicao_logica(posicao)
        for indice in range(2):
            controles = self._obter_controles_configuracao(indice)
            for acao, retangulo in controles.items():
                if retangulo.collidepoint(posicao_logica):
                    return acao, indice
        return None

    def obter_acao_tela_configuracao(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        if self.retangulo_iniciar_partida.collidepoint(posicao_logica):
            return "iniciar"
        if self.retangulo_voltar_menu.collidepoint(posicao_logica):
            return "voltar"
        return None

    def obter_acao_menu_inicial(
        self,
        posicao,
        salvamento_disponivel,
    ):
        """Retorna a opção escolhida na tela inicial."""
        posicao_logica = self._converter_para_posicao_logica(posicao)

        if self.retangulo_novo_jogo.collidepoint(posicao_logica):
            return _ACAO_NOVO_JOGO

        if (
            salvamento_disponivel
            and self.retangulo_continuar_jogo.collidepoint(posicao_logica)
        ):
            return _ACAO_CONTINUAR_JOGO

        if self.retangulo_sair.collidepoint(posicao_logica):
            return _ACAO_SAIR

        return None

    def obter_quantidade_paginas_arvore(self, arvore):
        quantidade = arvore.obter_no_atual().quantidade_filhos()

        if quantidade == 0:
            return 1

        paginas = quantidade // _FILHOS_POR_PAGINA_ARVORE

        if quantidade % _FILHOS_POR_PAGINA_ARVORE != 0:
            paginas += 1

        return paginas

    def obter_nome_regiao_clicada(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        for nome in POSICOES_REGIOES:
            origem = POSICOES_REGIOES[nome]
            retangulo = pygame.Rect(
                origem[0], origem[1], LARGURA_REGIAO, ALTURA_REGIAO
            )
            if retangulo.collidepoint(posicao_logica):
                return nome
        return None

    def obter_posicao_trilha_clicada(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        for indice in range(8):
            if self._retangulo_trilha(indice).collidepoint(posicao_logica):
                return indice + 1
        return None

    def obter_faccao_clicada(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        for faccao in self.retangulos_faccoes:
            if self.retangulos_faccoes[faccao].collidepoint(posicao_logica):
                return faccao
        return None

    def _obter_fronteiras_sem_repeticao(self, tabuleiro):
        """Obtém cada fronteira uma vez, apesar de ela ser bidirecional."""
        fronteiras = []
        fronteiras_adicionadas = set()

        for nome_origem in tabuleiro.obter_nomes_das_regioes():
            for nome_destino in tabuleiro.regioes_adjacentes(nome_origem):
                identificador = frozenset([nome_origem, nome_destino])

                if identificador not in fronteiras_adicionadas:
                    fronteiras.append((nome_origem, nome_destino))
                    fronteiras_adicionadas.add(identificador)

        return fronteiras

    def _obter_centro_regiao(self, nome):
        posicao_x, posicao_y = POSICOES_REGIOES[nome]
        centro_x = posicao_x + LARGURA_REGIAO // 2
        centro_y = posicao_y + ALTURA_REGIAO // 2
        return (centro_x, centro_y)

    def _calcular_ponto_na_borda_em_direcao(self, nome_origem, direcao):
        centro_origem = self._obter_centro_regiao(nome_origem)
        diferenca_x = direcao[0] - centro_origem[0]
        diferenca_y = direcao[1] - centro_origem[1]

        escala_x = float("inf")
        escala_y = float("inf")

        if diferenca_x != 0:
            escala_x = (LARGURA_REGIAO / 2) / abs(diferenca_x)
        if diferenca_y != 0:
            escala_y = (ALTURA_REGIAO / 2) / abs(diferenca_y)

        escala = min(escala_x, escala_y)
        ponto_x = centro_origem[0] + diferenca_x * escala
        ponto_y = centro_origem[1] + diferenca_y * escala
        return (round(ponto_x), round(ponto_y))

    def _obter_pontos_da_fronteira(self, nome_origem, nome_destino):
        """Monta a linha, usando um corredor livre quando necessário."""
        centro_origem = self._obter_centro_regiao(nome_origem)
        centro_destino = self._obter_centro_regiao(nome_destino)
        identificador = frozenset([nome_origem, nome_destino])
        pontos_intermediarios = ROTAS_FRONTEIRAS.get(identificador, []).copy()

        if centro_origem[0] > centro_destino[0]:
            pontos_intermediarios.reverse()

        if pontos_intermediarios:
            direcao_origem = pontos_intermediarios[0]
            direcao_destino = pontos_intermediarios[-1]
        else:
            direcao_origem = centro_destino
            direcao_destino = centro_origem

        ponto_origem = self._calcular_ponto_na_borda_em_direcao(
            nome_origem, direcao_origem
        )
        ponto_destino = self._calcular_ponto_na_borda_em_direcao(
            nome_destino, direcao_destino
        )

        return [ponto_origem] + pontos_intermediarios + [ponto_destino]

    def _desenhar_ponta_de_seta(self, ponta, origem):
        """Desenha uma pequena ponta triangular voltada para uma região."""
        diferenca_x = origem[0] - ponta[0]
        diferenca_y = origem[1] - ponta[1]
        comprimento = (diferenca_x ** 2 + diferenca_y ** 2) ** 0.5

        if comprimento == 0:
            return

        direcao_x = diferenca_x / comprimento
        direcao_y = diferenca_y / comprimento
        base_x = ponta[0] + direcao_x * 12
        base_y = ponta[1] + direcao_y * 12
        perpendicular_x = -direcao_y * 6
        perpendicular_y = direcao_x * 6

        pontos = [
            ponta,
            (base_x + perpendicular_x, base_y + perpendicular_y),
            (base_x - perpendicular_x, base_y - perpendicular_y),
        ]
        pygame.draw.polygon(self.tela, COR_FRONTEIRA, pontos)

    def _desenhar_fronteiras(self, tabuleiro):
        """Desenha uma seta dupla para cada fronteira do tabuleiro."""
        fronteiras = self._obter_fronteiras_sem_repeticao(tabuleiro)

        for nome_origem, nome_destino in fronteiras:
            pontos = self._obter_pontos_da_fronteira(
                nome_origem, nome_destino
            )

            pygame.draw.lines(self.tela, (49, 41, 27), False, pontos, 6)
            pygame.draw.lines(
                self.tela,
                COR_FRONTEIRA,
                False,
                pontos,
                3,
            )
            self._desenhar_ponta_de_seta(pontos[0], pontos[1])
            self._desenhar_ponta_de_seta(pontos[-1], pontos[-2])

    def _obter_retangulo_carta(self, indice):
        posicao_x = POSICAO_X_MAO + indice * (
            LARGURA_CARTA_ACAO + ESPACO_ENTRE_CARTAS
        )
        return pygame.Rect(
            posicao_x, POSICAO_Y_MAO, LARGURA_CARTA_ACAO, ALTURA_CARTA_ACAO
        )

    def obter_indice_carta_clicada(self, posicao, estado):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        mao = estado.obter_jogador_atual().obter_mao()

        for indice in range(len(mao)):
            retangulo = self._obter_retangulo_carta(indice)
            if retangulo.collidepoint(posicao_logica):
                return indice
        return None

    def _quebrar_texto(self, conteudo, largura):
        linhas = []
        linha = ""
        for palavra in conteudo.split():
            tentativa = f"{linha} {palavra}" if linha else palavra
            if linha and self.fonte_pequena.size(tentativa)[0] > largura:
                linhas.append(linha)
                linha = palavra
            else:
                linha = tentativa
        if linha:
            linhas.append(linha)
        return linhas

    def _texto(self, conteudo, posicao, fonte, cor, alinhamento="topleft", largura=None):
        texto = fonte.render(conteudo, True, cor)
        if largura and texto.get_width() > largura:
            texto = pygame.transform.smoothscale(texto, (largura, texto.get_height()))
        self.tela.blit(texto, texto.get_rect(**{alinhamento: posicao}))

    def _centralizar(self, conteudo, centro, fonte=None, cor=MARFIM, largura=None):
        self._texto(conteudo, centro, fonte or self.fonte_normal, cor, "center", largura)

    def _simbolo(self, simbolo, centro, cor=OURO):
        self._centralizar(simbolo, centro, self.fonte_simbolo, cor)

    def _coroa(self, centro, largura):
        x, y = centro
        escala = largura / 64
        pontos = [(0, 12), (10, 18), (19, 25), (27, 18), (24, 12),
                  (32, 1), (40, 12), (37, 18), (45, 25), (54, 18),
                  (64, 12), (56, 38), (8, 38)]
        forma = [(x + (px - 32) * escala, y + (py - 22) * escala)
                 for px, py in pontos]
        pygame.draw.polygon(self.tela, OURO, forma)
        pygame.draw.lines(self.tela, MARFIM, False, forma[:11], 1)
        base = pygame.Rect(x - 24 * escala, y + 20 * escala, 48 * escala, 4 * escala)
        pygame.draw.rect(self.tela, OURO, base, border_radius=2)

    def _filete(self, x1, x2, y, cor=OURO_ESCURO):
        pygame.draw.line(self.tela, cor, (x1, y), (x2, y))

    def _pergaminho(self, caixa, borda=OURO_ESCURO, tonalidade=None, escuro=False):
        pygame.draw.rect(self.tela, (14, 17, 18), caixa.move(0, 4), border_radius=9)
        self.tela.blit(self.tema.placa(caixa.size, tonalidade, escuro), caixa)
        pygame.draw.rect(self.tela, borda, caixa, 2, border_radius=9)
        pygame.draw.rect(self.tela, OURO_ESCURO, caixa.inflate(-9, -9), 1, border_radius=6)

    def _botao(self, caixa, texto, ativo=True, estilo="vinho", icone=None, fonte=None):
        estilo = estilo if ativo else "inativo"
        realce = ativo and caixa.collidepoint(self.posicao_mouse)
        pygame.draw.rect(self.tela, (12, 15, 16), caixa.move(0, 4), border_radius=12)
        self.tela.blit(self.tema.relevo(caixa.size, estilo, realce), caixa)
        fonte = fonte or self.fonte_rotulo
        cor = MARFIM if ativo else (196, 190, 173)
        if icone:
            if caixa.width >= 400:
                self._simbolo(icone, (caixa.x + 62, caixa.centery), cor)
                pygame.draw.line(self.tela, OURO_ESCURO, (caixa.x + 111, caixa.y + 16),
                                 (caixa.x + 111, caixa.bottom - 16))
                self._texto(texto, (caixa.x + 138, caixa.centery), fonte, cor,
                            "midleft", caixa.width - 155)
            else:
                self._simbolo(icone, (caixa.x + 30, caixa.centery), cor)
                self._centralizar(texto, (caixa.centerx + 15, caixa.centery),
                                  fonte, cor, caixa.width - 58)
        else:
            self._centralizar(texto, caixa.center, fonte, cor, caixa.width - 16)

    def _estandartes(self, x, largura, altura):
        for indice, faccao in enumerate(Faccao):
            px = x + indice * (largura + 9)
            ponta = largura // 4
            pontos = [(px, 5), (px + largura, 5), (px + largura, altura - ponta),
                      (px + largura // 2, altura), (px, altura - ponta)]
            cor = CORES_FACCOES[faccao.value]
            pygame.draw.polygon(self.tela, tuple(int(canal * .75) for canal in cor), pontos)
            pygame.draw.lines(self.tela, OURO, True, pontos, 2)
            centro = (px + largura // 2, (altura - ponta) // 2 + 4)
            self._simbolo(_MARCAS_FACCOES[faccao], centro, MARFIM)

    def _fundo(self, destaque=False):
        self.posicao_mouse = self._converter_para_posicao_logica(pygame.mouse.get_pos())
        arte = "ambiente" if destaque else "ardosia"
        self.tela.blit(self.tema.ajustar_arte(arte, self.tela.get_size()), (0, 0))
        caixa = self.tela.get_rect().inflate(-4, -4)
        pygame.draw.rect(self.tela, OURO_ESCURO, caixa, 3, border_radius=18)
        pygame.draw.rect(self.tela, OURO, caixa.inflate(-6, -6), 1, border_radius=14)

    def _cabecalho(self):
        self.tela.fill(FUNDO, pygame.Rect(4, 4, LARGURA_JANELA - 8, 59))
        paisagem = self.tema.ajustar_arte("ambiente", (620, 350))
        self.tela.blit(paisagem, (530, 5), pygame.Rect(0, 6, 620, 56))
        self._filete(4, LARGURA_JANELA - 5, 63, OURO)
        self._coroa((53, 33), 42)
        self._texto(TITULO_JANELA, (83, 33), self.fonte_titulo, MARFIM, "midleft")
        pygame.draw.line(self.tela, OURO_ESCURO, (472, 13), (472, 52))
        self._estandartes(977, 52, 77)

    def _desenhar_configuracao_jogadores(self, configuracao):
        for indice in range(2):
            controles = self._obter_controles_configuracao(indice)
            seletor = controles["tipo"]
            painel = pygame.Rect(seletor.x - 29, 254, 512, 378)
            self._pergaminho(painel, OURO)
            self._simbolo("♟", (painel.x + 48, 294), TINTA)
            self._texto(f"Jogador {indice + 1}", (painel.x + 77, 294), self.fonte_titulo, TINTA, "midleft")
            tipo = configuracao.obter_tipo_jogador(indice)
            permite_limite = tipo in TIPOS_COM_LIMITE_DE_TEMPO
            limite = configuracao.obter_limite_tempo(indice)
            self._botao(seletor, tipo.value, fonte=self.fonte_normal)
            self._simbolo("‹", (seletor.x + 25, seletor.centery), MARFIM)
            self._simbolo("›", (seletor.right - 25, seletor.centery), MARFIM)
            self._filete(seletor.x, seletor.right, 426)

            if tipo == TipoJogador.MONTE_CARLO:
                rotulo = "Simulações Monte Carlo"
                valor = configuracao.obter_simulacoes_monte_carlo(indice)
                opcoes = SIMULACOES_MONTE_CARLO_DISPONIVEIS
                pode_diminuir = valor > opcoes[0]
                pode_aumentar = valor < opcoes[-1]
            elif tipo == TipoJogador.Q_LEARNING:
                rotulo = "Modelo treinado"
                valor = "Tabela Q"
                pode_aumentar = pode_diminuir = False
            else:
                rotulo = (
                    "Profundidade máxima" if permite_limite and limite is not None
                    else "Antecipação (jogadas completas)"
                )
                profundidade = configuracao.obter_profundidade(indice)
                pode_aumentar = tipo != TipoJogador.HUMANO
                pode_diminuir = pode_aumentar and profundidade > 1
                valor = profundidade if pode_aumentar else "Não se aplica"

            self._centralizar(rotulo, (painel.centerx, 450), cor=TINTA)
            self._botao(controles["diminuir"], "−", pode_diminuir, "couro", fonte=self.fonte_normal)
            self._botao(controles["aumentar"], "+", pode_aumentar, "couro", fonte=self.fonte_normal)
            visor = pygame.Rect(seletor.x + 118, 473, 218, 51)
            self._pergaminho(visor)
            self._centralizar(str(valor), visor.center, cor=TINTA)
            if permite_limite:
                tempo = "Sem limite" if limite is None else f"{limite} s"
                botao_tempo = controles["tempo"]
                self._botao(
                    botao_tempo, f"Tempo por jogada · {tempo}", estilo="couro", fonte=self.fonte_rotulo,
                )
                self._simbolo("›", (botao_tempo.right - 22, botao_tempo.centery), MARFIM)

    def desenhar_tela_configuracao(self, configuracao_partida):
        self._fundo(destaque=True)
        self._cabecalho()
        self._filete(428, 562, 106, OURO)
        self._filete(638, 772, 106, OURO)
        self._coroa((600, 105), 51)
        self._centralizar("Configurar novo jogo", (600, 157), self.fonte_titulo)
        self._centralizar("Escolha o tipo de controle de cada jogador.", (600, 205), self.fonte_legenda)
        self._desenhar_configuracao_jogadores(configuracao_partida)
        self._centralizar("A IA joga automaticamente. Você pode pausá-la durante a partida.",
                          (600, 676), self.fonte_legenda)
        self._botao(self.retangulo_iniciar_partida, "INICIAR PARTIDA", icone="▶", fonte=self.fonte_normal)
        self._botao(self.retangulo_voltar_menu, "VOLTAR AO MENU", estilo="couro", icone="←", fonte=self.fonte_normal)
        self._apresentar_tela_redimensionada()
        pygame.display.flip()

    def desenhar_menu_inicial(self, salvamento_disponivel, mensagem=""):
        self._fundo(destaque=True)
        self._estandartes(495, 64, 109)
        self._filete(317, 554, 170, OURO)
        self._filete(646, 883, 170, OURO)
        self._coroa((600, 164), 80)
        self._centralizar(TITULO_JANELA, (600, 246), self.fonte_titulo_menu)

        faixa = pygame.Rect(288, 327, 624, 71)
        pygame.draw.polygon(self.tela, (165, 126, 69),
                            [(250, 342), (301, 342), (301, 387), (250, 387), (265, 365)])
        pygame.draw.polygon(self.tela, (165, 126, 69),
                            [(899, 342), (950, 342), (935, 365), (950, 387), (899, 387)])
        self._pergaminho(faixa, OURO)
        self._centralizar("Escolha como deseja iniciar", faixa.center, self.fonte_legenda, TINTA)
        self._botao(self.retangulo_novo_jogo, "NOVO JOGO", icone="♛", fonte=self.fonte_botao_menu)
        self._botao(self.retangulo_continuar_jogo, "CONTINUAR JOGO", salvamento_disponivel,
                    icone="▤", fonte=self.fonte_botao_menu)
        self._botao(self.retangulo_sair, "SAIR", icone="↪", fonte=self.fonte_botao_menu)
        if not salvamento_disponivel:
            self._centralizar("Nenhuma partida salva foi encontrada.", (600, 671), self.fonte_pequena)
        for indice, linha in enumerate(self._quebrar_texto(mensagem, 700)[:3]):
            self._centralizar(linha, (600, 795 + indice * 23), self.fonte_pequena)

        self._apresentar_tela_redimensionada()
        pygame.display.flip()

    def _desenhar_botoes_de_faccao(self):
        for faccao, caixa in self.retangulos_faccoes.items():
            self._botao(caixa, faccao.value.upper(), estilo=faccao.value, icone=_MARCAS_FACCOES[faccao])

    def _desenhar_botoes(self, estado, arvore, selecao):
        pode_passar = (
            not estado.finalizado
            and estado.fase_turno == FaseTurno.ESCOLHER_ACAO
        )
        pode_usar_carta = pode_passar and selecao.get("carta") is not None
        pode_voltar = (
            arvore is not None
            and not arvore.obter_no_atual().eh_raiz()
            and estado.fase_turno != FaseTurno.CONVOCAR_SEGUIDOR
        )
        self._botao(self.retangulo_botao_passar, "PASSAR", pode_passar, icone="»")
        self._botao(self.retangulo_botao_cancelar, "CANCELAR", pode_passar, "ardosia")
        self._botao(self.retangulo_botao_sem_efeito, "SEM EFEITO", pode_usar_carta, "couro")
        self._botao(self.retangulo_botao_salvar, "SALVAR", estilo="couro")
        self._botao(self.retangulo_botao_arvore, "ÁRVORE", estilo="couro")
        self._botao(self.retangulo_botao_voltar_jogada, "VOLTAR", pode_voltar, "ardosia")
    def _lista_faccoes(self, obter_quantidade, x, y, passo, cor):
        for indice, faccao in enumerate(Faccao):
            altura = y + indice * passo
            pygame.draw.rect(self.tela, CORES_FACCOES[faccao.value],
                             pygame.Rect(x, altura + 4, 11, 11), border_radius=2)
            self._texto(f"{faccao.value.capitalize()}: {obter_quantidade(faccao)}",
                        (x + 18, altura), self.fonte_pequena, cor)

    def _desenhar_regiao(self, regiao, posicao, selecionada):
        caixa = pygame.Rect(*posicao, LARGURA_REGIAO, ALTURA_REGIAO)
        lider, _ = regiao.obter_lideranca()
        faccao = regiao.controlador or lider
        tonalidade = CORES_FACCOES[faccao.value] if faccao else None
        self.tela.blit(self.tema.placa(caixa.size, tonalidade, regiao.instavel, True),
                       caixa)
        if selecionada:
            pygame.draw.rect(self.tela, (255, 217, 110), caixa.inflate(4, 4), 4, border_radius=11)
        elif caixa.collidepoint(self.posicao_mouse):
            pygame.draw.rect(self.tela, OURO, caixa, 2, border_radius=11)

        self._centralizar(regiao.nome, (caixa.centerx, caixa.y + 19), self.fonte_rotulo, TINTA)
        self._lista_faccoes(regiao.quantidade_de_seguidores, caixa.x + 32, caixa.y + 34, 18, TINTA)

        situacao = "Em disputa"
        estilo = "couro"
        if regiao.instavel:
            situacao = "Instável"
            estilo = "ardosia"
        elif regiao.controlador is not None:
            situacao = f"Controle: {regiao.controlador.value}"
            estilo = regiao.controlador.value
        selo = pygame.Rect(caixa.x + 12, caixa.bottom - 35, caixa.width - 24, 24)
        self.tela.blit(self.tema.relevo(selo.size, estilo, False), selo)
        self._centralizar(situacao, selo.center, self.fonte_pequena)

    def _desenhar_regioes(self, estado, selecao):
        selecionadas = set(selecao.get("regioes_troca", []))
        selecionadas.update(selecao.get("destinos_assemble", {}).values())
        selecionadas.add(selecao.get("regiao_convocacao"))
        for nome, posicao in POSICOES_REGIOES.items():
            regiao = estado.tabuleiro.obter_regiao(nome)
            self._desenhar_regiao(regiao, posicao, nome in selecionadas)

    def _desenhar_painel_lateral(self, estado):
        painel = pygame.Rect(922, 81, 262, 474)
        pygame.draw.rect(self.tela, (27, 36, 39), painel, border_radius=13)
        pygame.draw.rect(self.tela, OURO, painel, 2, border_radius=13)

        jogador_atual = estado.obter_jogador_atual()
        self._texto("Turno", (940, 94), self.fonte_rotulo, OURO)
        self._texto(jogador_atual.nome, (940, 123), self.fonte_normal, MARFIM, largura=225)
        faixa = pygame.Rect(938, 159, 230, 29)
        pygame.draw.rect(self.tela, (47, 57, 59), faixa, border_radius=5)
        resumo = f"Cartas: {jogador_atual.quantidade_cartas()}       Passes: {estado.passes_consecutivos}"
        self._centralizar(resumo, faixa.center, self.fonte_pequena)

        grupos = [("Reserva", estado.reserva.quantidade)]
        grupos.extend((f"Corte de {jogador.nome}", jogador.qtd_na_corte) for jogador in estado.obter_jogadores())
        for indice, (titulo, obter_quantidade) in enumerate(grupos):
            y = 200 + indice * 91
            self._texto(titulo, (941, y), self.fonte_rotulo, MARFIM, largura=224)
            self._filete(940, 1166, y + 23)
            self._lista_faccoes(obter_quantidade, 956, y + 26, 18, MARFIM)

        self._filete(940, 1166, 475)
        disputas = estado.trilha_disputas.quantidade_resolvida()
        instabilidades = estado.tabuleiro.quantidade_instabilidades()
        self._texto(f"Disputas: {disputas}/8", (941, 481), self.fonte_pequena, MARFIM)
        self._texto(f"Instabilidades: {instabilidades}/3", (941, 501), self.fonte_pequena, MARFIM)
        if estado.finalizado:
            self._texto("PARTIDA ENCERRADA", (941, 524), self.fonte_rotulo, OURO)

    @staticmethod
    def _retangulo_trilha(indice):
        return pygame.Rect(193 + indice * 88, 476, 84, 42)

    def _desenhar_trilha(self, estado, selecao):
        faixa = pygame.Rect(14, 466, 895, 61)
        pygame.draw.rect(self.tela, OURO_ESCURO, faixa, 2, border_radius=9)
        self._texto("Ordem das disputas", (24, faixa.centery), self.fonte_rotulo, OURO,
                    "midleft", largura=159)
        posicoes = selecao.get("posicoes_trilha", [])
        for indice, carta in enumerate(estado.trilha_disputas.obter_cartas()):
            caixa = self._retangulo_trilha(indice)
            selecionada = indice + 1 in posicoes
            self._pergaminho(caixa, OURO if selecionada else OURO_ESCURO,
                             escuro=not carta.virada_para_cima)
            if selecionada or caixa.collidepoint(self.posicao_mouse):
                pygame.draw.rect(self.tela, OURO, caixa, 3 if selecionada else 2, border_radius=8)
            self._centralizar(f"{indice + 1}. {carta.nome_regiao}", caixa.center,
                              self.fonte_pequena, TINTA, largura=caixa.width - 9)
            if carta.possui_disco_negociacao:
                pygame.draw.circle(self.tela, (142, 40, 33), (caixa.right - 10, caixa.y + 8), 5)

    def _desenhar_mao(self, estado, selecao):
        jogador = estado.obter_jogador_atual()
        self._texto(f"Cartas de {jogador.nome}", (23, 739), self.fonte_normal, MARFIM)
        self._filete(21, 1179, 768)
        for indice, carta in enumerate(jogador.obter_mao()):
            caixa = self._obter_retangulo_carta(indice)
            selecionada = carta is selecao.get("carta")
            realce = selecionada or caixa.collidepoint(self.posicao_mouse)
            self._pergaminho(caixa, OURO if realce else OURO_ESCURO)
            if selecionada:
                pygame.draw.rect(self.tela, (154, 63, 35), caixa, 4, border_radius=9)
            if eh_carta_de_apoio(carta.tipo):
                faccao, _ = obter_dados_da_carta_de_apoio(carta.tipo)
                simbolo = _MARCAS_FACCOES[faccao]
                cor = tuple(round(canal * .66) for canal in CORES_FACCOES[faccao.value])
            else:
                simbolo = _SIMBOLOS_CARTAS[carta.tipo]
                cor = TINTA
            self._simbolo(simbolo, (caixa.centerx, caixa.y + 35), cor)
            for numero, linha in enumerate(carta.nome.split()):
                self._centralizar(linha, (caixa.centerx, caixa.y + 72 + 23 * numero),
                                  self.fonte_rotulo, TINTA, largura=caixa.width - 14)

    def _desenhar_mensagem(self, estado, instrucao):
        caixa = pygame.Rect(14, 539, 895, 192)
        self._pergaminho(caixa, OURO)
        titulo = "Resultado" if estado.finalizado else "O que fazer agora"
        mensagem = f"Motivo: {estado.motivo_encerramento}" if estado.finalizado else instrucao
        secoes = [("Último acontecimento", estado.ultima_mensagem, "▤"),
                  (titulo, mensagem, "◎")]
        for indice, (rotulo, conteudo, icone) in enumerate(secoes):
            y = 550 + indice * 87
            self._simbolo(icone, (48, y + 21), TINTA)
            self._texto(rotulo, (77, y), self.fonte_rotulo, TINTA)
            for linha, texto in enumerate(self._quebrar_texto(conteudo, 806)[:3]):
                self._texto(texto, (77, y + 25 + linha * 18), self.fonte_pequena, TINTA, largura=806)
        self._filete(77, 883, 630)

    def _desenhar_no_da_arvore(self, no, caixa, cor_borda, titulo, numero=None):
        self._pergaminho(caixa, cor_borda)
        if numero is None:
            x = caixa.x + 13
        else:
            x = caixa.x + 68
            fita = pygame.Rect(caixa.x + 12, caixa.y + 12, 38, 48)
            pontos = [fita.topleft, fita.topright, fita.bottomright,
                      (fita.centerx, fita.bottom - 8), fita.bottomleft]
            pygame.draw.polygon(self.tela, (112, 40, 30), pontos)
            pygame.draw.lines(self.tela, OURO_ESCURO, True, pontos, 1)
            self._centralizar(str(numero), fita.move(0, -3).center, largura=fita.width - 6)
        nota = formatar_avaliacao_heuristica(no)
        self._texto(nota, (caixa.right - 12, caixa.y + 7), self.fonte_pequena, TINTA, "topright")
        largura_titulo = caixa.right - x - self.fonte_pequena.size(nota)[0] - 22
        self._texto(titulo, (x, caixa.y + 5), self.fonte_rotulo, cor_borda, largura=largura_titulo)
        jogada = no.obter_jogada_origem()
        descricao = jogada.descrever() if jogada is not None else "Estado inicial"
        largura = caixa.right - x - 13
        linhas = self._quebrar_texto(descricao, largura)
        limite = 3 if numero is not None else 2
        for indice, linha in enumerate(linhas[:limite]):
            if indice == limite - 1 and len(linhas) > limite:
                linha = linha.rstrip() + "…"
            self._texto(linha, (x, caixa.y + 27 + indice * 17), self.fonte_pequena, TINTA, largura=largura)

    def _desenhar_caminho_da_arvore(self, arvore):
        painel = pygame.Rect(19, 185, 358, 734)
        self._pergaminho(painel, OURO)
        faixa = pygame.Rect(19, 185, 358, 55)
        self.tela.blit(self.tema.relevo(faixa.size, "ardosia", False), faixa)
        self._centralizar("Caminho percorrido", faixa.center)
        caminho = arvore.obter_caminho_atual()
        nos_visiveis = caminho[-10:]
        if len(caminho) > len(nos_visiveis):
            self._texto("Níveis anteriores omitidos", (31, 246), self.fonte_pequena, TINTA)
        for indice, no in enumerate(nos_visiveis):
            atual = no is arvore.obter_no_atual()
            cor = (28, 75, 142) if atual else (37, 90, 57)
            titulo = f"Nível {no.obter_nivel()}"
            if atual:
                titulo += " · ESTADO ATUAL"
            caixa = pygame.Rect(30, 269 + indice * 64, 336, 62)
            self._desenhar_no_da_arvore(no, caixa, cor, titulo)

    def _desenhar_filhos_da_arvore(self, arvore, pagina):
        no_atual = arvore.obter_no_atual()
        total_paginas = self.obter_quantidade_paginas_arvore(arvore)
        pagina = max(0, min(pagina, total_paginas - 1))
        inicio = pagina * _FILHOS_POR_PAGINA_ARVORE
        filhos_visiveis = no_atual.obter_filhos()[inicio:inicio + _FILHOS_POR_PAGINA_ARVORE]
        titulo = f"Próximas jogadas – página {pagina + 1} de {total_paginas}"
        self._texto(titulo, (407, 229), self.fonte_normal, MARFIM, largura=760)

        if not filhos_visiveis:
            mensagem = "Nenhuma opção foi gerada para este estado."
            if no_atual.esta_expandido():
                mensagem = "Este estado não possui próximas jogadas."
            caixa = pygame.Rect(399, 269, 780, 80)
            self._pergaminho(caixa, OURO)
            self._texto(mensagem, (420, caixa.centery), self.fonte_pequena, TINTA, "midleft")
            return

        for indice, no in enumerate(filhos_visiveis):
            numero = inicio + indice + 1
            caixa = pygame.Rect(399, 269 + indice * 92, 780, 80)
            titulo_no = f"Opção {numero} · nível {no.obter_nivel()}"
            self._desenhar_no_da_arvore(no, caixa, (104, 62, 31), titulo_no, numero)

    def _desenhar_controles_da_arvore(self, arvore, pagina, texto_pagina, campo_pagina_ativo):
        total = self.obter_quantidade_paginas_arvore(arvore)
        self._botao(self.retangulo_fechar_arvore, "FECHAR", estilo="ardosia", icone="×")
        self._botao(self.retangulo_exportar_graphviz, "ABRIR GRAPHVIZ")
        self._botao(self.retangulo_gerar_opcoes, "GERAR OPÇÕES", icone="⚙")
        self._botao(self.retangulo_ir_pagina, "IR")
        self._botao(self.retangulo_pagina_anterior, "‹  ANTERIOR", pagina > 0, "couro")
        self._botao(self.retangulo_proxima_pagina, "PRÓXIMA  ›", pagina < total - 1, "couro")
        borda = (38, 101, 174) if campo_pagina_ativo else OURO
        campo = self.retangulo_campo_pagina
        self._pergaminho(campo, borda)
        self._centralizar(texto_pagina, campo.center, cor=TINTA, largura=campo.width - 12)
        nivel = arvore.obter_no_atual().obter_nivel()
        resumo = f"Nós: {arvore.quantidade_nos()}    |    Nível atual: {nivel}    |    Páginas: {total}"
        self._texto(resumo, (274, 976), self.fonte_pequena, MARFIM, "midleft", largura=376)

    def _desenhar_arvore(self, arvore, pagina, mensagem, texto_pagina, campo_pagina_ativo):
        self._fundo()
        self._cabecalho()
        self._texto("Árvore de estados", (25, 83), self.fonte_titulo, MARFIM)
        legenda = "Azul: atual  |  Verde: caminho  |  H: nota estática  |  J: jogador de referência"
        self._texto(legenda, (26, 131), self.fonte_pequena, MARFIM)
        self._filete(20, 1180, 166, OURO)
        self._filete(20, 1180, 932, OURO)

        if mensagem:
            for indice, linha in enumerate(self._quebrar_texto(mensagem, 754)[:2]):
                self._texto(linha, (407, 181 + indice * 18), self.fonte_pequena, OURO, largura=754)

        self._desenhar_caminho_da_arvore(arvore)
        self._desenhar_filhos_da_arvore(arvore, pagina)
        self._desenhar_controles_da_arvore(arvore, pagina, texto_pagina, campo_pagina_ativo)

    def desenhar(
        self,
        estado,
        selecao=None,
        instrucao="",
        arvore=None,
        arvore_aberta=False,
        pagina_arvore=0,
        mensagem_arvore="",
        texto_pagina_arvore="1",
        campo_pagina_arvore_ativo=False,
        possui_ia=False,
        ia_pausada=False,
        resumo_ia="",
    ):
        """Desenha e apresenta um quadro da aplicação."""
        if arvore_aberta and arvore is not None:
            self._desenhar_arvore(arvore, pagina_arvore, mensagem_arvore,
                                 texto_pagina_arvore, campo_pagina_arvore_ativo)
        else:
            selecao = selecao or {}
            self._fundo()
            self._cabecalho()
            self.tela.blit(self.tema.ajustar_arte("mapa", _MAPA.size), _MAPA)
            pygame.draw.rect(self.tela, OURO_ESCURO, _MAPA, 2, border_radius=10)
            self._desenhar_fronteiras(estado.tabuleiro)
            self._desenhar_regioes(estado, selecao)
            self._desenhar_painel_lateral(estado)
            self._desenhar_trilha(estado, selecao)
            self._desenhar_mensagem(estado, instrucao)
            self._desenhar_mao(estado, selecao)
            self._filete(21, 1179, 917, OURO)
            self._desenhar_botoes_de_faccao()
            self._desenhar_botoes(estado, arvore, selecao)
            if possui_ia and not estado.finalizado:
                texto = "RETOMAR IA" if ia_pausada else "PAUSAR IA"
                self._botao(self.retangulo_pausar_ia, texto, icone="▶" if ia_pausada else "Ⅱ")
            if resumo_ia:
                self._texto(resumo_ia, (22, 993), self.fonte_pequena, MARFIM, largura=1155)

        self._apresentar_tela_redimensionada()
        pygame.display.flip()
