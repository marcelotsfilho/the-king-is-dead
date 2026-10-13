import os
import tempfile
import unittest

from controller.start_menu_controller import ControladorMenuInicial


class VisaoFalsa:
    pass


class TesteControladorMenuInicial(unittest.TestCase):
    def test_informa_quando_existe_jogo_salvo(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "state_tree.json")

            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("{}")

            controlador = ControladorMenuInicial(
                VisaoFalsa(),
                caminho,
            )

            self.assertTrue(controlador.existe_jogo_salvo())

    def test_informa_quando_nao_existe_jogo_salvo(self):
        controlador = ControladorMenuInicial(
            VisaoFalsa(),
            "arquivo_inexistente.json",
        )

        self.assertFalse(controlador.existe_jogo_salvo())


if __name__ == "__main__":
    unittest.main()
