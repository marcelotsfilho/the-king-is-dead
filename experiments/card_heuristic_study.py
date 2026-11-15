import argparse
import json

from model.game_setup import ConfiguracaoJogo
from model.legal_move_executor import ExecutorJogada
from model.minimax_agent import AgenteMinimax
from model.state_evaluator import AvaliadorEstado


PESO_CARTA = 4100
QUANTIDADE_DISPUTAS = 8


class AvaliadorCartasExperimental(AvaliadorEstado):
    """Permite comparar fórmulas de cartas sem alterar o jogo principal."""

    def __init__(self, indice_jogador_ia, modelo):
        super().__init__(indice_jogador_ia)
        self._modelo = modelo

    def _avaliar_cartas_restantes(self, estado):
        jogadores = estado.obter_jogadores()
        cartas_ia = jogadores[self._indice_jogador_ia].quantidade_cartas()
        cartas_adversario = (
            jogadores[self._indice_adversario()].quantidade_cartas()
        )
        diferenca = cartas_ia - cartas_adversario
        resolvidas = estado.trilha_disputas.quantidade_resolvida()

        if self._modelo == "linear":
            peso = PESO_CARTA * (QUANTIDADE_DISPUTAS - resolvidas) // 8
        elif self._modelo == "constante":
            peso = PESO_CARTA
        elif self._modelo == "constante_4500":
            peso = 4500
        elif self._modelo == "suave":
            peso = PESO_CARTA - 100 * resolvidas
        elif self._modelo == "patamar":
            restantes = QUANTIDADE_DISPUTAS - resolvidas
            peso = PESO_CARTA
            if restantes < 4:
                peso = PESO_CARTA * restantes // 4
        elif self._modelo == "escassez":
            return self._valor_da_mao(cartas_ia, resolvidas, 4300, 100) - (
                self._valor_da_mao(cartas_adversario, resolvidas, 4300, 100)
            )
        elif self._modelo == "escassez_forte":
            return self._valor_da_mao(cartas_ia, resolvidas, 4500, 150) - (
                self._valor_da_mao(cartas_adversario, resolvidas, 4500, 150)
            )
        else:
            raise ValueError("Modelo experimental desconhecido.")

        return diferenca * peso

    def _valor_da_mao(self, quantidade, resolvidas, valor_ultima, desconto):
        valor_ultima -= 100 * resolvidas
        return (
            quantidade * valor_ultima
            - desconto * quantidade * (quantidade - 1) // 2
        )


def executar_partida(semente, modelos):
    estado = ConfiguracaoJogo(semente).criar_estado_inicial(
        ["Jogador 1", "Jogador 2"]
    )
    executor = ExecutorJogada()
    metricas = {
        "semente": semente,
        "modelos": modelos,
        "turnos": 0,
        "cartas_jogadas": 0,
        "passes_voluntarios": 0,
        "disputas_com_cartas": 0,
        "cartas_na_primeira_disputa": None,
        "maior_sequencia_cartas": 0,
    }
    sequencia_cartas = 0

    while not estado.finalizado:
        if metricas["turnos"] >= 100:
            raise RuntimeError("A partida ultrapassou o limite de 100 turnos.")

        indice = estado.indice_jogador_atual
        jogadores = estado.obter_jogadores()
        cartas_antes = [jogador.quantidade_cartas() for jogador in jogadores]
        disputas_antes = estado.trilha_disputas.quantidade_resolvida()
        avaliador = AvaliadorCartasExperimental(indice, modelos[indice])
        agente = AgenteMinimax(indice, avaliador=avaliador)
        jogada = agente.escolher_jogada(
            estado,
            profundidade_maxima=1,
            usar_poda=False,
        )

        if jogada.eh_passe():
            if cartas_antes[indice] > 0:
                metricas["passes_voluntarios"] += 1
            sequencia_cartas = 0
        else:
            metricas["cartas_jogadas"] += 1
            sequencia_cartas += 1
            metricas["maior_sequencia_cartas"] = max(
                metricas["maior_sequencia_cartas"],
                sequencia_cartas,
            )

        estado = executor.executar(estado, jogada)
        metricas["turnos"] += 1
        disputas_depois = estado.trilha_disputas.quantidade_resolvida()
        if disputas_depois > disputas_antes:
            cartas_depois = sum(
                jogador.quantidade_cartas()
                for jogador in estado.obter_jogadores()
            )
            if metricas["cartas_na_primeira_disputa"] is None:
                metricas["cartas_na_primeira_disputa"] = cartas_depois
            if cartas_depois > 0:
                metricas["disputas_com_cartas"] += 1

    metricas["motivo"] = estado.motivo_encerramento
    metricas["vencedor"] = (
        None if estado.vencedor is None else estado.vencedor.nome
    )
    metricas["cartas_restantes"] = [
        jogador.quantidade_cartas()
        for jogador in estado.obter_jogadores()
    ]
    return metricas


def criar_argumentos():
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--sementes", nargs="+", type=int, required=True)
    analisador.add_argument(
        "--modelos",
        nargs=2,
        choices=[
            "linear", "constante", "constante_4500", "suave", "patamar",
            "escassez", "escassez_forte",
        ],
        required=True,
    )
    return analisador


def principal():
    argumentos = criar_argumentos().parse_args()
    for semente in argumentos.sementes:
        resultado = executar_partida(semente, argumentos.modelos)
        print(json.dumps(resultado, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    principal()
