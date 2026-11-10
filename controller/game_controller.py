from copy import deepcopy
import os

import pygame

from model.action_card import eh_carta_de_apoio
from model.enums import (
    Faccao,
    FaseTurno,
    TipoCartaAcao,
    TipoJogada,
)
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada
from model.state_tree import ArvoreEstados
from model.state_tree_serializer import SerializadorArvoreEstados
from view.state_tree_graphviz_view import VisaoArvoreGraphviz


QUADROS_POR_SEGUNDO = 60


class ControladorJogo:
    """Transforma os cliques do usuário em comandos para o Model."""

    def __init__(
        self,
        jogo,
        visao,
        arvore=None,
        serializador_arvore=None,
        caminho_salvamento=None,
    ):
        self.jogo = jogo
        self.visao = visao

        if arvore is None:
            arvore = ArvoreEstados(jogo.estado)

        if serializador_arvore is None:
            serializador_arvore = SerializadorArvoreEstados()

        self.arvore = arvore
        self.serializador_arvore = serializador_arvore
        self.caminho_salvamento = caminho_salvamento
        self.visualizador_graphviz = VisaoArvoreGraphviz()
        self.caminho_graphviz = None

        if caminho_salvamento is not None:
            pasta = os.path.dirname(caminho_salvamento)
            self.caminho_graphviz = os.path.join(
                pasta,
                "state_tree.svg",
            )

        self._validar_sincronia_inicial()

        self.relogio = pygame.time.Clock()
        self.executando = True
        self.carta_selecionada = None
        self.jogada_pendente = None
        self.destinos_assemble = {}
        self.regioes_troca = []
        self.faccoes_troca = []
        self.posicoes_trilha = []
        self.regiao_convocacao = None
        self.arvore_aberta = False
        self.pagina_arvore = 0
        self.texto_pagina_arvore = "1"
        self.campo_pagina_arvore_ativo = False
        self.mensagem_arvore = ""
        self.arvore_salva = False
        self.instrucao = "Escolha uma carta de ação ou passe."

    def _validar_sincronia_inicial(self):
        comparador = SerializadorEstadoJogo()
        estado_da_arvore = self.arvore.obter_estado_atual()

        if not comparador.possuem_mesmo_estado(
            self.jogo.estado,
            estado_da_arvore,
        ):
            raise ValueError(
                "O jogo e a árvore devem começar no mesmo estado."
            )

    def _mostrar_ajuda_da_carta(self, proximo_passo):
        carta = self.carta_selecionada
        self.instrucao = (
            "Carta: "
            + carta.nome
            + ". Efeito: "
            + carta.descricao
            + " Próximo passo: "
            + proximo_passo
        )

    def _atualizar_instrucao_da_carta(self):
        tipo = self.carta_selecionada.tipo
        proximo_passo = ""

        if tipo == TipoCartaAcao.REUNIR:
            primeira = None

            for faccao in Faccao:
                if self.jogo.estado.reserva.quantidade(faccao) > 0:
                    primeira = faccao
                    break

            if primeira is None:
                proximo_passo = "use o botão SEM EFEITO."
            else:
                proximo_passo = (
                    "clique na região dos " + primeira.value + "."
                )
        elif eh_carta_de_apoio(tipo):
            proximo_passo = (
                "clique na região que receberá os seguidores."
            )
        elif tipo == TipoCartaAcao.NEGOCIAR:
            proximo_passo = "escolha a primeira carta da trilha."
        else:
            proximo_passo = "escolha a primeira região da troca."

        self._mostrar_ajuda_da_carta(proximo_passo)

    def _registrar_jogada_realizada(self, jogada):
        self.arvore.registrar_jogada_realizada(
            jogada,
            self.jogo.estado,
        )
        self.arvore_salva = False
        self._reiniciar_paginacao_arvore()

        if self.jogo.estado.finalizado:
            self._salvar_arvore()

    def _salvar_arvore(self):
        if self.caminho_salvamento is None:
            return False

        if self.arvore_salva:
            return True

        try:
            self.serializador_arvore.salvar(
                self.arvore,
                self.caminho_salvamento,
            )
            self.arvore_salva = True
            return True
        except (OSError, TypeError, ValueError) as erro:
            self.instrucao = "Não foi possível salvar a árvore: " + str(
                erro
            )
            return False

    def _processar_inicio_da_jogada(self, posicao):
        if self.visao.botao_passar_foi_clicado(
            posicao,
            self.jogo.estado,
        ):
            try:
                self.jogo.passar()
                jogada = Jogada(TipoJogada.PASSE)
                self._registrar_jogada_realizada(jogada)
                self.instrucao = (
                    "Escolha uma carta de ação ou passe."
                )
            except (TypeError, ValueError) as erro:
                self.instrucao = "Erro: " + str(erro)

            return

        indice = self.visao.obter_indice_carta_clicada(
            posicao,
            self.jogo.estado,
        )

        if indice is None:
            return

        mao = self.jogo.estado.obter_jogador_atual().obter_mao()
        self.carta_selecionada = mao[indice]
        self._atualizar_instrucao_da_carta()

    def _tentar_jogar_carta(self, parametros):
        try:
            tipo_carta = self.carta_selecionada.tipo
            self.jogo.jogar_carta(
                self.carta_selecionada,
                parametros,
            )
            self.jogada_pendente = {
                "tipo_carta": tipo_carta,
                "parametros": deepcopy(parametros),
            }
            self._mostrar_ajuda_da_carta(
                "escolha uma região e uma facção para a convocação."
            )
            self.carta_selecionada = None
            self._limpar_parametros_da_carta()
        except (TypeError, ValueError) as erro:
            mensagem_erro = str(erro)
            self._limpar_parametros_da_carta()
            self._atualizar_instrucao_da_carta()
            self.instrucao = (
                "Erro: "
                + mensagem_erro
                + " "
                + self.instrucao
            )

    def _processar_assemble(self, posicao):
        nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

        if nome_regiao is None:
            return

        faccoes_pendentes = []

        for faccao in Faccao:
            disponivel = (
                self.jogo.estado.reserva.quantidade(faccao) > 0
            )

            if disponivel and faccao not in self.destinos_assemble:
                faccoes_pendentes.append(faccao)

        if not faccoes_pendentes:
            self._tentar_jogar_carta(
                {"destinos": self.destinos_assemble}
            )
            return

        faccao = faccoes_pendentes[0]
        self.destinos_assemble[faccao] = nome_regiao
        ainda_pendentes = []

        for outra_faccao in Faccao:
            disponivel = (
                self.jogo.estado.reserva.quantidade(outra_faccao) > 0
            )

            if (
                disponivel
                and outra_faccao not in self.destinos_assemble
            ):
                ainda_pendentes.append(outra_faccao)

        if ainda_pendentes:
            self._mostrar_ajuda_da_carta(
                "clique na região dos "
                + ainda_pendentes[0].value
                + "."
            )
        else:
            self._tentar_jogar_carta(
                {"destinos": self.destinos_assemble}
            )

    def _processar_support(self, posicao):
        nome_regiao = self.visao.obter_nome_regiao_clicada(posicao)

        if nome_regiao is not None:
            self._tentar_jogar_carta({"regiao": nome_regiao})

    def _processar_negotiate(self, posicao):
        posicao_trilha = self.visao.obter_posicao_trilha_clicada(
            posicao
        )

        if posicao_trilha is None:
            return

        if len(self.posicoes_trilha) < 2:
            if posicao_trilha in self.posicoes_trilha:
                self._mostrar_ajuda_da_carta(
                    "escolha duas posições diferentes."
                )
                return

            self.posicoes_trilha.append(posicao_trilha)

            if len(self.posicoes_trilha) == 1:
                self._mostrar_ajuda_da_carta(
                    "escolha a segunda carta da trilha."
                )
            else:
                self._mostrar_ajuda_da_carta(
                    "clique em uma das duas para pôr o disco."
                )

            return

        if posicao_trilha not in self.posicoes_trilha:
            self._mostrar_ajuda_da_carta(
                "o disco deve ficar em uma das cartas escolhidas."
            )
            return

        parametros = {
            "posicao_a": self.posicoes_trilha[0],
            "posicao_b": self.posicoes_trilha[1],
            "posicao_disco": posicao_trilha,
        }
        self._tentar_jogar_carta(parametros)

    def _processar_troca_de_seguidores(self, posicao):
        if len(self.regioes_troca) == len(self.faccoes_troca):
            nome_regiao = self.visao.obter_nome_regiao_clicada(
                posicao
            )

            if nome_regiao is not None:
                self.regioes_troca.append(nome_regiao)
                self._mostrar_ajuda_da_carta(
                    "escolha a facção que sairá de "
                    + nome_regiao
                    + "."
                )

            return

        faccao = self.visao.obter_faccao_clicada(posicao)

        if faccao is None:
            return

        self.faccoes_troca.append(faccao)

        if len(self.faccoes_troca) == 1:
            self._mostrar_ajuda_da_carta(
                "escolha a segunda região da troca."
            )
            return

        parametros = {
            "regiao_a": self.regioes_troca[0],
            "faccao_a": self.faccoes_troca[0],
            "regiao_b": self.regioes_troca[1],
            "faccao_b": self.faccoes_troca[1],
        }
        self._tentar_jogar_carta(parametros)

    def _limpar_parametros_da_carta(self):
        self.destinos_assemble = {}
        self.regioes_troca = []
        self.faccoes_troca = []
        self.posicoes_trilha = []

    def _limpar_selecao(self):
        self.carta_selecionada = None
        self.jogada_pendente = None
        self._limpar_parametros_da_carta()
        self.regiao_convocacao = None

    def _reiniciar_paginacao_arvore(self):
        self.pagina_arvore = 0
        self.texto_pagina_arvore = "1"
        self.campo_pagina_arvore_ativo = False

    def _processar_convocacao(self, posicao):
        if self.regiao_convocacao is None:
            nome_regiao = self.visao.obter_nome_regiao_clicada(
                posicao
            )

            if nome_regiao is not None:
                self.regiao_convocacao = nome_regiao
                self.instrucao = (
                    "Escolha a facção que será convocada para a corte."
                )

            return

        faccao = self.visao.obter_faccao_clicada(posicao)

        if faccao is None:
            return

        try:
            dados = self.jogada_pendente
            nome_regiao = self.regiao_convocacao
            self.jogo.convocar_seguidor(nome_regiao, faccao)
            jogada = Jogada(
                TipoJogada.CARTA,
                tipo_carta=dados["tipo_carta"],
                parametros=dados["parametros"],
                nome_regiao_convocacao=nome_regiao,
                faccao_convocacao=faccao,
            )
            self._registrar_jogada_realizada(jogada)
            self._limpar_selecao()
            self.instrucao = (
                "Escolha uma carta de ação ou passe."
            )
        except (TypeError, ValueError) as erro:
            self.regiao_convocacao = None
            self.instrucao = (
                "Erro: "
                + str(erro)
                + " Escolha novamente."
            )

    def _pode_voltar_jogada(self):
        fase = self.jogo.estado.fase_turno
        fase_permitida = fase in [
            FaseTurno.ESCOLHER_ACAO,
            FaseTurno.ENCERRADO,
        ]

        return (
            fase_permitida
            and self.carta_selecionada is None
            and not self.arvore.obter_no_atual().eh_raiz()
        )

    def _voltar_jogada(self):
        if not self._pode_voltar_jogada():
            self.instrucao = (
                "Só é possível voltar depois de concluir uma jogada."
            )
            return

        self.arvore.voltar()
        self.jogo.estado = self.arvore.obter_estado_atual()
        self.arvore_salva = False
        self._reiniciar_paginacao_arvore()
        self._limpar_selecao()
        self.instrucao = "A última jogada foi desfeita."

    def _ir_para_pagina_digitada(self):
        total_paginas = self.visao.obter_quantidade_paginas_arvore(
            self.arvore
        )
        texto = self.texto_pagina_arvore

        if not texto:
            self.mensagem_arvore = "Digite o número da página."
            return

        numero_pagina = int(texto)

        if numero_pagina < 1 or numero_pagina > total_paginas:
            self.mensagem_arvore = (
                "Escolha uma página entre 1 e "
                + str(total_paginas)
                + "."
            )
            return

        self.pagina_arvore = numero_pagina - 1
        self.campo_pagina_arvore_ativo = False
        self.mensagem_arvore = (
            "Página " + str(numero_pagina) + " selecionada."
        )

    def _processar_tecla_da_arvore(self, evento):
        if not self.arvore_aberta or not self.campo_pagina_arvore_ativo:
            return

        if evento.key == pygame.K_RETURN:
            self._ir_para_pagina_digitada()
            return

        if evento.key == pygame.K_ESCAPE:
            self.campo_pagina_arvore_ativo = False
            self.texto_pagina_arvore = str(self.pagina_arvore + 1)
            return

        if evento.key == pygame.K_BACKSPACE:
            self.texto_pagina_arvore = self.texto_pagina_arvore[:-1]
            return

        texto_digitado = getattr(evento, "unicode", "")

        if texto_digitado.isdigit() and len(self.texto_pagina_arvore) < 6:
            self.texto_pagina_arvore += texto_digitado

    def _processar_clique_da_arvore(self, posicao):
        if self.visao.botao_fechar_arvore_foi_clicado(posicao):
            self.arvore_aberta = False
            self.campo_pagina_arvore_ativo = False
            return

        if self.visao.campo_pagina_arvore_foi_clicado(posicao):
            self.campo_pagina_arvore_ativo = True
            self.texto_pagina_arvore = ""
            self.mensagem_arvore = (
                "Digite a página e pressione ENTER ou IR."
            )
            return

        if self.visao.botao_ir_pagina_foi_clicado(posicao):
            self._ir_para_pagina_digitada()
            return

        if self.visao.botao_pagina_anterior_foi_clicado(posicao):
            if self.pagina_arvore > 0:
                self.pagina_arvore -= 1
                self.texto_pagina_arvore = str(self.pagina_arvore + 1)
            self.campo_pagina_arvore_ativo = False
            return

        if self.visao.botao_proxima_pagina_foi_clicado(posicao):
            total_paginas = (
                self.visao.obter_quantidade_paginas_arvore(
                    self.arvore
                )
            )

            if self.pagina_arvore + 1 < total_paginas:
                self.pagina_arvore += 1
                self.texto_pagina_arvore = str(self.pagina_arvore + 1)
            self.campo_pagina_arvore_ativo = False
            return

        if self.visao.botao_exportar_graphviz_foi_clicado(posicao):
            if self.caminho_graphviz is None:
                self.mensagem_arvore = (
                    "Não existe um caminho para exportar a árvore."
                )
                return

            self.mensagem_arvore = "Gerando a árvore completa. Aguarde..."
            self._desenhar_quadro()

            try:
                caminho = self.visualizador_graphviz.exportar(
                    self.arvore,
                    self.caminho_graphviz,
                )
                self.mensagem_arvore = "Árvore aberta em " + caminho
            except (OSError, RuntimeError, TypeError, ValueError) as erro:
                self.mensagem_arvore = "Erro no Graphviz: " + str(erro)

            return

        if self.visao.botao_gerar_opcoes_foi_clicado(posicao):
            if self.arvore.obter_no_atual().esta_expandido():
                self.mensagem_arvore = (
                    "As opções deste estado já foram geradas."
                )
                return

            self.mensagem_arvore = (
                "Gerando jogadas possíveis. Aguarde..."
            )
            self._desenhar_quadro()

            try:
                filhos = self.arvore.expandir_no_atual()
                self.mensagem_arvore = (
                    str(len(filhos))
                    + " jogadas possíveis foram geradas."
                )
                self._reiniciar_paginacao_arvore()
                self.arvore_salva = False
            except (TypeError, ValueError) as erro:
                self.mensagem_arvore = (
                    "Erro ao gerar opções: " + str(erro)
                )

    def _processar_clique(self, posicao):
        if self.arvore_aberta:
            self._processar_clique_da_arvore(posicao)
            return

        if self.visao.botao_salvar_foi_clicado(posicao):
            salvou = self._salvar_arvore()

            if salvou:
                self.instrucao = "Partida salva com sucesso."
            elif self.caminho_salvamento is None:
                self.instrucao = "Não existe um caminho para salvar a partida."

            return

        if self.visao.botao_arvore_foi_clicado(posicao):
            self.arvore_aberta = True
            self._reiniciar_paginacao_arvore()
            self.mensagem_arvore = ""
            return

        if self.visao.botao_voltar_jogada_foi_clicado(posicao):
            self._voltar_jogada()
            return

        estado = self.jogo.estado

        if estado.finalizado:
            return

        if self.visao.botao_cancelar_foi_clicado(posicao):
            if estado.fase_turno == FaseTurno.ESCOLHER_ACAO:
                self._limpar_selecao()
                self.instrucao = (
                    "Seleção cancelada. Escolha uma carta ou passe."
                )

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
        elif eh_carta_de_apoio(tipo):
            self._processar_support(posicao)
        elif tipo == TipoCartaAcao.NEGOCIAR:
            self._processar_negotiate(posicao)
        elif tipo in [
            TipoCartaAcao.MANOBRAR,
            TipoCartaAcao.SUPERAR_MANOBRA,
        ]:
            self._processar_troca_de_seguidores(posicao)

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False

            if evento.type == pygame.KEYDOWN:
                self._processar_tecla_da_arvore(evento)

            if (
                evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
            ):
                self._processar_clique(evento.pos)

    def _obter_selecao(self):
        return {
            "carta": self.carta_selecionada,
            "destinos_assemble": self.destinos_assemble.copy(),
            "regioes_troca": self.regioes_troca.copy(),
            "posicoes_trilha": self.posicoes_trilha.copy(),
            "regiao_convocacao": self.regiao_convocacao,
        }

    def _desenhar_quadro(self):
        selecao = self._obter_selecao()
        self.visao.desenhar(
            self.jogo.estado,
            selecao,
            self.instrucao,
            self.arvore,
            self.arvore_aberta,
            self.pagina_arvore,
            self.mensagem_arvore,
            self.texto_pagina_arvore,
            self.campo_pagina_arvore_ativo,
        )

    def executar(self):
        """Mantém o loop principal ativo até o fechamento da janela."""
        while self.executando:
            self._processar_eventos()
            self._desenhar_quadro()
            self.relogio.tick(QUADROS_POR_SEGUNDO)

        self._salvar_arvore()
