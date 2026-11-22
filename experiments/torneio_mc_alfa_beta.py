"""Torneio local Monte Carlo contra Minimax com alfa-beta."""

import argparse
import csv
from pathlib import Path
import sys
from time import perf_counter

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from model.enums import FaseTurno
from model.game_setup import ConfiguracaoJogo
from model.legal_move_executor import ExecutorJogada
from model.minimax_agent import AgenteMinimax
from model.monte_carlo_agent import AgenteMonteCarlo


CAMPOS = (
    "seed", "mc_player", "first_player", "simulations", "minimax_depth",
    "winner", "status", "duration_seconds", "plies", "mc_decisions",
    "mc_avg_seconds", "mc_max_seconds", "mc_nodes", "mc_simulations",
    "ab_decisions", "ab_avg_seconds", "ab_max_seconds", "ab_nodes",
    "ab_leaves", "ab_prunes", "mc_passes", "ab_passes", "pass_pairs",
    "regions_resolved_by_passes", "early_resolutions_with_cards_remaining",
    "early_resolutions_with_both_hands_nonempty",
)
EVENT_FIELDS = (
    "seed", "ply", "actor", "algorithm", "action", "description",
    "pass_streak_before", "pass_streak_after", "pass_pair_completed",
    "region_resolved", "region_name", "resolved_regions_before",
    "resolved_regions_after", "mc_cards_before", "ab_cards_before",
    "mc_cards_after", "ab_cards_after", "both_hands_nonempty_after",
    "last_message",
)


def executar_partida(
    seed, simulacoes, profundidade, max_plies=100,
    escritor_eventos=None, arquivo_eventos=None,
):
    estado = ConfiguracaoJogo(seed).criar_estado_inicial(["Monte Carlo", "Alfa-beta"])
    mc_player = seed % 2
    first_player = (seed // 2) % 2
    estado.indice_jogador_atual = first_player
    executor = ExecutorJogada()
    mc_times, ab_times = [], []
    mc_nodes = mc_sims = ab_nodes = ab_leaves = ab_prunes = 0
    mc_passes = ab_passes = pass_pairs = 0
    regions_resolved_by_passes = early_with_cards = early_with_both_hands = 0
    inicio_partida = perf_counter()
    plies = 0

    while not estado.finalizado and plies < max_plies:
        if estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
            raise RuntimeError("Partida chegou a uma fase intermediária inesperada.")
        indice = estado.indice_jogador_atual
        inicio_decisao = perf_counter()
        if indice == mc_player:
            agente = AgenteMonteCarlo(indice, semente=seed * 100_000 + plies)
            jogada = agente.escolher_jogada(
                estado,
                quantidade_simulacoes=simulacoes,
            )
            mc_times.append(perf_counter() - inicio_decisao)
            mc_nodes += agente.nos_visitados
            mc_sims += agente.simulacoes_realizadas
        else:
            agente = AgenteMinimax(indice)
            jogada = agente.escolher_jogada(
                estado,
                profundidade_maxima=profundidade,
                usar_poda=True,
            )
            ab_times.append(perf_counter() - inicio_decisao)
            ab_nodes += agente.nos_visitados
            ab_leaves += agente.folhas_avaliadas
            ab_prunes += agente.podas_realizadas

        if jogada is None:
            raise RuntimeError("Agente não retornou jogada para estado não terminal.")
        jogadores = estado.obter_jogadores()
        mao_mc_antes = jogadores[mc_player].quantidade_cartas()
        mao_ab_antes = jogadores[1 - mc_player].quantidade_cartas()
        passes_antes = estado.passes_consecutivos
        resolvidas_antes = estado.trilha_disputas.quantidade_resolvida()
        proxima_carta = estado.trilha_disputas.obter_proxima_carta()
        regiao_alvo = proxima_carta.nome_regiao if proxima_carta is not None else ""
        eh_passe = jogada.eh_passe()
        if eh_passe:
            if indice == mc_player:
                mc_passes += 1
            else:
                ab_passes += 1
            if passes_antes == 1:
                pass_pairs += 1
        estado = executor.executar(estado, jogada)
        plies += 1
        resolvidas_depois = estado.trilha_disputas.quantidade_resolvida()
        houve_resolucao = resolvidas_depois > resolvidas_antes
        pares_passe = eh_passe and passes_antes == 1
        jogadores_depois = estado.obter_jogadores()
        mao_mc_depois = jogadores_depois[mc_player].quantidade_cartas()
        mao_ab_depois = jogadores_depois[1 - mc_player].quantidade_cartas()
        ambos_com_cartas = mao_mc_depois > 0 and mao_ab_depois > 0
        if pares_passe and houve_resolucao:
            regions_resolved_by_passes += 1
            if mao_mc_depois + mao_ab_depois > 0:
                early_with_cards += 1
            if ambos_com_cartas:
                early_with_both_hands += 1
        if escritor_eventos is not None:
            escritor_eventos.writerow({
                "seed": seed,
                "ply": plies,
                "actor": "Monte Carlo" if indice == mc_player else "Alfa-beta",
                "algorithm": "Monte Carlo" if indice == mc_player else "Alfa-beta",
                "action": "pass" if eh_passe else "card",
                "description": jogada.descrever(),
                "pass_streak_before": passes_antes,
                "pass_streak_after": estado.passes_consecutivos,
                "pass_pair_completed": pares_passe,
                "region_resolved": houve_resolucao,
                "region_name": regiao_alvo if houve_resolucao else "",
                "resolved_regions_before": resolvidas_antes,
                "resolved_regions_after": resolvidas_depois,
                "mc_cards_before": mao_mc_antes,
                "ab_cards_before": mao_ab_antes,
                "mc_cards_after": mao_mc_depois,
                "ab_cards_after": mao_ab_depois,
                "both_hands_nonempty_after": ambos_com_cartas,
                "last_message": estado.ultima_mensagem,
            })
            if arquivo_eventos is not None:
                arquivo_eventos.flush()
        agente_nome = "MC" if indice == mc_player else "alfa-beta"
        print(
            f"Seed {seed}, jogada {plies}: {agente_nome}, "
            f"decisão={perf_counter() - inicio_decisao:.3f} s, "
            f"partida={perf_counter() - inicio_partida:.1f} s",
            flush=True,
        )

    duracao = perf_counter() - inicio_partida
    if estado.finalizado:
        vencedor = "Empate" if estado.vencedor is None else estado.vencedor.nome
        status = "concluida"
    else:
        vencedor = ""
        status = "limite_de_jogadas"
    return {
        "seed": seed,
        "mc_player": mc_player + 1,
        "first_player": "Monte Carlo" if first_player == mc_player else "Alfa-beta",
        "simulations": simulacoes,
        "minimax_depth": profundidade,
        "winner": vencedor,
        "status": status,
        "duration_seconds": f"{duracao:.6f}",
        "plies": plies,
        "mc_decisions": len(mc_times),
        "mc_avg_seconds": f"{sum(mc_times) / len(mc_times):.6f}" if mc_times else "0",
        "mc_max_seconds": f"{max(mc_times):.6f}" if mc_times else "0",
        "mc_nodes": mc_nodes,
        "mc_simulations": mc_sims,
        "ab_decisions": len(ab_times),
        "ab_avg_seconds": f"{sum(ab_times) / len(ab_times):.6f}" if ab_times else "0",
        "ab_max_seconds": f"{max(ab_times):.6f}" if ab_times else "0",
        "ab_nodes": ab_nodes,
        "ab_leaves": ab_leaves,
        "ab_prunes": ab_prunes,
        "mc_passes": mc_passes,
        "ab_passes": ab_passes,
        "pass_pairs": pass_pairs,
        "regions_resolved_by_passes": regions_resolved_by_passes,
        "early_resolutions_with_cards_remaining": early_with_cards,
        "early_resolutions_with_both_hands_nonempty": early_with_both_hands,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulacoes", type=int, default=3000)
    parser.add_argument("--profundidade", type=int, default=1)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--eventos", type=Path)
    args = parser.parse_args()
    if args.simulacoes < 1 or args.profundidade < 1 or args.seeds < 1:
        parser.error("Simulações, profundidade e quantidade de seeds devem ser positivos.")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    concluidas = set()
    if args.saida.exists():
        with args.saida.open(newline="", encoding="utf-8-sig") as arquivo:
            for linha in csv.DictReader(arquivo):
                if (
                    linha["status"] == "concluida"
                    and int(linha["simulations"]) == args.simulacoes
                    and int(linha["minimax_depth"]) == args.profundidade
                ):
                    concluidas.add(int(linha["seed"]))

    escrever_cabecalho = not args.saida.exists() or args.saida.stat().st_size == 0
    with args.saida.open("a", newline="", encoding="utf-8-sig") as arquivo:
        gravador = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        if escrever_cabecalho:
            gravador.writeheader()
            arquivo.flush()
        eventos_arquivo = None
        eventos_gravador = None
        if args.eventos:
            args.eventos.parent.mkdir(parents=True, exist_ok=True)
            eventos_arquivo = args.eventos.open("a", newline="", encoding="utf-8-sig")
            eventos_gravador = csv.DictWriter(eventos_arquivo, fieldnames=EVENT_FIELDS)
            if eventos_arquivo.tell() == 0:
                eventos_gravador.writeheader()
                eventos_arquivo.flush()
        try:
            for seed in range(args.seeds):
                if seed in concluidas:
                    print(f"Seed {seed}: já registrada; pulando.", flush=True)
                    continue
                resultado = executar_partida(
                    seed, args.simulacoes, args.profundidade,
                    escritor_eventos=eventos_gravador,
                    arquivo_eventos=eventos_arquivo,
                )
                gravador.writerow(resultado)
                arquivo.flush()
                print(
                    f"Seed {seed}: {resultado['status']}, vencedor={resultado['winner'] or 'sem vencedor'}, "
                    f"duração={resultado['duration_seconds']} s, "
                    f"MC médio={resultado['mc_avg_seconds']} s, "
                    f"passes={resultado['mc_passes'] + resultado['ab_passes']}, "
                    f"pares={resultado['pass_pairs']}, "
                    f"regiões resolvidas por passes={resultado['regions_resolved_by_passes']}, "
                    f"resoluções com cartas restantes={resultado['early_resolutions_with_cards_remaining']}",
                    flush=True,
                )
        finally:
            if eventos_arquivo is not None:
                eventos_arquivo.close()


if __name__ == "__main__":
    main()
