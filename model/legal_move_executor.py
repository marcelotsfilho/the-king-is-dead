from model.game import Jogo
from model.game_state import EstadoJogo
from model.legal_move import Jogada


class ExecutorJogada:
    """Aplica uma jogada completa em uma cópia do estado recebido."""

    def executar(self, estado, jogada):
        """Retorna o estado resultante sem modificar o estado original."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")

        if not isinstance(jogada, Jogada):
            raise TypeError("A jogada deve ser uma instância de Jogada.")

        if jogada.eh_passe():
            novo_estado = estado.copiar()
            Jogo(novo_estado).passar()
            return novo_estado

        novo_estado = self.executar_carta(
            estado,
            jogada.tipo_carta,
            jogada.obter_parametros(),
        )
        Jogo(novo_estado).convocar_seguidor(
            jogada.nome_regiao_convocacao,
            jogada.faccao_convocacao,
        )

        return novo_estado

    def executar_carta(self, estado, tipo_carta, parametros):
        """Aplica o efeito em uma cópia e deixa a convocação pendente."""
        novo_estado = estado.copiar()
        carta = self._obter_carta_do_jogador(novo_estado, tipo_carta)
        Jogo(novo_estado).jogar_carta(carta, parametros)
        return novo_estado

    def executar_convocacao(self, estado, nome_regiao, faccao):
        """Conclui a convocação pendente em uma cópia do estado."""
        novo_estado = estado.copiar()
        Jogo(novo_estado).convocar_seguidor(nome_regiao, faccao)
        return novo_estado

    def _obter_carta_do_jogador(self, estado, tipo_carta):
        jogador = estado.obter_jogador_atual()

        for carta in jogador.obter_mao():
            if carta.tipo == tipo_carta:
                return carta

        raise ValueError("O jogador atual não possui a carta informada.")
