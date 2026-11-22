from model.enums import Faccao
from model.validacao import validar_quantidade_de_seguidores


class ReservaSeguidores:
    """Armazena os seguidores disponíveis fora do tabuleiro e das cortes."""

    def __init__(self, quantidade_por_faccao=16):
        if not isinstance(quantidade_por_faccao, int):
            raise TypeError("A quantidade inicial deve ser um número inteiro.")

        if quantidade_por_faccao < 0:
            raise ValueError("A quantidade inicial não pode ser negativa.")

        self._quantidades = {
            Faccao.ESCOCESES: quantidade_por_faccao,
            Faccao.GALESES: quantidade_por_faccao,
            Faccao.INGLESES: quantidade_por_faccao,
        }

    def obter_quantidades(self):
        """Retorna uma cópia das quantidades disponíveis."""
        return self._quantidades.copy()

    def quantidade(self, faccao):
        """Retorna quantos seguidores de uma facção estão disponíveis."""
        return self._quantidades[faccao]

    def total(self):
        """Retorna a soma dos seguidores de todas as facções."""
        return sum(self._quantidades.values())

    def retirar(self, faccao, quantidade=1):
        """Retira seguidores da reserva quando houver quantidade suficiente."""
        validar_quantidade_de_seguidores(quantidade)

        if quantidade > self._quantidades[faccao]:
            raise ValueError("Não há seguidores suficientes na reserva.")

        self._quantidades[faccao] -= quantidade

    def devolver(self, faccao, quantidade=1):
        """Devolve seguidores para a reserva."""
        validar_quantidade_de_seguidores(quantidade)
        self._quantidades[faccao] += quantidade
