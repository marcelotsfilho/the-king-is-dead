from model.enums import TipoJogador


SIMULACOES_MONTE_CARLO_DISPONIVEIS = (100, 300, 1000, 3000, 5000)
LIMITES_TEMPO_BUSCA = (None, 5, 10, 20, 30, 60)
TIPOS_COM_LIMITE_DE_TEMPO = (TipoJogador.MINIMAX, TipoJogador.ALFA_BETA)


class ConfiguracaoPartida:
    """Guarda tipo e profundidade de cada jogador, separados das regras."""

    def __init__(self):
        self._tipos = [TipoJogador.HUMANO, TipoJogador.HUMANO]
        self._profundidades = [1, 1]
        self._simulacoes_monte_carlo = [100, 100]
        self._limites_tempo = [None, None]

    def _validar_indice(self, indice):
        if isinstance(indice, bool) or not isinstance(indice, int):
            raise TypeError("O índice do jogador deve ser inteiro.")
        if indice not in (0, 1):
            raise ValueError("O índice do jogador deve ser 0 ou 1.")

    def obter_tipo_jogador(self, indice):
        self._validar_indice(indice)
        return self._tipos[indice]

    def obter_profundidade(self, indice):
        self._validar_indice(indice)
        return self._profundidades[indice]

    def definir_tipo_jogador(self, indice, tipo):
        self._validar_indice(indice)
        if not isinstance(tipo, TipoJogador):
            raise TypeError("O tipo deve ser um TipoJogador.")
        self._tipos[indice] = tipo

    def definir_profundidade(self, indice, profundidade):
        self._validar_indice(indice)
        if isinstance(profundidade, bool) or not isinstance(profundidade, int):
            raise TypeError("A profundidade deve ser um inteiro.")
        if profundidade < 1:
            raise ValueError("A profundidade mínima é 1.")
        self._profundidades[indice] = profundidade

    def obter_simulacoes_monte_carlo(self, indice):
        self._validar_indice(indice)
        return self._simulacoes_monte_carlo[indice]

    def definir_simulacoes_monte_carlo(self, indice, quantidade):
        self._validar_indice(indice)
        if isinstance(quantidade, bool) or not isinstance(quantidade, int):
            raise TypeError("A quantidade de simulações deve ser inteira.")
        if quantidade not in SIMULACOES_MONTE_CARLO_DISPONIVEIS:
            raise ValueError("A quantidade de simulações não está disponível.")
        self._simulacoes_monte_carlo[indice] = quantidade

    def obter_limite_tempo(self, indice):
        self._validar_indice(indice)
        return self._limites_tempo[indice]

    def definir_limite_tempo(self, indice, segundos):
        self._validar_indice(indice)
        if segundos is not None and type(segundos) is not int:
            raise TypeError("O limite de tempo deve ser inteiro ou None.")
        if segundos not in LIMITES_TEMPO_BUSCA:
            raise ValueError("O limite de tempo não está disponível.")
        self._limites_tempo[indice] = segundos
