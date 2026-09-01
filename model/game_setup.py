import random

from model.dispute_track import TrilhaDisputas

class ConfiguracaoJogo:
    """Preparando a configuração inicial do jogo"""

    def criar_trilha_disputas(self, tabuleiro):
        nomes_regioes = tabuleiro.obter_nomes_das_regioes()
        random.shuffle(nomes_regioes)
        trilha = TrilhaDisputas(nomes_regioes)
        return trilha