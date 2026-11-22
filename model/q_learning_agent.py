import json
import random
from pathlib import Path

from model.endgame_search import BuscaFinal
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game import Jogo
from model.legal_move_generator import GeradorJogadas
from model.state_evaluator import AvaliadorEstado


CAMINHO_TABELA_Q = Path(__file__).resolve().parents[1] / "experiments" / "etapa4" / "tabela_q.json"
CAMINHO_TABELA_Q_JOGO = CAMINHO_TABELA_Q.parent / "bateria_3000" / "tabela_selecionada.json"
_VERSAO = 1
_TIPOS_ACAO = ("PASSE", *(carta.name for carta in TipoCartaAcao))


def _sinal(valor):
    return (valor > 0) - (valor < 0)


class TabelaQ:
    """Valores esparsos de estado e ação, com valor inicial zero."""

    def __init__(self):
        self.valores = {}
        self.metadados = {}

    def consultar(self, chave, acao):
        return self.valores.get(chave, {}).get(acao, 0.0)

    def atualizar(self, chave, acao, recompensa, proximas, alpha, gamma):
        futuro = 0.0
        if proximas is not None:
            proxima_chave, opcoes = proximas
            futuro = max(self.consultar(proxima_chave, opcao) for opcao in opcoes)
        valor = self.consultar(chave, acao)
        self.valores.setdefault(chave, {})[acao] = valor + alpha * (
            recompensa + gamma * futuro - valor
        )

    def salvar(self, caminho, metadados):
        dados = {"versao": _VERSAO, "metadados": metadados, "valores": self.valores}
        caminho = Path(caminho)
        temporario = caminho.with_suffix(".json.tmp")
        temporario.write_text(json.dumps(dados, indent=2, sort_keys=True), encoding="utf-8")
        temporario.replace(caminho)

    @classmethod
    def carregar(cls, caminho):
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if not isinstance(dados, dict) or dados.get("versao") != _VERSAO:
            raise ValueError("Versão da tabela Q inválida")
        valores = dados.get("valores")
        if not isinstance(valores, dict) or not valores:
            raise ValueError("A tabela Q não contém valores treinados")
        for acoes in valores.values():
            if not isinstance(acoes, dict) or not acoes:
                raise ValueError("A tabela Q contém um estado inválido")
            for acao, valor in acoes.items():
                if acao not in _TIPOS_ACAO or type(valor) not in (float, int) or not -1 <= valor <= 1:
                    raise ValueError("A tabela Q contém uma ação ou valor inválido")
        tabela = cls()
        tabela.valores = valores
        tabela.metadados = dados.get("metadados", {})
        if not isinstance(tabela.metadados, dict):
            raise ValueError("Metadados da tabela Q inválidos")
        return tabela


class AgenteQLearning:
    """Aprende a escolha entre passar e usar cada tipo de carta disponível."""

    def __init__(self, tabela, semente=None, analisar_finais=False):
        self.tabela = tabela
        self._aleatorio = random.Random(semente)
        self._gerador = GeradorJogadas()
        self._busca_final = BuscaFinal(limite_nos=800) if analisar_finais else None
        self.nos_busca_final = 0
        self.busca_final_concluida = False
        self.busca_final_alterou = False
        self.ultima_pontuacao = None
        self.nos_visitados = 0
        self.folhas_avaliadas = 0
        self.podas_realizadas = 0

    def preparar_turno(self, estado, registrar=None):
        indice = estado.indice_jogador_atual
        jogador = estado.obter_jogador_atual()
        adversario = estado.obter_jogadores()[1 - indice]
        avaliador = AvaliadorEstado(indice)
        resolvidas = estado.trilha_disputas.quantidade_resolvida()
        opcoes = {}

        if resolvidas == 7:
            candidatos = self._gerador.gerar_com_estados(estado)
        else:
            candidatos = self._amostrar_jogadas(estado)

        self.nos_visitados = 0
        for jogada, resultante in candidatos:
            tipo = "PASSE" if jogada.eh_passe() else jogada.tipo_carta.name
            nota = avaliador.avaliar(resultante, profundidade=1)
            if registrar is not None:
                registrar(tipo, jogada, resultante, nota)
            self.nos_visitados += 1
            if tipo not in opcoes or nota > opcoes[tipo][2]:
                opcoes[tipo] = (jogada, resultante, nota)
        self.folhas_avaliadas = self.nos_visitados

        faccao_forte = Jogo(estado).obter_faccoes_por_poder()[0]
        carta = estado.trilha_disputas.obter_proxima_carta()
        lider, _ = estado.tabuleiro.obter_regiao(carta.nome_regiao).obter_lideranca()
        instabilidades = estado.tabuleiro.quantidade_instabilidades()
        risco_invasao = instabilidades == 2 and lider is None
        vantagem = jogador.qtd_na_corte(faccao_forte) - adversario.qtd_na_corte(faccao_forte)
        if risco_invasao:
            vantagem = min(jogador.qtd_na_corte(f) for f in Faccao) - min(
                adversario.qtd_na_corte(f) for f in Faccao
            )
        chave = json.dumps((
            resolvidas // 3, estado.passes_consecutivos, risco_invasao,
            _sinal(vantagem), min(jogador.quantidade_cartas(), 3),
            _sinal(opcoes["PASSE"][2] - max(opcao[2] for opcao in opcoes.values())),
        ), separators=(",", ":"))
        return chave, opcoes

    def _amostrar_jogadas(self, estado):
        # A amostra das concretizações é estável durante o treino e a apresentação.
        yield next(self._gerador.gerar_com_estados(estado))
        aleatorio = random.Random(0)
        tipos = dict.fromkeys(carta.tipo for carta in estado.obter_jogador_atual().obter_mao())
        for tipo in tipos:
            for _ in range(2):
                resultado = self._gerador.sortear_carta_com_estado(estado, tipo, aleatorio)
                if resultado is not None:
                    yield resultado

    def escolher_opcao(self, turno, epsilon=0.0):
        chave, opcoes = turno
        if epsilon and self._aleatorio.random() < epsilon:
            acao = self._aleatorio.choice(tuple(opcoes))
        else:
            acao = max(opcoes, key=lambda tipo: (self.tabela.consultar(chave, tipo), opcoes[tipo][2]))
        self.ultima_pontuacao = self.tabela.consultar(chave, acao)
        jogada, estado, _ = opcoes[acao]
        return acao, jogada, estado

    def escolher_jogada(self, estado):
        if estado.finalizado or estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
            return None
        return self.decidir_turno(estado, self.preparar_turno(estado))[1]

    def decidir_turno(self, estado, turno):
        acao, jogada, seguinte = self.escolher_opcao(turno)
        if self._busca_final is None:
            return acao, jogada, seguinte
        melhor, resultante = self._busca_final.melhorar(estado, jogada, seguinte)
        self.nos_busca_final = self._busca_final.nos_visitados
        self.busca_final_concluida = self._busca_final.concluida
        self.busca_final_alterou = melhor is not jogada
        if self.busca_final_alterou:
            acao = "PASSE" if melhor.eh_passe() else melhor.tipo_carta.name
            self.ultima_pontuacao = self.tabela.consultar(turno[0], acao)
        return acao, melhor, resultante
