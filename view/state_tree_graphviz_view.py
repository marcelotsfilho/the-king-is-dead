import os
from pathlib import Path
import shutil
import subprocess
import webbrowser

from model.state_tree import ArvoreEstados


class VisaoArvoreGraphviz:
    """Exporta todos os nós conhecidos para o formato do Graphviz."""

    def gerar_dot(self, arvore):
        """Monta o texto DOT que representa a árvore completa."""
        if not isinstance(arvore, ArvoreEstados):
            raise TypeError("O valor informado deve ser uma ArvoreEstados.")

        nos = arvore.obter_nos()
        indices = {}

        for indice in range(len(nos)):
            indices[id(nos[indice])] = indice

        linhas = [
            "digraph ArvoreEstados {",
            '  graph [rankdir="TB", bgcolor="#f5eedc"];',
            '  node [shape="box", style="rounded,filled", fontsize="9"];',
            '  edge [color="#5a4b37"];',
        ]

        for indice in range(len(nos)):
            no = nos[indice]
            rotulo = self._criar_rotulo(no, indice)
            cor = "#ded9cf"
            borda = "#5a4b37"
            espessura = 1

            if no.esta_visitado():
                cor = "#b8d8b8"

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

        for indice in range(1, len(nos)):
            pai = nos[indice].obter_pai()
            indice_pai = indices[id(pai)]
            linhas.append(
                "  n" + str(indice_pai) + " -> n" + str(indice) + ";"
            )

        linhas.append("}")
        return "\n".join(linhas)

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

        return rotulo

    def _escapar_texto(self, texto):
        return texto.replace("\\", "\\\\").replace('"', '\\"')

    def _validar_caminho(self, caminho):
        if not isinstance(caminho, str):
            raise TypeError("O caminho do SVG deve ser um texto.")

        if not caminho.strip():
            raise ValueError("O caminho do SVG deve ser preenchido.")
