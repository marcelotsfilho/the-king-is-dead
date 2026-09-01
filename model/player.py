from model.enums import Faccao

class Jogador:
    def __init__(self, nome):
        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("O nome do jogador deve ser preenchido.")

        self.nome = nome_limpo
        self._mao = []
        self._descarte_mao = []

        self.corte = {
            Faccao.ESCOCESES: 0,
            Faccao.INGLESES: 0,
            Faccao.IRLANDESES: 0,
        }

        self.disco_negociacao_disponivel = True

    def  obter_mao(self):
        return self._mao.copy()

    def obter_descarte_mao(self):
        return self._descarte_mao.copy()

    def adicionar_carta_mao(self, carta):
        self._mao.append(carta)

    def usar_carta(self, carta):
        if carta not in self._mao:
            raise ValueError("Carta indisponível.")
        self._mao.remove(carta)
        self._descarte_mao.append(carta)

    def obter_corte(self, faccao):
        return self._corte.copy()

    def qtd_na_corte(self, faccao):
        return self._corte[faccao]

    def adicionar_seguidor_na_corte(self, faccao):
        self._corte[faccao] += 1

    def remover_seguidor_da_corte(self, faccao):
        if self._corte[faccao] <= 0:
            raise ValueError("Não há seguidores suficientes na corte selecionada.")
        self._corte[faccao] -= 1

    def usar_disco_negociacao(self):
        if not self.disco_negociacao_disponivel:
            raise ValueError("O disco de negociação já foi usado.")
        self.disco_negociacao_disponivel = False