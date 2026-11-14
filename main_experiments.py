import argparse
import main
from pathlib import Path
import sys

from experiments.runner import executar_bateria


def inteiro_positivo(texto):
    numero = int(texto)
    if numero < 1:
        raise argparse.ArgumentTypeError("Informe um inteiro a partir de 1.")
    return numero


def criar_argumentos():
    analisador = argparse.ArgumentParser(description="Experimentos locais: uma decisão por execução.")
    analisador.add_argument("--bateria", choices=["atual", "inicial", "ambas"], default="ambas")
    analisador.add_argument("--profundidades", nargs="+", type=inteiro_positivo, default=[1, 2])
    analisador.add_argument("--repeticoes", type=inteiro_positivo, default=1)
    analisador.add_argument("--algoritmos", nargs="+", choices=["minimax", "alfa_beta"], default=["minimax", "alfa_beta"])
    analisador.add_argument("--seed", type=int, default=main.SEMENTE_JOGO, help="Semente para gerar a árvore de estados.")
    analisador.add_argument("--cenario", choices=["inicial", "reduzido", "salvo"], default="inicial")
    analisador.add_argument("--arvore", help="JSON da árvore para o cenário salvo.")
    analisador.add_argument("--saida", default=str(Path(__file__).resolve().parent / "experiments"))
    analisador.add_argument("--retomar", action="store_true", help="Pula configurações já concluídas neste código e ambiente.")
    analisador.add_argument("--preparar", action="store_true", help="Prepara arquivos e mostra o plano, sem iniciar buscas.")
    return analisador


def principal():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    analisador = criar_argumentos()
    argumentos = analisador.parse_args()
    if argumentos.cenario == "salvo" and not argumentos.arvore:
        analisador.error("O cenário salvo exige --arvore caminho.json.")
    if argumentos.arvore and argumentos.cenario != "salvo":
        analisador.error("Use --cenario salvo com --arvore.")
    argumentos.profundidades = list(dict.fromkeys(argumentos.profundidades))
    argumentos.algoritmos = list(dict.fromkeys(argumentos.algoritmos))
    try:
        return executar_bateria(argumentos)
    except KeyboardInterrupt:
        print("Interrompido. Resultados já gravados continuam disponíveis.")
        return 130
    except (OSError, TypeError, ValueError, KeyError) as erro:
        print("Não foi possível executar os experimentos:", erro, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(principal())
