import unittest

from model.enums import Faccao
from model.region import Regiao


class TesteRegiao(unittest.TestCase):
    """Verifica o estado e as operações básicas de uma região."""

    def test_regiao_comeca_sem_seguidores(self):
        regiao = Regiao("Moray")

        for faccao in Faccao:
            self.assertEqual(regiao.quantidade_de_seguidores(faccao), 0)

    def test_adiciona_seguidores_de_uma_faccao(self):
        regiao = Regiao("Moray")

        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)

        self.assertEqual(
            regiao.quantidade_de_seguidores(Faccao.ESCOCESES),
            2,
        )
        self.assertEqual(regiao.quantidade_de_seguidores(Faccao.GALESES), 0)

    def test_remove_seguidores_existentes(self):
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)

        regiao.remover_seguidores(Faccao.ESCOCESES)

        self.assertEqual(
            regiao.quantidade_de_seguidores(Faccao.ESCOCESES),
            1,
        )

    def test_nao_remove_mais_seguidores_do_que_existem(self):
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES)

        with self.assertRaises(ValueError):
            regiao.remover_seguidores(Faccao.ESCOCESES, 2)

    def test_quantidade_deve_ser_positiva(self):
        regiao = Regiao("Moray")

        with self.assertRaises(ValueError):
            regiao.adicionar_seguidores(Faccao.ESCOCESES, 0)

    def test_regiao_controlada_esta_resolvida(self):
        regiao = Regiao("Moray")

        regiao.definir_controlador(Faccao.ESCOCESES)

        self.assertTrue(regiao.esta_resolvida())
        self.assertEqual(regiao.controlador, Faccao.ESCOCESES)
        self.assertFalse(regiao.instavel)

    def test_regiao_instavel_esta_resolvida_e_sem_controlador(self):
        regiao = Regiao("Moray")
        regiao.definir_controlador(Faccao.ESCOCESES)

        regiao.marcar_como_instavel()

        self.assertTrue(regiao.esta_resolvida())
        self.assertIsNone(regiao.controlador)
        self.assertTrue(regiao.instavel)

    def test_total_de_seguidores_soma_todas_as_faccoes(self):
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)
        regiao.adicionar_seguidores(Faccao.GALESES)

        self.assertEqual(regiao.total_de_seguidores(), 3)

    def test_remove_todos_os_seguidores(self):
        regiao = Regiao("Moray")
        regiao.adicionar_seguidores(Faccao.ESCOCESES, 2)
        regiao.adicionar_seguidores(Faccao.INGLESES)

        removidos = regiao.remover_todos_os_seguidores()

        self.assertEqual(removidos[Faccao.ESCOCESES], 2)
        self.assertEqual(removidos[Faccao.INGLESES], 1)
        self.assertEqual(regiao.total_de_seguidores(), 0)

    def test_regiao_resolvida_nao_pode_receber_seguidores(self):
        regiao = Regiao("Moray")
        regiao.definir_controlador(Faccao.ESCOCESES)

        with self.assertRaises(ValueError):
            regiao.adicionar_seguidores(Faccao.GALESES)


if __name__ == "__main__":
    unittest.main()
