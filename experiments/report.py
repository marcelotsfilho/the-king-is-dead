import csv
from pathlib import Path
from statistics import mean


CAMPOS = [
    "inicio", "codigo", "cenario", "semente", "estado_sha256",
    "heuristica", "versao_heuristica", "algoritmo", "profundidade", "repeticao",
    "indice_jogador", "status", "tempo_segundos", "nos_visitados",
    "folhas_avaliadas", "podas", "pontuacao", "jogada", "jogada_json",
    "erro", "python", "sistema", "processador", "processadores_logicos",
    "hash_python",
]


def carregar_resultados(pasta):
    caminho = Path(pasta) / "results.csv"
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        if leitor.fieldnames != CAMPOS:
            raise ValueError("O CSV existente possui outro formato; escolha outra pasta de saída.")
        return list(leitor)


def salvar_relatorios(caminho_diario, resultados, plano, inicio_bateria=0, puladas=0):
    """Grava o histórico no CSV e as tentativas desta bateria no diário."""
    pasta = caminho_diario.parent
    temporario = pasta / "results.csv.tmp"
    with temporario.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, delimiter=";")
        escritor.writeheader()
        escritor.writerows(resultados)
    temporario.replace(pasta / "results.csv")

    texto = gerar_diario(resultados[inicio_bateria:], plano, puladas)
    temporario = caminho_diario.with_suffix(".md.tmp")
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(caminho_diario)


def gerar_diario(resultados, plano, puladas):
    linhas = [
        "# Diário automático de experimentos", "",
        "Este diário reúne os testes desta chamada do executor.",
        "O [histórico completo](results.csv) reúne os registros de todas as baterias.", "",
        "## Cenário e protocolo", "",
        plano, "",
        f"Configurações já concluídas e puladas nesta chamada · {puladas}", "",
        "Cada execução mede UMA decisão de jogada, não uma partida inteira.",
        "A busca usa o jogador atual como referência. As execuções rodam sequencialmente",
        "no terminal, sem Pygame. Não há limite automático de tempo; Ctrl+C interrompe",
        "a execução atual e encerra a bateria preservando os registros anteriores.", "",
        "Atual: avaliação estática do jogo. Inicial: reconstrução da fórmula anterior",
        "à otimização, com expansão de ameaças e mobilidade. As fórmulas e pesos",
        "diferem: comparar seus tempos não comprova qual joga melhor.", "",
        "O tempo inclui apenas escolher_jogada (geração, simulações e avaliação).",
        "Não inclui preparação, carregamento, salvamento, impressão ou relatórios.",
        "Em interrupções, os contadores são parciais e a pontuação/jogada ficam vazias.",
        "Os contadores do Minimax não incluem simulações internas da heurística antiga.", "",
        "## Execuções registradas", "",
        "| Nº | Cenário | Heurística | Algoritmo | Prof. | Rep. | Status | Tempo (s) | Nós | Folhas | Cortes | Pontuação |",
        "|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    grupos = {}
    comparacoes = {}
    interrupcoes = []
    for indice, resultado in enumerate(resultados, 1):
        r = resultado
        linhas.append(
            "| " + " | ".join(str(valor) for valor in (
                indice, r["cenario"], r["heuristica"], r["algoritmo"],
                r["profundidade"], r["repeticao"], r["status"],
                r["tempo_segundos"], r["nos_visitados"], r["folhas_avaliadas"],
                r["podas"], r["pontuacao"],
            )) + " |"
        )
        if r["status"] == "interrompido":
            interrupcoes.append((indice, r))
        if r["status"] != "concluido":
            continue
        chave = tuple(str(r[campo]) for campo in (
            "codigo", "estado_sha256", "heuristica", "versao_heuristica",
            "algoritmo", "profundidade", "python", "sistema", "processador", "processadores_logicos", "hash_python",
        ))
        grupos.setdefault(chave, []).append(r)
        chave_comparacao = tuple(str(r[campo]) for campo in (
            "codigo", "estado_sha256", "heuristica", "versao_heuristica",
            "profundidade", "repeticao", "python", "sistema", "processador", "processadores_logicos", "hash_python",
        ))
        comparacoes.setdefault(chave_comparacao, {})[r["algoritmo"]] = r
    if grupos:
        linhas.extend(["", "## Jogadas escolhidas", ""])
        for indice, resultado in enumerate(resultados, 1):
            if resultado["status"] == "concluido":
                linhas.append(f"- Execução {indice} · {resultado['jogada']}")
    linhas.extend(["", "## Tempos das execuções concluídas", ""])
    for registros in grupos.values():
        r = registros[0]
        tempos = [float(item["tempo_segundos"]) for item in registros]
        linhas.append(
            "- " + r["cenario"] + ", seed " + str(r["semente"])
            + ", " + r["heuristica"] + ", " + r["algoritmo"]
            + ", profundidade " + str(r["profundidade"])
            + ": n=" + str(len(tempos)) + ", média=" + format(mean(tempos), ".6f")
            + " s, mínimo=" + format(min(tempos), ".6f")
            + " s, máximo=" + format(max(tempos), ".6f")
            + " s. Estado/código: " + r["estado_sha256"][:12] + "/" + r["codigo"][:12] + "."
        )
    if not grupos:
        linhas.append("Ainda não há execuções concluídas; não é possível concluir sobre desempenho.")

    linhas.extend(["", "## Resultados parciais dos testes interrompidos", ""])
    if interrupcoes:
        linhas.extend([
            "Os valores mostram o progresso até a interrupção. As médias usam apenas testes concluídos.",
            "O traço indica uma medição indisponível.", "",
            "| Nº | Heurística | Algoritmo | Prof. | Rep. | Tempo parcial (s) | Nós visitados | Folhas avaliadas | Cortes |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for indice, r in interrupcoes:
            valores = (
                indice, r["heuristica"], r["algoritmo"], r["profundidade"],
                r["repeticao"], r["tempo_segundos"], r["nos_visitados"],
                r["folhas_avaliadas"], r["podas"],
            )
            linhas.append("| " + " | ".join("—" if valor == "" else str(valor) for valor in valores) + " |")
    else:
        linhas.append("Nenhum teste interrompido nesta bateria.")

    pares = 0
    divergencias = 0
    for par in comparacoes.values():
        if "minimax" in par and "alfa_beta" in par:
            pares += 1
            a, b = par["minimax"], par["alfa_beta"]
            if float(a["pontuacao"]) != float(b["pontuacao"]) or a["jogada_json"] != b["jogada_json"]:
                divergencias += 1
    linhas.extend([
        "", "## Comparação e limites", "",
        "Pares concluídos comparáveis entre Minimax e alfa-beta: " + str(pares) + ".",
        "Pares com divergência de nota ou jogada: " + str(divergencias) + ".",
        "Compare somente pares da mesma heurística, posição, código e profundidade.",
        "Interrompido não significa derrota ou erro do algoritmo; não é tempo de conclusão.",
        "Uma execução longa não estabelece o limite máximo viável. Ainda é necessário",
        "definir o tempo aceitável para o usuário e analisar outras posições e seeds.", "",
        "## Ambiente e rastreabilidade", "",
    ])
    ambientes = set()
    for r in resultados:
        ambiente = (r["codigo"], r["python"], r["sistema"], r["processador"], str(r["processadores_logicos"]))
        if ambiente not in ambientes:
            ambientes.add(ambiente)
            linhas.append("- Código/Python/SO/CPU/CPUs lógicas: " + " / ".join(ambiente))
    linhas.extend([
        "", "## Erros e interrupções", "",
    ])
    ocorrencias = False
    for indice, r in enumerate(resultados, 1):
        if r["erro"]:
            ocorrencias = True
            linhas.append("- Execução " + str(indice) + ": " + r["erro"].replace("\n", " "))
    if not ocorrencias:
        linhas.append("Nenhum erro ou interrupção registrado.")
    linhas.extend([
        "", "As posições são arquivadas em states/<estado_sha256>.json.",
        "O hash do código identifica os fontes usados, inclusive alterações sem commit.",
        "Não foram medidos consumo de memória, taxa de vitória ou treinamento.", "",
    ])
    return "\n".join(linhas)
