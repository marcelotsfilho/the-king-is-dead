from model.region import Regiao


_NOMES_DAS_REGIOES = (
    "Moray",
    "Strathclyde",
    "Northumbria",
    "Lancaster",
    "Gwynedd",
    "Warwick",
    "Essex",
    "Devon",
)

_ADJACENCIAS = {
    "Moray": frozenset({"Strathclyde", "Northumbria"}),
    "Strathclyde": frozenset({"Moray", "Northumbria", "Lancaster"}),
    "Northumbria": frozenset(
        {"Moray", "Strathclyde", "Lancaster", "Warwick", "Essex"}
    ),
    "Lancaster": frozenset(
        {"Strathclyde", "Northumbria", "Gwynedd", "Warwick"}
    ),
    "Gwynedd": frozenset({"Lancaster", "Warwick", "Devon"}),
    "Warwick": frozenset(
        {"Northumbria", "Lancaster", "Gwynedd", "Essex", "Devon"}
    ),
    "Essex": frozenset({"Northumbria", "Warwick", "Devon"}),
    "Devon": frozenset({"Gwynedd", "Warwick", "Essex"}),
}


class Tabuleiro:
    """Reúne as regiões e representa suas fronteiras como um grafo."""

    def __init__(self) -> None:
        self._regioes = {
            nome: Regiao(nome)
            for nome in _NOMES_DAS_REGIOES
        }
        self._adjacencias = _ADJACENCIAS.copy()
        self._validar_grafo()

    @property
    def regioes(self) -> dict[str, Regiao]:
        """Retorna uma cópia do catálogo de regiões."""
        return self._regioes.copy()

    @property
    def nomes_das_regioes(self) -> tuple[str, ...]:
        """Retorna os nomes das oito regiões, sem indicar ordem de disputa."""
        return tuple(self._regioes)

    def obter_regiao(self, nome: str) -> Regiao:
        """Retorna a região correspondente ao nome informado."""
        self._validar_nome(nome)
        return self._regioes[nome]

    def regioes_adjacentes(self, nome: str) -> frozenset[str]:
        """Retorna os nomes das regiões que fazem fronteira com a região."""
        self._validar_nome(nome)
        return self._adjacencias[nome]

    def sao_adjacentes(self, nome_regiao_a: str, nome_regiao_b: str) -> bool:
        """Informa se duas regiões compartilham uma fronteira."""
        self._validar_nome(nome_regiao_a)
        self._validar_nome(nome_regiao_b)
        return nome_regiao_b in self._adjacencias[nome_regiao_a]

    def _validar_nome(self, nome: str) -> None:
        if nome not in self._regioes:
            raise ValueError(f"Região desconhecida: {nome!r}.")

    def _validar_grafo(self) -> None:
        nomes = set(self._regioes)

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

