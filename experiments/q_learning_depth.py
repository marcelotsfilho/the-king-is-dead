"""Mede busca na abertura e compara profundidades em finais de partidas reais."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from main_q_learning import _CAMPOS, _gravar_csv, executar_partida
from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.minimax_agent import AgenteMinimax
from model.q_learning_agent import AgenteQLearning, TabelaQ


def medir_decisao(caminho, algoritmo, profundidade):
    estado = SerializadorEstadoJogo().restaurar(json.loads(caminho.read_text(encoding="utf-8")))
    agente = AgenteMinimax(estado.indice_jogador_atual)
    inicio = perf_counter()
    jogada = agente.escolher_jogada(estado, profundidade, algoritmo == "alfa_beta")
    print(json.dumps({"segundos": round(perf_counter() - inicio, 4), "jogada": jogada.descrever(),
                      "nos": agente.nos_visitados, "podas": agente.podas_realizadas}, ensure_ascii=True))


def _salvar_estado(estado, caminho):
    dados = SerializadorEstadoJogo().serializar(estado)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def medir_abertura(saida, semente, limite):
    saida.mkdir(parents=True, exist_ok=False)
    caminho = saida / "abertura.json"
    _salvar_estado(ConfiguracaoJogo(semente).criar_estado_inicial(["Jogador 1", "Jogador 2"]), caminho)
    campos = ("semente", "algoritmo", "profundidade", "limite_segundos", "status",
              "segundos", "jogada", "nos", "podas")
    with _gravar_csv(saida / "tempos.csv", campos) as escritor:
        for profundidade in (1, 2):
            for algoritmo in ("minimax", "alfa_beta"):
                comando = [sys.executable, "-m", "experiments.q_learning_depth", "medir", str(caminho),
                           algoritmo, str(profundidade)]
                try:
                    processo = subprocess.run(comando, check=True, capture_output=True, timeout=limite)
                except subprocess.TimeoutExpired:
                    medida = {"status": "tempo_esgotado", "segundos": limite}
                else:
                    medida = {"status": "concluido", **json.loads(processo.stdout)}
                escritor.writerow({"semente": semente, "algoritmo": algoritmo, "profundidade": profundidade,
                                   "limite_segundos": limite, **medida})
                print(f"Abertura {algoritmo} {profundidade}: {medida['status']}", flush=True)


def _gerar_final(semente, politica):
    estado = ConfiguracaoJogo(semente).criar_estado_inicial(["Jogador 1", "Jogador 2"])
    turno = 0
    while not estado.finalizado:
        cartas = [jogador.quantidade_cartas() for jogador in estado.obter_jogadores()]
        disputas = estado.trilha_disputas.quantidade_resolvida()
        if disputas == 6 and all(1 <= quantidade <= 2 for quantidade in cartas):
            opcoes = politica.preparar_turno(estado)[1]
            if len(opcoes) > 1:
                return estado, turno
        _, _, estado = politica.escolher_opcao(politica.preparar_turno(estado))
        turno += 1
    return None


def confrontar_finais(saida, tabela, quantidade, semente):
    saida.mkdir(parents=True, exist_ok=False)
    pasta_estados = saida / "estados"
    pasta_estados.mkdir()
    inicial = AgenteQLearning(TabelaQ())
    carregada = TabelaQ.carregar(tabela)
    treinada = AgenteQLearning(carregada)
    campos = ("posicao", "jogadas_ate_posicao", "politica", *_CAMPOS)
    with _gravar_csv(saida / "confrontos.csv", campos) as escritor:
        obtidas = 0
        for numero in range(semente, semente + 1000):
            final = _gerar_final(numero, inicial)
            if final is None:
                continue
            estado, turno = final
            nome = f"final_{numero}.json"
            _salvar_estado(estado, pasta_estados / nome)
            obtidas += 1
            for profundidade in (1, 2):
                for algoritmo in ("minimax", "alfa_beta"):
                    for agente, politica, treinadas in (
                        (inicial, "inicial", 0), (treinada, "treinada", carregada.metadados["partidas_treinadas"]),
                    ):
                        for lado in (0, 1):
                            resultado = executar_partida(
                                agente, inicial, numero, lado, estado.indice_jogador_atual,
                                algoritmo, profundidade, estado_inicial=estado,
                            )
                            escritor.writerow({"posicao": nome, "jogadas_ate_posicao": turno, "politica": politica,
                                               "treinadas": treinadas, "partida": obtidas, **resultado})
            print(f"Final {obtidas}/{quantidade}: seed {numero}", flush=True)
            if obtidas == quantidade:
                return
    raise RuntimeError(f"Foram encontradas {obtidas} das {quantidade} posições solicitadas")


def jogar_da_abertura(tabela, semente, lado):
    carregada = TabelaQ.carregar(tabela)
    resultado = executar_partida(
        AgenteQLearning(carregada), AgenteQLearning(TabelaQ()), semente, lado, 0, "alfa_beta", 2,
    )
    print(json.dumps({"treinadas": carregada.metadados["partidas_treinadas"], **resultado}))


def testar_partidas(saida, tabela, semente, limite):
    carregada = TabelaQ.carregar(tabela)
    campos = (*_CAMPOS, "limite_segundos")
    with _gravar_csv(saida, campos) as escritor:
        for lado in (0, 1):
            comando = [sys.executable, "-m", "experiments.q_learning_depth", "jogar", str(tabela),
                       str(semente), str(lado)]
            try:
                processo = subprocess.run(comando, check=True, capture_output=True, timeout=limite)
            except subprocess.TimeoutExpired:
                resultado = dict(treinadas=carregada.metadados["partidas_treinadas"], semente=semente,
                                 lado_q=lado + 1, lado_inicial=1, adversario="alfa_beta", epsilon=0,
                                 resultado="tempo_esgotado", segundos=limite, profundidade_adversario=2,
                                 poda_adversario=True)
            else:
                resultado = json.loads(processo.stdout)
            escritor.writerow({"partida": lado + 1, "limite_segundos": limite, **resultado})
            print(f"Partida de abertura, lado {lado + 1}: {resultado['resultado']}", flush=True)


def principal():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    abertura = comandos.add_parser("abertura")
    abertura.add_argument("saida", type=Path)
    abertura.add_argument("--semente", type=int, default=53000)
    abertura.add_argument("--limite", type=int, default=30)
    finais = comandos.add_parser("finais")
    finais.add_argument("saida", type=Path)
    finais.add_argument("tabela", type=Path)
    finais.add_argument("--posicoes", type=int, default=8)
    finais.add_argument("--semente", type=int, default=54000)
    partidas = comandos.add_parser("partidas")
    partidas.add_argument("saida", type=Path)
    partidas.add_argument("tabela", type=Path)
    partidas.add_argument("--semente", type=int, default=53010)
    partidas.add_argument("--limite", type=int, default=60)
    jogar = comandos.add_parser("jogar")
    jogar.add_argument("tabela", type=Path)
    jogar.add_argument("semente", type=int)
    jogar.add_argument("lado", type=int, choices=(0, 1))
    medir = comandos.add_parser("medir")
    medir.add_argument("estado", type=Path)
    medir.add_argument("algoritmo", choices=("minimax", "alfa_beta"))
    medir.add_argument("profundidade", type=int)
    args = parser.parse_args()
    if args.comando == "abertura":
        medir_abertura(args.saida, args.semente, args.limite)
    elif args.comando == "finais":
        confrontar_finais(args.saida, args.tabela, args.posicoes, args.semente)
    elif args.comando == "partidas":
        testar_partidas(args.saida, args.tabela, args.semente, args.limite)
    elif args.comando == "jogar":
        jogar_da_abertura(args.tabela, args.semente, args.lado)
    else:
        medir_decisao(args.estado, args.algoritmo, args.profundidade)


if __name__ == "__main__":
    principal()
