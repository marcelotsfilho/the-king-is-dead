import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.legacy_evaluator import AvaliadorInicial
from experiments.report import CAMPOS, carregar_resultados, salvar_relatorios
from experiments.runner import (
    arquivar_estado, criar_cenario, criar_registro, executar_bateria,
    executar_decisao, montar_plano,
)
from main_experiments import criar_argumentos
from model.minimax_agent import AgenteMinimax
from model.state_evaluator import AvaliadorEstado
from tests.test_minimax_agent import criar_estado


class TesteExperimentos(unittest.TestCase):
    def test_plano_padrao_possui_36_configuracoes(self):
        argumentos = criar_argumentos().parse_args([])
        plano = montar_plano(argumentos.bateria, argumentos.profundidades, argumentos.repeticoes, argumentos.algoritmos)
        self.assertEqual(len(plano), 36)
        self.assertEqual(len({tuple(item.values()) for item in plano}), 36)

    def test_argumentos_rejeitam_profundidade_ou_repeticao_zero(self):
        for opcao in ("--profundidades", "--repeticoes"):
            with patch("sys.stderr"):
                with self.assertRaises(SystemExit):
                    criar_argumentos().parse_args([opcao, "0"])

    def test_inicial_reproduz_custo_de_mobilidade_no_cenario_sem_cartas(self):
        estado = criar_estado()
        self.assertEqual(AvaliadorInicial(0).avaliar(estado), 2)
        self.assertEqual(AvaliadorEstado(0).avaliar(estado), 0)
        agente = AgenteMinimax(0, avaliador=AvaliadorInicial(0))
        self.assertTrue(agente.escolher_jogada(estado).eh_passe())

    def test_estado_arquivado_e_reproduzivel_e_independe_da_heuristica(self):
        estado = criar_cenario("inicial", 42)
        with tempfile.TemporaryDirectory() as pasta:
            resumo = arquivar_estado(estado, pasta)
            outro = arquivar_estado(criar_cenario("inicial", 42), pasta)
            self.assertEqual(resumo, outro)
            self.assertEqual(len(list((Path(pasta) / "states").glob("*.json"))), 1)
            dados = json.loads((Path(pasta) / "states" / (resumo + ".json")).read_text(encoding="utf-8"))
            self.assertIn("jogadores", dados)

    def test_ctrl_c_registra_interrupcao_e_nao_inventa_pontuacao(self):
        estado = criar_estado()
        item = montar_plano("atual", [1], 1, ["minimax"])[0]
        registro = criar_registro(item, estado, "estado", "codigo", "reduzido", "")
        with patch.object(AgenteMinimax, "escolher_jogada", side_effect=KeyboardInterrupt):
            self.assertTrue(executar_decisao(estado, registro))
        self.assertEqual(registro["status"], "interrompido")
        self.assertEqual(registro["pontuacao"], "")
        self.assertEqual(registro["jogada_json"], "")
        self.assertGreaterEqual(float(registro["tempo_segundos"]), 0)

    def test_erro_e_registrado_sem_ser_classificado_como_conclusao(self):
        estado = criar_estado()
        item = montar_plano("atual", [1], 1, ["minimax"])[0]
        registro = criar_registro(item, estado, "estado", "codigo", "reduzido", "")
        with patch.object(AgenteMinimax, "escolher_jogada", side_effect=ValueError("falha")):
            self.assertFalse(executar_decisao(estado, registro))
        self.assertEqual(registro["status"], "erro")
        self.assertIn("falha", registro["erro"])

    def test_csv_preserva_acentos_e_diario_exclui_interrompidos_da_media(self):
        estado = criar_estado()
        item = montar_plano("atual", [1], 1, ["minimax"])[0]
        r = criar_registro(item, estado, "estado", "codigo", "reduzido", "")
        executar_decisao(estado, r)
        interrompido = r.copy()
        interrompido.update(status="interrompido", tempo_segundos="999", pontuacao="", jogada_json="")
        sem_medicao = interrompido.copy()
        sem_medicao.update(tempo_segundos="", nos_visitados="", folhas_avaliadas="", podas="")
        with tempfile.TemporaryDirectory() as pasta:
            diario = Path(pasta) / "diario.md"
            salvar_relatorios(diario, [r, interrompido, sem_medicao], "Cenário reduzido")
            carregados = carregar_resultados(pasta)
            self.assertEqual(len(carregados), 3)
            self.assertEqual(carregados[0]["jogada"], "Passar.")
            texto = diario.read_text(encoding="utf-8")
            self.assertIn("n=1", texto)
            self.assertNotIn("máximo=999", texto)
            self.assertIn("| 3 | atual | minimax | 1 | 1 | — | — | — | — |", texto)

    def test_bateria_reduzida_compara_algoritmos_e_retomada_nao_repete(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta_saida = Path(pasta)
            diario_antigo = pasta_saida / "DIARIO_DE_EXPERIMENTOS.md"
            diario_antigo.write_text("Histórico anterior", encoding="utf-8")
            argumentos = criar_argumentos().parse_args([
                "--cenario", "reduzido", "--profundidades", "1", "--repeticoes", "1", "--saida", pasta,
            ])
            with patch("builtins.print"):
                self.assertEqual(executar_bateria(argumentos), 0)
            registros = carregar_resultados(pasta)
            self.assertEqual(len(registros), 4)
            self.assertTrue(all(r["status"] == "concluido" for r in registros))
            primeiro, = pasta_saida.glob("DIARIO_DE_EXPERIMENTOS_*.md")
            texto = primeiro.read_text(encoding="utf-8")
            self.assertIn("Pares com divergência de nota ou jogada: 0", texto)
            self.assertIn(registros[0]["tempo_segundos"], texto)
            self.assertEqual(texto.count("| concluido |"), 4)

            argumentos.retomar = True
            with patch("builtins.print"):
                self.assertEqual(executar_bateria(argumentos), 0)
            self.assertEqual(len(carregar_resultados(pasta)), 4)
            diarios = set(pasta_saida.glob("DIARIO_DE_EXPERIMENTOS_*.md"))
            retomada, = diarios - {primeiro}
            texto_retomada = retomada.read_text(encoding="utf-8")
            self.assertIn("puladas nesta chamada · 4", texto_retomada)
            self.assertNotIn("| concluido |", texto_retomada)

            argumentos.retomar = False
            with patch("builtins.print"):
                self.assertEqual(executar_bateria(argumentos), 0)
            novo, = set(pasta_saida.glob("DIARIO_DE_EXPERIMENTOS_*.md")) - diarios
            self.assertEqual(novo.read_text(encoding="utf-8").count("| concluido |"), 4)
            self.assertEqual(len(carregar_resultados(pasta)), 8)
            self.assertEqual(primeiro.read_text(encoding="utf-8"), texto)
            self.assertEqual(retomada.read_text(encoding="utf-8"), texto_retomada)
            self.assertEqual(diario_antigo.read_text(encoding="utf-8"), "Histórico anterior")
            self.assertFalse((pasta_saida / "execucoes").exists())

    def test_diario_da_bateria_registra_interrupcao_da_busca(self):
        with tempfile.TemporaryDirectory() as pasta:
            argumentos = criar_argumentos().parse_args([
                "--cenario", "reduzido", "--profundidades", "1", "--saida", pasta,
            ])
            pasta_saida = Path(pasta)

            def interromper_busca(agente, *args, **kwargs):
                caminho, = pasta_saida.glob("DIARIO_DE_EXPERIMENTOS_*.md")
                texto = caminho.read_text(encoding="utf-8")
                self.assertIn("| em_andamento |", texto)
                agente.nos_visitados = 123
                agente.folhas_avaliadas = 120
                raise KeyboardInterrupt

            with (
                patch.object(AgenteMinimax, "escolher_jogada", autospec=True, side_effect=interromper_busca),
                patch("experiments.runner.perf_counter", side_effect=[100, 112.5]),
                patch("builtins.print"),
            ):
                self.assertEqual(executar_bateria(argumentos), 130)

            diario, = pasta_saida.glob("*.md")
            texto = diario.read_text(encoding="utf-8")
            self.assertIn("| interrompido |", texto)
            self.assertIn("Interrupção solicitada pelo usuário (Ctrl+C).", texto)
            _, secao_parcial = texto.split("## Resultados parciais dos testes interrompidos", 1)
            self.assertIn("| 1 | atual | minimax | 1 | 1 | 12.500000 | 123 | 120 | 0 |", secao_parcial)

    def test_preparar_cria_arquivos_sem_iniciar_busca(self):
        with tempfile.TemporaryDirectory() as pasta:
            argumentos = criar_argumentos().parse_args(["--saida", pasta, "--preparar"])
            with patch("builtins.print"):
                with patch("experiments.runner.executar_decisao") as executar:
                    self.assertEqual(executar_bateria(argumentos), 0)
            executar.assert_not_called()
            self.assertEqual(carregar_resultados(pasta), [])
            diario, = Path(pasta).glob("DIARIO_DE_EXPERIMENTOS_*.md")
            self.assertIn("Ainda não há execuções concluídas", diario.read_text(encoding="utf-8"))
            with (Path(pasta) / "results.csv").open(encoding="utf-8-sig", newline="") as arquivo:
                self.assertEqual(next(csv.reader(arquivo, delimiter=";")), CAMPOS)


if __name__ == "__main__":
    unittest.main()
