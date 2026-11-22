"""Seleciona e avalia finais táticos com desfechos verificáveis pelas regras."""

import argparse
import csv
import json
from pathlib import Path
import random

from main_q_learning import _gravar_csv
from model.enums import TipoJogada
from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada, serializar_jogada
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.minimax_agent import AgenteMinimax
from model.q_learning_agent import AgenteQLearning, TabelaQ


_PASSE = Jogada(TipoJogada.PASSE)
_CENARIOS = ("passe_favoravel", "carta_necessaria", "guardar_carta")
_CAMPOS = ("arquivo", "semente", "turno", "cenario", "melhor_passe", "melhor_carta", "apenas_passes")


def _resultado(estado, lado):
    if estado.vencedor is None:
        return 0
    return 1 if estado.vencedor is estado.obter_jogadores()[lado] else -1


def _continuar(estado, lado, escolher):
    executor = ExecutorJogada()
    jogadas = []
    while not estado.finalizado:
        atual = estado.indice_jogador_atual
        jogada = escolher(estado) if atual == lado else _PASSE
        jogadas.append(jogada)
        estado = executor.executar(estado, jogada)
    return _resultado(estado, lado), jogadas


def _melhor_resultado(estado, lado, gerador, executor):
    if estado.finalizado:
        return _resultado(estado, lado)
    if estado.indice_jogador_atual != lado:
        return _melhor_resultado(executor.executar(estado, _PASSE), lado, gerador, executor)
    melhor = -1
    for _, seguinte in gerador.gerar_com_estados(estado):
        melhor = max(melhor, _melhor_resultado(seguinte, lado, gerador, executor))
        if melhor == 1:
            return 1
    return melhor


def _classificar(estado, gerador, executor, pendentes):
    lado = estado.indice_jogador_atual
    pos_passe = executor.executar(estado, _PASSE)
    if pendentes == {"guardar_carta"} and pos_passe.finalizado:
        return None
    melhor_passe = _melhor_resultado(pos_passe, lado, gerador, executor)
    if pendentes == {"guardar_carta"} and melhor_passe != 1:
        return None
    somente_passe, _ = _continuar(pos_passe, lado, lambda _: _PASSE)
    if pendentes == {"guardar_carta"} and somente_passe == 1:
        return None
    melhor_carta = max((
        _melhor_resultado(seguinte, lado, gerador, executor)
        for jogada, seguinte in gerador.gerar_com_estados(estado) if jogada.eh_carta()
    ), default=None)
    if melhor_carta is None:
        return None
    categoria = None
    if pos_passe.finalizado and melhor_passe == 1:
        categoria = "passe_favoravel"
    elif melhor_passe == -1 and melhor_carta == 1:
        categoria = "carta_necessaria"
    elif not pos_passe.finalizado and melhor_passe == 1 and max(somente_passe, melhor_carta) < 1:
        categoria = "guardar_carta"
    if categoria in pendentes:
        return dict(cenario=categoria, melhor_passe=melhor_passe, melhor_carta=melhor_carta,
                    apenas_passes=somente_passe)


def gerar(saida, semente, quantidade, tentativas, continuar):
    caminho_csv = saida / "posicoes.csv"
    gerador, executor = GeradorJogadas(), ExecutorJogada()
    serializador = SerializadorEstadoJogo()
    contagem = dict.fromkeys(_CENARIOS, 0)
    usadas = set()
    if continuar:
        with caminho_csv.open(encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                contagem[linha["cenario"]] += 1
                usadas.add(int(linha["semente"]))
    else:
        saida.mkdir(parents=True, exist_ok=False)
    with caminho_csv.open("a" if continuar else "w", encoding="utf-8", newline="", buffering=1) as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=_CAMPOS)
        if not continuar:
            escritor.writeheader()
        for numero in range(semente, semente + tentativas):
            pendentes = {cenario for cenario, total in contagem.items() if total < quantidade}
            if not pendentes:
                return
            if numero in usadas:
                continue
            aleatorio = random.Random(numero)
            estado = ConfiguracaoJogo(numero).criar_estado_inicial(["Jogador 1", "Jogador 2"])
            turno = 0
            while not estado.finalizado:
                lado = estado.indice_jogador_atual
                jogadores = estado.obter_jogadores()
                if (estado.passes_consecutivos == 1
                        and estado.trilha_disputas.quantidade_resolvida() in (6, 7)
                        and jogadores[lado].quantidade_cartas() == 1
                        and jogadores[1 - lado].quantidade_cartas() == 0):
                    dados = _classificar(estado, gerador, executor, pendentes)
                    if dados:
                        nome = f"{dados['cenario']}_{numero}.json"
                        foto = serializador.serializar(estado)
                        (saida / nome).write_text(json.dumps(foto, ensure_ascii=False, indent=2), encoding="utf-8")
                        escritor.writerow({"arquivo": nome, "semente": numero, "turno": turno, **dados})
                        contagem[dados["cenario"]] += 1
                        print(contagem, flush=True)
                        break
                _, estado = gerador.sortear_com_estado(estado, aleatorio)
                turno += 1
    print(f"Amostra após o limite de tentativas: {contagem}", flush=True)


def avaliar(saida, tabela):
    serializador = SerializadorEstadoJogo()
    treinada = AgenteQLearning(TabelaQ.carregar(tabela))
    inicial = AgenteQLearning(TabelaQ())
    with (saida / "posicoes.csv").open(encoding="utf-8", newline="") as arquivo:
        posicoes = list(csv.DictReader(arquivo))
    campos = (*_CAMPOS, "agente", "primeira_jogada", "jogadas", "resultado")
    with _gravar_csv(saida / "decisoes.csv", campos) as escritor:
        for dados in posicoes:
            caminho = saida / dados["arquivo"]
            estado = serializador.restaurar(json.loads(caminho.read_text(encoding="utf-8")))
            lado = estado.indice_jogador_atual
            minimax = AgenteMinimax(lado)
            for nome, escolher in (
                ("q_learning", treinada.escolher_jogada),
                ("politica_inicial", inicial.escolher_jogada),
                ("minimax_1", lambda atual: minimax.escolher_jogada(atual, 1, False)),
                ("minimax_2", lambda atual: minimax.escolher_jogada(atual, 2, True)),
                ("minimax_3", lambda atual: minimax.escolher_jogada(atual, 3, True)),
            ):
                resultado, jogadas = _continuar(estado, lado, escolher)
                escritor.writerow({**dados, "agente": nome, "resultado": resultado,
                                   "primeira_jogada": jogadas[0].descrever(),
                                   "jogadas": json.dumps([serializar_jogada(jogada) for jogada in jogadas],
                                                         ensure_ascii=False, sort_keys=True)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    selecao = comandos.add_parser("gerar")
    selecao.add_argument("saida", type=Path)
    selecao.add_argument("--semente", type=int, default=55000)
    selecao.add_argument("--quantidade", type=int, default=4)
    selecao.add_argument("--tentativas", type=int, default=20000)
    selecao.add_argument("--continuar", action="store_true")
    teste = comandos.add_parser("avaliar")
    teste.add_argument("saida", type=Path)
    teste.add_argument("tabela", type=Path)
    args = parser.parse_args()
    if args.comando == "gerar":
        if args.quantidade < 1 or args.tentativas < 1:
            parser.error("Use quantidades positivas para posições e tentativas.")
        gerar(args.saida, args.semente, args.quantidade, args.tentativas, args.continuar)
    else:
        avaliar(args.saida, args.tabela)
