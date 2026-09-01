class EstadoJogo:
    """Reúne o estado atual de uma partida."""

    def __init__(self, tabuleiro, trilha_disputas, jogadores, reserva=None):
        if not isinstance(jogadores, list):
            raise ValueError("Os jogadores devem ser informados em uma lista.")

        if len(jogadores) != 2:
            raise ValueError("A partida deve possuir exatamente dois jogadores.")

        self.tabuleiro = tabuleiro
        self.trilha_disputas = trilha_disputas
        self._jogadores = jogadores.copy()
        self.reserva = reserva

        self.indice_jogador_atual = 0
        self.passes_consecutivos = 0
        self.disputas_resolvidas = 0
        self.quantidade_instabilidades = 0
        self.historico_vitorias_faccoes = []
        self.finalizado = False
        self.vencedor = None
        self.faccao_vencedora = None
        self.motivo_encerramento = None
        self.ultima_mensagem = "Partida iniciada."

    def obter_jogadores(self):
        return self._jogadores.copy()

    def obter_jogador_atual(self):
        return self._jogadores[self.indice_jogador_atual]

    def avancar_jogador(self):
        """Passa o turno para o próximo jogador."""
        ultimo_indice = len(self._jogadores) - 1

        if self.indice_jogador_atual == ultimo_indice:
            self.indice_jogador_atual = 0
        else:
            self.indice_jogador_atual += 1
