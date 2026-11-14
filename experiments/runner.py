import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from experiments.legacy_evaluator import AvaliadorInicial
from experiments.report import CAMPOS, carregar_resultados, salvar_relatorios
from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game_setup import ConfiguracaoJogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import serializar_jogada
from model.minimax_agent import AgenteMinimax
from model.player import Jogador
from model.state_evaluator import AvaliadorEstado, VERSAO_HEURISTICA
from model.state_tree_serializer import SerializadorArvoreEstados
from model.supply import ReservaSeguidores


RAIZ = Path(__file__).resolve().parent.parent


def criar_cenario(cenario, semente, caminho_arvore=None):
    if cenario == "inicial":
        return ConfiguracaoJogo(semente).criar_estado_inicial(["Jogador 1", "Jogador 2"])
    if cenario == "salvo":
        arvore = SerializadorArvoreEstados().carregar(str(caminho_arvore))
        return arvore.obter_estado_atual()
    if cenario != "reduzido":
        raise ValueError("Cenário desconhecido.")
    # Cenário sintético pequeno para validar o executor, não o desempenho inicial.
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Jogador 1"), Jogador("Jogador 2")]
    for jogador in jogadores:
        jogador.adicionar_carta_mao(CartaAcao(TipoCartaAcao.REUNIR))
    tabuleiro.obter_regiao("Moray").adicionar_seguidores(Faccao.ESCOCESES)
    tabuleiro.obter_regiao("Gwynedd").adicionar_seguidores(Faccao.GALESES)
    return EstadoJogo(tabuleiro, trilha, jogadores, ReservaSeguidores(0))


def identificar_codigo():
    resumo = hashlib.sha256()
    caminhos = [RAIZ / "main_experiments.py"]
    for pasta in ("model", "experiments"):
        caminhos.extend(sorted((RAIZ / pasta).glob("*.py")))
    for caminho in caminhos:
        resumo.update(caminho.relative_to(RAIZ).as_posix().encode())
        resumo.update(caminho.read_bytes())
    return resumo.hexdigest()


def arquivar_estado(estado, pasta):
    serializador = SerializadorEstadoJogo()
    identificador = serializador.obter_identificador(estado)
    resumo = hashlib.sha256(identificador.encode("utf-8")).hexdigest()
    pasta = Path(pasta) / "states"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / (resumo + ".json")
    if not caminho.exists():
        caminho.write_text(
            json.dumps(serializador.serializar(estado), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return resumo


def montar_plano(bateria, profundidades, repeticoes, algoritmos):
    heuristicas = ["atual", "inicial"] if bateria == "ambas" else [bateria]
    plano = []
    for heuristica in heuristicas:
        for profundidade in profundidades:
            for repeticao in range(1, repeticoes + 1):
                for algoritmo in algoritmos:
                    plano.append({
                        "heuristica": heuristica, "profundidade": profundidade,
                        "repeticao": repeticao, "algoritmo": algoritmo,
                    })
    return plano


def chave_execucao(registro):
    campos = (
        "codigo", "estado_sha256", "heuristica", "versao_heuristica", "algoritmo",
        "profundidade", "repeticao", "indice_jogador", "python", "sistema",
        "processador", "processadores_logicos",
        "hash_python",
    )
    return tuple(str(registro[campo]) for campo in campos)


def criar_registro(item, estado, estado_sha, codigo, cenario, semente):
    registro = dict.fromkeys(CAMPOS, "")
    registro.update(item)
    registro.update({
        "inicio": datetime.now(timezone.utc).isoformat(),
        "codigo": codigo, "cenario": cenario, "semente": semente,
        "estado_sha256": estado_sha, "indice_jogador": estado.indice_jogador_atual,
        "versao_heuristica": str(VERSAO_HEURISTICA) if item["heuristica"] == "atual" else "historica-1",
        "status": "em_andamento", "python": platform.python_version(),
        "sistema": platform.platform(),
        "processador": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "não informado"),
        "processadores_logicos": os.cpu_count() or "não informado",
        "hash_python": str(hash("the-king-is-dead-experiments")),
    })
    return registro


def executar_decisao(estado, registro):
    """Mede só a decisão; interrupções mantêm os contadores parciais."""
    indice = estado.indice_jogador_atual
    avaliador = AvaliadorEstado(indice)
    if registro["heuristica"] == "inicial":
        avaliador = AvaliadorInicial(indice)
    agente = AgenteMinimax(indice, avaliador=avaliador)
    inicio = perf_counter()
    interrompido = False
    try:
        jogada = agente.escolher_jogada(
            estado,
            profundidade_maxima=registro["profundidade"],
            usar_poda=registro["algoritmo"] == "alfa_beta",
        )
        tempo = perf_counter() - inicio
        if jogada is None:
            raise ValueError("A busca não retornou uma jogada completa.")
        registro["jogada"] = jogada.descrever()
        registro["jogada_json"] = json.dumps(serializar_jogada(jogada), sort_keys=True, ensure_ascii=False)
        registro["pontuacao"] = agente.ultima_pontuacao
        registro["status"] = "concluido"
    except KeyboardInterrupt:
        tempo = perf_counter() - inicio
        registro["status"] = "interrompido"
        registro["erro"] = "Interrupção solicitada pelo usuário (Ctrl+C)."
        interrompido = True
    except Exception as erro:
        tempo = perf_counter() - inicio
        registro["status"] = "erro"
        registro["erro"] = type(erro).__name__ + ": " + str(erro)
    registro["tempo_segundos"] = format(tempo, ".6f")
    registro["nos_visitados"] = agente.nos_visitados
    registro["folhas_avaliadas"] = agente.folhas_avaliadas
    registro["podas"] = agente.podas_realizadas
    return interrompido


def executar_bateria(argumentos):
    inicio = datetime.now(timezone.utc)
    pasta = Path(argumentos.saida).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    estado = criar_cenario(argumentos.cenario, argumentos.seed, argumentos.arvore)
    if estado.finalizado or estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
        raise ValueError("Use um estado em andamento, sem convocação pendente.")
    estado_sha = arquivar_estado(estado, pasta)
    codigo = identificar_codigo()
    resultados = carregar_resultados(pasta)
    for registro in resultados:
        if registro["status"] == "em_andamento":
            registro["status"] = "interrompido"
            registro["erro"] = "Execução anterior terminou sem registrar o resultado; tempo desconhecido."
    plano = montar_plano(
        argumentos.bateria, argumentos.profundidades,
        argumentos.repeticoes, argumentos.algoritmos,
    )
    inicio_bateria = len(resultados)
    puladas = 0
    semente = argumentos.seed if argumentos.cenario == "inicial" else "não se aplica"
    descricao = (
        f"Início (UTC) · {inicio.isoformat()}\n\n"
        "Cenário: " + argumentos.cenario + "; seed: " + str(semente)
        + "; bateria: " + argumentos.bateria + "; profundidades: "
        + str(argumentos.profundidades) + "; repetições: " + str(argumentos.repeticoes)
        + "; algoritmos: " + str(argumentos.algoritmos) + ". "
        + "Plano desta invocação: " + str(len(plano)) + " decisões. "
        + "Estado: " + estado_sha + "."
    )
    if argumentos.cenario == "reduzido":
        descricao += (
            " Cenário sintético de validação: reserva vazia, um escocês em Moray,"
            " um galês em Gwynedd e uma Assemble na mão de cada jogador."
        )
    elif argumentos.cenario == "inicial":
        descricao += " Estado inicial completo criado pelo setup padrão, sem ações anteriores."
    else:
        descricao += " Estado do nó atual da árvore informada em --arvore."
    horario = inicio.strftime("%Y-%m-%d_%H-%M-%S_%fZ")
    caminho_diario = pasta / f"DIARIO_DE_EXPERIMENTOS_{horario}.md"
    caminho_diario.touch(exist_ok=False)
    salvar_relatorios(caminho_diario, resultados, descricao, inicio_bateria, puladas)
    print(descricao, flush=True)
    print("Diário desta bateria:", caminho_diario, flush=True)
    if os.environ.get("PYTHONHASHSEED") != "0":
        print("Para repetir a ordem dos conjuntos entre sessões, use PYTHONHASHSEED=0 antes de iniciar o Python.", flush=True)
    if argumentos.preparar:
        print("Arquivos preparados. Nenhuma busca foi iniciada.", flush=True)
        return 0

    concluidas = {chave_execucao(r) for r in resultados if r["status"] == "concluido"}
    houve_erro = False
    for numero, item in enumerate(plano, 1):
        registro = criar_registro(item, estado, estado_sha, codigo, argumentos.cenario, semente)
        if argumentos.retomar and chave_execucao(registro) in concluidas:
            puladas += 1
            print("[" + str(numero) + "/" + str(len(plano)) + "] Já concluída; pulando.", flush=True)
            continue
        resultados.append(registro)
        try:
            salvar_relatorios(caminho_diario, resultados, descricao, inicio_bateria, puladas)
            print(
                "[" + str(numero) + "/" + str(len(plano)) + "] "
                + item["heuristica"] + " / " + item["algoritmo"]
                + " / profundidade " + str(item["profundidade"])
                + " / repetição " + str(item["repeticao"])
                + ". Calculando sem limite de tempo. Ctrl+C para interromper.", flush=True,
            )
            interrompido = executar_decisao(estado, registro)
        except KeyboardInterrupt:
            registro["status"] = "interrompido"
            registro["erro"] = "Interrompido fora da região medida; tempo desconhecido."
            interrompido = True
        finally:
            salvar_relatorios(caminho_diario, resultados, descricao, inicio_bateria, puladas)
        print(
            registro["status"] + ": " + str(registro["tempo_segundos"])
            + " s; nós=" + str(registro["nos_visitados"])
            + "; cortes=" + str(registro["podas"]), flush=True,
        )
        if interrompido:
            print("Bateria interrompida. Relatórios preservados. Use --retomar depois.", flush=True)
            return 130
        if registro["status"] == "erro":
            houve_erro = True
    if puladas:
        salvar_relatorios(caminho_diario, resultados, descricao, inicio_bateria, puladas)
    print("Plano finalizado. Consulte o CSV e o diário para verificar erros e resultados.", flush=True)
    return 1 if houve_erro else 0
