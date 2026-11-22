import os
import sys

import pygame

from controller.game_controller import ControladorJogo
from controller.start_menu_controller import (
    ACAO_CONTINUAR_JOGO,
    ACAO_NOVO_JOGO,
    ACAO_SAIR,
    ControladorMenuInicial,
)
from model.game import Jogo
from model.game_setup import ConfiguracaoJogo
from model.match_settings import ConfiguracaoPartida
from model.state_tree import ArvoreEstados
from model.state_tree_serializer import SerializadorArvoreEstados
from view.game_view import VisaoJogo


SEMENTE_JOGO = 40

_PASTA_DO_PROJETO = os.path.dirname(os.path.abspath(__file__))
_PASTA_DE_SALVAMENTOS = os.path.join(_PASTA_DO_PROJETO, "saves")
_CAMINHO_DA_ARVORE = os.path.join(
    _PASTA_DE_SALVAMENTOS,
    "state_tree.json",
)


def _preparar_arvore(argumentos, serializador):
    if "--carregar" in argumentos:
        return serializador.carregar(_CAMINHO_DA_ARVORE)

    # geracao da arvore com uma determinada seed
    configuracao = ConfiguracaoJogo(semente=SEMENTE_JOGO)
    estado = configuracao.criar_estado_inicial(
        ["Jogador 1", "Jogador 2"]
    )
    return ArvoreEstados(estado)


def _escolher_arvore_pelo_menu(
    visao, serializador, mensagem="", configuracao_partida=None
):
    controlador_menu = ControladorMenuInicial(
        visao,
        _CAMINHO_DA_ARVORE,
        configuracao_partida,
    )

    while True:
        acao = controlador_menu.executar(mensagem)

        if acao == ACAO_SAIR:
            return None

        if acao == ACAO_NOVO_JOGO:
            return _preparar_arvore([], serializador)

        if acao == ACAO_CONTINUAR_JOGO:
            visao.desenhar_menu_inicial(
                True,
                "Carregando a partida salva...",
            )

            try:
                return _preparar_arvore(["--carregar"], serializador)
            except (OSError, KeyError, TypeError, ValueError) as erro:
                mensagem = "Não foi possível carregar a partida: " + str(
                    erro
                )


def principal():
    """Monta as camadas MVC e inicia a aplicação."""
    os.makedirs(_PASTA_DE_SALVAMENTOS, exist_ok=True)
    pygame.init()
    serializador = SerializadorArvoreEstados()
    visao = VisaoJogo()
    configuracao_partida = ConfiguracaoPartida()

    if "--carregar" in sys.argv[1:]:
        try:
            arvore = _preparar_arvore(sys.argv[1:], serializador)
        except (OSError, KeyError, TypeError, ValueError) as erro:
            mensagem = "Não foi possível carregar a partida: " + str(
                erro
            )
            arvore = _escolher_arvore_pelo_menu(
                visao,
                serializador,
                mensagem,
                configuracao_partida,
            )
    else:
        arvore = _escolher_arvore_pelo_menu(
            visao, serializador, configuracao_partida=configuracao_partida
        )

    if arvore is None:
        pygame.quit()
        return

    estado = arvore.obter_estado_atual()
    jogo = Jogo(estado)
    controlador = ControladorJogo(
        jogo,
        visao,
        arvore,
        serializador,
        _CAMINHO_DA_ARVORE,
        configuracao_partida=configuracao_partida,
    )
    controlador.executar()

    pygame.quit()


if __name__ == "__main__":
    principal()
