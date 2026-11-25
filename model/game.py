from collections import Counter

from model.action_card import (
    CartaAcao,
    eh_carta_de_apoio,
    obter_dados_da_carta_de_apoio,
)
from model.enums import Faccao, FaseTurno, TipoCartaAcao


class Jogo:
    """Executa as regras do modo básico para dois jogadores."""

    def __init__(self, estado):
        self.estado = estado

    def obter_regioes_validas_para_apoio(self, tipo_carta):
        """Retorna regiões que podem receber uma carta Support."""
        faccao, nome_regiao_inicial = obter_dados_da_carta_de_apoio(
            tipo_carta
        )
        nomes_validos = []
        tabuleiro = self.estado.tabuleiro
        regiao_inicial = tabuleiro.obter_regiao(nome_regiao_inicial)

        for nome_candidata in tabuleiro.obter_nomes_das_regioes():
            candidata = tabuleiro.obter_regiao(nome_candidata)

            if candidata.esta_resolvida():
                continue

            pode_receber = False

            if not regiao_inicial.esta_resolvida():
                if tabuleiro.sao_adjacentes(nome_candidata, nome_regiao_inicial):
                    pode_receber = True

            for outra_regiao in tabuleiro.obter_regioes().values():
                if outra_regiao.controlador == faccao:
                    if tabuleiro.sao_adjacentes(nome_candidata, outra_regiao.nome):
                        pode_receber = True

            if pode_receber:
                nomes_validos.append(nome_candidata)

        return nomes_validos

    def _obter_dados_de_troca(self, parametros, exigir_adjacencia=False):
        nome_a = parametros.get("regiao_a")
        nome_b = parametros.get("regiao_b")
        faccao_a = parametros.get("faccao_a")
        faccao_b = parametros.get("faccao_b")

        if not isinstance(faccao_a, Faccao) or not isinstance(faccao_b, Faccao):
            raise TypeError("As duas facções da troca devem ser informadas.")

        if nome_a == nome_b:
            raise ValueError("A troca deve utilizar duas regiões diferentes.")

        regiao_a = self.estado.tabuleiro.obter_regiao(nome_a)
        regiao_b = self.estado.tabuleiro.obter_regiao(nome_b)

        if regiao_a.esta_resolvida() or regiao_b.esta_resolvida():
            raise ValueError("Não é possível alterar uma região resolvida.")

        if exigir_adjacencia:
            if not self.estado.tabuleiro.sao_adjacentes(nome_a, nome_b):
                raise ValueError("Outmanoeuvre exige regiões adjacentes.")

        return regiao_a, faccao_a, regiao_b, faccao_b

    def obter_trocas_superar_manobra(self):
        """Retorna pares ordenados pela origem e a quantidade exigida no destino."""
        tabuleiro = self.estado.tabuleiro
        regioes = {
            regiao.nome: regiao
            for regiao in tabuleiro.obter_regioes_com_seguidores()
        }
        pares = []
        quantidade_destino = 0
        for nome_a, regiao_a in regioes.items():
            for nome_b in sorted(tabuleiro.regioes_adjacentes(nome_a)):
                if nome_b not in regioes:
                    continue
                regiao_b = regioes[nome_b]
                pares.append((regiao_a, regiao_b))
                if quantidade_destino < 2:
                    maior_grupo = max(regiao_b.obter_seguidores().values())
                    quantidade_destino = min(maior_grupo, 2)
        return pares, quantidade_destino

    def _obter_ultima_acao_adversaria(self, tipo):
        if self.estado.ultima_acao is None:
            return None

        ultima_acao = self.estado.ultima_acao
        jogador_atual = self.estado.obter_jogador_atual()

        if ultima_acao["tipo"] != tipo:
            return None

        if ultima_acao["jogador"] is jogador_atual:
            return None

        return ultima_acao

    def _validar_manobra_nao_desfaz_acao(self, detalhes):
        ultima_acao = self._obter_ultima_acao_adversaria(TipoCartaAcao.MANOBRAR)

        if ultima_acao is None:
            return

        anterior = ultima_acao["detalhes"]
        desfaz_mesma_ordem = (
            detalhes["regiao_a"] == anterior["regiao_a"]
            and detalhes["faccao_a"] == anterior["faccao_b"]
            and detalhes["regiao_b"] == anterior["regiao_b"]
            and detalhes["faccao_b"] == anterior["faccao_a"]
        )
        desfaz_ordem_invertida = (
            detalhes["regiao_a"] == anterior["regiao_b"]
            and detalhes["faccao_a"] == anterior["faccao_a"]
            and detalhes["regiao_b"] == anterior["regiao_a"]
            and detalhes["faccao_b"] == anterior["faccao_b"]
        )

        if desfaz_mesma_ordem or desfaz_ordem_invertida:
            raise ValueError("Não é permitido desfazer imediatamente a manobra adversária.")

    def _validar_superacao_nao_desfaz_acao(self, detalhes):
        ultima_acao = self._obter_ultima_acao_adversaria(
            TipoCartaAcao.SUPERAR_MANOBRA
        )

        if ultima_acao is None:
            return

        anterior = ultima_acao["detalhes"]
        desfaz = (
            detalhes["regiao_a"] == anterior["regiao_b"]
            and detalhes["faccao_a"] == anterior["faccao_a"]
            and detalhes["regiao_b"] == anterior["regiao_a"]
            and detalhes["faccao_b"] == anterior["faccao_b"]
            and detalhes["quantidade_b"] == anterior["quantidade_b"]
        )

        if desfaz:
            raise ValueError(
                "Não é permitido desfazer imediatamente o Outmanoeuvre adversário."
            )

    def _registrar_carta_jogada(self, carta, detalhes):
        jogador = self.estado.obter_jogador_atual()
        jogador.usar_carta(carta)
        self.estado.passes_consecutivos = 0
        self.estado.ultimo_jogador_que_agiu = jogador
        self.estado.carta_em_execucao = carta
        self.estado.fase_turno = FaseTurno.CONVOCAR_SEGUIDOR
        self.estado.ultima_acao = {
            "jogador": jogador,
            "tipo": carta.tipo,
            "detalhes": detalhes,
            "convocacao": None,
        }

        if jogador.quantidade_cartas() == 0:
            if jogador not in self.estado.ordem_jogadores_sem_cartas:
                self.estado.ordem_jogadores_sem_cartas.append(jogador)

        self.estado.ultima_mensagem = (
            jogador.nome
            + " jogou "
            + carta.nome
            + ". Agora deve convocar um seguidor."
        )

    def _validar_carta_do_jogador(self, carta):
        if not isinstance(carta, CartaAcao):
            raise TypeError("A carta informada não é uma CartaAcao.")

        jogador = self.estado.obter_jogador_atual()

        if not jogador.possui_carta(carta):
            raise ValueError("A carta não pertence à mão do jogador atual.")

    def _validar_convocacao_possivel(self, quantidade_adicionada):
        total = quantidade_adicionada

        for regiao in self.estado.tabuleiro.obter_regioes().values():
            if not regiao.esta_resolvida():
                total += regiao.total_de_seguidores()

        if total == 0:
            raise ValueError("Não existe seguidor no tabuleiro para convocar.")

    def _executar_assemble(self, parametros):
        destinos = parametros.get("destinos", {})

        if not isinstance(destinos, dict):
            raise TypeError("Os destinos de Assemble devem estar em um dicionário.")

        adicoes = []

        for faccao in Faccao:
            if self.estado.reserva.quantidade(faccao) > 0:
                if faccao not in destinos:
                    raise ValueError("Informe uma região para cada facção disponível.")

                nome_regiao = destinos[faccao]
                regiao = self.estado.tabuleiro.obter_regiao(nome_regiao)

                if regiao.esta_resolvida():
                    raise ValueError("Assemble não pode alterar uma região resolvida.")

                adicoes.append((faccao, regiao))

        self._validar_convocacao_possivel(len(adicoes))
        detalhes_destinos = {}

        for faccao, regiao in adicoes:
            self.estado.reserva.retirar(faccao)
            regiao.adicionar_seguidores(faccao)
            detalhes_destinos[faccao] = regiao.nome

        return {"destinos": detalhes_destinos}

    def _executar_apoio(self, tipo_carta, parametros):
        faccao, _ = obter_dados_da_carta_de_apoio(tipo_carta)
        regioes_validas = self.obter_regioes_validas_para_apoio(tipo_carta)
        quantidade_disponivel = self.estado.reserva.quantidade(faccao)
        quantidade_colocada = 0
        nome_regiao = None

        if regioes_validas and quantidade_disponivel > 0:
            nome_regiao = parametros.get("regiao")

            if nome_regiao not in regioes_validas:
                raise ValueError("A região escolhida não pode receber esse apoio.")

            quantidade_colocada = 2

            if quantidade_disponivel < 2:
                quantidade_colocada = quantidade_disponivel

        self._validar_convocacao_possivel(quantidade_colocada)

        if quantidade_colocada > 0:
            regiao = self.estado.tabuleiro.obter_regiao(nome_regiao)
            self.estado.reserva.retirar(faccao, quantidade_colocada)
            regiao.adicionar_seguidores(faccao, quantidade_colocada)

        return {
            "regiao": nome_regiao,
            "faccao": faccao,
            "quantidade": quantidade_colocada,
        }

    def _executar_negociar(self, parametros):
        posicoes_validas = self.estado.trilha_disputas.obter_posicoes_negociaveis()

        if len(posicoes_validas) < 2:
            self._validar_convocacao_possivel(0)
            return {"sem_efeito": True}

        jogador = self.estado.obter_jogador_atual()

        if not jogador.disco_negociacao_disponivel:
            raise ValueError("O jogador não possui disco de negociação disponível.")

        posicao_a = parametros.get("posicao_a")
        posicao_b = parametros.get("posicao_b")
        posicao_disco = parametros.get("posicao_disco")

        if posicao_a == posicao_b:
            raise ValueError("Selecione duas cartas de região diferentes.")

        if posicao_a not in posicoes_validas or posicao_b not in posicoes_validas:
            raise ValueError("Uma das cartas de região não pode ser negociada.")

        if posicao_disco not in [posicao_a, posicao_b]:
            raise ValueError("O disco deve ficar em uma das cartas selecionadas.")

        self._validar_convocacao_possivel(0)
        carta_a = self.estado.trilha_disputas.obter_carta(posicao_a)
        carta_b = self.estado.trilha_disputas.obter_carta(posicao_b)

        if posicao_disco == posicao_a:
            carta_com_disco = carta_a
        else:
            carta_com_disco = carta_b

        self.estado.trilha_disputas.trocar_cartas(posicao_a, posicao_b)
        carta_com_disco.colocar_disco_negociacao()
        jogador.usar_disco_negociacao()

        return {
            "posicao_a": posicao_a,
            "posicao_b": posicao_b,
            "carta_com_disco": carta_com_disco.nome_regiao,
        }

    def _executar_manobra(self, parametros):
        if len(self.estado.tabuleiro.obter_regioes_com_seguidores()) < 2:
            self._validar_convocacao_possivel(0)
            return {"sem_efeito": True}

        regiao_a, faccao_a, regiao_b, faccao_b = self._obter_dados_de_troca(
            parametros
        )

        if regiao_a.quantidade_de_seguidores(faccao_a) < 1:
            raise ValueError("A primeira região não possui o seguidor escolhido.")

        if regiao_b.quantidade_de_seguidores(faccao_b) < 1:
            raise ValueError("A segunda região não possui o seguidor escolhido.")

        detalhes = {
            "regiao_a": regiao_a.nome,
            "faccao_a": faccao_a,
            "regiao_b": regiao_b.nome,
            "faccao_b": faccao_b,
        }
        self._validar_manobra_nao_desfaz_acao(detalhes)
        self._validar_convocacao_possivel(0)

        regiao_a.remover_seguidores(faccao_a)
        regiao_b.remover_seguidores(faccao_b)
        regiao_a.adicionar_seguidores(faccao_b)
        regiao_b.adicionar_seguidores(faccao_a)
        return detalhes

    def _executar_superar_manobra(self, parametros):
        _, quantidade_b = self.obter_trocas_superar_manobra()
        if quantidade_b == 0:
            self._validar_convocacao_possivel(0)
            return {"sem_efeito": True}

        regiao_a, faccao_a, regiao_b, faccao_b = self._obter_dados_de_troca(
            parametros,
            exigir_adjacencia=True,
        )

        if regiao_a.quantidade_de_seguidores(faccao_a) < 1:
            raise ValueError("A primeira região não possui o seguidor escolhido.")

        if regiao_b.quantidade_de_seguidores(faccao_b) < quantidade_b:
            if quantidade_b == 2:
                raise ValueError("Existe uma troca completa e ela deve ser realizada.")
            raise ValueError("A segunda região não possui o seguidor escolhido.")

        detalhes = {
            "regiao_a": regiao_a.nome,
            "faccao_a": faccao_a,
            "regiao_b": regiao_b.nome,
            "faccao_b": faccao_b,
            "quantidade_b": quantidade_b,
        }
        self._validar_superacao_nao_desfaz_acao(detalhes)
        self._validar_convocacao_possivel(0)

        regiao_a.remover_seguidores(faccao_a)
        regiao_b.remover_seguidores(faccao_b, quantidade_b)
        regiao_a.adicionar_seguidores(faccao_b, quantidade_b)
        regiao_b.adicionar_seguidores(faccao_a)
        return detalhes

    def _devolver_seguidores_para_reserva(self, seguidores_removidos):
        for faccao in Faccao:
            quantidade = seguidores_removidos[faccao]

            if quantidade > 0:
                self.estado.reserva.devolver(faccao, quantidade)

    def obter_quantidade_conjuntos(self, jogador):
        """Retorna quantos conjuntos completos o jogador possui na corte."""
        return min(jogador.qtd_na_corte(faccao) for faccao in Faccao)

    def _determinar_vencedor_invasao(self):
        jogadores = self.estado.obter_jogadores()
        conjuntos_jogador_1 = self.obter_quantidade_conjuntos(jogadores[0])
        conjuntos_jogador_2 = self.obter_quantidade_conjuntos(jogadores[1])

        if conjuntos_jogador_1 > conjuntos_jogador_2:
            return jogadores[0]

        if conjuntos_jogador_2 > conjuntos_jogador_1:
            return jogadores[1]

        return self.estado.ultimo_jogador_que_agiu

    def _finalizar_por_invasao(self):
        self.estado.finalizado = True
        self.estado.fase_turno = FaseTurno.ENCERRADO
        self.estado.motivo_encerramento = "Invasão francesa"
        self.estado.vencedor = self._determinar_vencedor_invasao()

        if self.estado.vencedor is None:
            self.estado.ultima_mensagem += " A partida terminou empatada."
        else:
            self.estado.ultima_mensagem += " Vencedor: "
            self.estado.ultima_mensagem += self.estado.vencedor.nome + "."

    def obter_faccoes_por_poder(self):
        """Ordena por regiões controladas e, no empate, pela vitória mais recente."""
        regioes = self.estado.tabuleiro.obter_regioes().values()
        controles = Counter(regiao.controlador for regiao in regioes)
        ultima_vitoria = {
            faccao: indice
            for indice, faccao in enumerate(self.estado.historico_vitorias_faccoes)
        }
        return sorted(
            Faccao,
            key=lambda faccao: (controles[faccao], ultima_vitoria.get(faccao, -1)),
            reverse=True,
        )

    def _determinar_vencedor_coroacao(self, faccoes_ordenadas):
        jogadores = self.estado.obter_jogadores()

        for indice_faccao in range(2):
            faccao = faccoes_ordenadas[indice_faccao]
            quantidade_1 = jogadores[0].qtd_na_corte(faccao)
            quantidade_2 = jogadores[1].qtd_na_corte(faccao)

            if quantidade_1 > quantidade_2:
                return jogadores[0]

            if quantidade_2 > quantidade_1:
                return jogadores[1]

        if self.estado.ordem_jogadores_sem_cartas:
            return self.estado.ordem_jogadores_sem_cartas[0]

        return None

    def _finalizar_por_coroacao(self):
        self.estado.finalizado = True
        self.estado.fase_turno = FaseTurno.ENCERRADO
        self.estado.motivo_encerramento = "Coroação"
        faccoes_ordenadas = self.obter_faccoes_por_poder()

        if faccoes_ordenadas:
            self.estado.faccao_vencedora = faccoes_ordenadas[0]

        self.estado.vencedor = self._determinar_vencedor_coroacao(
            faccoes_ordenadas
        )

        if self.estado.vencedor is None:
            self.estado.ultima_mensagem += " Coroação com empate entre jogadores."
        else:
            self.estado.ultima_mensagem += " Vencedor: "
            self.estado.ultima_mensagem += self.estado.vencedor.nome + "."

    def _validar_fase(self, fase_esperada):
        if self.estado.fase_turno != fase_esperada:
            if fase_esperada == FaseTurno.ESCOLHER_ACAO:
                raise ValueError("É necessário concluir a convocação primeiro.")
            raise ValueError("Não existe convocação pendente.")

    def _validar_partida_em_andamento(self):
        if self.estado.finalizado:
            raise ValueError("A partida já foi finalizada.")
    def passar(self):
        """Registra um passe e resolve uma disputa após todos passarem."""
        self._validar_partida_em_andamento()
        self._validar_fase(FaseTurno.ESCOLHER_ACAO)

        jogador = self.estado.obter_jogador_atual()
        self.estado.passes_consecutivos += 1
        self.estado.ultima_mensagem = jogador.nome + " passou."

        quantidade_jogadores = len(self.estado.obter_jogadores())

        if self.estado.passes_consecutivos == quantidade_jogadores:
            self.resolver_proxima_disputa()

        if not self.estado.finalizado:
            self.estado.avancar_jogador()

    def jogar_carta(self, carta, parametros=None):
        """Valida a carta, executa seu efeito e inicia a convocação."""
        self._validar_partida_em_andamento()
        self._validar_fase(FaseTurno.ESCOLHER_ACAO)
        self._validar_carta_do_jogador(carta)

        if parametros is None:
            parametros = {}

        if not isinstance(parametros, dict):
            raise TypeError("Os parâmetros da ação devem estar em um dicionário.")

        if carta.tipo == TipoCartaAcao.REUNIR:
            detalhes = self._executar_assemble(parametros)
        elif eh_carta_de_apoio(carta.tipo):
            detalhes = self._executar_apoio(carta.tipo, parametros)
        elif carta.tipo == TipoCartaAcao.NEGOCIAR:
            detalhes = self._executar_negociar(parametros)
        elif carta.tipo == TipoCartaAcao.MANOBRAR:
            detalhes = self._executar_manobra(parametros)
        elif carta.tipo == TipoCartaAcao.SUPERAR_MANOBRA:
            detalhes = self._executar_superar_manobra(parametros)
        else:
            raise ValueError("O tipo da carta não é reconhecido.")

        self._registrar_carta_jogada(carta, detalhes)

    def convocar_seguidor(self, nome_regiao, faccao):
        """Move um seguidor de uma região para a corte e encerra o turno."""
        self._validar_partida_em_andamento()
        self._validar_fase(FaseTurno.CONVOCAR_SEGUIDOR)

        if not isinstance(faccao, Faccao):
            raise TypeError("A facção escolhida é inválida.")

        regiao = self.estado.tabuleiro.obter_regiao(nome_regiao)

        if regiao.esta_resolvida():
            raise ValueError("Não é possível convocar de uma região resolvida.")

        if regiao.quantidade_de_seguidores(faccao) == 0:
            raise ValueError("Não há seguidor dessa facção na região.")

        jogador = self.estado.obter_jogador_atual()
        regiao.remover_seguidores(faccao)
        jogador.adicionar_seguidor_na_corte(faccao)

        ultima_acao = self.estado.ultima_acao
        ultima_acao["convocacao"] = {
            "regiao": nome_regiao,
            "faccao": faccao,
        }

        self.estado.carta_em_execucao = None
        self.estado.fase_turno = FaseTurno.ESCOLHER_ACAO
        self.estado.ultima_mensagem = (
            jogador.nome
            + " convocou um seguidor "
            + faccao.value
            + " de "
            + nome_regiao
            + "."
        )
        self.estado.avancar_jogador()

    def avaliar_convocacoes(self, convocacoes, avaliar):
        """Avalia convocações em uma cópia privada com um avaliador de leitura."""
        estado = self.estado
        jogador = estado.obter_jogador_atual()
        indice = estado.indice_jogador_atual
        carta = estado.carta_em_execucao
        fase = estado.fase_turno
        mensagem = estado.ultima_mensagem
        ultima_acao = estado.ultima_acao
        convocacao_anterior = ultima_acao["convocacao"]

        for nome_regiao, faccao in convocacoes:
            self.convocar_seguidor(nome_regiao, faccao)
            try:
                pontuacao = avaliar(estado)
            finally:
                jogador.remover_seguidor_da_corte(faccao)
                estado.tabuleiro.obter_regiao(nome_regiao).adicionar_seguidores(faccao)
                ultima_acao["convocacao"] = convocacao_anterior
                estado.carta_em_execucao = carta
                estado.fase_turno = fase
                estado.ultima_mensagem = mensagem
                estado.indice_jogador_atual = indice
            yield pontuacao

    def resolver_proxima_disputa(self):
        """Resolve a primeira carta ainda virada para cima na trilha."""
        self._validar_partida_em_andamento()
        self._validar_fase(FaseTurno.ESCOLHER_ACAO)
        carta = self.estado.trilha_disputas.obter_proxima_carta()

        if carta is None:
            self._finalizar_por_coroacao()
            return

        regiao = self.estado.tabuleiro.obter_regiao(carta.nome_regiao)
        faccao_controladora, _ = regiao.obter_lideranca()
        seguidores_removidos = regiao.remover_todos_os_seguidores()

        self._devolver_seguidores_para_reserva(seguidores_removidos)

        if faccao_controladora is None:
            regiao.marcar_como_instavel()
            resultado = regiao.nome + " ficou instável."
        else:
            regiao.definir_controlador(faccao_controladora)
            self.estado.historico_vitorias_faccoes.append(faccao_controladora)
            resultado = regiao.nome + " foi controlada pelos "
            resultado += faccao_controladora.value + "."

        carta.virar_para_baixo()
        self.estado.passes_consecutivos = 0
        self.estado.ultima_mensagem = resultado

        if self.estado.tabuleiro.quantidade_instabilidades() >= 3:
            self._finalizar_por_invasao()
        elif self.estado.trilha_disputas.obter_proxima_carta() is None:
            self._finalizar_por_coroacao()
