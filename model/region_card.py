class CartaRegiao:
    """Representa uma carta de região no jogo, utilizada para determinar a região
    a ser disputada na rodada atual."""

    def __init__(self, nome_regiao):
        nome_limpo = nome_regiao.strip()
        if not nome_limpo:
            raise ValueError("O nome da região não pode ser vazio.")

        self.nome_regiao = nome_limpo
        self.virada_para_cima = True
        self.possui_disco_negociacao = False

    def virar_para_baixo(self):
        self.virada_para_cima = False

    def virar_para_cima(self):
        self.virada_para_cima = True

    def colocar_disco_negociacao(self):
        if not self.virada_para_cima:
            raise ValueError("Não é possível colocar o disco de negociação em uma carta virada para baixo.")
        self.possui_disco_negociacao = True

    def remover_disco_negociacao(self):
        self.possui_disco_negociacao = False