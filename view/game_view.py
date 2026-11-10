import pygame

from model.enums import Faccao, FaseTurno, TipoJogador
from view.constants import (
    ALTURA_CARTA_ACAO,
    ALTURA_JANELA,
    ALTURA_REGIAO,
    CORES_FACCOES,
    COR_BORDA,
    COR_BOTAO,
    COR_BOTAO_DESATIVADO,
    COR_BRANCA,
    COR_DE_FUNDO,
    COR_FRONTEIRA,
    COR_INSTABILIDADE,
    COR_PAINEL,
    COR_TEXTO,
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


_FILHOS_POR_PAGINA_ARVORE = 7
_ACAO_NOVO_JOGO = "novo_jogo"
_ACAO_CONTINUAR_JOGO = "continuar_jogo"
_ACAO_SAIR = "sair"


class VisaoJogo:
    """Desenha a partida e identifica em qual elemento ocorreu um clique."""

    def __init__(self):
        tamanho_janela = self._calcular_tamanho_inicial_da_janela()
        self.janela = pygame.display.set_mode(tamanho_janela, pygame.RESIZABLE)
        self.tela = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.fonte_titulo = pygame.font.Font(None, 38)
        self.fonte_titulo_menu = pygame.font.Font(None, 64)
        self.fonte_normal = pygame.font.Font(None, 26)
        self.fonte_pequena = pygame.font.Font(None, 20)
        self.retangulo_novo_jogo = pygame.Rect(420, 410, 360, 70)
        self.retangulo_continuar_jogo = pygame.Rect(420, 510, 360, 70)
        self.retangulo_sair = pygame.Rect(420, 610, 360, 70)
        self.retangulo_iniciar_partida = pygame.Rect(420, 650, 360, 70)
        self.retangulo_voltar_menu = pygame.Rect(420, 750, 360, 70)
        self.retangulo_pausar_ia = pygame.Rect(650, 35, 240, 45)
        self.retangulo_botao_passar = pygame.Rect(930, 680, 240, 52)
        self.retangulo_botao_cancelar = pygame.Rect(930, 750, 115, 45)
        self.retangulo_botao_sem_efeito = pygame.Rect(1055, 750, 115, 45)
        self.retangulo_botao_salvar = pygame.Rect(805, 925, 110, 45)
        self.retangulo_botao_arvore = pygame.Rect(930, 925, 115, 45)
        self.retangulo_botao_voltar_jogada = pygame.Rect(
            1055,
            925,
            115,
            45,
        )
        self.retangulo_fechar_arvore = pygame.Rect(1030, 45, 120, 45)
        self.retangulo_exportar_graphviz = pygame.Rect(800, 45, 210, 45)
        self.retangulo_gerar_opcoes = pygame.Rect(40, 940, 220, 50)
        self.retangulo_campo_pagina = pygame.Rect(650, 940, 55, 50)
        self.retangulo_ir_pagina = pygame.Rect(715, 940, 55, 50)
        self.retangulo_pagina_anterior = pygame.Rect(
            785,
            940,
            120,
            50,
        )
        self.retangulo_proxima_pagina = pygame.Rect(
            920,
            940,
            120,
            50,
        )
        self.retangulos_faccoes = {
            Faccao.ESCOCESES: pygame.Rect(40, 925, 180, 45),
            Faccao.GALESES: pygame.Rect(235, 925, 180, 45),
            Faccao.INGLESES: pygame.Rect(430, 925, 180, 45),
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

        self.janela.fill(COR_DE_FUNDO)
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
        posicao_x = 200 + indice * 440
        return {
            "tipo": pygame.Rect(posicao_x, 365, 360, 55),
            "diminuir": pygame.Rect(posicao_x + 35, 475, 55, 45),
            "aumentar": pygame.Rect(posicao_x + 270, 475, 55, 45),
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
            retangulo = pygame.Rect(40 + indice * 110, 490, 102, 62)
            if retangulo.collidepoint(posicao_logica):
                return indice + 1
        return None

    def obter_faccao_clicada(self, posicao):
        posicao_logica = self._converter_para_posicao_logica(posicao)
        for faccao in self.retangulos_faccoes:
            if self.retangulos_faccoes[faccao].collidepoint(posicao_logica):
                return faccao
        return None

    def _desenhar_titulo(self):
        texto = self.fonte_titulo.render(TITULO_JANELA, True, COR_TEXTO)
        self.tela.blit(texto, (40, 35))

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

    def _calcular_ponto_na_borda(self, nome_origem, nome_destino):
        """Encontra onde a linha entre duas regiões toca a primeira caixa."""
        centro_destino = self._obter_centro_regiao(nome_destino)
        return self._calcular_ponto_na_borda_em_direcao(
            nome_origem, centro_destino
        )

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
        palavras = conteudo.split()
        linhas = []
        linha = ""

        for palavra in palavras:
            tentativa = palavra if not linha else linha + " " + palavra
            if self.fonte_pequena.size(tentativa)[0] <= largura:
                linha = tentativa
            else:
                linhas.append(linha)
                linha = palavra
        if linha:
            linhas.append(linha)
        return linhas

    def _desenhar_texto_centralizado(
        self, conteudo, retangulo, cor, pequena=False
    ):
        fonte = self.fonte_pequena if pequena else self.fonte_normal
        texto = fonte.render(conteudo, True, cor)
        centro = texto.get_rect(center=retangulo.center)
        self.tela.blit(texto, centro)

    def _desenhar_botao_menu(self, retangulo, texto, ativo=True):
        cor = COR_BOTAO if ativo else COR_BOTAO_DESATIVADO
        pygame.draw.rect(self.tela, cor, retangulo)
        pygame.draw.rect(self.tela, COR_BORDA, retangulo, 3)
        self._desenhar_texto_centralizado(
            texto,
            retangulo,
            COR_BRANCA,
        )

    def _desenhar_configuracao_jogadores(self, configuracao):
        for indice in range(2):
            controles = self._obter_controles_configuracao(indice)
            posicao_x = controles["tipo"].x
            painel = pygame.Rect(posicao_x - 20, 290, 400, 290)
            pygame.draw.rect(self.tela, COR_PAINEL, painel)
            pygame.draw.rect(self.tela, COR_BORDA, painel, 2)
            self._desenhar_texto("Jogador " + str(indice + 1), posicao_x, 315)
            tipo = configuracao.obter_tipo_jogador(indice)
            self._desenhar_botao_menu(controles["tipo"], tipo.value)
            self._desenhar_texto("Antecipação (jogadas completas)", posicao_x, 440)
            eh_ia = tipo != TipoJogador.HUMANO
            profundidade = configuracao.obter_profundidade(indice)
            self._desenhar_botao_menu(
                controles["diminuir"], "-", eh_ia and profundidade > 1
            )
            self._desenhar_botao_menu(controles["aumentar"], "+", eh_ia)
            texto = str(profundidade) if eh_ia else "Não se aplica"
            self._desenhar_texto_centralizado(
                texto, pygame.Rect(posicao_x + 95, 475, 170, 45), COR_TEXTO
            )
            self._desenhar_texto(
                "Clique no tipo para alternar.", posicao_x, 545, pequena=True
            )

    def desenhar_tela_configuracao(self, configuracao_partida):
        """Apresenta as escolhas exclusivas da criação de uma partida."""
        self.tela.fill(COR_DE_FUNDO)
        titulo = self.fonte_titulo_menu.render("Configurar novo jogo", True, COR_TEXTO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA_JANELA // 2, 150)))
        self._desenhar_texto_centralizado(
            "Escolha o controle e a antecipação de cada jogador.",
            pygame.Rect(150, 210, 900, 30), COR_TEXTO,
        )
        self._desenhar_configuracao_jogadores(configuracao_partida)
        self._desenhar_texto_centralizado(
            "A IA joga automaticamente. Você pode pausá-la durante a partida.",
            pygame.Rect(150, 605, 900, 25), COR_TEXTO, True,
        )
        self._desenhar_botao_menu(self.retangulo_iniciar_partida, "INICIAR PARTIDA")
        self._desenhar_botao_menu(self.retangulo_voltar_menu, "VOLTAR AO MENU")
        self._apresentar_tela_redimensionada()
        pygame.display.flip()

    def desenhar_menu_inicial(
        self,
        salvamento_disponivel,
        mensagem="",
    ):
        """Desenha as opções exibidas antes do início da partida."""
        self.tela.fill(COR_DE_FUNDO)
        titulo = self.fonte_titulo_menu.render(
            TITULO_JANELA,
            True,
            COR_TEXTO,
        )
        titulo_centralizado = titulo.get_rect(
            center=(LARGURA_JANELA // 2, 225)
        )
        self.tela.blit(titulo, titulo_centralizado)

        subtitulo = "Escolha como deseja iniciar"
        texto_subtitulo = self.fonte_normal.render(
            subtitulo,
            True,
            COR_TEXTO,
        )
        subtitulo_centralizado = texto_subtitulo.get_rect(
            center=(LARGURA_JANELA // 2, 300)
        )
        self.tela.blit(texto_subtitulo, subtitulo_centralizado)

        self._desenhar_botao_menu(
            self.retangulo_novo_jogo,
            "NOVO JOGO",
        )
        self._desenhar_botao_menu(
            self.retangulo_continuar_jogo,
            "CONTINUAR JOGO",
            salvamento_disponivel,
        )
        self._desenhar_botao_menu(
            self.retangulo_sair,
            "SAIR",
        )

        if not salvamento_disponivel:
            aviso = "Nenhuma partida salva foi encontrada."
            self._desenhar_texto_centralizado(
                aviso,
                pygame.Rect(350, 585, 500, 20),
                COR_TEXTO,
                True,
            )

        if mensagem:
            linhas = self._quebrar_texto(mensagem, 700)
            altura = 735

            for linha in linhas[:3]:
                self._desenhar_texto_centralizado(
                    linha,
                    pygame.Rect(250, altura, 700, 24),
                    COR_BOTAO,
                    True,
                )
                altura += 24

        self._apresentar_tela_redimensionada()
        pygame.display.flip()

    def _desenhar_botoes_de_faccao(self):
        for faccao in Faccao:
            retangulo = self.retangulos_faccoes[faccao]
            pygame.draw.rect(self.tela, CORES_FACCOES[faccao.value], retangulo)
            pygame.draw.rect(self.tela, COR_BORDA, retangulo, 2)
            texto = faccao.value.upper()
            self._desenhar_texto_centralizado(texto, retangulo, COR_BRANCA, True)

    def _desenhar_botoes(self, estado, arvore):
        pode_passar = (
            not estado.finalizado
            and estado.fase_turno == FaseTurno.ESCOLHER_ACAO
        )
        cor_passar = COR_BOTAO if pode_passar else COR_BOTAO_DESATIVADO
        pygame.draw.rect(self.tela, cor_passar, self.retangulo_botao_passar)
        pygame.draw.rect(self.tela, COR_BORDA, self.retangulo_botao_passar, 2)
        self._desenhar_texto_centralizado(
            "PASSAR", self.retangulo_botao_passar, COR_BRANCA
        )

        pygame.draw.rect(self.tela, COR_BOTAO_DESATIVADO, self.retangulo_botao_cancelar)
        pygame.draw.rect(self.tela, COR_BORDA, self.retangulo_botao_cancelar, 2)
        self._desenhar_texto_centralizado(
            "CANCELAR", self.retangulo_botao_cancelar, COR_BRANCA, True
        )

        pygame.draw.rect(self.tela, COR_BOTAO, self.retangulo_botao_sem_efeito)
        pygame.draw.rect(self.tela, COR_BORDA, self.retangulo_botao_sem_efeito, 2)
        self._desenhar_texto_centralizado(
            "SEM EFEITO", self.retangulo_botao_sem_efeito, COR_BRANCA, True
        )

        pygame.draw.rect(
            self.tela,
            COR_BOTAO,
            self.retangulo_botao_salvar,
        )
        pygame.draw.rect(
            self.tela,
            COR_BORDA,
            self.retangulo_botao_salvar,
            2,
        )
        self._desenhar_texto_centralizado(
            "SALVAR",
            self.retangulo_botao_salvar,
            COR_BRANCA,
            True,
        )

        pygame.draw.rect(
            self.tela,
            COR_BOTAO,
            self.retangulo_botao_arvore,
        )
        pygame.draw.rect(
            self.tela,
            COR_BORDA,
            self.retangulo_botao_arvore,
            2,
        )
        self._desenhar_texto_centralizado(
            "ÁRVORE",
            self.retangulo_botao_arvore,
            COR_BRANCA,
            True,
        )

        pode_voltar = (
            arvore is not None
            and not arvore.obter_no_atual().eh_raiz()
            and estado.fase_turno != FaseTurno.CONVOCAR_SEGUIDOR
        )
        cor_voltar = (
            COR_BOTAO if pode_voltar else COR_BOTAO_DESATIVADO
        )
        pygame.draw.rect(
            self.tela,
            cor_voltar,
            self.retangulo_botao_voltar_jogada,
        )
        pygame.draw.rect(
            self.tela,
            COR_BORDA,
            self.retangulo_botao_voltar_jogada,
            2,
        )
        self._desenhar_texto_centralizado(
            "VOLTAR",
            self.retangulo_botao_voltar_jogada,
            COR_BRANCA,
            True,
        )

    def _desenhar_texto(
        self, conteudo, posicao_x, posicao_y, cor=COR_TEXTO, pequena=False
    ):
        fonte = self.fonte_pequena if pequena else self.fonte_normal
        texto = fonte.render(conteudo, True, cor)
        self.tela.blit(texto, (posicao_x, posicao_y))
    def _desenhar_regiao(self, regiao, posicao, selecionada):
        retangulo = pygame.Rect(
            posicao[0], posicao[1], LARGURA_REGIAO, ALTURA_REGIAO
        )
        pygame.draw.rect(self.tela, COR_PAINEL, retangulo)

        cor_borda = COR_BORDA
        espessura = 4

        if regiao.instavel:
            cor_borda = COR_INSTABILIDADE
        elif regiao.controlador is not None:
            cor_borda = CORES_FACCOES[regiao.controlador.value]

        if selecionada:
            cor_borda = COR_BOTAO
            espessura = 7

        pygame.draw.rect(self.tela, cor_borda, retangulo, espessura)
        self._desenhar_texto(regiao.nome, posicao[0] + 10, posicao[1] + 8)

        deslocamento = 38
        for faccao in Faccao:
            quantidade = regiao.quantidade_de_seguidores(faccao)
            texto = faccao.value.capitalize() + ": " + str(quantidade)
            self._desenhar_texto(
                texto,
                posicao[0] + 10,
                posicao[1] + deslocamento,
                CORES_FACCOES[faccao.value],
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
            situacao, posicao[0] + 10, posicao[1] + 108, pequena=True
        )

    def _desenhar_regioes(self, estado, selecao):
        selecionadas = selecao.get("regioes_troca", []).copy()
        regiao_convocacao = selecao.get("regiao_convocacao")
        if regiao_convocacao is not None:
            selecionadas.append(regiao_convocacao)

        for nome in POSICOES_REGIOES:
            regiao = estado.tabuleiro.obter_regiao(nome)
            selecionada = nome in selecionadas
            self._desenhar_regiao(regiao, POSICOES_REGIOES[nome], selecionada)

    def _desenhar_painel_lateral(self, estado):
        painel = pygame.Rect(930, 30, 240, 620)
        pygame.draw.rect(self.tela, COR_PAINEL, painel)
        pygame.draw.rect(self.tela, COR_BORDA, painel, 3)

        jogador_atual = estado.obter_jogador_atual()
        self._desenhar_texto("Turno", 955, 55)
        self._desenhar_texto(jogador_atual.nome, 955, 85)
        self._desenhar_texto(
            "Cartas: " + str(jogador_atual.quantidade_cartas()),
            955,
            115,
            pequena=True,
        )
        self._desenhar_texto(
            "Passes: " + str(estado.passes_consecutivos), 955, 138, pequena=True
        )

        self._desenhar_texto("Reserva", 955, 175)
        altura = 205
        for faccao in Faccao:
            quantidade = estado.reserva.quantidade(faccao)
            texto = faccao.value.capitalize() + ": " + str(quantidade)
            self._desenhar_texto(
                texto, 955, altura, CORES_FACCOES[faccao.value], pequena=True
            )
            altura += 25

        altura = 300
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
            "Disputas: "
            + str(estado.trilha_disputas.quantidade_resolvida())
            + "/8",
            955,
            555,
            pequena=True,
        )
        self._desenhar_texto(
            "Instabilidades: "
            + str(estado.tabuleiro.quantidade_instabilidades())
            + "/3",
            955,
            580,
            pequena=True,
        )
        if estado.finalizado:
            self._desenhar_texto("PARTIDA ENCERRADA", 955, 615, COR_BOTAO)

    def _desenhar_trilha(self, estado, selecao):
        self._desenhar_texto("Ordem das disputas", 40, 455)
        cartas = estado.trilha_disputas.obter_cartas()
        posicoes_selecionadas = selecao.get("posicoes_trilha", [])

        for indice in range(len(cartas)):
            carta = cartas[indice]
            posicao_x = 40 + indice * 110
            retangulo = pygame.Rect(posicao_x, 490, 102, 62)
            cor_carta = COR_PAINEL if carta.virada_para_cima else (175, 170, 160)
            pygame.draw.rect(self.tela, cor_carta, retangulo)
            espessura = 5 if indice + 1 in posicoes_selecionadas else 2
            pygame.draw.rect(self.tela, COR_BORDA, retangulo, espessura)
            self._desenhar_texto(
                str(indice + 1) + ".",
                posicao_x + 5,
                497,
                pequena=True,
            )
            self._desenhar_texto(carta.nome_regiao, posicao_x + 5, 523, pequena=True)
            if carta.possui_disco_negociacao:
                pygame.draw.circle(self.tela, COR_BOTAO, (posicao_x + 88, 503), 7)

    def _desenhar_mao(self, estado, selecao):
        jogador = estado.obter_jogador_atual()
        self._desenhar_texto("Cartas de " + jogador.nome, 40, 785)
        mao = jogador.obter_mao()
        selecionada = selecao.get("carta")

        for indice in range(len(mao)):
            carta = mao[indice]
            retangulo = self._obter_retangulo_carta(indice)
            pygame.draw.rect(self.tela, COR_PAINEL, retangulo)
            espessura = 6 if carta is selecionada else 2
            pygame.draw.rect(self.tela, COR_BORDA, retangulo, espessura)
            linhas = self._quebrar_texto(carta.nome, LARGURA_CARTA_ACAO - 12)
            altura = POSICAO_Y_MAO + 12
            for linha in linhas:
                self._desenhar_texto(
                    linha, retangulo.x + 6, altura, pequena=True
                )
                altura += 20

    def _desenhar_texto_quebrado(self, conteudo, x, y, largura):
        linhas = self._quebrar_texto(conteudo, largura)
        for linha in linhas[:2]:
            self._desenhar_texto(linha, x, y, pequena=True)
            y += 22

    def _desenhar_mensagem(self, estado, instrucao):
        caixa = pygame.Rect(40, 585, 850, 190)
        pygame.draw.rect(self.tela, COR_PAINEL, caixa)
        pygame.draw.rect(self.tela, COR_BORDA, caixa, 2)
        self._desenhar_texto("Último acontecimento", 60, 605)
        self._desenhar_texto_quebrado(estado.ultima_mensagem, 60, 640, 790)
        if estado.finalizado:
            self._desenhar_texto("Resultado", 60, 690)
            motivo = "Motivo: " + estado.motivo_encerramento
            self._desenhar_texto(motivo, 60, 722, pequena=True)
        else:
            self._desenhar_texto("O que fazer agora", 60, 690)
            self._desenhar_texto_quebrado(instrucao, 60, 722, 790)

    def _desenhar_no_da_arvore(
        self,
        no,
        retangulo,
        cor_borda,
        titulo,
    ):
        pygame.draw.rect(self.tela, COR_PAINEL, retangulo)
        pygame.draw.rect(self.tela, cor_borda, retangulo, 3)
        self._desenhar_texto(
            titulo,
            retangulo.x + 10,
            retangulo.y + 7,
            cor_borda,
            pequena=True,
        )

        jogada = no.obter_jogada_origem()
        descricao = "Estado inicial"

        if jogada is not None:
            descricao = jogada.descrever()

        linhas = self._quebrar_texto(
            descricao,
            retangulo.width - 20,
        )
        altura = retangulo.y + 29

        for linha in linhas[:2]:
            self._desenhar_texto(
                linha,
                retangulo.x + 10,
                altura,
                pequena=True,
            )
            altura += 18

    def _desenhar_caminho_da_arvore(self, arvore):
        self._desenhar_texto("Caminho percorrido", 40, 120)
        caminho = arvore.obter_caminho_atual()
        primeiro_indice = max(0, len(caminho) - 10)

        if primeiro_indice > 0:
            self._desenhar_texto(
                "... níveis anteriores omitidos",
                40,
                148,
                pequena=True,
            )

        nos_visiveis = caminho[primeiro_indice:]

        for indice in range(len(nos_visiveis)):
            no = nos_visiveis[indice]
            posicao_y = 175 + indice * 72
            retangulo = pygame.Rect(40, posicao_y, 430, 60)
            cor = (80, 140, 90)
            titulo = "Nível " + str(no.obter_nivel())

            if no is arvore.obter_no_atual():
                cor = CORES_FACCOES[Faccao.ESCOCESES.value]
                titulo += " - ESTADO ATUAL"

            self._desenhar_no_da_arvore(
                no,
                retangulo,
                cor,
                titulo,
            )

    def _desenhar_filhos_da_arvore(self, arvore, pagina):
        no_atual = arvore.obter_no_atual()
        filhos = no_atual.obter_filhos()
        total_paginas = self.obter_quantidade_paginas_arvore(arvore)
        pagina = min(pagina, total_paginas - 1)
        inicio = pagina * _FILHOS_POR_PAGINA_ARVORE
        fim = inicio + _FILHOS_POR_PAGINA_ARVORE
        filhos_visiveis = filhos[inicio:fim]

        titulo = "Próximas jogadas"
        titulo += " - página " + str(pagina + 1)
        titulo += " de " + str(total_paginas)
        self._desenhar_texto(titulo, 510, 120)

        if not filhos_visiveis:
            mensagem = "Nenhuma opção foi gerada para este estado."

            if no_atual.esta_expandido():
                mensagem = "Este estado não possui próximas jogadas."

            self._desenhar_texto(
                mensagem,
                510,
                175,
                pequena=True,
            )
            return

        for indice in range(len(filhos_visiveis)):
            no = filhos_visiveis[indice]
            posicao_y = 160 + indice * 105
            retangulo = pygame.Rect(510, posicao_y, 640, 88)
            numero = inicio + indice + 1
            titulo_no = (
                "Opção "
                + str(numero)
                + " - nível "
                + str(no.obter_nivel())
            )
            self._desenhar_no_da_arvore(
                no,
                retangulo,
                COR_BORDA,
                titulo_no,
            )

    def _desenhar_controles_da_arvore(
        self,
        arvore,
        pagina,
        mensagem,
        texto_pagina,
        campo_pagina_ativo,
    ):
        botoes = [
            (self.retangulo_fechar_arvore, "FECHAR", COR_BOTAO),
            (
                self.retangulo_exportar_graphviz,
                "ABRIR GRAPHVIZ",
                COR_BOTAO,
            ),
            (
                self.retangulo_gerar_opcoes,
                "GERAR OPÇÕES",
                COR_BOTAO,
            ),
            (
                self.retangulo_ir_pagina,
                "IR",
                COR_BOTAO,
            ),
            (
                self.retangulo_pagina_anterior,
                "ANTERIOR",
                COR_BOTAO,
            ),
            (
                self.retangulo_proxima_pagina,
                "PRÓXIMA",
                COR_BOTAO,
            ),
        ]

        for retangulo, texto, cor in botoes:
            pygame.draw.rect(self.tela, cor, retangulo)
            pygame.draw.rect(self.tela, COR_BORDA, retangulo, 2)
            self._desenhar_texto_centralizado(
                texto,
                retangulo,
                COR_BRANCA,
                True,
            )

        cor_borda_campo = COR_BORDA

        if campo_pagina_ativo:
            cor_borda_campo = CORES_FACCOES[Faccao.ESCOCESES.value]

        pygame.draw.rect(
            self.tela,
            COR_PAINEL,
            self.retangulo_campo_pagina,
        )
        pygame.draw.rect(
            self.tela,
            cor_borda_campo,
            self.retangulo_campo_pagina,
            3,
        )
        self._desenhar_texto_centralizado(
            texto_pagina,
            self.retangulo_campo_pagina,
            COR_TEXTO,
            True,
        )
        self._desenhar_texto("PÁG.", 605, 955, pequena=True)

        total_paginas = self.obter_quantidade_paginas_arvore(arvore)
        resumo = (
            "Nós: "
            + str(arvore.quantidade_nos())
            + " | Nível atual: "
            + str(arvore.obter_no_atual().obter_nivel())
            + " | Total de páginas: "
            + str(total_paginas)
        )
        self._desenhar_texto(resumo, 285, 955, pequena=True)

        if mensagem:
            self._desenhar_texto(
                mensagem,
                510,
                95,
                COR_BOTAO,
                pequena=True,
            )

    def _desenhar_arvore(
        self,
        arvore,
        pagina,
        mensagem,
        texto_pagina,
        campo_pagina_ativo,
    ):
        self.tela.fill(COR_DE_FUNDO)
        self._desenhar_texto("Árvore de estados", 40, 45)
        self._desenhar_texto(
            "Azul: estado atual | Verde: caminho percorrido",
            40,
            82,
            pequena=True,
        )
        self._desenhar_caminho_da_arvore(arvore)
        self._desenhar_filhos_da_arvore(arvore, pagina)
        self._desenhar_controles_da_arvore(
            arvore,
            pagina,
            mensagem,
            texto_pagina,
            campo_pagina_ativo,
        )

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
        if selecao is None:
            selecao = {}

        self.tela.fill(COR_DE_FUNDO)
        self._desenhar_titulo()
        if resumo_ia:
            self._desenhar_texto(resumo_ia, 40, 990, pequena=True)
        self._desenhar_fronteiras(estado.tabuleiro)
        self._desenhar_regioes(estado, selecao)
        self._desenhar_painel_lateral(estado)
        self._desenhar_trilha(estado, selecao)
        self._desenhar_mensagem(estado, instrucao)
        self._desenhar_mao(estado, selecao)
        self._desenhar_botoes_de_faccao()
        self._desenhar_botoes(estado, arvore)
        if possui_ia and not estado.finalizado:
            texto = "RETOMAR IA" if ia_pausada else "PAUSAR IA"
            self._desenhar_botao_menu(self.retangulo_pausar_ia, texto)

        if arvore_aberta and arvore is not None:
            self._desenhar_arvore(
                arvore,
                pagina_arvore,
                mensagem_arvore,
                texto_pagina_arvore,
                campo_pagina_arvore_ativo,
            )

        self._apresentar_tela_redimensionada()
        pygame.display.flip()
