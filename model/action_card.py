from model.enums import TipoCartaAcao


_DESCRICOES_DAS_CARTAS = {
    TipoCartaAcao.APOIO_ESCOCES: (
        "Adiciona até dois seguidores Escoceses em uma região permitida."
    ),
    TipoCartaAcao.APOIO_GALES: (
        "Adiciona até dois seguidores Galeses em uma região permitida."
    ),
    TipoCartaAcao.APOIO_INGLES: (
        "Adiciona até dois seguidores Ingleses em uma região permitida."
    ),
    TipoCartaAcao.NEGOCIAR: (
        "Troca duas cartas de região ainda ativas na trilha de disputas."
    ),
    TipoCartaAcao.MANOBRAR: (
        "Troca um seguidor de uma região por um seguidor de outra região."
    ),
    TipoCartaAcao.SUPERAR_MANOBRA: (
        "Troca um seguidor por dois seguidores de uma região adjacente."
    ),
    TipoCartaAcao.REUNIR: (
        "Adiciona um seguidor de cada facção em regiões permitidas."
    ),
}


class CartaAcao:
    """Representa uma carta de ação do modo básico."""

    def __init__(self, tipo):
        if not isinstance(tipo, TipoCartaAcao):
            raise TypeError("O tipo deve ser um item de TipoCartaAcao.")

        self.tipo = tipo
        self.nome = tipo.value
        self.descricao = _DESCRICOES_DAS_CARTAS[tipo]


def criar_conjunto_padrao():
    """Cria as oito cartas utilizadas por um jogador no modo básico."""
    tipos = [
        TipoCartaAcao.APOIO_ESCOCES,
        TipoCartaAcao.APOIO_GALES,
        TipoCartaAcao.APOIO_INGLES,
        TipoCartaAcao.NEGOCIAR,
        TipoCartaAcao.MANOBRAR,
        TipoCartaAcao.SUPERAR_MANOBRA,
        TipoCartaAcao.REUNIR,
        TipoCartaAcao.REUNIR,
    ]

    cartas = []

    for tipo in tipos:
        cartas.append(CartaAcao(tipo))

    return cartas
