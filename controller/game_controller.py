from copy import deepcopy
import os
from queue import Queue
from threading import Thread
from time import perf_counter

import pygame

from model.action_card import eh_carta_de_apoio
from model.enums import (
    Faccao,
    FaseTurno,
    TipoCartaAcao,
    TipoJogada,
    TipoJogador,
)
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada
from model.match_settings import TIPOS_COM_LIMITE_DE_TEMPO, ConfiguracaoPartida
from model.minimax_agent import AgenteMinimax
from model.monte_carlo_agent import AgenteMonteCarlo
from model.q_learning_agent import CAMINHO_TABELA_Q_JOGO, AgenteQLearning, TabelaQ
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
        configuracao_partida=None,
        caminho_tabela_q=CAMINHO_TABELA_Q_JOGO,
    ):
        self.jogo = jogo
        self.visao = visao
        if configuracao_partida is None:
            configuracao_partida = ConfiguracaoPartida()
        self.configuracao_partida = configuracao_partida
        self.caminho_tabela_q = caminho_tabela_q
        self._tabela_q = None

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
        self.ia_pausada = False
        self.ultima_decisao_ia = None
        self._fila_ia = Queue()
        self._tarefa_ia = None
        self._estado_busca_ia = None
        self._inicio_busca_ia = None
        self._erro_ia = ""

    def _possui_ia(self):
        for indice in range(2):
            if self.configuracao_partida.obter_tipo_jogador(indice) != TipoJogador.HUMANO:
                return True
        return False

    def _turno_da_ia(self):
        indice = self.jogo.estado.indice_jogador_atual
        return self.configuracao_partida.obter_tipo_jogador(indice) != TipoJogador.HUMANO

    def _alternar_pausa_ia(self):
        self.ia_pausada = not self.ia_pausada
        if not self.ia_pausada:
            self._erro_ia = ""
        self.instrucao = self._obter_status_ia()
        if not self.instrucao:
            self.instrucao = "IA liberada para o próximo turno."

    def _obter_status_ia(self):
        """Descreve a situação real da busca, inclusive depois de retomar."""
        if self._tarefa_ia is not None:
            segundos = perf_counter() - self._inicio_busca_ia
            tempo = format(segundos, ".1f") + " s"
            if self.jogo.estado is not self._estado_busca_ia:
                return (
                    "A posição mudou. Aguardando o cálculo anterior terminar para "
                    "descartá-lo (" + tempo + "). Ele não alterará o tabuleiro."
                )
            pronta = not self._fila_ia.empty()
            if self.ia_pausada:
                if pronta:
                    return "IA pausada. Jogada pronta; clique em RETOMAR IA para aplicá-la."
                return (
                    "IA pausada. O cálculo continua (" + tempo
                    + "), mas não será aplicado até clicar em RETOMAR IA."
                )
            if pronta:
                if self.arvore_aberta:
                    return "Jogada pronta. Feche a árvore para a partida continuar."
                return "Jogada calculada. Aplicando o resultado..."
            indice = self._estado_busca_ia.indice_jogador_atual
            nome = self._estado_busca_ia.obter_jogador_atual().nome
            tipo_jogador = self.configuracao_partida.obter_tipo_jogador(indice)
            tipo = tipo_jogador.value
            if tipo_jogador == TipoJogador.MONTE_CARLO:
                detalhe = (
                    str(self.configuracao_partida.obter_simulacoes_monte_carlo(indice))
                    + " simulações"
                )
            elif tipo_jogador == TipoJogador.Q_LEARNING:
                detalhe = "tabela treinada"
            else:
                profundidade = self.configuracao_partida.obter_profundidade(indice)
                limite = self.configuracao_partida.obter_limite_tempo(indice)
                if limite is None:
                    detalhe = f"profundidade {profundidade}"
                else:
                    detalhe = f"até profundidade {profundidade}, limite de {limite} s"
            mensagem = (
                nome + " calculando com " + tipo + ", " + detalhe
                + ". Decorrido: " + tempo + "."
            )
            if segundos >= 10:
                mensagem += (
                    " Muitas opções podem tornar a busca demorada. "
                    "Você pode pausar a aplicação ou salvar a posição."
                )
            return mensagem
        if self.ia_pausada:
            if self._erro_ia:
                return self._erro_ia
            return "IA pausada. Clique em RETOMAR IA para continuar os turnos automáticos."
        return ""

    def _calcular_jogada_ia(
        self, estado, indice, tipo, profundidade, simulacoes=100, limite_segundos=None
    ):
        """Calcula sobre uma cópia e envia o resultado sem acessar o Pygame."""
        inicio = perf_counter()
        resultado = {"erro": None}
        try:
            if tipo == TipoJogador.MONTE_CARLO:
                agente = AgenteMonteCarlo(indice)
                jogada = agente.escolher_jogada(
                    estado,
                    quantidade_simulacoes=simulacoes,
                )
            elif tipo == TipoJogador.Q_LEARNING:
                if self._tabela_q is None:
                    try:
                        self._tabela_q = TabelaQ.carregar(self.caminho_tabela_q)
                    except (OSError, ValueError) as erro:
                        raise ValueError("Não foi possível carregar a tabela Q: " + str(erro)) from erro
                agente = AgenteQLearning(self._tabela_q, analisar_finais=True)
                jogada = agente.escolher_jogada(estado)
            else:
                agente = AgenteMinimax(indice)
                opcoes = {} if limite_segundos is None else {"limite_segundos": limite_segundos}
                jogada = agente.escolher_jogada(
                    estado,
                    profundidade_maxima=profundidade,
                    usar_poda=tipo == TipoJogador.ALFA_BETA,
                    **opcoes,
                )
            novo_estado = None
            if jogada is not None:
                novo_estado = ExecutorJogada().executar(estado, jogada)
            resultado.update({
                "jogada": jogada,
                "estado": novo_estado,
                "jogador": indice,
                "algoritmo": tipo.value,
                "profundidade": profundidade,
                "limite_segundos": limite_segundos,
                "profundidade_concluida": (
                    profundidade if limite_segundos is None else agente.profundidade_concluida
                ),
                "tempo_esgotado": limite_segundos is not None and agente.tempo_esgotado,
                "simulacoes_configuradas": (
                    simulacoes if tipo == TipoJogador.MONTE_CARLO else 0
                ),
                "pontuacao": agente.ultima_pontuacao,
                "nos_visitados": agente.nos_visitados,
                "folhas_avaliadas": agente.folhas_avaliadas,
                "podas_realizadas": agente.podas_realizadas,
                "simulacoes_realizadas": getattr(
                    agente,
                    "simulacoes_realizadas",
                    0,
                ),
                "busca_final_concluida": getattr(agente, "busca_final_concluida", False),
                "busca_final_alterou": getattr(agente, "busca_final_alterou", False),
            })
        except Exception as erro:
            # Um erro na thread precisa chegar ao Controller, sem sumir em silêncio.
            resultado["erro"] = str(erro)
        resultado["tempo_segundos"] = perf_counter() - inicio
        self._fila_ia.put(resultado)

    def _iniciar_busca_ia(self):
        estado = self.jogo.estado
        indice = estado.indice_jogador_atual
        tipo = self.configuracao_partida.obter_tipo_jogador(indice)
        profundidade = self.configuracao_partida.obter_profundidade(indice)
        simulacoes = self.configuracao_partida.obter_simulacoes_monte_carlo(indice)
        limite = None
        if tipo in TIPOS_COM_LIMITE_DE_TEMPO:
            limite = self.configuracao_partida.obter_limite_tempo(indice)
        copia = SerializadorEstadoJogo().copiar(estado)
        self._estado_busca_ia = estado
        self._inicio_busca_ia = perf_counter()
        self._erro_ia = ""
        self._tarefa_ia = Thread(
            target=self._calcular_jogada_ia,
            args=(copia, indice, tipo, profundidade, simulacoes, limite),
            daemon=True,
        )
        self.instrucao = self._obter_status_ia()
        self._tarefa_ia.start()

    def _receber_jogada_ia(self):
        if self._fila_ia.empty():
            return

        # Uma volta troca o objeto de estado, mesmo se o conteúdo for igual.
        estado_mudou = self.jogo.estado is not self._estado_busca_ia
        if not estado_mudou and (self.ia_pausada or self.arvore_aberta):
            return

        resultado = self._fila_ia.get_nowait()
        self._tarefa_ia = None
        self._estado_busca_ia = None
        self._inicio_busca_ia = None
        if estado_mudou:
            return

        if resultado["erro"] is not None:
            self.ia_pausada = True
            self._erro_ia = (
                "Erro na IA: " + resultado["erro"]
                + ". A posição foi preservada e a IA está pausada. "
                "Use RETOMAR IA para tentar novamente ou SALVAR para guardar a partida."
            )
            self.instrucao = self._erro_ia
            return
        if resultado["jogada"] is None:
            self.ia_pausada = True
            self._erro_ia = (
                "A IA não retornou uma jogada completa. Nenhuma ação foi aplicada. "
                "IA pausada: use RETOMAR IA para tentar novamente ou SALVAR."
            )
            self.instrucao = self._erro_ia
            return

        try:
            self._registrar_jogada_realizada(
                resultado["jogada"], resultado["estado"]
            )
        except (TypeError, ValueError) as erro:
            self.ia_pausada = True
            self._erro_ia = (
                "Não foi possível registrar a jogada da IA: " + str(erro)
                + ". A posição foi preservada. IA pausada; use RETOMAR IA para tentar novamente."
            )
            self.instrucao = self._erro_ia
            return

        self._limpar_selecao()
        self.ultima_decisao_ia = resultado
        resumo = self._obter_resumo_ia()
        if not (
            self.jogo.estado.finalizado
            and self.caminho_salvamento is not None
            and not self.arvore_salva
        ):
            self.instrucao = resumo

    def _obter_resumo_ia(self):
        resultado = self.ultima_decisao_ia
        if resultado is None:
            return ""
        if resultado["algoritmo"] == TipoJogador.MONTE_CARLO.value:
            return (
                resultado["algoritmo"] + " | "
                + str(resultado["simulacoes_realizadas"])
                + " simulações | "
                + format(resultado["tempo_segundos"], ".3f") + " s | "
                + str(resultado["nos_visitados"]) + " estados simulados."
            )
        if resultado["algoritmo"] == TipoJogador.Q_LEARNING.value:
            detalhe = "tabela treinada"
            if resultado.get("busca_final_alterou"):
                detalhe = "jogada ajustada pela busca de final"
            elif resultado.get("busca_final_concluida"):
                detalhe = "jogada confirmada pela busca de final"
            return (
                resultado["algoritmo"] + " | " + detalhe + " | "
                + format(resultado["tempo_segundos"], ".3f") + " s."
            )
        profundidade = resultado["profundidade"]
        detalhe = f"profundidade {profundidade}"
        limite = resultado.get("limite_segundos")
        if limite is not None:
            concluida = resultado["profundidade_concluida"]
            if concluida:
                detalhe = f"profundidade {concluida} de {profundidade}"
            elif resultado["pontuacao"] is not None:
                detalhe = "profundidade 1 parcial"
            else:
                detalhe = "passe de segurança"
            if resultado["tempo_esgotado"]:
                detalhe += f" | limite de {limite} s atingido"
        return (
            resultado["algoritmo"] + " | " + detalhe + " | "
            + format(resultado["tempo_segundos"], ".3f") + " s | "
            + str(resultado["nos_visitados"]) + " nós | "
            + str(resultado["podas_realizadas"]) + " cortes."
        )

    def _atualizar_turno_ia(self):
        """Verifica o cálculo sem bloquear o loop principal da janela."""
        if not self.executando:
            return
        if self._tarefa_ia is not None:
            self._receber_jogada_ia()
            return
        estado = self.jogo.estado
        if (
            estado.finalizado or self.ia_pausada or self.arvore_aberta
            or not self._turno_da_ia()
            or estado.fase_turno != FaseTurno.ESCOLHER_ACAO
        ):
            return
        self._iniciar_busca_ia()

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

    def _registrar_jogada_realizada(self, jogada, estado_resultante):
        self.arvore.registrar_jogada_realizada(
            jogada,
            estado_resultante,
        )
        self.jogo.estado = estado_resultante
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
                configuracao_partida=self.configuracao_partida,
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
                jogada = Jogada(TipoJogada.PASSE)
                resultado = ExecutorJogada().executar(self.jogo.estado, jogada)
                self._registrar_jogada_realizada(jogada, resultado)
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
        if len(faccoes_pendentes) > 1:
            self._mostrar_ajuda_da_carta(
                "clique na região dos "
                + faccoes_pendentes[1].value
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
            jogada = Jogada(
                TipoJogada.CARTA,
                tipo_carta=dados["tipo_carta"],
                parametros=dados["parametros"],
                nome_regiao_convocacao=nome_regiao,
                faccao_convocacao=faccao,
            )
            resultado = ExecutorJogada().executar_convocacao(
                self.jogo.estado, nome_regiao, faccao
            )
            self._registrar_jogada_realizada(jogada, resultado)
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
        self.ultima_decisao_ia = None
        if self._possui_ia():
            self._erro_ia = ""
            self.ia_pausada = True
            self.instrucao += " IA pausada; use RETOMAR IA para continuar."

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

        if self._possui_ia() and self.visao.botao_pausar_ia_foi_clicado(posicao):
            self._alternar_pausa_ia()
            return

        if self._turno_da_ia():
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
                return

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
        instrucao = self._obter_status_ia() or self.instrucao
        self.visao.desenhar(
            self.jogo.estado,
            selecao,
            instrucao,
            self.arvore,
            self.arvore_aberta,
            self.pagina_arvore,
            self.mensagem_arvore,
            self.texto_pagina_arvore,
            self.campo_pagina_arvore_ativo,
            self._possui_ia(),
            self.ia_pausada,
            self._obter_resumo_ia(),
        )

    def executar(self):
        """Mantém o loop principal ativo até o fechamento da janela."""
        while self.executando:
            self._processar_eventos()
            self._atualizar_turno_ia()
            self._desenhar_quadro()
            self.relogio.tick(QUADROS_POR_SEGUNDO)

        self._salvar_arvore()
