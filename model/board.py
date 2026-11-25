from types import MappingProxyType

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

_ADJACENCIAS = MappingProxyType({
    "Moray": frozenset(("Strathclyde", "Northumbria")),
    "Strathclyde": frozenset(("Moray", "Northumbria", "Lancaster")),
    "Northumbria": frozenset(("Moray", "Strathclyde", "Lancaster", "Warwick", "Essex")),
    "Lancaster": frozenset(("Strathclyde", "Northumbria", "Gwynedd", "Warwick")),
    "Gwynedd": frozenset(("Lancaster", "Warwick", "Devon")),
    "Warwick": frozenset(("Northumbria", "Lancaster", "Gwynedd", "Essex", "Devon")),
    "Essex": frozenset(("Northumbria", "Warwick", "Devon")),
    "Devon": frozenset(("Gwynedd", "Warwick", "Essex")),
})


class Tabuleiro:
    """Reúne as regiões e representa suas fronteiras como um grafo."""

    def __init__(self):
        self._regioes = {}
        for nome in _NOMES_DAS_REGIOES:
            self._regioes[nome] = Regiao(nome)

        self._validar_grafo()

    def copiar(self):
        copia = Tabuleiro.__new__(Tabuleiro)
        copia._regioes = {
            nome: regiao.copiar() for nome, regiao in self._regioes.items()
        }
        return copia

    def _validar_nome(self, nome):
        if nome not in self._regioes:
            raise ValueError(f"Região desconhecida: {nome}.")

    def obter_regioes(self):
        """Retorna uma cópia do catálogo de regiões."""
        return self._regioes.copy()

    def obter_regioes_com_seguidores(self):
        """Retorna as regiões em disputa que possuem seguidores."""
        return [
            regiao for regiao in self._regioes.values()
            if not regiao.esta_resolvida() and regiao.total_de_seguidores() > 0
        ]

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
        return set(_ADJACENCIAS[nome])

    def sao_adjacentes(self, nome_regiao_a, nome_regiao_b):
        """Informa se duas regiões compartilham uma fronteira."""
        self._validar_nome(nome_regiao_a)
        self._validar_nome(nome_regiao_b)
        return nome_regiao_b in _ADJACENCIAS[nome_regiao_a]

    def quantidade_instabilidades(self):
        """Conta quantas regiões do tabuleiro estão instáveis."""
        quantidade = 0

        for regiao in self._regioes.values():
            if regiao.instavel:
                quantidade += 1

        return quantidade

    def _validar_grafo(self):
        nomes = set(self._regioes.keys())

        if set(_ADJACENCIAS) != nomes:
            raise RuntimeError("O grafo não possui uma entrada para cada região.")

        for origem, destinos in _ADJACENCIAS.items():
            if origem in destinos:
                raise RuntimeError(f"{origem} não pode ser adjacente a si mesma.")

            for destino in destinos:
                if destino not in nomes:
                    raise RuntimeError(f"Região desconhecida no grafo: {destino}.")

                if origem not in _ADJACENCIAS[destino]:
                    raise RuntimeError(
                        f"A fronteira entre {origem} e {destino} não é simétrica."
                    )
