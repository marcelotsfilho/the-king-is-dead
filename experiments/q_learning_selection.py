"""Seleciona uma tabela pela validação, antes de abrir as partidas reservadas."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import random
from shutil import copyfile


def selecionar(pasta):
    curvas = []
    candidatos = []
    sustentados = []
    for rodada in sorted(pasta.glob("semente_*")):
        resultados = defaultdict(Counter)
        with (rodada / "validacao.csv").open(encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                resultados[int(linha["treinadas"])][linha["resultado"]] += 1
        pontos = []
        semente = int(rodada.name.split("_")[1])
        for treinadas in range(0, 3001, 500):
            contagem = resultados[treinadas]
            total = sum(contagem.values())
            if total != 200:
                raise ValueError(f"Validação incompleta em {rodada.name}, ponto {treinadas}: {total}")
            pontos.append({"semente": semente, "treinadas": treinadas, "partidas": total,
                           "vitorias": contagem["vitoria"], "derrotas": contagem["derrota"],
                           "empates": contagem["empate"], "interrompidas": contagem["interrompida"]})
        candidatos.extend(pontos[1:])
        primeiro = next((pontos[indice] for indice in range(1, len(pontos) - 2)
                         if all(ponto["vitorias"] >= 110 for ponto in pontos[indice:indice + 3])), None)
        if primeiro is not None:
            sustentados.append(primeiro)
        curvas.append({"semente": semente, "primeiro_sustentado": primeiro, "pontos": pontos})

    if len(curvas) != 3:
        raise ValueError("A seleção exige três execuções completas")
    criterio = len(sustentados) >= 2
    if criterio:
        escolhido = min(sustentados, key=lambda ponto: (ponto["treinadas"], -ponto["vitorias"], ponto["semente"]))
    else:
        escolhido = max(candidatos, key=lambda ponto: (ponto["vitorias"], -ponto["treinadas"], -ponto["semente"]))
    origem = Path(f"semente_{escolhido['semente']}") / "checkpoints" / f"{escolhido['treinadas']:05d}.json"
    resumo = {"criterio_sustentado": criterio, "escolhido": escolhido,
              "origem_tabela": origem.as_posix(), "execucoes": curvas}
    copyfile(pasta / origem, pasta / "tabela_selecionada.json")
    (pasta / "selecao.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")
    print(json.dumps({chave: valor for chave, valor in resumo.items() if chave != "execucoes"}), flush=True)


def _ler_amostra(caminho):
    por_semente = defaultdict(dict)
    contagem = Counter()
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            par = por_semente[int(linha["semente"])]
            lado = linha["lado_q"], linha["lado_inicial"]
            resultado = linha["resultado"]
            if lado in par or resultado not in ("vitoria", "derrota", "empate"):
                raise ValueError(f"Partida reservada duplicada ou incompleta em {caminho}")
            par[lado] = int(resultado == "vitoria")
            contagem[resultado] += 1
    if not por_semente or any(len(par) != 2 for par in por_semente.values()):
        raise ValueError("A amostra reservada deve ter duas partidas por semente")
    return por_semente, contagem


def _intervalo95(valores):
    aleatorio = random.Random(0)
    quantidade = len(valores)
    amostras = sorted(sum(aleatorio.choices(valores, k=quantidade)) / quantidade for _ in range(10000))
    return [round(amostras[indice], 4) for indice in (250, 9749)]


def comparar_reservada(pasta):
    resumo = {}
    pareadas = []
    for nome in ("selecionada", "anterior"):
        partidas, contagem = _ler_amostra(pasta / f"reservada_tabela_{nome}.csv")
        taxas = {semente: sum(par.values()) / len(par) for semente, par in partidas.items()}
        resumo[nome] = {"resultados": dict(contagem), "sementes": len(taxas),
                        "taxa_vitoria": round(sum(taxas.values()) / len(taxas), 4),
                        "intervalo95": _intervalo95(list(taxas.values()))}
        pareadas.append((partidas, taxas))
    (nova_partidas, nova_taxas), (anterior_partidas, anterior_taxas) = pareadas
    if {s: par.keys() for s, par in nova_partidas.items()} != {s: par.keys() for s, par in anterior_partidas.items()}:
        raise ValueError("As duas tabelas devem ser avaliadas nas mesmas partidas reservadas")
    diferencas = [nova_taxas[s] - anterior_taxas[s] for s in nova_taxas]
    resumo["diferenca_selecionada_menos_anterior"] = {
        "taxa_vitoria": round(sum(diferencas) / len(diferencas), 4),
        "intervalo95": _intervalo95(diferencas),
    }
    (pasta / "reservada_resumo.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")
    print(json.dumps(resumo), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--comparar-reservada", action="store_true")
    args = parser.parse_args()
    if args.comparar_reservada:
        comparar_reservada(args.pasta)
    else:
        selecionar(args.pasta)
