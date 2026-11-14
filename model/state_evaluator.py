from model.enums import Faccao
from model.game import Jogo
from model.game_state import EstadoJogo


_VALOR_VITORIA = 1000000
VERSAO_HEURISTICA = 1


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

    def avaliar(self, estado, profundidade=0):
        """Retorna uma pontuação maior quando o estado favorece a IA."""
        self._validar_estado(estado)
        self._validar_profundidade(profundidade)

        if estado.finalizado:
            return self._avaliar_resultado_final(estado, profundidade)

        pontuacao = self._avaliar_coroacao(estado)
        pontuacao += self._avaliar_invasao(estado)
        # Uma estimativa nunca deve valer mais que um resultado confirmado.
        return max(-100000, min(100000, pontuacao))

    def _avaliar_resultado_final(self, estado, profundidade):
        vencedor = estado.vencedor

        if vencedor is None:
            return 0

        jogadores = estado.obter_jogadores()

        if vencedor is jogadores[self._indice_jogador_ia]:
            return _VALOR_VITORIA - profundidade

        return -_VALOR_VITORIA + profundidade

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

        peso = 20
        if quantidade_instabilidades == 1:
            peso = 100
        elif quantidade_instabilidades >= 2:
            peso = 600

        carta = estado.trilha_disputas.obter_proxima_carta()
        if carta is not None:
            regiao = estado.tabuleiro.obter_regiao(carta.nome_regiao)
            lider, margem = self._obter_lider_da_regiao(regiao)
            if lider is None:
                peso *= 2
                if estado.passes_consecutivos == 1:
                    peso *= 2

        pontuacao = diferenca * peso
        # No empate de conjuntos, a invasão usa quem jogou a última carta.
        if diferenca == 0:
            ultimo = estado.ultimo_jogador_que_agiu
            if ultimo is jogadores[self._indice_jogador_ia]:
                pontuacao += peso // 10
            elif ultimo is jogadores[self._indice_adversario()]:
                pontuacao -= peso // 10
        return pontuacao

    def _avaliar_coroacao(self, estado):
        faccoes = Jogo(estado).obter_faccoes_por_poder()
        projetadas = self._obter_faccoes_projetadas(estado, faccoes)
        # O poder já conquistado pesa três vezes mais que a previsão.
        return (
            3 * self._pontuar_cortes(estado, faccoes)
            + self._pontuar_cortes(estado, projetadas)
        )

    def _pontuar_cortes(self, estado, faccoes):
        jogadores = estado.obter_jogadores()
        jogador_ia = jogadores[self._indice_jogador_ia]
        adversario = jogadores[self._indice_adversario()]
        primeira = self._diferenca_na_corte(jogador_ia, adversario, faccoes[0])
        segunda = self._diferenca_na_corte(jogador_ia, adversario, faccoes[1])
        pontuacao = primeira * 1000 + segunda * 20
        if primeira == 0 and segunda == 0 and estado.ordem_jogadores_sem_cartas:
            if estado.ordem_jogadores_sem_cartas[0] is jogador_ia:
                pontuacao += 1
            else:
                pontuacao -= 1
        return pontuacao

    def _obter_faccoes_projetadas(self, estado, ordem_atual):
        """Estima poder futuro com lideranças locais, sem executar jogadas."""
        poder = {}
        for faccao in Faccao:
            poder[faccao] = 0
        for regiao in estado.tabuleiro.obter_regioes().values():
            if regiao.controlador is not None:
                poder[regiao.controlador] += 4

        proxima = True
        for carta in estado.trilha_disputas.obter_cartas():
            if not carta.virada_para_cima:
                continue
            regiao = estado.tabuleiro.obter_regiao(carta.nome_regiao)
            if regiao.esta_resolvida():
                continue
            lider, margem = self._obter_lider_da_regiao(regiao)
            if lider is not None:
                poder[lider] += min(margem, 2)
                if proxima:
                    poder[lider] += 1
            proxima = False

        restantes = ordem_atual.copy()
        ordenadas = []
        while restantes:
            maior = restantes[0]
            for faccao in restantes:
                if poder[faccao] > poder[maior]:
                    maior = faccao
            ordenadas.append(maior)
            restantes.remove(maior)
        return ordenadas

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
