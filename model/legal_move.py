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
            + " e convocar "
            + self.faccao_convocacao.value
            + " de "
            + self.nome_regiao_convocacao
            + "."
        )
