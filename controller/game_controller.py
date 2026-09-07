import pygame

from model.enums import Faccao, FaseTurno, TipoCartaAcao


QUADROS_POR_SEGUNDO = 60


class ControladorJogo:
    """Transforma os cliques do usuário em comandos para o Model."""

    def __init__(self, jogo, visao):
        self.jogo = jogo
        self.visao = visao
        self.relogio = pygame.time.Clock()
        self.executando = True
        self.carta_selecionada = None
        self.destinos_assemble = {}
        self.regioes_troca = []
        self.faccoes_troca = []
        self.posicoes_trilha = []
        self.regiao_convocacao = None
        self.instrucao = "Escolha uma carta de ação ou passe."

    def executar(self):
        """Mantém o loop principal ativo até o fechamento da janela."""
        while self.executando:
            self._processar_eventos()
            selecao = self._obter_selecao()
            self.visao.desenhar(self.jogo.estado, selecao, self.instrucao)
            self.relogio.tick(QUADROS_POR_SEGUNDO)

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self._processar_clique(evento.pos)

    def _processar_clique(self, posicao):
        estado = self.jogo.estado

        if estado.finalizado:
            return

        if self.visao.botao_cancelar_foi_clicado(posicao):
            if estado.fase_turno == FaseTurno.ESCOLHER_ACAO:
                self._limpar_selecao()
                self.instrucao = "Seleção cancelada. Escolha uma carta ou passe."
            return

        if estado.fase_turno == FaseTurno.CONVOCAR_SEGUIDOR:
            self._processar_convocacao(posicao)
            return

        if self.carta_selecionada is None:
            self._processar_inicio_da_jogada(posicao)
            return

        if self.visao.botao_sem_efeito_foi_clicado(posicao):
            self._tentar_jogar_carta({})
            return

        tipo = self.carta_selecionada.tipo

        if tipo == TipoCartaAcao.REUNIR:
            self._processar_assemble(posicao)
        elif tipo in [
            TipoCartaAcao.APOIO_ESCOCES,
            TipoCartaAcao.APOIO_GALES,
            TipoCartaAcao.APOIO_INGLES,
        ]:
            self._processar_support(posicao)
        elif tipo == TipoCartaAcao.NEGOCIAR:
            self._processar_negotiate(posicao)
        elif tipo in [TipoCartaAcao.MANOBRAR, TipoCartaAcao.SUPERAR_MANOBRA]:
            self._processar_troca_de_seguidores(posicao)

    def _processar_inicio_da_jogada(self, posicao):
        if self.visao.botao_passar_foi_clicado(posicao, self.jogo.estado):
            try:
                self.jogo.passar()
                self.instrucao = "Escolha uma carta de ação ou passe."
            except (TypeError, ValueError) as erro:
                self.instrucao = "Erro: " + str(erro)
            return

        indice = self.visao.obter_indice_carta_clicada(posicao, self.jogo.estado)

        if indice is None:
            return

        mao = self.jogo.estado.obter_jogador_atual().obter_mao()
        self.carta_selecionada = mao[indice]
        self._atualizar_instrucao_da_carta()

    def _processar_assemble(self, posicao):
        nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

        if nome_regiao is None:
            return

        faccoes_pendentes = []

        for faccao in Faccao:
            disponivel = self.jogo.estado.reserva.quantidade(faccao) > 0
            if disponivel and faccao not in self.destinos_assemble:
                faccoes_pendentes.append(faccao)

        if not faccoes_pendentes:
            self._tentar_jogar_carta({"destinos": self.destinos_assemble})
            return

        faccao = faccoes_pendentes[0]
        self.destinos_assemble[faccao] = nome_regiao

        ainda_pendentes = []
        for outra_faccao in Faccao:
            if self.jogo.estado.reserva.quantidade(outra_faccao) > 0:
                if outra_faccao not in self.destinos_assemble:
                    ainda_pendentes.append(outra_faccao)

        if ainda_pendentes:
            self.instrucao = (
                "Assemble: clique na região dos " + ainda_pendentes[0].value + "."
            )
        else:
            self._tentar_jogar_carta({"destinos": self.destinos_assemble})

    def _processar_support(self, posicao):
        nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

        if nome_regiao is not None:
            self._tentar_jogar_carta({"regiao": nome_regiao})

    def _processar_negotiate(self, posicao):
        posicao_trilha = self.visao.obter_posicao_trilha_clicada(posicao)

        if posicao_trilha is None:
            return

        if len(self.posicoes_trilha) < 2:
            if posicao_trilha in self.posicoes_trilha:
                self.instrucao = "Negotiate: escolha duas posições diferentes."
                return

            self.posicoes_trilha.append(posicao_trilha)

            if len(self.posicoes_trilha) == 1:
                self.instrucao = "Negotiate: escolha a segunda carta da trilha."
            else:
                self.instrucao = "Negotiate: clique em uma das duas para pôr o disco."
            return

        if posicao_trilha not in self.posicoes_trilha:
            self.instrucao = "O disco deve ficar em uma das cartas escolhidas."
            return

        parametros = {
            "posicao_a": self.posicoes_trilha[0],
            "posicao_b": self.posicoes_trilha[1],
            "posicao_disco": posicao_trilha,
        }
        self._tentar_jogar_carta(parametros)

    def _processar_troca_de_seguidores(self, posicao):
        if len(self.regioes_troca) == len(self.faccoes_troca):
            nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

            if nome_regiao is not None:
                self.regioes_troca.append(nome_regiao)
                self.instrucao = "Escolha a facção que sairá de " + nome_regiao + "."
            return

        faccao = self.visao.obter_faccao_clicada(posicao)

        if faccao is None:
            return

        self.faccoes_troca.append(faccao)

        if len(self.faccoes_troca) == 1:
            self.instrucao = "Escolha a segunda região da troca."
            return

        parametros = {
            "regiao_a": self.regioes_troca[0],
            "faccao_a": self.faccoes_troca[0],
            "regiao_b": self.regioes_troca[1],
            "faccao_b": self.faccoes_troca[1],
        }
        self._tentar_jogar_carta(parametros)

    def _processar_convocacao(self, posicao):
        if self.regiao_convocacao is None:
            nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

            if nome_regiao is not None:
                self.regiao_convocacao = nome_regiao
                self.instrucao = "Escolha a facção que será convocada para a corte."
            return

        faccao = self.visao.obter_faccao_clicada(posicao)

        if faccao is None:
            return

        try:
            self.jogo.convocar_seguidor(self.regiao_convocacao, faccao)
            self._limpar_selecao()
            self.instrucao = "Escolha uma carta de ação ou passe."
        except (TypeError, ValueError) as erro:
            self.regiao_convocacao = None
            self.instrucao = "Erro: " + str(erro) + " Escolha novamente."

    def _tentar_jogar_carta(self, parametros):
        try:
            self.jogo.jogar_carta(self.carta_selecionada, parametros)
            self.carta_selecionada = None
            self.destinos_assemble = {}
            self.regioes_troca = []
            self.faccoes_troca = []
            self.posicoes_trilha = []
            self.instrucao = "Convocação obrigatória: escolha uma região."
        except (TypeError, ValueError) as erro:
            mensagem_erro = str(erro)
            self.destinos_assemble = {}
            self.regioes_troca = []
            self.faccoes_troca = []
            self.posicoes_trilha = []
            self._atualizar_instrucao_da_carta()
            self.instrucao = "Erro: " + mensagem_erro + " " + self.instrucao

    def _atualizar_instrucao_da_carta(self):
        tipo = self.carta_selecionada.tipo

        if tipo == TipoCartaAcao.REUNIR:
            primeira = None
            for faccao in Faccao:
                if self.jogo.estado.reserva.quantidade(faccao) > 0:
                    primeira = faccao
                    break
            if primeira is None:
                self.instrucao = "Assemble não tem efeito. Use SEM EFEITO."
            else:
                self.instrucao = "Assemble: clique na região dos " + primeira.value + "."
        elif tipo in [
            TipoCartaAcao.APOIO_ESCOCES,
            TipoCartaAcao.APOIO_GALES,
            TipoCartaAcao.APOIO_INGLES,
        ]:
            self.instrucao = "Support: clique na região que receberá os seguidores."
        elif tipo == TipoCartaAcao.NEGOCIAR:
            self.instrucao = "Negotiate: escolha a primeira carta da trilha."
        else:
            self.instrucao = "Escolha a primeira região da troca."

    def _limpar_selecao(self):
        self.carta_selecionada = None
        self.destinos_assemble = {}
        self.regioes_troca = []
        self.faccoes_troca = []
        self.posicoes_trilha = []
        self.regiao_convocacao = None

    def _obter_selecao(self):
        return {
            "carta": self.carta_selecionada,
            "destinos_assemble": self.destinos_assemble.copy(),
            "regioes_troca": self.regioes_troca.copy(),
            "posicoes_trilha": self.posicoes_trilha.copy(),
            "regiao_convocacao": self.regiao_convocacao,
        }
