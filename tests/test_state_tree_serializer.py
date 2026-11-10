import json
import os
import tempfile
import unittest

from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, TipoCartaAcao
from model.game_state import EstadoJogo
from model.player import Jogador
from model.state_tree import ArvoreEstados
from model.state_tree_serializer import SerializadorArvoreEstados
from model.supply import ReservaSeguidores


def criar_arvore_com_tres_niveis():
    tabuleiro = Tabuleiro()
    trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
    jogadores = [Jogador("Ana"), Jogador("Bruno")]
    estado = EstadoJogo(
        tabuleiro,
        trilha,
        jogadores,
        ReservaSeguidores(0),
    )
    arvore = ArvoreEstados(estado)
    primeiro_filho = arvore.expandir_no_atual()[0]
    arvore.avancar_para(primeiro_filho)
    segundo_filho = arvore.expandir_no_atual()[0]
    arvore.avancar_para(segundo_filho)
    return arvore


class TesteSerializadorArvoreEstados(unittest.TestCase):
    def setUp(self):
        self.serializador = SerializadorArvoreEstados()

    def test_serializa_e_restaura_estrutura_da_arvore(self):
        arvore = criar_arvore_com_tres_niveis()

        dados = self.serializador.serializar(arvore)
        restaurada = self.serializador.restaurar(dados)

        self.assertEqual(restaurada.quantidade_nos(), 3)
        self.assertEqual(restaurada.obter_no_atual().obter_nivel(), 2)
        self.assertTrue(restaurada.obter_raiz().esta_expandido())
        primeiro_filho = restaurada.obter_raiz().obter_filhos()[0]
        self.assertTrue(primeiro_filho.esta_expandido())
        self.assertFalse(restaurada.obter_no_atual().esta_expandido())
        self.assertTrue(restaurada.obter_raiz().esta_visitado())
        self.assertTrue(primeiro_filho.esta_visitado())
        self.assertTrue(restaurada.obter_no_atual().esta_visitado())

    def test_dados_da_arvore_podem_ser_convertidos_em_json(self):
        arvore = criar_arvore_com_tres_niveis()
        dados = self.serializador.serializar(arvore)

        texto = json.dumps(dados, ensure_ascii=False)

        self.assertIn('"indice_no_atual": 2', texto)
        self.assertIn('"jogada_origem"', texto)

    def test_salva_e_carrega_arquivo_json(self):
        arvore = criar_arvore_com_tres_niveis()

        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "arvore.json")
            self.serializador.salvar(arvore, caminho)
            restaurada = self.serializador.carregar(caminho)

        self.assertEqual(restaurada.quantidade_nos(), 3)
        self.assertEqual(
            restaurada.obter_no_atual().obter_identificador(),
            arvore.obter_no_atual().obter_identificador(),
        )

    def test_preserva_marca_de_jogada_voltada(self):
        arvore = criar_arvore_com_tres_niveis()
        arvore.voltar()

        dados = self.serializador.serializar(arvore)
        restaurada = self.serializador.restaurar(dados)
        no_atual = restaurada.obter_no_atual()
        no_voltado = no_atual.obter_filhos()[0]

        self.assertTrue(no_voltado.representa_jogada_voltada())
        self.assertFalse(no_voltado.esta_visitado())

    def test_carrega_arquivo_antigo_sem_marca_de_jogada_voltada(self):
        arvore = criar_arvore_com_tres_niveis()
        dados = self.serializador.serializar(arvore)

        for dados_no in dados["nos"]:
            del dados_no["jogada_voltada"]

        restaurada = self.serializador.restaurar(dados)

        for no in restaurada.obter_nos():
            self.assertFalse(no.representa_jogada_voltada())

    def test_restaura_jogada_de_carta_na_arvore(self):
        tabuleiro = Tabuleiro()
        trilha = TrilhaDisputas(tabuleiro.obter_nomes_das_regioes())
        jogadores = [Jogador("Ana"), Jogador("Bruno")]
        reserva = ReservaSeguidores(2)
        reserva.retirar(Faccao.ESCOCESES)
        tabuleiro.obter_regiao("Moray").adicionar_seguidores(
            Faccao.ESCOCESES
        )
        jogadores[0].adicionar_carta_mao(
            CartaAcao(TipoCartaAcao.APOIO_ESCOCES)
        )
        estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)
        arvore = ArvoreEstados(estado)
        arvore.expandir_no_atual()

        restaurada = self.serializador.restaurar(
            self.serializador.serializar(arvore)
        )
        tipos_restaurados = []

        for filho in restaurada.obter_raiz().obter_filhos():
            jogada = filho.obter_jogada_origem()

            if jogada.eh_carta():
                tipos_restaurados.append(jogada.tipo_carta)

        self.assertIn(TipoCartaAcao.APOIO_ESCOCES, tipos_restaurados)

    def test_rejeita_versao_desconhecida(self):
        arvore = criar_arvore_com_tres_niveis()
        dados = self.serializador.serializar(arvore)
        dados["versao"] = 999

        with self.assertRaises(ValueError):
            self.serializador.restaurar(dados)

    def test_rejeita_indice_atual_fora_da_arvore(self):
        arvore = criar_arvore_com_tres_niveis()
        dados = self.serializador.serializar(arvore)
        dados["indice_no_atual"] = 99

        with self.assertRaises(ValueError):
            self.serializador.restaurar(dados)

    def test_rejeita_valores_invalidos(self):
        with self.assertRaises(TypeError):
            self.serializador.serializar("árvore")

        with self.assertRaises(TypeError):
            self.serializador.restaurar("dados")

        with self.assertRaises(TypeError):
            self.serializador.carregar(10)

        with self.assertRaises(TypeError):
            self.serializador.salvar("árvore", "arvore.json")

        with self.assertRaises(ValueError):
            self.serializador.salvar(ArvoreEstados.__name__, "")


if __name__ == "__main__":
    unittest.main()
