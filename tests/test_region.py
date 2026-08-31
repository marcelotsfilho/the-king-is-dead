import unittest

from model.enums import Faccao
from model.region import Regiao


class TesteRegiao(unittest.TestCase):
    """Verifica o estado e as operações básicas de uma região."""

    def test_regiao_comeca_sem_seguidores(self) -> None:
        regiao = Regiao("Moray")

        for faccao in Faccao:
            self.assertEqual(regiao.quantidade_de_seguidores(faccao), 0)

    def test_adiciona_seguidores_de_uma_faccao(self) -> None:
        regiao = Regiao("Moray")

        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)

        self.assertEqual(
            regiao.quantidade_de_seguidores(Faccao.ESCOCESES),
            2,
        )
        self.assertEqual(regiao.quantidade_de_seguidores(Faccao.GALESES), 0)

    def test_remove_seguidores_existentes(self) -> None:
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)

        regiao.remover_seguidores(Faccao.ESCOCESES)

        self.assertEqual(
            regiao.quantidade_de_seguidores(Faccao.ESCOCESES),
            1,
        )

    def test_nao_remove_mais_seguidores_do_que_existem(self) -> None:
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES)

        with self.assertRaises(ValueError):
            regiao.remover_seguidores(Faccao.ESCOCESES, 2)

    def test_quantidade_deve_ser_positiva(self) -> None:
        regiao = Regiao("Moray")

        with self.assertRaises(ValueError):
            regiao.adicionar_seguidores(Faccao.ESCOCESES, 0)

    def test_regiao_controlada_esta_resolvida(self) -> None:
        regiao = Regiao("Moray")

        regiao.definir_controlador(Faccao.ESCOCESES)

        self.assertTrue(regiao.esta_resolvida())
        self.assertEqual(regiao.controlador, Faccao.ESCOCESES)
        self.assertFalse(regiao.instavel)

    def test_regiao_instavel_esta_resolvida_e_sem_controlador(self) -> None:
        regiao = Regiao("Moray")
        regiao.definir_controlador(Faccao.ESCOCESES)

        regiao.marcar_como_instavel()

        self.assertTrue(regiao.esta_resolvida())
        self.assertIsNone(regiao.controlador)
        self.assertTrue(regiao.instavel)


if __name__ == "__main__":
    unittest.main()

