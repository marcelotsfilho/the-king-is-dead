import sys

from model.game_setup import ConfiguracaoJogo
from model.state_tree import ArvoreEstados
from view.state_tree_view import VisaoArvoreEstados


def principal():
    """Cria a raiz, gera o primeiro nível e mostra parte da árvore."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    configuracao = ConfiguracaoJogo(semente=42)
    estado = configuracao.criar_estado_inicial(
        ["Jogador 1", "Jogador 2"]
    )
    arvore = ArvoreEstados(estado)

    print("Gerando as jogadas possíveis do estado inicial...")
    arvore.expandir_no_atual()

    visao = VisaoArvoreEstados()
    visao.mostrar(arvore, limite_filhos=20)


if __name__ == "__main__":
    principal()
