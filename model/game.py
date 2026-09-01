from model.enums import Faccao


class Jogo:
    """Executa turnos, passes, disputas e encerramento da partida."""

    def __init__(self, estado):
        self.estado = estado

    def passar(self):
        """Registra um passe e resolve uma disputa após todos passarem."""
        self._validar_partida_em_andamento()

        jogador = self.estado.obter_jogador_atual()
        self.estado.passes_consecutivos += 1
        self.estado.ultima_mensagem = jogador.nome + " passou."

        quantidade_jogadores = len(self.estado.obter_jogadores())

        if self.estado.passes_consecutivos == quantidade_jogadores:
            self.resolver_proxima_disputa()

        if not self.estado.finalizado:
            self.estado.avancar_jogador()

    def resolver_proxima_disputa(self):
        """Resolve a primeira carta ainda virada para cima na trilha."""
        self._validar_partida_em_andamento()
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

    def _finalizar_por_invasao(self):
        self.estado.finalizado = True
        self.estado.motivo_encerramento = "Invasão francesa"
        self.estado.vencedor = self._determinar_vencedor_invasao()

        if self.estado.vencedor is None:
            self.estado.ultima_mensagem += " A partida terminou empatada."
        else:
            self.estado.ultima_mensagem += " Vencedor: "
            self.estado.ultima_mensagem += self.estado.vencedor.nome + "."

    def _determinar_vencedor_invasao(self):
        jogadores = self.estado.obter_jogadores()
        conjuntos_jogador_1 = self._quantidade_conjuntos(jogadores[0])
        conjuntos_jogador_2 = self._quantidade_conjuntos(jogadores[1])

        if conjuntos_jogador_1 > conjuntos_jogador_2:
            return jogadores[0]

        if conjuntos_jogador_2 > conjuntos_jogador_1:
            return jogadores[1]

        return None

    def _quantidade_conjuntos(self, jogador):
        menor_quantidade = jogador.qtd_na_corte(Faccao.ESCOCESES)

        for faccao in Faccao:
            quantidade = jogador.qtd_na_corte(faccao)

            if quantidade < menor_quantidade:
                menor_quantidade = quantidade

        return menor_quantidade

    def _finalizar_por_coroacao(self):
        self.estado.finalizado = True
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

    def _determinar_vencedor_coroacao(self, faccoes_ordenadas):
        jogadores = self.estado.obter_jogadores()

        for faccao in faccoes_ordenadas:
            quantidade_1 = jogadores[0].qtd_na_corte(faccao)
            quantidade_2 = jogadores[1].qtd_na_corte(faccao)

            if quantidade_1 > quantidade_2:
                return jogadores[0]

            if quantidade_2 > quantidade_1:
                return jogadores[1]

        return None

    def _validar_partida_em_andamento(self):
        if self.estado.finalizado:
            raise ValueError("A partida já foi finalizada.")
