from model.enums import Faccao
from model.game import Jogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.state_evaluator import AvaliadorEstado


class AvaliadorInicial(AvaliadorEstado):
    """Reproduz a fórmula anterior à otimização, somente para experimentos."""

    def avaliar(self, estado, profundidade=0):
        self._validar_estado(estado)
        self._validar_profundidade(profundidade)
        if estado.finalizado:
            return self._avaliar_resultado_final(estado, profundidade)

        jogadores = estado.obter_jogadores()
        ia = jogadores[self._indice_jogador_ia]
        adversario = jogadores[self._indice_adversario()]
        jogadas = GeradorJogadas().gerar(estado)
        pontuacao = 0
        executor = ExecutorJogada()
        for jogada in jogadas:
            resultado = executor.executar(estado, jogada)
            if resultado.finalizado and resultado.vencedor is not None:
                vencedor_ia = resultado.obter_jogadores()[self._indice_jogador_ia]
                if resultado.vencedor is vencedor_ia:
                    pontuacao += 50000
                else:
                    pontuacao -= 50000

        jogo = Jogo(estado)
        peso = 20
        instabilidades = estado.tabuleiro.quantidade_instabilidades()
        if instabilidades == 1:
            peso = 100
        elif instabilidades >= 2:
            peso = 1000
        pontuacao += peso * (
            jogo.obter_quantidade_conjuntos(ia)
            - jogo.obter_quantidade_conjuntos(adversario)
        )
        faccoes = jogo.obter_faccoes_por_poder()
        pontuacao += 100 * self._diferenca_na_corte(ia, adversario, faccoes[0])
        pontuacao += 10 * self._diferenca_na_corte(ia, adversario, faccoes[1])
        for regiao in estado.tabuleiro.obter_regioes().values():
            if not regiao.esta_resolvida():
                lider, margem = self._obter_lider_da_regiao(regiao)
                if lider is not None:
                    pontuacao += margem * self._diferenca_na_corte(ia, adversario, lider) * 3
        mobilidade = len(jogadas) * 2
        if estado.indice_jogador_atual == self._indice_jogador_ia:
            pontuacao += mobilidade
        else:
            pontuacao -= mobilidade
        return pontuacao
