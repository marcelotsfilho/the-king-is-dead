from itertools import combinations

from model.action_card import (
    eh_carta_de_apoio,
    obter_dados_da_carta_de_apoio,
)
from model.enums import Faccao, FaseTurno, TipoCartaAcao, TipoJogada
from model.game import Jogo
from model.game_state import EstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada


class GeradorJogadas:
    """Encontra as jogadas completas permitidas em um estado."""

    def __init__(self):
        self._executor = ExecutorJogada()

    def gerar(self, estado):
        """Retorna todas as jogadas completas encontradas para o estado."""
        return [jogada for jogada, _ in self.gerar_com_estados(estado)]

    def gerar_com_estados(self, estado):
        """Produz cada jogada legal junto com seu estado resultante."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")

        if estado.finalizado or estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
            return

        yield self._executar_passe(estado)

        for tipo_carta in self._obter_tipos_de_carta(estado):
            opcoes = self._gerar_parametros(estado, tipo_carta)
            for parametros, estado_apos_carta in self._simular_cartas(
                estado, tipo_carta, opcoes
            ):
                for convocacao in self._obter_convocacoes(estado_apos_carta):
                    yield self._concluir_carta(
                        estado_apos_carta, tipo_carta, parametros, convocacao
                    )

    def sortear_com_estado(self, estado, aleatorio):
        """Sorteia um tipo de ação, depois parâmetros e convocação."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")
        if estado.finalizado or estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
            return None

        tipo_carta = aleatorio.choice([None, *self._obter_tipos_de_carta(estado)])
        if tipo_carta is not None:
            resultado = self.sortear_carta_com_estado(estado, tipo_carta, aleatorio)
            if resultado is not None:
                return resultado

        return self._executar_passe(estado)

    def sortear_carta_com_estado(self, estado, tipo_carta, aleatorio):
        """Sorteia parâmetros e convocação para o tipo de carta indicado."""
        opcoes = self._gerar_parametros(estado, tipo_carta)
        aleatorio.shuffle(opcoes)
        for parametros, estado_apos_carta in self._simular_cartas(
            estado, tipo_carta, opcoes
        ):
            convocacoes = self._obter_convocacoes(estado_apos_carta)
            if convocacoes:
                return self._concluir_carta(
                    estado_apos_carta, tipo_carta, parametros,
                    aleatorio.choice(convocacoes),
                )
        return None

    def _obter_tipos_de_carta(self, estado):
        mao = estado.obter_jogador_atual().obter_mao()
        return list(dict.fromkeys(carta.tipo for carta in mao))

    def _executar_passe(self, estado):
        passe = Jogada(TipoJogada.PASSE)
        return passe, self._executor.executar(estado, passe)

    def _simular_cartas(self, estado, tipo_carta, opcoes):
        for parametros in opcoes:
            try:
                estado_apos_carta = self._executor.executar_carta(
                    estado, tipo_carta, parametros
                )
            except ValueError:
                # As regras podem rejeitar uma troca que desfaz a ação anterior.
                continue
            yield parametros, estado_apos_carta

    def _concluir_carta(self, estado_apos_carta, tipo_carta, parametros, convocacao):
        nome_regiao, faccao = convocacao
        jogada = Jogada(
            TipoJogada.CARTA,
            tipo_carta=tipo_carta,
            parametros=parametros,
            nome_regiao_convocacao=nome_regiao,
            faccao_convocacao=faccao,
        )
        resultado = self._executor.executar_convocacao(
            estado_apos_carta, nome_regiao, faccao
        )
        return jogada, resultado

    def _obter_convocacoes(self, estado):
        convocacoes = []

        for nome_regiao in estado.tabuleiro.obter_nomes_das_regioes():
            regiao = estado.tabuleiro.obter_regiao(nome_regiao)

            if regiao.esta_resolvida():
                continue

            for faccao in Faccao:
                if regiao.quantidade_de_seguidores(faccao) > 0:
                    convocacoes.append((nome_regiao, faccao))

        return convocacoes

    def _gerar_parametros(self, estado, tipo_carta):
        if eh_carta_de_apoio(tipo_carta):
            return self._gerar_parametros_apoio(estado, tipo_carta)

        if tipo_carta == TipoCartaAcao.NEGOCIAR:
            return self._gerar_parametros_negociar(estado)

        if tipo_carta == TipoCartaAcao.MANOBRAR:
            return self._gerar_parametros_manobrar(estado)

        if tipo_carta == TipoCartaAcao.SUPERAR_MANOBRA:
            return self._gerar_parametros_superar_manobra(estado)

        if tipo_carta == TipoCartaAcao.REUNIR:
            return self._gerar_parametros_reunir(estado)

        return []

    def _gerar_parametros_apoio(self, estado, tipo_carta):
        jogo = Jogo(estado)
        regioes = jogo.obter_regioes_validas_para_apoio(tipo_carta)

        faccao, _ = obter_dados_da_carta_de_apoio(tipo_carta)

        if estado.reserva.quantidade(faccao) == 0 or not regioes:
            return [{}]

        parametros = []

        for nome_regiao in regioes:
            parametros.append({"regiao": nome_regiao})

        return parametros

    def _gerar_parametros_negociar(self, estado):
        posicoes = estado.trilha_disputas.obter_posicoes_negociaveis()
        if len(posicoes) < 2:
            return [{}]

        if not estado.obter_jogador_atual().disco_negociacao_disponivel:
            return []

        parametros = []
        for posicao_a, posicao_b in combinations(posicoes, 2):
            for posicao_disco in (posicao_a, posicao_b):
                parametros.append({
                    "posicao_a": posicao_a,
                    "posicao_b": posicao_b,
                    "posicao_disco": posicao_disco,
                })
        return parametros

    def _gerar_parametros_manobrar(self, estado):
        regioes = estado.tabuleiro.obter_regioes_com_seguidores()
        if len(regioes) < 2:
            return [{}]

        parametros = []
        for regiao_a, regiao_b in combinations(regioes, 2):
            parametros.extend(self._gerar_trocas(regiao_a, regiao_b, 1))
        return parametros

    def _gerar_parametros_superar_manobra(self, estado):
        pares, quantidade_destino = Jogo(estado).obter_trocas_superar_manobra()
        if quantidade_destino == 0:
            return [{}]

        parametros = []
        for regiao_a, regiao_b in pares:
            parametros.extend(self._gerar_trocas(
                regiao_a, regiao_b, quantidade_destino
            ))
        return parametros

    def _gerar_trocas(self, regiao_a, regiao_b, quantidade_destino):
        for faccao_a in Faccao:
            if regiao_a.quantidade_de_seguidores(faccao_a) == 0:
                continue
            for faccao_b in Faccao:
                if regiao_b.quantidade_de_seguidores(faccao_b) >= quantidade_destino:
                    yield {
                        "regiao_a": regiao_a.nome,
                        "faccao_a": faccao_a,
                        "regiao_b": regiao_b.nome,
                        "faccao_b": faccao_b,
                    }

    def _gerar_parametros_reunir(self, estado):
        regioes = []

        for nome_regiao in estado.tabuleiro.obter_nomes_das_regioes():
            regiao = estado.tabuleiro.obter_regiao(nome_regiao)

            if not regiao.esta_resolvida():
                regioes.append(nome_regiao)

        destinos_parciais = [{}]

        for faccao in Faccao:
            if estado.reserva.quantidade(faccao) == 0:
                continue

            novos_destinos = []

            for destinos in destinos_parciais:
                for nome_regiao in regioes:
                    copia_destinos = destinos.copy()
                    copia_destinos[faccao] = nome_regiao
                    novos_destinos.append(copia_destinos)

            destinos_parciais = novos_destinos

        parametros = []

        for destinos in destinos_parciais:
            parametros.append({"destinos": destinos})

        return parametros
