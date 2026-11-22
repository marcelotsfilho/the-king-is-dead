from model.legal_move_generator import GeradorJogadas


class _LimiteDeBusca(Exception):
    pass


class BuscaFinal:
    """Compara jogadas até o fim da partida em finais com poucas cartas."""

    def __init__(self, limite_nos):
        self._limite_nos = limite_nos
        self._gerador = GeradorJogadas()
        self.nos_visitados = 0
        self.concluida = False

    def melhorar(self, estado, jogada_q, estado_q):
        self.nos_visitados = 0
        self.concluida = False
        atual = estado.obter_jogador_atual()
        if (not atual.quantidade_cartas()
                or estado.trilha_disputas.quantidade_resolvida() < 6
                or sum(jogador.quantidade_cartas() for jogador in estado.obter_jogadores()) > 2):
            return jogada_q, estado_q

        lado = estado.indice_jogador_atual
        melhor = jogada_q, estado_q
        try:
            valor = self._valor(estado_q, lado, -2, 2)
            if valor < 1:
                for jogada, seguinte in self._gerador.gerar_com_estados(estado):
                    if jogada.possui_mesmos_dados(jogada_q):
                        continue
                    novo_valor = self._valor(seguinte, lado, valor, 2)
                    if novo_valor > valor:
                        melhor, valor = (jogada, seguinte), novo_valor
                    if valor == 1:
                        break
        except _LimiteDeBusca:
            return jogada_q, estado_q
        self.concluida = True
        return melhor

    def _valor(self, estado, lado, alfa, beta):
        if self.nos_visitados >= self._limite_nos:
            raise _LimiteDeBusca
        self.nos_visitados += 1
        if estado.finalizado:
            if estado.vencedor is None:
                return 0
            return 1 if estado.vencedor is estado.obter_jogadores()[lado] else -1

        if estado.indice_jogador_atual == lado:
            valor = -1
            for _, seguinte in self._gerador.gerar_com_estados(estado):
                valor = max(valor, self._valor(seguinte, lado, alfa, beta))
                alfa = max(alfa, valor)
                if alfa >= beta or valor == 1:
                    break
        else:
            valor = 1
            for _, seguinte in self._gerador.gerar_com_estados(estado):
                valor = min(valor, self._valor(seguinte, lado, alfa, beta))
                beta = min(beta, valor)
                if alfa >= beta or valor == -1:
                    break
        return valor
