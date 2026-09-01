from model.region_card import CartaRegiao

class TrilhaDisputas:
    """Representa a trilha de disputas do jogo"""

    def __init__(self, nomes_regioes):
        if not isinstance(nomes_regioes, list):
            raise ValueError("Os nomes das regiões devem ser informados em uma lista.")
        if not nomes_regioes:
            raise ValueError("A lista de nomes de regiões não pode ser vazia.")
        if len(nomes_regioes) != 8:
            raise ValueError("A lista de nomes de regiões deve conter exatamente 8 elementos.")

        nomes_encontrados = set()
        for nome in nomes_regioes:
            if nome in nomes_encontrados:
                raise ValueError("Os nomes das regiões não podem se repetir.")
            nomes_encontrados.add(nome)

        self.cartas_regiao = []

        for nome in nomes_regioes:
            carta = CartaRegiao(nome)
            self.cartas_regiao.append(carta)

    def obter_cartas(self):
        return self.cartas_regiao.copy()

    def obter_carta(self, posicao):
        if not isinstance(posicao, int):
            raise ValueError("A posição da carta deve ser um número inteiro.")
        if posicao < 1 or posicao > 8:
            raise ValueError("A posição da carta deve ser um número inteiro entre 1 e 8.")
        return self.cartas_regiao[posicao - 1]

    def obter_proxima_carta(self):
        for carta in self.cartas_regiao:
            if carta.virada_para_cima:
                return carta
        return None

    def trocar_cartas(self, posicao_a, posicao_b):
        if not isinstance(posicao_a, int) or not isinstance(posicao_b, int):
            raise ValueError("As posições para troca devem ser números inteiros.")
        if posicao_a < 1 or posicao_a > 8 or posicao_b < 1 or posicao_b > 8:
            raise ValueError("As posições para troca devem ser números inteiros entre 1 e 8.")

        self.cartas_regiao[posicao_a - 1], self.cartas_regiao[posicao_b - 1] = self.cartas_regiao[posicao_b - 1], self.cartas_regiao[posicao_a - 1]
        