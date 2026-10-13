from copy import deepcopy

from model.enums import Faccao, TipoCartaAcao, TipoJogada


class Jogada:
    """Representa uma jogada completa que pode gerar um novo estado."""

    def __init__(
        self,
        tipo,
        tipo_carta=None,
        parametros=None,
        nome_regiao_convocacao=None,
        faccao_convocacao=None,
    ):
        if not isinstance(tipo, TipoJogada):
            raise TypeError("O tipo da jogada deve ser um item de TipoJogada.")

        self.tipo = tipo

        if tipo == TipoJogada.PASSE:
            self._configurar_passe(
                tipo_carta,
                parametros,
                nome_regiao_convocacao,
                faccao_convocacao,
            )
        else:
            self._configurar_carta(
                tipo_carta,
                parametros,
                nome_regiao_convocacao,
                faccao_convocacao,
            )

    def _configurar_passe(
        self,
        tipo_carta,
        parametros,
        nome_regiao_convocacao,
        faccao_convocacao,
    ):
        possui_dados_de_carta = (
            tipo_carta is not None
            or parametros is not None
            or nome_regiao_convocacao is not None
            or faccao_convocacao is not None
        )

        if possui_dados_de_carta:
            raise ValueError("Uma jogada de passe não pode possuir dados de carta.")

        self.tipo_carta = None
        self._parametros = {}
        self.nome_regiao_convocacao = None
        self.faccao_convocacao = None

    def _configurar_carta(
        self,
        tipo_carta,
        parametros,
        nome_regiao_convocacao,
        faccao_convocacao,
    ):
        if not isinstance(tipo_carta, TipoCartaAcao):
            raise TypeError("O tipo da carta deve ser um item de TipoCartaAcao.")

        if parametros is None:
            parametros = {}

        if not isinstance(parametros, dict):
            raise TypeError("Os parâmetros da carta devem estar em um dicionário.")

        if not isinstance(nome_regiao_convocacao, str):
            raise TypeError("A região da convocação deve ser informada em um texto.")

        nome_limpo = nome_regiao_convocacao.strip()

        if not nome_limpo:
            raise ValueError("A região da convocação deve ser preenchida.")

        if not isinstance(faccao_convocacao, Faccao):
            raise TypeError("A facção da convocação deve ser um item de Faccao.")

        self.tipo_carta = tipo_carta
        self._parametros = deepcopy(parametros)
        self.nome_regiao_convocacao = nome_limpo
        self.faccao_convocacao = faccao_convocacao

    def obter_parametros(self):
        """Retorna uma cópia dos parâmetros usados pelo efeito da carta."""
        return deepcopy(self._parametros)

    def eh_passe(self):
        """Informa se a jogada representa um passe."""
        return self.tipo == TipoJogada.PASSE

    def eh_carta(self):
        """Informa se a jogada representa o uso completo de uma carta."""
        return self.tipo == TipoJogada.CARTA

    def possui_mesmos_dados(self, outra_jogada):
        """Compara todas as escolhas que formam duas jogadas."""
        if not isinstance(outra_jogada, Jogada):
            return False

        mesma_regiao = (
            self.nome_regiao_convocacao
            == outra_jogada.nome_regiao_convocacao
        )

        return (
            self.tipo == outra_jogada.tipo
            and self.tipo_carta == outra_jogada.tipo_carta
            and self._parametros == outra_jogada._parametros
            and mesma_regiao
            and self.faccao_convocacao == outra_jogada.faccao_convocacao
        )

    def descrever(self):
        """Retorna uma descrição curta para apresentar a jogada."""
        if self.eh_passe():
            return "Passar."

        return (
            "Jogar "
            + self.tipo_carta.value
            + self._descrever_efeito()
            + " e convocar "
            + self.faccao_convocacao.value
            + " de "
            + self.nome_regiao_convocacao
            + "."
        )

    def _descrever_efeito(self):
        if not self._parametros:
            return " sem efeito"

        if "regiao" in self._parametros:
            return " em " + self._parametros["regiao"]

        if self.tipo_carta == TipoCartaAcao.REUNIR:
            partes = []
            destinos = self._parametros["destinos"]

            for faccao in Faccao:
                if faccao in destinos:
                    partes.append(faccao.value + " em " + destinos[faccao])

            return " colocando " + ", ".join(partes)

        if self.tipo_carta == TipoCartaAcao.NEGOCIAR:
            return (
                " trocando as posições "
                + str(self._parametros["posicao_a"])
                + " e "
                + str(self._parametros["posicao_b"])
                + ", com disco na posição "
                + str(self._parametros["posicao_disco"])
            )

        return (
            " trocando "
            + self._parametros["faccao_a"].value
            + " de "
            + self._parametros["regiao_a"]
            + " por "
            + self._parametros["faccao_b"].value
            + " de "
            + self._parametros["regiao_b"]
        )


def serializar_jogada(jogada):
    """Transforma uma Jogada em dados simples para salvar em arquivo."""
    if not isinstance(jogada, Jogada):
        raise TypeError("O valor informado deve ser uma Jogada.")

    dados = {"tipo": jogada.tipo.name}

    if jogada.eh_passe():
        return dados

    dados["tipo_carta"] = jogada.tipo_carta.name
    dados["parametros"] = _serializar_parametros(
        jogada.obter_parametros()
    )
    dados["nome_regiao_convocacao"] = jogada.nome_regiao_convocacao
    dados["faccao_convocacao"] = jogada.faccao_convocacao.name
    return dados


def restaurar_jogada(dados):
    """Reconstrói uma Jogada a partir dos dados salvos."""
    if not isinstance(dados, dict):
        raise TypeError("Os dados da jogada devem estar em um dicionário.")

    try:
        tipo = TipoJogada[dados["tipo"]]
    except (KeyError, TypeError):
        raise ValueError("O tipo da jogada salva é inválido.")

    if tipo == TipoJogada.PASSE:
        return Jogada(TipoJogada.PASSE)

    try:
        tipo_carta = TipoCartaAcao[dados["tipo_carta"]]
        faccao = Faccao[dados["faccao_convocacao"]]
        parametros = _restaurar_parametros(dados["parametros"])
        nome_regiao = dados["nome_regiao_convocacao"]
    except (KeyError, TypeError):
        raise ValueError("Os dados da carta salva estão incompletos.")

    return Jogada(
        TipoJogada.CARTA,
        tipo_carta=tipo_carta,
        parametros=parametros,
        nome_regiao_convocacao=nome_regiao,
        faccao_convocacao=faccao,
    )


def _serializar_parametros(parametros):
    resultado = parametros.copy()

    if "destinos" in resultado:
        destinos = {}

        for faccao in resultado["destinos"]:
            destinos[faccao.name] = resultado["destinos"][faccao]

        resultado["destinos"] = destinos

    for chave in ["faccao_a", "faccao_b"]:
        if chave in resultado:
            resultado[chave] = resultado[chave].name

    return resultado


def _restaurar_parametros(parametros):
    if not isinstance(parametros, dict):
        raise TypeError("Os parâmetros salvos devem estar em um dicionário.")

    resultado = parametros.copy()

    if "destinos" in resultado:
        destinos = {}

        for nome_faccao in resultado["destinos"]:
            destinos[Faccao[nome_faccao]] = resultado["destinos"][
                nome_faccao
            ]

        resultado["destinos"] = destinos

    for chave in ["faccao_a", "faccao_b"]:
        if chave in resultado:
            resultado[chave] = Faccao[resultado[chave]]

    return resultado
