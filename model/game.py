from model.action_card import CartaAcao
from model.enums import Faccao, FaseTurno, TipoCartaAcao


_DADOS_DOS_APOIOS = {
    TipoCartaAcao.APOIO_ESCOCES: (Faccao.ESCOCESES, "Moray"),
    TipoCartaAcao.APOIO_GALES: (Faccao.GALESES, "Gwynedd"),
    TipoCartaAcao.APOIO_INGLES: (Faccao.INGLESES, "Essex"),
}


class Jogo:
    """Executa as regras do modo básico para dois jogadores."""

    def __init__(self, estado):
        self.estado = estado

    def obter_regioes_validas_para_apoio(self, tipo_carta):
        """Retorna regiões que podem receber uma carta Support."""
        if tipo_carta not in _DADOS_DOS_APOIOS:
            raise ValueError("A carta informada não é uma carta Support.")

        faccao, nome_regiao_inicial = _DADOS_DOS_APOIOS[tipo_carta]
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

    def _obter_posicoes_validas_para_negociar(self):
        posicoes = []

        for posicao in range(1, 9):
            carta = self.estado.trilha_disputas.obter_carta(posicao)

            if carta.virada_para_cima and not carta.possui_disco_negociacao:
                posicoes.append(posicao)

        return posicoes

    def _existe_manobra_possivel(self):
        regioes_com_seguidores = 0

        for regiao in self.estado.tabuleiro.obter_regioes().values():
            if not regiao.esta_resolvida() and regiao.total_de_seguidores() > 0:
                regioes_com_seguidores += 1

        return regioes_com_seguidores >= 2

    def _existe_superacao_completa(self):
        tabuleiro = self.estado.tabuleiro

        for nome_a in tabuleiro.obter_nomes_das_regioes():
            regiao_a = tabuleiro.obter_regiao(nome_a)

            if regiao_a.esta_resolvida() or regiao_a.total_de_seguidores() == 0:
                continue

            for nome_b in tabuleiro.regioes_adjacentes(nome_a):
                regiao_b = tabuleiro.obter_regiao(nome_b)

                if regiao_b.esta_resolvida():
                    continue

                for faccao in Faccao:
                    if regiao_b.quantidade_de_seguidores(faccao) >= 2:
                        return True

        return False

    def _existe_superacao_parcial(self):
        tabuleiro = self.estado.tabuleiro

        for nome_a in tabuleiro.obter_nomes_das_regioes():
            regiao_a = tabuleiro.obter_regiao(nome_a)

            if regiao_a.esta_resolvida() or regiao_a.total_de_seguidores() == 0:
                continue

            for nome_b in tabuleiro.regioes_adjacentes(nome_a):
                regiao_b = tabuleiro.obter_regiao(nome_b)

                if not regiao_b.esta_resolvida():
                    if regiao_b.total_de_seguidores() > 0:
                        return True

        return False

    def _obter_ultima_acao_adversaria(self, tipo):
        if not self.estado.historico_acoes:
            return None

        ultima_acao = self.estado.historico_acoes[-1]
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
        self.estado.historico_acoes.append(
            {
                "jogador": jogador,
                "tipo": carta.tipo,
                "detalhes": detalhes,
                "convocacao": None,
            }
        )

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
        faccao, _ = _DADOS_DOS_APOIOS[tipo_carta]
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
        posicoes_validas = self._obter_posicoes_validas_para_negociar()

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
        if not self._existe_manobra_possivel():
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
        existe_completa = self._existe_superacao_completa()
        existe_parcial = self._existe_superacao_parcial()

        if not existe_parcial:
            self._validar_convocacao_possivel(0)
            return {"sem_efeito": True}

        regiao_a, faccao_a, regiao_b, faccao_b = self._obter_dados_de_troca(
            parametros,
            exigir_adjacencia=True,
        )

        if regiao_a.quantidade_de_seguidores(faccao_a) < 1:
            raise ValueError("A primeira região não possui o seguidor escolhido.")

        quantidade_b = 1

        if existe_completa:
            quantidade_b = 2

        if regiao_b.quantidade_de_seguidores(faccao_b) < quantidade_b:
            if existe_completa:
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

    def _determinar_faccao_controladora(self, regiao):
        maior_quantidade = -1
        faccoes_com_maior_quantidade = []

        for faccao in Faccao:
            quantidade = regiao.quantidade_de_seguidores(faccao)

            if quantidade > maior_quantidade:
                maior_quantidade = quantidade
                faccoes_com_maior_quantidade = [faccao]
            elif quantidade == maior_quantidade:
                faccoes_com_maior_quantidade.append(faccao)

        if maior_quantidade == 0 or len(faccoes_com_maior_quantidade) > 1:
            return None

        return faccoes_com_maior_quantidade[0]

    def _devolver_seguidores_para_reserva(self, seguidores_removidos):
        for faccao in Faccao:
            quantidade = seguidores_removidos[faccao]

            if quantidade > 0:
                self.estado.reserva.devolver(faccao, quantidade)

    def _quantidade_conjuntos(self, jogador):
        menor_quantidade = jogador.qtd_na_corte(Faccao.ESCOCESES)

        for faccao in Faccao:
            quantidade = jogador.qtd_na_corte(faccao)

            if quantidade < menor_quantidade:
                menor_quantidade = quantidade

        return menor_quantidade

    def _determinar_vencedor_invasao(self):
        jogadores = self.estado.obter_jogadores()
        conjuntos_jogador_1 = self._quantidade_conjuntos(jogadores[0])
        conjuntos_jogador_2 = self._quantidade_conjuntos(jogadores[1])

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

    def _quantidade_regioes_controladas(self, faccao):
        quantidade = 0

        for regiao in self.estado.tabuleiro.obter_regioes().values():
            if regiao.controlador == faccao:
                quantidade += 1

        return quantidade

    def _indice_ultima_vitoria(self, faccao):
        indice_encontrado = -1
        indice_atual = 0

        for vencedora in self.estado.historico_vitorias_faccoes:
            if vencedora == faccao:
                indice_encontrado = indice_atual

            indice_atual += 1

        return indice_encontrado

    def _faccao_tem_prioridade(self, faccao_a, faccao_b):
        controles_a = self._quantidade_regioes_controladas(faccao_a)
        controles_b = self._quantidade_regioes_controladas(faccao_b)

        if controles_a > controles_b:
            return True

        if controles_a < controles_b:
            return False

        ultima_a = self._indice_ultima_vitoria(faccao_a)
        ultima_b = self._indice_ultima_vitoria(faccao_b)
        return ultima_a > ultima_b

    def _ordenar_faccoes_por_poder(self):
        faccoes_restantes = []

        for faccao in Faccao:
            faccoes_restantes.append(faccao)

        faccoes_ordenadas = []

        while faccoes_restantes:
            mais_poderosa = faccoes_restantes[0]

            for faccao in faccoes_restantes:
                if self._faccao_tem_prioridade(faccao, mais_poderosa):
                    mais_poderosa = faccao

            faccoes_ordenadas.append(mais_poderosa)
            faccoes_restantes.remove(mais_poderosa)

        return faccoes_ordenadas

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
        faccoes_ordenadas = self._ordenar_faccoes_por_poder()

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
        elif carta.tipo in _DADOS_DOS_APOIOS:
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

        ultima_acao = self.estado.historico_acoes[-1]
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

    def resolver_proxima_disputa(self):
        """Resolve a primeira carta ainda virada para cima na trilha."""
        self._validar_partida_em_andamento()
        self._validar_fase(FaseTurno.ESCOLHER_ACAO)
        carta = self.estado.trilha_disputas.obter_proxima_carta()

        if carta is None:
            self._finalizar_por_coroacao()
            return

        regiao = self.estado.tabuleiro.obter_regiao(carta.nome_regiao)
        faccao_controladora = self._determinar_faccao_controladora(regiao)
        seguidores_removidos = regiao.remover_todos_os_seguidores()

        self._devolver_seguidores_para_reserva(seguidores_removidos)

        if faccao_controladora is None:
            regiao.marcar_como_instavel()
            self.estado.quantidade_instabilidades += 1
            resultado = regiao.nome + " ficou instável."
        else:
            regiao.definir_controlador(faccao_controladora)
            self.estado.historico_vitorias_faccoes.append(faccao_controladora)
            resultado = regiao.nome + " foi controlada pelos "
            resultado += faccao_controladora.value + "."

        carta.virar_para_baixo()
        self.estado.disputas_resolvidas += 1
        self.estado.passes_consecutivos = 0
        self.estado.ultima_mensagem = resultado

        if self.estado.quantidade_instabilidades >= 3:
            self._finalizar_por_invasao()
        elif self.estado.trilha_disputas.obter_proxima_carta() is None:
            self._finalizar_por_coroacao()
