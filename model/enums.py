from enum import Enum


class Faccao(Enum):
    """Identidades das três facções presentes no jogo."""

    ESCOCESES = "escoceses"
    GALESES = "galeses"
    INGLESES = "ingleses"


class TipoCartaAcao(Enum):
    """Identidades das sete ações do modo básico."""

    APOIO_ESCOCES = "Scottish Support"
    APOIO_GALES = "Welsh Support"
    APOIO_INGLES = "English Support"
    NEGOCIAR = "Negotiate"
    MANOBRAR = "Manoeuvre"
    SUPERAR_MANOBRA = "Outmanoeuvre"
    REUNIR = "Assemble"


class TipoJogada(Enum):
    """Distingue as duas formas de concluir uma jogada."""

    PASSE = "passe"
    CARTA = "carta"


class FaseTurno(Enum):
    """Etapas possíveis de um turno do modo básico."""

    ESCOLHER_ACAO = "escolher_acao"
    CONVOCAR_SEGUIDOR = "convocar_seguidor"
    ENCERRADO = "encerrado"
