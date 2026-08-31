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
