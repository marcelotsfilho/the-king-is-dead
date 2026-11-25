"""Compara a política Q com a mesma tabela apoiada pela busca de finais."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from math import ceil
from pathlib import Path
import random
from time import perf_counter

from experiments.q_learning_tactics import _continuar, _melhor_resultado
from main_q_learning import _CAMPOS, _gravar_csv, executar_partida
from model.game_setup import ConfiguracaoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import serializar_jogada
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.minimax_agent import AgenteMinimax
from model.q_learning_agent import CAMINHO_TABELA_Q, AgenteQLearning, TabelaQ


_TABELA_HISTORICA = CAMINHO_TABELA_Q.parent / "bateria_3000" / "tabela_selecionada.json"
_PASTA_HISTORICA = _TABELA_HISTORICA.parent / "taticas"


def _ler_estado(caminho):
    return SerializadorEstadoJogo().restaurar(json.loads(caminho.read_text(encoding="utf-8")))


def _jogada_json(jogada):
    return json.dumps(serializar_jogada(jogada), ensure_ascii=False, sort_keys=True)


def auditar(saida, tabela):
    saida.mkdir(parents=True, exist_ok=True)
    agente = AgenteQLearning(tabela)
    gerador, executor = GeradorJogadas(), ExecutorJogada()
    campos = ("posicao", "semente", "acao", "jogada", "descricao", "nota_imediata", "q",
              "candidata", "representante", "escolhida", "desfecho_otimo")
    with (_PASTA_HISTORICA / "posicoes.csv").open(encoding="utf-8", newline="") as arquivo:
        posicoes = list(csv.DictReader(arquivo))
    with _gravar_csv(saida / "auditoria.csv", campos) as escritor:
        for dados in posicoes:
            estado = _ler_estado(_PASTA_HISTORICA / dados["arquivo"])
            lado = estado.indice_jogador_atual
            amostra = {}

            def registrar(_acao, jogada, _seguinte, nota):
                amostra[_jogada_json(jogada)] = nota

            chave, opcoes = agente.preparar_turno(estado, registrar)
            _, escolhida, _ = agente.escolher_opcao((chave, opcoes))
            for jogada, seguinte in gerador.gerar_com_estados(estado):
                acao = "PASSE" if jogada.eh_passe() else jogada.tipo_carta.name
                chave_jogada = _jogada_json(jogada)
                escritor.writerow({
                    "posicao": dados["arquivo"], "semente": dados["semente"],
                    "acao": acao, "jogada": chave_jogada, "descricao": jogada.descrever(),
                    "nota_imediata": amostra.get(chave_jogada, ""), "q": tabela.consultar(chave, acao),
                    "candidata": chave_jogada in amostra,
                    "representante": acao in opcoes and jogada.possui_mesmos_dados(opcoes[acao][0]),
                    "escolhida": jogada.possui_mesmos_dados(escolhida),
                    "desfecho_otimo": _melhor_resultado(seguinte, lado, gerador, executor),
                })


def _valor_exaustivo(estado, lado, gerador):
    if estado.finalizado:
        if estado.vencedor is None:
            return 0
        return 1 if estado.vencedor is estado.obter_jogadores()[lado] else -1
    valores = (_valor_exaustivo(seguinte, lado, gerador) for _, seguinte in gerador.gerar_com_estados(estado))
    return max(valores) if estado.indice_jogador_atual == lado else min(valores)


def _gerar_posicao(semente, gerador, cartas):
    estado = ConfiguracaoJogo(semente).criar_estado_inicial(["Jogador 1", "Jogador 2"])
    aleatorio = random.Random(semente)
    while not estado.finalizado:
        jogadores = estado.obter_jogadores()
        lado = estado.indice_jogador_atual
        jogador, adversario = jogadores[lado], jogadores[1 - lado]
        maos = jogador.quantidade_cartas(), adversario.quantidade_cartas()
        if estado.trilha_disputas.quantidade_resolvida() == 6 and maos == cartas:
            return estado
        _, estado = gerador.sortear_com_estado(estado, aleatorio)
    return None


def avaliar_posicoes(saida, tabela, semente, por_grupo):
    saida.mkdir(parents=True, exist_ok=True)
    fotos = saida / "estados"
    fotos.mkdir(exist_ok=True)
    gerador = GeradorJogadas()
    serializador = SerializadorEstadoJogo()
    original, hibrido = AgenteQLearning(tabela), AgenteQLearning(tabela, analisar_finais=True)
    campos = ("posicao", "semente", "amostra", "mao_atual", "mao_oponente", "passes_antes",
              "agente", "valor_otimo", "valor_escolha", "jogada", "milissegundos", "nos_busca",
              "busca_concluida", "busca_alterou")
    with _gravar_csv(saida / "posicoes.csv", campos) as escritor:
        for caminho in sorted(_PASTA_HISTORICA.glob("*.json")):
            estado = _ler_estado(caminho)
            _avaliar_posicao(escritor, estado, caminho.name, "regressao", gerador, original, hibrido)
        for grupo, cartas in enumerate(((1, 0), (1, 1), (2, 0))):
            obtidas = 0
            for numero in range(semente + grupo * 10000, semente + grupo * 10000 + 10000):
                estado = _gerar_posicao(numero, gerador, cartas)
                if estado is None:
                    continue
                valores = _desfechos_legais(estado, gerador)
                # A amostra separa decisões que de fato admitem resultados diferentes.
                if len(set(valores.values())) < 2:
                    continue
                nome = f"posicao_{numero}.json"
                (fotos / nome).write_text(json.dumps(serializador.serializar(estado), ensure_ascii=False, indent=2),
                                          encoding="utf-8")
                _avaliar_posicao(escritor, estado, nome, "inedita", gerador, original, hibrido, valores)
                obtidas += 1
                if obtidas == por_grupo:
                    break
            if obtidas != por_grupo:
                raise RuntimeError(f"Amostra incompleta para mãos {cartas}: {obtidas}")


def _desfechos_legais(estado, gerador):
    lado = estado.indice_jogador_atual
    return {_jogada_json(jogada): _valor_exaustivo(seguinte, lado, gerador)
            for jogada, seguinte in gerador.gerar_com_estados(estado)}


def _avaliar_posicao(escritor, estado, nome, amostra, gerador, original, hibrido, valores=None):
    if valores is None:
        valores = _desfechos_legais(estado, gerador)
    lado = estado.indice_jogador_atual
    jogadores = estado.obter_jogadores()
    minimax = AgenteMinimax(lado)
    for rotulo, escolher in (("q", original.escolher_jogada), ("q_com_busca", hibrido.escolher_jogada),
                             ("alfa_beta_3", lambda atual: minimax.escolher_jogada(atual, 3, True))):
        inicio = perf_counter()
        jogada = _jogada_json(escolher(estado))
        milissegundos = (perf_counter() - inicio) * 1000
        escritor.writerow({"posicao": nome, "semente": nome.rsplit("_", 1)[1].removesuffix(".json"),
                           "amostra": amostra, "mao_atual": jogadores[lado].quantidade_cartas(),
                           "mao_oponente": jogadores[1 - lado].quantidade_cartas(),
                           "passes_antes": estado.passes_consecutivos, "agente": rotulo,
                           "valor_otimo": max(valores.values()), "valor_escolha": valores[jogada], "jogada": jogada,
                           "milissegundos": round(milissegundos, 3),
                           "nos_busca": hibrido.nos_busca_final if rotulo == "q_com_busca" else "",
                           "busca_concluida": hibrido.busca_final_concluida if rotulo == "q_com_busca" else "",
                           "busca_alterou": hibrido.busca_final_alterou if rotulo == "q_com_busca" else ""})


def confrontar(saida, tabela, adversario, partidas, semente):
    saida.mkdir(parents=True, exist_ok=False)
    inicial = AgenteQLearning(TabelaQ())
    campos = ("agente", "jogada", "acao", "milissegundos", "nos_busca", "busca_concluida", "busca_alterou",
              "semente", "lado_q", "lado_inicial")
    with _gravar_csv(saida / "partidas.csv", ("agente", *_CAMPOS)) as jogo_csv, \
            _gravar_csv(saida / "turnos.csv", campos) as turno_csv:
        for analise, rotulo in ((False, "q"), (True, "q_com_busca")):
            agente = AgenteQLearning(tabela, analisar_finais=analise)
            for partida in range(partidas):
                numero, lado, primeiro = semente + partida // 2, partida % 2, (partida // 2) % 2

                def registrar(jogada, acao, ms):
                    turno_csv.writerow({"agente": rotulo, "jogada": jogada, "acao": acao,
                                       "milissegundos": round(ms, 3), "nos_busca": agente.nos_busca_final,
                                       "busca_concluida": agente.busca_final_concluida,
                                       "busca_alterou": agente.busca_final_alterou, "semente": numero,
                                       "lado_q": lado + 1, "lado_inicial": primeiro + 1})

                resultado = executar_partida(agente, inicial, numero, lado, primeiro, adversario, 1,
                                             registrar_turno=registrar)
                jogo_csv.writerow({"agente": rotulo, "treinadas": tabela.metadados["partidas_treinadas"],
                                   "partida": partida + 1, **resultado})
            print(f"{rotulo}: {partidas} partidas registradas", flush=True)


def _linhas(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def _tempos(linhas):
    ordenados = sorted(float(linha["milissegundos"]) for linha in linhas)
    return {"n": len(ordenados), "p95_ms": ordenados[ceil(0.95 * len(ordenados)) - 1],
            "max_ms": ordenados[-1]}


def resumir(saida):
    posicoes = defaultdict(list)
    for linha in _linhas(saida / "avaliacao_tatica" / "posicoes.csv"):
        posicoes[f"{linha['amostra']}/{linha['agente']}"].append(linha)
    resumo = {"posicoes": {nome: {
        "otimas": sum(linha["valor_escolha"] == linha["valor_otimo"] for linha in grupo),
        "mudancas": sum(linha["busca_alterou"] == "True" for linha in grupo),
        "limites": sum(int(linha["nos_busca"] or 0) > 0 and linha["busca_concluida"] == "False" for linha in grupo),
        **_tempos(grupo),
    } for nome, grupo in sorted(posicoes.items())}}

    for pasta in ("partidas_politica_inicial", "partidas_alfa_beta"):
        jogos = _linhas(saida / pasta / "partidas.csv")
        turnos = _linhas(saida / pasta / "turnos.csv")
        grupos = {}
        pareados = defaultdict(dict)
        for linha in jogos:
            chave = linha["semente"], linha["lado_q"], linha["lado_inicial"]
            pareados[chave][linha["agente"]] = linha["resultado"]
        for agente in ("q", "q_com_busca"):
            decisoes = [linha for linha in turnos if linha["agente"] == agente]
            grupos[agente] = {"resultados": dict(Counter(linha["resultado"] for linha in jogos if linha["agente"] == agente)),
                              "mudancas": sum(linha["busca_alterou"] == "True" for linha in decisoes),
                              **_tempos(decisoes)}
        grupos["mudancas_de_resultado"] = dict(Counter(
            f"{par['q']} -> {par['q_com_busca']}" for par in pareados.values() if par["q"] != par["q_com_busca"]
        ))
        resumo[pasta] = grupos
    (saida / "resumo.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")


def demonstrar(caminho, tabela):
    estado = _ler_estado(caminho)
    lado = estado.indice_jogador_atual
    if estado.obter_jogadores()[1 - lado].quantidade_cartas():
        raise ValueError("A demonstração usa uma posição em que o adversário só pode passar")
    nomes = {1: "vitória", 0: "empate", -1: "derrota"}
    for analise, rotulo in ((False, "Q-learning"), (True, "Q-learning com busca de final")):
        agente = AgenteQLearning(tabela, analisar_finais=analise)
        resultado, jogadas = _continuar(estado, lado, agente.escolher_jogada)
        print(rotulo + " — " + nomes[resultado])
        for jogada in jogadas:
            print("  " + jogada.descrever())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modo", choices=("auditoria", "posicoes", "confrontos", "resumo", "demonstrar"))
    parser.add_argument("saida", type=Path)
    parser.add_argument("--tabela", type=Path, default=_TABELA_HISTORICA)
    parser.add_argument("--semente", type=int, default=174000)
    parser.add_argument("--adversario", choices=("politica_inicial", "alfa_beta"), default="politica_inicial")
    parser.add_argument("--partidas", type=int, default=200)
    parser.add_argument("--por-grupo", type=int, default=8)
    args = parser.parse_args()
    if args.partidas < 4 or args.partidas % 4 or args.por_grupo < 1:
        parser.error("Use um múltiplo positivo de quatro para partidas e um tamanho de grupo positivo.")
    if args.modo == "resumo":
        resumir(args.saida)
    else:
        tabela = TabelaQ.carregar(args.tabela)
        if args.modo == "auditoria":
            auditar(args.saida, tabela)
        elif args.modo == "posicoes":
            avaliar_posicoes(args.saida, tabela, args.semente, args.por_grupo)
        elif args.modo == "demonstrar":
            demonstrar(args.saida, tabela)
        else:
            confrontar(args.saida, tabela, args.adversario, args.partidas, args.semente)
