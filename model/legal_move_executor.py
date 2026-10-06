from model.game import Jogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada


class ExecutorJogada:
    """Aplica uma jogada completa em uma cópia do estado recebido."""

    def __init__(self):
        self._serializador = SerializadorEstadoJogo()

    def executar(self, estado, jogada):
        """Retorna o estado resultante sem modificar o estado original."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")

        if not isinstance(jogada, Jogada):
            raise TypeError("A jogada deve ser uma instância de Jogada.")

        novo_estado = self._serializador.copiar(estado)
        jogo = Jogo(novo_estado)

        if jogada.eh_passe():
            jogo.passar()
            return novo_estado

        carta = self._obter_carta_do_jogador(
            novo_estado,
            jogada.tipo_carta,
        )
        jogo.jogar_carta(carta, jogada.obter_parametros())
        jogo.convocar_seguidor(
            jogada.nome_regiao_convocacao,
            jogada.faccao_convocacao,
        )

        return novo_estado

    def _obter_carta_do_jogador(self, estado, tipo_carta):
        jogador = estado.obter_jogador_atual()

        for carta in jogador.obter_mao():
            if carta.tipo == tipo_carta:
                return carta

        raise ValueError("O jogador atual não possui a carta informada.")
