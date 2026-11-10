from model.enums import Faccao
from model.game import Jogo
from model.game_state import EstadoJogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas


_VALOR_VITORIA = 1000000
_VALOR_AMEACA_IMEDIATA = 50000


class AvaliadorEstado:
    """Calcula uma pontuação do estado pela perspectiva da IA."""

    def __init__(self, indice_jogador_ia):
        if (
            isinstance(indice_jogador_ia, bool)
            or not isinstance(indice_jogador_ia, int)
        ):
            raise TypeError("O índice do jogador da IA deve ser inteiro.")

        if indice_jogador_ia not in (0, 1):
            raise ValueError("O índice do jogador da IA deve ser 0 ou 1.")

        self._indice_jogador_ia = indice_jogador_ia
        self._gerador = GeradorJogadas()
        self._executor = ExecutorJogada()

    def avaliar(self, estado, profundidade=0):
        """Retorna uma pontuação maior quando o estado favorece a IA."""
        self._validar_estado(estado)
        self._validar_profundidade(profundidade)

        if estado.finalizado:
            return self._avaliar_resultado_final(estado, profundidade)

        jogadas = self._gerador.gerar(estado)
        pontuacao = 0
        pontuacao += self._avaliar_ameacas_imediatas(
            estado,
            jogadas,
        )
        pontuacao += self._avaliar_invasao(estado)
        pontuacao += self._avaliar_coroacao(estado)
        pontuacao += self._avaliar_potencial_das_regioes(estado)
        pontuacao += self._avaliar_mobilidade(estado, len(jogadas))
        return pontuacao

    def _avaliar_resultado_final(self, estado, profundidade):
        vencedor = estado.vencedor

        if vencedor is None:
            return 0

        jogadores = estado.obter_jogadores()

        if vencedor is jogadores[self._indice_jogador_ia]:
            return _VALOR_VITORIA - profundidade

        return -_VALOR_VITORIA + profundidade

    def _avaliar_ameacas_imediatas(self, estado, jogadas):
        valor = 0

        for jogada in jogadas:
            estado_resultante = self._executor.executar(estado, jogada)

            if not estado_resultante.finalizado:
                continue

            if self._ia_venceu(estado_resultante):
                valor += _VALOR_AMEACA_IMEDIATA
            elif self._adversario_venceu(estado_resultante):
                valor -= _VALOR_AMEACA_IMEDIATA

        return valor

    def _avaliar_invasao(self, estado):
        jogadores = estado.obter_jogadores()
        jogo = Jogo(estado)
        conjuntos_ia = jogo.obter_quantidade_conjuntos(
            jogadores[self._indice_jogador_ia]
        )
        conjuntos_adversario = jogo.obter_quantidade_conjuntos(
            jogadores[self._indice_adversario()]
        )
        diferenca = conjuntos_ia - conjuntos_adversario

        quantidade_instabilidades = estado.tabuleiro.quantidade_instabilidades()

        if quantidade_instabilidades >= 2:
            return diferenca * 1000

        if quantidade_instabilidades == 1:
            return diferenca * 100

        return diferenca * 20

    def _avaliar_coroacao(self, estado):
        jogadores = estado.obter_jogadores()
        jogo = Jogo(estado)
        faccoes = jogo.obter_faccoes_por_poder()
        jogador_ia = jogadores[self._indice_jogador_ia]
        adversario = jogadores[self._indice_adversario()]
        pontuacao = 0

        if len(faccoes) >= 1:
            pontuacao += self._diferenca_na_corte(
                jogador_ia,
                adversario,
                faccoes[0],
            ) * 100

        if len(faccoes) >= 2:
            pontuacao += self._diferenca_na_corte(
                jogador_ia,
                adversario,
                faccoes[1],
            ) * 10

        return pontuacao

    def _avaliar_potencial_das_regioes(self, estado):
        jogadores = estado.obter_jogadores()
        jogador_ia = jogadores[self._indice_jogador_ia]
        adversario = jogadores[self._indice_adversario()]
        pontuacao = 0

        for regiao in estado.tabuleiro.obter_regioes().values():
            if regiao.esta_resolvida():
                continue

            faccao_lider, margem = self._obter_lider_da_regiao(regiao)

            if faccao_lider is None:
                continue

            diferenca_corte = self._diferenca_na_corte(
                jogador_ia,
                adversario,
                faccao_lider,
            )
            pontuacao += margem * diferenca_corte * 3

        return pontuacao

    def _avaliar_mobilidade(self, estado, quantidade_jogadas):
        if estado.obter_jogador_atual() is estado.obter_jogadores()[
            self._indice_jogador_ia
        ]:
            return quantidade_jogadas * 2

        return quantidade_jogadas * -2

    def _obter_lider_da_regiao(self, regiao):
        maior_quantidade = 0
        segunda_maior = 0
        lider = None

        for faccao in Faccao:
            quantidade = regiao.quantidade_de_seguidores(faccao)

            if quantidade > maior_quantidade:
                segunda_maior = maior_quantidade
                maior_quantidade = quantidade
                lider = faccao
            elif quantidade > segunda_maior:
                segunda_maior = quantidade

        if lider is None or maior_quantidade == segunda_maior:
            return None, 0

        return lider, maior_quantidade - segunda_maior

    def _diferenca_na_corte(self, jogador_ia, adversario, faccao):
        return (
            jogador_ia.qtd_na_corte(faccao)
            - adversario.qtd_na_corte(faccao)
        )

    def _ia_venceu(self, estado):
        return estado.vencedor is estado.obter_jogadores()[
            self._indice_jogador_ia
        ]

    def _adversario_venceu(self, estado):
        return estado.vencedor is estado.obter_jogadores()[
            self._indice_adversario()
        ]

    def _indice_adversario(self):
        if self._indice_jogador_ia == 0:
            return 1
        return 0

    def _validar_estado(self, estado):
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser um EstadoJogo.")

    def _validar_profundidade(self, profundidade):
        if isinstance(profundidade, bool) or not isinstance(profundidade, int):
            raise TypeError("A profundidade deve ser um inteiro.")

        if profundidade < 0:
            raise ValueError("A profundidade não pode ser negativa.")
