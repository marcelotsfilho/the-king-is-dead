"""Gera o gráfico PNG de treino e validação a partir dos CSVs."""

import argparse
import csv
from pathlib import Path

import pygame

from model.q_learning_agent import CAMINHO_TABELA_Q


def _contar_vitorias(caminho, bloco=None):
    pontos = {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            treinadas = int(linha["treinadas"])
            grupo = (treinadas - 1) // bloco if bloco else treinadas
            vitorias = pontos.get(grupo, (0, 0))[1]
            pontos[grupo] = treinadas, vitorias + (linha["resultado"] == "vitoria")
    return list(pontos.values())


def gerar_grafico(pasta, bloco):
    treino = _contar_vitorias(pasta / "treino.csv", bloco)
    validacao = _contar_vitorias(pasta / "validacao.csv")
    with (pasta / "validacao.csv").open(encoding="utf-8", newline="") as arquivo:
        partidas_validacao = sum(linha["treinadas"] == "0" for linha in csv.DictReader(arquivo))

    pygame.font.init()
    tela = pygame.Surface((1080, 840))
    tela.fill("#f5f8fa")
    fonte = pygame.font.SysFont("segoeui", 19)
    subtitulo = pygame.font.SysFont("segoeui", 24, bold=True)
    titulo = pygame.font.SysFont("segoeui", 34, bold=True)

    def texto(conteudo, x, y, estilo=fonte, cor="#1f3344"):
        tela.blit(estilo.render(conteudo, True, cor), (x, y))

    texto("Aprendizado do agente Q-learning", 58, 30, titulo)
    texto("Vitórias por bloco de treino e em partidas de validação com a tabela congelada", 60, 80)
    maximo_x = treino[-1][0]
    paineis = (
        (treino, 128, bloco, f"Treino · vitórias por bloco de {bloco} partidas", "#087d72"),
        (validacao, 460, partidas_validacao, f"Validação · vitórias em {partidas_validacao} partidas por ponto", "#305aad"),
    )
    for dados, topo, maximo_y, rotulo, cor in paineis:
        pygame.draw.rect(tela, "white", (54, topo, 972, 306), border_radius=12)
        texto(rotulo, 79, topo + 15, subtitulo)
        esquerda, direita = 116, 985
        base, altura = topo + 251, 183
        valores_y = range(0, maximo_y + 1, max(1, maximo_y // 4))
        for valor in valores_y:
            y = round(base - altura * valor / maximo_y)
            pygame.draw.line(tela, "#d9e4eb", (esquerda, y), (direita, y))
            texto(str(valor), 78, y - 12)
        for indice in range(7):
            x = round(esquerda + (direita - esquerda) * indice / 6)
            texto(str(round(maximo_x * indice / 6)), x - 10, base + 10)
        if dados is validacao:
            y_linha = round(base - altura * validacao[0][1] / maximo_y)
            pygame.draw.line(tela, "#899eae", (esquerda, y_linha), (direita, y_linha), 2)
        coordenadas = [
            (round(esquerda + (direita - esquerda) * x / maximo_x), round(base - altura * y / maximo_y))
            for x, y in dados
        ]
        if len(coordenadas) > 1:
            pygame.draw.lines(tela, cor, False, coordenadas, width=3)
        for x, y in coordenadas:
            pygame.draw.circle(tela, cor, (x, y), 4)
    texto("Partidas de treino jogadas", 420, 785, subtitulo)
    texto("Linha cinza = política inicial", 70, 789)
    pygame.image.save(tela, pasta / "aprendizado.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pasta", type=Path, default=CAMINHO_TABELA_Q.parent)
    parser.add_argument("--bloco", type=int, default=100)
    args = parser.parse_args()
    if args.bloco < 1:
        parser.error("O tamanho do bloco deve ser positivo.")
    gerar_grafico(args.pasta, args.bloco)
