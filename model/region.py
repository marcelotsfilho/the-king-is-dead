from model.enums import Faccao


class Regiao:
    """Armazena e protege o estado de uma região do tabuleiro."""

    def __init__(self, nome):
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome da região não pode ser vazio.")

        self.nome = nome_limpo
        self._seguidores = {
            Faccao.ESCOCESES: 0,
            Faccao.GALESES: 0,
            Faccao.INGLESES: 0,
        }
        self.controlador = None
        self.instavel = False

    def obter_seguidores(self):
        """Retorna uma cópia das quantidades de seguidores."""
        return self._seguidores.copy()

    def quantidade_de_seguidores(self, faccao):
        """Retorna quantos seguidores de uma facção estão na região."""
        return self._seguidores[faccao]

    def adicionar_seguidores(self, faccao, quantidade=1):
        """Adiciona uma quantidade positiva de seguidores de uma facção."""
        self._validar_quantidade(quantidade)
        self._seguidores[faccao] += quantidade

    def remover_seguidores(self, faccao, quantidade=1):
        """Remove seguidores sem permitir que a quantidade fique negativa."""
        self._validar_quantidade(quantidade)

        if quantidade > self._seguidores[faccao]:
            raise ValueError("Não há seguidores suficientes para remover.")

        self._seguidores[faccao] -= quantidade

    def definir_controlador(self, faccao):
        """Marca a região como controlada por uma facção."""
        self.controlador = faccao
        self.instavel = False

    def marcar_como_instavel(self):
        """Marca a região como instável e sem facção controladora."""
        self.controlador = None
        self.instavel = True

    def esta_resolvida(self):
        """Informa se a disputa de poder da região já foi resolvida."""
        return self.controlador is not None or self.instavel

    def _validar_quantidade(self, quantidade):
        if isinstance(quantidade, bool) or not isinstance(quantidade, int):
            raise TypeError("A quantidade deve ser um número inteiro.")

        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
