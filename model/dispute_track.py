from model.region_card import CartaRegiao

class TrilhaDisputas:
    """Representa a trilha de disputas do jogo"""

    def __init__(self, nomes_regioes):
        if not nomes_regioes:
            raise ValueError("A lista de nomes de regiões não pode ser vazia.")
        if len(nomes_regioes) != 8:
            raise ValueError("A lista de nomes de regiões deve conter exatamente 8 elementos.")

        self.cartas_regiao = []

        for nome in nomes_regioes:
            carta = CartaRegiao(nome)
            self.cartas_regiao.append(carta)

    def obter_cartas(self):
        return self.cartas_regiao.copy()

    def obter_carta(self, posicao):
        if not isinstance(posicao, int):
            raise ValueError("A posição da carta deve ser um número inteiro.")
        if posicao < 0 or posicao >= len(self.cartas_regiao):
            # TODO: CONSIDERAR A PARTIR DO 1, JÁ QUE O JOGADOR VERÁ 1 AO 8
            raise ValueError("A posição da carta deve ser um número inteiro entre 0 e 7.")
        return self.cartas_regiao[posicao]

    def obter_proxima_carta(self):
        for carta in self.cartas_regiao:
            if carta.virada_para_cima:
                return carta
        return None

    def trocar_cartas(self, posicao_a, posicao_b):
        if not isinstance(posicao_a, int) or not isinstance(posicao_b, int):
            raise ValueError("As posições para troca devem ser números inteiros.")
        if posicao_a < 0 or posicao_a >= len(self.cartas_regiao) or posicao_b < 0 or posicao_b >= len(self.cartas_regiao):
            raise ValueError("As posições para troca devem ser números inteiros entre 0 e 7.")

        self.cartas_regiao[posicao_a], self.cartas_regiao[posicao_b] = self.cartas_regiao[posicao_b], self.cartas_regiao[posicao_a]
        