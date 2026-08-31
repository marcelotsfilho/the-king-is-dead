from model.region import Regiao


_NOMES_DAS_REGIOES = [
    "Moray",
    "Strathclyde",
    "Northumbria",
    "Lancaster",
    "Gwynedd",
    "Warwick",
    "Essex",
    "Devon",
]

_ADJACENCIAS = {
    "Moray": {"Strathclyde", "Northumbria"},
    "Strathclyde": {"Moray", "Northumbria", "Lancaster"},
    "Northumbria": {"Moray", "Strathclyde", "Lancaster", "Warwick", "Essex"},
    "Lancaster": {"Strathclyde", "Northumbria", "Gwynedd", "Warwick"},
    "Gwynedd": {"Lancaster", "Warwick", "Devon"},
    "Warwick": {"Northumbria", "Lancaster", "Gwynedd", "Essex", "Devon"},
    "Essex": {"Northumbria", "Warwick", "Devon"},
    "Devon": {"Gwynedd", "Warwick", "Essex"},
}


class Tabuleiro:
    """Reúne as regiões e representa suas fronteiras como um grafo."""

    def __init__(self):
        self._regioes = {}
        for nome in _NOMES_DAS_REGIOES:
            self._regioes[nome] = Regiao(nome)

        self._adjacencias = {}
        for nome in _ADJACENCIAS:
            self._adjacencias[nome] = _ADJACENCIAS[nome].copy()

        self._validar_grafo()

    def obter_regioes(self):
        """Retorna uma cópia do catálogo de regiões."""
        return self._regioes.copy()

    def obter_nomes_das_regioes(self):
        """Retorna os nomes das oito regiões, sem indicar ordem de disputa."""
        nomes = []
        for nome in self._regioes:
            nomes.append(nome)
        return nomes

    def obter_regiao(self, nome):
        """Retorna a região correspondente ao nome informado."""
        self._validar_nome(nome)
        return self._regioes[nome]

    def regioes_adjacentes(self, nome):
        """Retorna os nomes das regiões que fazem fronteira com a região."""
        self._validar_nome(nome)
        return self._adjacencias[nome].copy()

    def sao_adjacentes(self, nome_regiao_a, nome_regiao_b):
        """Informa se duas regiões compartilham uma fronteira."""
        self._validar_nome(nome_regiao_a)
        self._validar_nome(nome_regiao_b)
        return nome_regiao_b in self._adjacencias[nome_regiao_a]

    def _validar_nome(self, nome):
        if nome not in self._regioes:
            raise ValueError(f"Região desconhecida: {nome}.")

    def _validar_grafo(self):
        nomes = set(self._regioes.keys())

        if set(self._adjacencias) != nomes:
            raise RuntimeError("O grafo não possui uma entrada para cada região.")

        for origem, destinos in self._adjacencias.items():
            if origem in destinos:
                raise RuntimeError(f"{origem} não pode ser adjacente a si mesma.")

            for destino in destinos:
                if destino not in nomes:
                    raise RuntimeError(f"Região desconhecida no grafo: {destino}.")

                if origem not in self._adjacencias[destino]:
                    raise RuntimeError(
                        f"A fronteira entre {origem} e {destino} não é simétrica."
                    )
