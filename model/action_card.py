from model.enums import Faccao, TipoCartaAcao


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


_DADOS_DAS_CARTAS_DE_APOIO = {
    TipoCartaAcao.APOIO_ESCOCES: (Faccao.ESCOCESES, "Moray"),
    TipoCartaAcao.APOIO_GALES: (Faccao.GALESES, "Gwynedd"),
    TipoCartaAcao.APOIO_INGLES: (Faccao.INGLESES, "Essex"),
}


def eh_carta_de_apoio(tipo_carta):
    """Informa se o tipo pertence a uma das três cartas Support."""
    return tipo_carta in _DADOS_DAS_CARTAS_DE_APOIO


def obter_dados_da_carta_de_apoio(tipo_carta):
    """Retorna a facção e a região inicial associadas ao Support."""
    if not eh_carta_de_apoio(tipo_carta):
        raise ValueError("A carta informada não é uma carta Support.")

    return _DADOS_DAS_CARTAS_DE_APOIO[tipo_carta]


class CartaAcao:
    """Cartas de ação."""

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
