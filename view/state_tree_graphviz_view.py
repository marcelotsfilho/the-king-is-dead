import os
from pathlib import Path
import shutil
import subprocess
import webbrowser

from model.state_tree import ArvoreEstados


class VisaoArvoreGraphviz:
    """Exporta o caminho atual e suas próximas opções para o Graphviz."""

    def gerar_dot(self, arvore):
        """Monta o texto DOT que representa a árvore completa."""
        if not isinstance(arvore, ArvoreEstados):
            raise TypeError("O valor informado deve ser uma ArvoreEstados.")

        todos_os_nos = arvore.obter_nos()
        nos_visiveis = self._obter_nos_visiveis(arvore)
        indices = {}

        for indice in range(len(todos_os_nos)):
            indices[id(todos_os_nos[indice])] = indice

        linhas = [
            "digraph ArvoreEstados {",
            (
                '  graph [rankdir="TB", bgcolor="#f5eedc", '
                'ranksep="1.0"];'
            ),
            '  node [shape="box", style="rounded,filled", fontsize="9"];',
            '  edge [color="#5a4b37"];',
        ]

        for no in nos_visiveis:
            indice = indices[id(no)]
            rotulo = self._criar_rotulo(no, indice)
            cor = "#ded9cf"
            borda = "#5a4b37"
            espessura = 1

            if no.esta_visitado():
                cor = "#b8d8b8"

            if no.representa_jogada_voltada():
                cor = "#a8a8a8"
                borda = "#5f5f5f"
                espessura = 2

            if no is arvore.obter_no_atual():
                cor = "#9ec5f8"
                borda = "#3169b7"
                espessura = 3

            linhas.append(
                "  n"
                + str(indice)
                + ' [label="'
                + rotulo
                + '", fillcolor="'
                + cor
                + '", color="'
                + borda
                + '", penwidth="'
                + str(espessura)
                + '"];'
            )

        for no in nos_visiveis:
            if no.eh_raiz():
                continue

            indice = indices[id(no)]
            pai = no.obter_pai()
            indice_pai = indices[id(pai)]
            linhas.append(
                "  n" + str(indice_pai) + " -> n" + str(indice) + ";"
            )

        self._organizar_jogadas_voltadas(linhas, arvore, indices)
        linhas.append("}")
        return "\n".join(linhas)

    def _organizar_jogadas_voltadas(self, linhas, arvore, indices):
        """Mantém cada volta próxima da nova escolha do mesmo nível."""
        caminho_atual = arvore.obter_caminho_atual()

        for no_do_caminho in caminho_atual:
            pai = no_do_caminho.obter_pai()

            if pai is None:
                continue

            nomes_dos_nos = []

            for filho in pai.obter_filhos():
                if filho.representa_jogada_voltada():
                    indice = indices[id(filho)]
                    nomes_dos_nos.append("n" + str(indice))

            if not nomes_dos_nos:
                continue

            indice_do_caminho = indices[id(no_do_caminho)]
            nomes_dos_nos.append("n" + str(indice_do_caminho))

            linhas.append(
                "  { rank=same; " + "; ".join(nomes_dos_nos) + "; }"
            )

            for posicao in range(len(nomes_dos_nos) - 1):
                origem = nomes_dos_nos[posicao]
                destino = nomes_dos_nos[posicao + 1]
                linhas.append(
                    "  "
                    + origem
                    + " -> "
                    + destino
                    + ' [style="invis", weight="100"];'
                )

    def _obter_nos_visiveis(self, arvore):
        """Retorna o caminho, as voltas e os filhos diretos atuais."""
        nos_visiveis = arvore.obter_caminho_atual()
        no_atual = arvore.obter_no_atual()

        for filho in no_atual.obter_filhos():
            nos_visiveis.append(filho)

        for no in arvore.obter_nos():
            if (
                no.representa_jogada_voltada()
                and no not in nos_visiveis
            ):
                nos_visiveis.append(no)

        return nos_visiveis

    def exportar(self, arvore, caminho_svg, abrir=True):
        """Cria os arquivos DOT e SVG e abre o SVG no navegador."""
        self._validar_caminho(caminho_svg)
        caminho_base = os.path.splitext(caminho_svg)[0]
        caminho_dot = caminho_base + ".dot"
        pasta = os.path.dirname(caminho_svg)

        if pasta:
            os.makedirs(pasta, exist_ok=True)

        conteudo = self.gerar_dot(arvore)

        with open(caminho_dot, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)

        executavel = self._localizar_dot()

        if executavel is None:
            raise RuntimeError(
                "Graphviz não foi encontrado. O arquivo DOT foi criado em "
                + caminho_dot
            )

        resultado = subprocess.run(
            [executavel, "-Tsvg", caminho_dot, "-o", caminho_svg],
            capture_output=True,
            text=True,
            check=False,
        )

        if resultado.returncode != 0:
            raise RuntimeError(
                "Graphviz não conseguiu gerar o SVG: "
                + resultado.stderr.strip()
            )

        if abrir:
            endereco = Path(caminho_svg).resolve().as_uri()
            webbrowser.open(endereco)

        return caminho_svg

    def _localizar_dot(self):
        executavel = shutil.which("dot")

        if executavel is not None:
            return executavel

        caminhos_comuns = [
            os.path.join(
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                "Graphviz",
                "bin",
                "dot.exe",
            ),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Programs",
                "Graphviz",
                "bin",
                "dot.exe",
            ),
        ]

        for caminho in caminhos_comuns:
            if os.path.isfile(caminho):
                return caminho

        return None

    def _criar_rotulo(self, no, indice):
        jogada = no.obter_jogada_origem()
        descricao = "Estado inicial"

        if jogada is not None:
            descricao = jogada.descrever()

        descricao = self._escapar_texto(descricao)

        rotulo = (
            "Nó "
            + str(indice)
            + "\\nNível "
            + str(no.obter_nivel())
            + "\\n"
            + descricao
        )

        if no.esta_expandido():
            rotulo += "\\nOpções geradas"

        if no.representa_jogada_voltada():
            rotulo += "\\nJogada voltada"

        return rotulo

    def _escapar_texto(self, texto):
        return texto.replace("\\", "\\\\").replace('"', '\\"')

    def _validar_caminho(self, caminho):
        if not isinstance(caminho, str):
            raise TypeError("O caminho do SVG deve ser um texto.")

        if not caminho.strip():
            raise ValueError("O caminho do SVG deve ser preenchido.")
