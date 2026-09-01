import unittest

from model.enums import Faccao
from model.supply import ReservaSeguidores


class TesteReservaSeguidores(unittest.TestCase):
    """Verifica a entrada e a saída de seguidores da reserva."""

    def test_reserva_comeca_com_quantidade_por_faccao(self):
        reserva = ReservaSeguidores(16)

        for faccao in Faccao:
            self.assertEqual(reserva.quantidade(faccao), 16)

        self.assertEqual(reserva.total(), 48)

    def test_retirar_e_devolver_seguidores(self):
        reserva = ReservaSeguidores(16)

        reserva.retirar(Faccao.ESCOCESES, 3)
        reserva.devolver(Faccao.ESCOCESES, 2)

        self.assertEqual(reserva.quantidade(Faccao.ESCOCESES), 15)

    def test_nao_permite_retirar_mais_do_que_existe(self):
        reserva = ReservaSeguidores(1)

        with self.assertRaises(ValueError):
            reserva.retirar(Faccao.GALESES, 2)

    def test_quantidade_de_movimentacao_deve_ser_positiva(self):
        reserva = ReservaSeguidores(16)

        with self.assertRaises(ValueError):
            reserva.retirar(Faccao.INGLESES, 0)

    def test_obter_quantidades_retorna_uma_copia(self):
        reserva = ReservaSeguidores(16)

        quantidades = reserva.obter_quantidades()
        quantidades[Faccao.ESCOCESES] = 0

        self.assertEqual(reserva.quantidade(Faccao.ESCOCESES), 16)


if __name__ == "__main__":
    unittest.main()
