from model.state_tree import ArvoreEstados


class VisaoArvoreEstados:
    """Produz uma apresentação textual da árvore de estados."""

    def formatar(self, arvore, limite_filhos=None):
        """Retorna um texto com níveis, jogadas e marcações dos nós."""
        if not isinstance(arvore, ArvoreEstados):
            raise TypeError("O valor informado deve ser uma ArvoreEstados.")

        self._validar_limite(limite_filhos)
        linhas = [
            "ÁRVORE DE ESTADOS",
            "Total de nós: " + str(arvore.quantidade_nos()),
            "Nível atual: " + str(arvore.obter_no_atual().obter_nivel()),
            "",
        ]
        self._adicionar_no(
            linhas,
            arvore.obter_raiz(),
            arvore.obter_no_atual(),
            limite_filhos,
        )
        return "\n".join(linhas)

    def mostrar(self, arvore, limite_filhos=None):
        """Mostra a apresentação textual no terminal."""
        texto = self.formatar(arvore, limite_filhos)
        print(texto)

    def _adicionar_no(self, linhas, no, no_atual, limite_filhos):
        recuo = "  " * no.obter_nivel()
        marcador = self._obter_marcador(no, no_atual)
        descricao = self._obter_descricao(no)
        expansao = "não expandido"

        if no.esta_expandido():
            expansao = "expandido"

        linha = (
            recuo
            + marcador
            + " Nível "
            + str(no.obter_nivel())
            + " - "
            + descricao
            + " ("
            + expansao
            + ")"
        )
        linhas.append(linha)
        filhos = no.obter_filhos()
        quantidade_mostrada = len(filhos)

        if limite_filhos is not None:
            quantidade_mostrada = min(limite_filhos, len(filhos))

        for indice in range(quantidade_mostrada):
            self._adicionar_no(
                linhas,
                filhos[indice],
                no_atual,
                limite_filhos,
            )

        quantidade_omitida = len(filhos) - quantidade_mostrada

        if quantidade_omitida > 0:
            linhas.append(
                recuo
                + "  ... "
                + str(quantidade_omitida)
                + " filho(s) omitido(s)"
            )

    def _obter_marcador(self, no, no_atual):
        if no is no_atual:
            return "[ATUAL]"

        if no.esta_visitado():
            return "[CAMINHO]"

        return "[NÃO VISITADO]"

    def _obter_descricao(self, no):
        jogada = no.obter_jogada_origem()

        if jogada is None:
            return "Estado inicial"

        return jogada.descrever()

    def _validar_limite(self, limite_filhos):
        if limite_filhos is None:
            return

        if isinstance(limite_filhos, bool) or not isinstance(
            limite_filhos,
            int,
        ):
            raise TypeError("O limite de filhos deve ser um número inteiro.")

        if limite_filhos <= 0:
            raise ValueError("O limite de filhos deve ser maior que zero.")
