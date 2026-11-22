"""Reproduz duas decisões de passe com resultado verificável pelas regras."""

import argparse
import csv
import json
from pathlib import Path

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, TipoCartaAcao, TipoJogada
from model.game import Jogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada, serializar_jogada
from model.legal_move_executor import ExecutorJogada
from model.legal_move_generator import GeradorJogadas
from model.minimax_agent import AgenteMinimax
from model.monte_carlo_agent import AgenteMonteCarlo
from model.player import Jogador
from model.q_learning_agent import CAMINHO_TABELA_Q, AgenteQLearning, TabelaQ
from model.supply import ReservaSeguidores


def criar_posicao(passe_favoravel):
    tabuleiro = Tabuleiro()
    nomes = tabuleiro.obter_nomes_das_regioes()
    trilha = TrilhaDisputas(nomes)
    jogadores = [Jogador("Jogador da vez"), Jogador("Adversário")]
    reserva = ReservaSeguidores(16)
    estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)
    jogo = Jogo(estado)
    ingleses, galeses = Faccao.INGLESES, Faccao.GALESES
    for nome, faccao in zip(nomes[:-1], [ingleses] * 5 + [galeses] * 2):
        reserva.retirar(faccao)
        tabuleiro.obter_regiao(nome).adicionar_seguidores(faccao)
        jogo.resolver_proxima_disputa()
    ultima = tabuleiro.obter_regiao(nomes[-1])
    for faccao, quantidade in ((ingleses, 2), (galeses, 1 if passe_favoravel else 2)):
        reserva.retirar(faccao, quantidade)
        ultima.adicionar_seguidores(faccao, quantidade)
    reserva.retirar(galeses)
    jogadores[0].adicionar_seguidor_na_corte(galeses)
    reserva.retirar(ingleses)
    jogadores[0 if passe_favoravel else 1].adicionar_seguidor_na_corte(ingleses)
    jogadores[0].adicionar_carta_mao(CartaAcao(TipoCartaAcao.APOIO_INGLES))
    estado.ordem_jogadores_sem_cartas.append(jogadores[1])
    estado.indice_jogador_atual = 1
    jogo.passar()
    return estado


def desfecho(estado, jogada):
    executor = ExecutorJogada()
    estado = executor.executar(estado, jogada)
    # Ao jogar a única carta disponível, os dois só podem passar em seguida.
    while not estado.finalizado:
        if estado.obter_jogador_atual().quantidade_cartas():
            raise ValueError("A posição tem uma resposta além de passar")
        estado = executor.executar(estado, Jogada(TipoJogada.PASSE))
    if estado.vencedor is None:
        return "empate"
    return "vitoria" if estado.vencedor is estado.obter_jogadores()[0] else "derrota"


def executar(saida, tabela):
    saida.mkdir(parents=True, exist_ok=True)
    serializador = SerializadorEstadoJogo()
    campos = ("cenario", "algoritmo", "acao", "jogada", "descricao", "pontuacao", "resultado")
    with (saida / "posicoes.csv").open("w", newline="", encoding="utf-8") as arquivo:
        csv_saida = csv.DictWriter(arquivo, fieldnames=campos)
        csv_saida.writeheader()
        for nome, passe_favoravel in (("passe_favoravel", True), ("carta_necessaria", False)):
            estado = criar_posicao(passe_favoravel)
            (saida / f"{nome}.json").write_text(
                json.dumps(serializador.serializar(estado), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            escolhas = [("jogada_legal", jogada, None) for jogada in GeradorJogadas().gerar(estado)]
            for rotulo, agente, argumentos in (
                ("minimax", AgenteMinimax(0), {"usar_poda": False}),
                ("alfa_beta", AgenteMinimax(0), {"usar_poda": True}),
                ("monte_carlo_3000", AgenteMonteCarlo(0, semente=0), {"quantidade_simulacoes": 3000}),
                ("politica_inicial", AgenteQLearning(TabelaQ()), {}),
                ("q_learning", AgenteQLearning(tabela), {}),
            ):
                jogada = agente.escolher_jogada(estado, **argumentos)
                escolhas.append((rotulo, jogada, agente.ultima_pontuacao))
            for algoritmo, jogada, pontuacao in escolhas:
                csv_saida.writerow({
                    "cenario": nome, "algoritmo": algoritmo, "acao": jogada.tipo.value,
                    "jogada": json.dumps(serializar_jogada(jogada), sort_keys=True),
                    "descricao": jogada.descrever(), "pontuacao": pontuacao,
                    "resultado": desfecho(estado, jogada),
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=CAMINHO_TABELA_Q.parent / "posicoes")
    parser.add_argument("--tabela", type=Path, default=CAMINHO_TABELA_Q)
    args = parser.parse_args()
    executar(args.saida, TabelaQ.carregar(args.tabela))
