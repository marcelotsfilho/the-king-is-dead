"""Treina e avalia o Q-learning usando somente as regras do modelo."""

import argparse
from contextlib import contextmanager
import csv
from pathlib import Path
import random
from time import perf_counter

from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.minimax_agent import AgenteMinimax
from model.q_learning_agent import CAMINHO_TABELA_Q, AgenteQLearning, TabelaQ


_ALPHA = 0.12
_GAMMA = 0.97
_LIMITE_JOGADAS = 100
_CAMPOS = (
    "treinadas", "partida", "semente", "lado_q", "lado_inicial", "adversario",
    "epsilon", "resultado", "jogadas", "cartas_primeiro_passe_q",
    "cartas_primeiro_passe_adversario", "cartas_primeira_disputa_q",
    "cartas_primeira_disputa_adversario", "turnos_q", "estados_q_conhecidos",
    "segundos", "profundidade_adversario", "poda_adversario",
    "nos_adversario", "podas_adversario",
)


@contextmanager
def _gravar_csv(caminho, campos=_CAMPOS):
    with caminho.open("w", newline="", encoding="utf-8", buffering=1) as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        yield escritor


def executar_partida(agente, inicial, semente, lado, primeiro, adversario, profundidade,
                     epsilon=0.0, treinamento=False, estado_inicial=None, registrar_turno=None,
                     *, sortear_jogadas_q=False):
    if estado_inicial is None:
        estado = ConfiguracaoJogo(semente).criar_estado_inicial(["Jogador 1", "Jogador 2"])
        estado.indice_jogador_atual = primeiro
    else:
        estado = SerializadorEstadoJogo().copiar(estado_inicial)
        primeiro = estado.indice_jogador_atual
    executor = ExecutorJogada()
    gerador = GeradorJogadas()
    aleatorio = random.Random(semente * 100 + lado * 10 + primeiro)
    minimax = AgenteMinimax(1 - lado) if adversario in ("minimax", "alfa_beta") else None
    primeiros_passes = [None, None]
    maos_primeira_disputa = None
    anterior = None
    jogadas = turnos_q = conhecidos = 0
    nos_adversario = podas_adversario = 0
    inicio = perf_counter()

    while not estado.finalizado and jogadas < _LIMITE_JOGADAS:
        indice = estado.indice_jogador_atual
        disputas_antes = estado.trilha_disputas.quantidade_resolvida()
        cartas_antes = estado.obter_jogador_atual().quantidade_cartas()
        if indice == lado:
            inicio_turno = perf_counter() if registrar_turno is not None else None
            turno = agente.preparar_turno(estado)
            if treinamento and anterior is not None:
                agente.tabela.atualizar(*anterior, 0, turno, _ALPHA, _GAMMA)
            conhecidos += turno[0] in agente.tabela.valores
            if sortear_jogadas_q:
                jogada, novo_estado = gerador.sortear_com_estado(estado, aleatorio)
                acao = "PASSE" if jogada.eh_passe() else jogada.tipo_carta.name
            elif treinamento or epsilon:
                acao, jogada, novo_estado = agente.escolher_opcao(turno, epsilon)
            else:
                acao, jogada, novo_estado = agente.decidir_turno(estado, turno)
            if registrar_turno is not None:
                registrar_turno(jogadas + 1, acao, (perf_counter() - inicio_turno) * 1000)
            anterior = turno[0], acao
            turnos_q += 1
        elif minimax is not None:
            jogada = minimax.escolher_jogada(estado, profundidade, adversario == "alfa_beta")
            novo_estado = executor.executar(estado, jogada)
            nos_adversario += minimax.nos_visitados
            podas_adversario += minimax.podas_realizadas
        elif adversario == "aleatorio":
            jogada, novo_estado = gerador.sortear_com_estado(estado, aleatorio)
        else:
            _, jogada, novo_estado = inicial.escolher_opcao(inicial.preparar_turno(estado))

        if jogada.eh_passe() and primeiros_passes[indice] is None:
            primeiros_passes[indice] = cartas_antes
        if maos_primeira_disputa is None and novo_estado.trilha_disputas.quantidade_resolvida() > disputas_antes:
            maos_primeira_disputa = [jogador.quantidade_cartas() for jogador in novo_estado.obter_jogadores()]
        estado = novo_estado
        jogadas += 1

    resultado = "interrompida"
    if estado.finalizado:
        recompensa, resultado = 0, "empate"
        if estado.vencedor is estado.obter_jogadores()[lado]:
            recompensa, resultado = 1, "vitoria"
        elif estado.vencedor is not None:
            recompensa, resultado = -1, "derrota"
        if treinamento and anterior is not None:
            agente.tabela.atualizar(*anterior, recompensa, None, _ALPHA, _GAMMA)

    maos_primeira_disputa = maos_primeira_disputa or [None, None]
    return {
        "semente": semente, "lado_q": lado + 1, "lado_inicial": primeiro + 1,
        "adversario": adversario, "epsilon": 1.0 if sortear_jogadas_q else round(epsilon, 6),
        "resultado": resultado,
        "jogadas": jogadas, "cartas_primeiro_passe_q": primeiros_passes[lado],
        "cartas_primeiro_passe_adversario": primeiros_passes[1 - lado],
        "cartas_primeira_disputa_q": maos_primeira_disputa[lado],
        "cartas_primeira_disputa_adversario": maos_primeira_disputa[1 - lado],
        "turnos_q": turnos_q, "estados_q_conhecidos": conhecidos,
        "segundos": round(perf_counter() - inicio, 4),
        "profundidade_adversario": profundidade if minimax else "",
        "poda_adversario": adversario == "alfa_beta" if minimax else "",
        "nos_adversario": nos_adversario if minimax else "",
        "podas_adversario": podas_adversario if minimax else "",
    }


def _avaliar(agente, inicial, partidas, semente, adversario, profundidade, treinadas, escritor):
    vitorias = 0
    for partida in range(partidas):
        lado = partida % 2
        primeiro = (partida // 2) % 2
        resultado = executar_partida(
            agente, inicial, semente + partida // 2, lado, primeiro, adversario, profundidade
        )
        escritor.writerow({"treinadas": treinadas, "partida": partida + 1, **resultado})
        vitorias += resultado["resultado"] == "vitoria"
    return vitorias


def treinar(args):
    args.saida.mkdir(parents=True, exist_ok=False)
    pasta_checkpoints = args.saida / "checkpoints"
    if args.salvar_checkpoints:
        pasta_checkpoints.mkdir()
    tabela = TabelaQ()
    agente = AgenteQLearning(tabela, args.semente)
    inicial = AgenteQLearning(TabelaQ())
    sortear_jogadas = args.jogadas_aleatorias_contra_heuristica
    epsilon_inicial, epsilon_final = (1.0, 1.0) if sortear_jogadas else (0.90, 0.10)
    metadados = {
        "alpha": _ALPHA, "gamma": _GAMMA, "semente_treino": args.semente,
        "semente_validacao": (
            args.semente_validacao if args.semente_validacao is not None
            else args.semente + args.partidas + 1
        ),
        "partidas_validacao": args.validacao, "intervalo": args.intervalo,
        "partidas_planejadas": args.partidas, "epsilon_inicial": epsilon_inicial,
        "epsilon_final": epsilon_final,
    }
    if sortear_jogadas:
        metadados.update(exploracao="jogadas_legais_completas", adversario_treino="politica_inicial")
    caminho_tabela = args.saida / "tabela_q.json"
    melhor_validacao = -1
    with _gravar_csv(args.saida / "treino.csv") as treino, _gravar_csv(args.saida / "validacao.csv") as validacao:
        for numero in range(args.partidas + 1):
            if numero:
                fracao = (numero - 1) / max(args.partidas - 1, 1)
                epsilon = epsilon_inicial - (epsilon_inicial - epsilon_final) * fracao
                lado = (numero - 1) % 2
                primeiro = ((numero - 1) // 2) % 2
                adversario = "politica_inicial"
                if not sortear_jogadas and ((numero - 1) // 4) % 2:
                    adversario = "aleatorio"
                resultado = executar_partida(
                    agente, inicial, args.semente + numero - 1, lado, primeiro,
                    adversario, 1, epsilon, treinamento=True, sortear_jogadas_q=sortear_jogadas,
                )
                treino.writerow({"treinadas": numero, "partida": numero, **resultado})
            if numero % args.intervalo == 0 or numero == args.partidas:
                vitorias = _avaliar(
                    agente, inicial, args.validacao, metadados["semente_validacao"],
                    "politica_inicial", 1, numero, validacao,
                )
                if numero and vitorias > melhor_validacao:
                    tabela.salvar(caminho_tabela, {**metadados, "partidas_treinadas": numero})
                    melhor_validacao = vitorias
                if numero and args.salvar_checkpoints:
                    tabela.salvar(
                        pasta_checkpoints / f"{numero:05d}.json",
                        {**metadados, "partidas_treinadas": numero},
                    )
                print(f"{numero:>5} de treino | {vitorias}/{args.validacao} vitórias na validação | "
                      f"{len(tabela.valores)} estados", flush=True)


def avaliar(args):
    tabela = TabelaQ() if args.politica_inicial else TabelaQ.carregar(args.tabela)
    agente = AgenteQLearning(tabela)
    treinadas = tabela.metadados.get("partidas_treinadas", 0)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with _gravar_csv(args.saida) as escritor:
        for nome in args.adversarios:
            vitorias = _avaliar(
                agente, AgenteQLearning(TabelaQ()), args.partidas, args.semente,
                nome, args.profundidade, treinadas, escritor,
            )
            print(f"{nome}: {vitorias}/{args.partidas} vitórias", flush=True)


def principal():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    treino = comandos.add_parser("treinar")
    treino.add_argument("--partidas", type=int, default=1000)
    treino.add_argument("--intervalo", type=int, default=100)
    treino.add_argument("--validacao", type=int, default=40)
    treino.add_argument("--semente", type=int, default=10000)
    treino.add_argument("--semente-validacao", type=int)
    treino.add_argument("--salvar-checkpoints", action="store_true")
    treino.add_argument(
        "--jogadas-aleatorias-contra-heuristica", action="store_true",
        help="Treina com sorteio de jogadas completas em todos os turnos do Q-learning, "
             "sempre contra a política heurística inicial.",
    )
    treino.add_argument("--saida", type=Path, default=CAMINHO_TABELA_Q.parent)
    treino.set_defaults(executar=treinar)
    avaliacao = comandos.add_parser("avaliar")
    avaliacao.add_argument("--tabela", type=Path, default=CAMINHO_TABELA_Q)
    avaliacao.add_argument("--politica-inicial", action="store_true",
                           help="Avalia a mesma política com a tabela Q vazia.")
    avaliacao.add_argument("--saida", type=Path, default=CAMINHO_TABELA_Q.parent / "confrontos.csv")
    avaliacao.add_argument("--partidas", type=int, default=8, help="Partidas por adversário.")
    avaliacao.add_argument("--profundidade", type=int, default=1)
    avaliacao.add_argument("--semente", type=int, default=90000)
    avaliacao.add_argument("--adversarios", nargs="+", choices=("minimax", "alfa_beta", "politica_inicial"),
                           default=("minimax", "alfa_beta"))
    avaliacao.set_defaults(executar=avaliar)
    args = parser.parse_args()
    if args.partidas < 1:
        parser.error("Informe uma quantidade positiva de partidas.")
    if args.comando == "treinar" and (args.intervalo < 1 or args.validacao < 4 or args.validacao % 4):
        parser.error("Use intervalo positivo e uma validação com múltiplo positivo de quatro partidas.")
    if args.comando == "treinar" and args.semente_validacao is not None:
        inicio, fim = args.semente_validacao, args.semente_validacao + args.validacao // 2
        if inicio < args.semente + args.partidas and fim > args.semente:
            parser.error("As sementes da validação devem ser diferentes das de treino.")
    if args.comando == "avaliar" and (args.profundidade < 1 or args.partidas % 4):
        parser.error("Use profundidade positiva e um múltiplo de quatro partidas por adversário.")
    args.executar(args)


if __name__ == "__main__":
    principal()
