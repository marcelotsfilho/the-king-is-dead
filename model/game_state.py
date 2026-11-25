from copy import deepcopy

from model.enums import FaseTurno


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
        self.historico_vitorias_faccoes = []
        self.ultima_acao = None
        self.ultimo_jogador_que_agiu = None
        self.ordem_jogadores_sem_cartas = []
        self.fase_turno = FaseTurno.ESCOLHER_ACAO
        self.carta_em_execucao = None
        self.finalizado = False
        self.vencedor = None
        self.faccao_vencedora = None
        self.motivo_encerramento = None
        self.ultima_mensagem = "Partida iniciada."

    def copiar(self):
        """Cria um estado independente para executar uma jogada em memória."""
        jogadores = {jogador: jogador.copiar() for jogador in self._jogadores}
        copia = EstadoJogo(
            self.tabuleiro.copiar(),
            self.trilha_disputas.copiar(),
            list(jogadores.values()),
            self.reserva.copiar() if self.reserva is not None else None,
        )
        copia.indice_jogador_atual = self.indice_jogador_atual
        copia.passes_consecutivos = self.passes_consecutivos
        copia.historico_vitorias_faccoes = self.historico_vitorias_faccoes.copy()
        # A última ação deve apontar para o jogador da cópia.
        copia.ultima_acao = deepcopy(
            self.ultima_acao,
            {id(original): novo for original, novo in jogadores.items()},
        )
        copia.ultimo_jogador_que_agiu = jogadores.get(self.ultimo_jogador_que_agiu)
        copia.ordem_jogadores_sem_cartas = [
            jogadores[jogador] for jogador in self.ordem_jogadores_sem_cartas
        ]
        copia.fase_turno = self.fase_turno
        if self.carta_em_execucao is not None:
            descarte = copia.obter_jogador_atual().obter_descarte_mao()
            for carta in reversed(descarte):
                if carta.tipo == self.carta_em_execucao.tipo:
                    copia.carta_em_execucao = carta
                    break
            else:
                raise ValueError("A carta em execução não foi encontrada no descarte.")
        copia.finalizado = self.finalizado
        copia.vencedor = jogadores.get(self.vencedor)
        copia.faccao_vencedora = self.faccao_vencedora
        copia.motivo_encerramento = self.motivo_encerramento
        copia.ultima_mensagem = self.ultima_mensagem
        return copia

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
