from model.action_card import (
    eh_carta_de_apoio,
    obter_dados_da_carta_de_apoio,
)
from model.enums import Faccao, FaseTurno, TipoCartaAcao, TipoJogada
from model.game import Jogo
from model.game_state import EstadoJogo
from model.game_state_serializer import SerializadorEstadoJogo
from model.legal_move import Jogada
from model.legal_move_executor import ExecutorJogada


class GeradorJogadas:
    """Encontra as jogadas completas permitidas em um estado."""

    def __init__(self):
        self._serializador = SerializadorEstadoJogo()
        self._executor = ExecutorJogada()

    def gerar(self, estado):
        """Retorna todas as jogadas completas encontradas para o estado."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")

        if estado.finalizado:
            return []

        if estado.fase_turno != FaseTurno.ESCOLHER_ACAO:
            return []

        jogadas = []
        passe = Jogada(TipoJogada.PASSE)
        self._adicionar_se_valida(estado, passe, jogadas)

        tipos_processados = []
        jogador = estado.obter_jogador_atual()

        for carta in jogador.obter_mao():
            if carta.tipo in tipos_processados:
                continue

            tipos_processados.append(carta.tipo)
            parametros_possiveis = self._gerar_parametros(
                estado,
                carta.tipo,
            )

            for parametros in parametros_possiveis:
                estado_apos_carta = self._simular_carta(
                    estado,
                    carta.tipo,
                    parametros,
                )

                if estado_apos_carta is None:
                    continue

                convocacoes = self._obter_convocacoes(estado_apos_carta)

                for nome_regiao, faccao in convocacoes:
                    jogada = Jogada(
                        TipoJogada.CARTA,
                        tipo_carta=carta.tipo,
                        parametros=parametros,
                        nome_regiao_convocacao=nome_regiao,
                        faccao_convocacao=faccao,
                    )
                    self._adicionar_se_valida(estado, jogada, jogadas)

        return jogadas

    def _adicionar_se_valida(self, estado, jogada, jogadas):
        try:
            self._executor.executar(estado, jogada)
            jogadas.append(jogada)
        except (TypeError, ValueError):
            pass

    def _simular_carta(self, estado, tipo_carta, parametros):
        copia = self._serializador.copiar(estado)
        jogador = copia.obter_jogador_atual()
        carta_encontrada = None

        for carta in jogador.obter_mao():
            if carta.tipo == tipo_carta:
                carta_encontrada = carta
                break

        if carta_encontrada is None:
            return None

        try:
            jogo = Jogo(copia)
            jogo.jogar_carta(carta_encontrada, parametros)
            return copia
        except (TypeError, ValueError):
            return None

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
        posicoes = []

        for posicao in range(1, 9):
            carta = estado.trilha_disputas.obter_carta(posicao)

            if carta.virada_para_cima and not carta.possui_disco_negociacao:
                posicoes.append(posicao)

        if len(posicoes) < 2:
            return [{}]

        jogador = estado.obter_jogador_atual()

        if not jogador.disco_negociacao_disponivel:
            return []

        parametros = []

        for indice_a in range(len(posicoes)):
            for indice_b in range(indice_a + 1, len(posicoes)):
                posicao_a = posicoes[indice_a]
                posicao_b = posicoes[indice_b]
                parametros.append(
                    {
                        "posicao_a": posicao_a,
                        "posicao_b": posicao_b,
                        "posicao_disco": posicao_a,
                    }
                )
                parametros.append(
                    {
                        "posicao_a": posicao_a,
                        "posicao_b": posicao_b,
                        "posicao_disco": posicao_b,
                    }
                )

        return parametros

    def _gerar_parametros_manobrar(self, estado):
        regioes = self._obter_regioes_com_seguidores(estado)

        if len(regioes) < 2:
            return [{}]

        parametros = []

        for indice_a in range(len(regioes)):
            for indice_b in range(indice_a + 1, len(regioes)):
                regiao_a = regioes[indice_a]
                regiao_b = regioes[indice_b]

                for faccao_a in Faccao:
                    if regiao_a.quantidade_de_seguidores(faccao_a) == 0:
                        continue

                    for faccao_b in Faccao:
                        if regiao_b.quantidade_de_seguidores(faccao_b) == 0:
                            continue

                        parametros.append(
                            {
                                "regiao_a": regiao_a.nome,
                                "faccao_a": faccao_a,
                                "regiao_b": regiao_b.nome,
                                "faccao_b": faccao_b,
                            }
                        )

        return parametros

    def _obter_regioes_com_seguidores(self, estado):
        regioes = []

        for regiao in estado.tabuleiro.obter_regioes().values():
            if regiao.esta_resolvida():
                continue

            if regiao.total_de_seguidores() > 0:
                regioes.append(regiao)

        return regioes

    def _gerar_parametros_superar_manobra(self, estado):
        existe_troca_com_dois = self._existe_troca_com_dois(estado)
        quantidade_destino = 1

        if existe_troca_com_dois:
            quantidade_destino = 2

        parametros = []
        tabuleiro = estado.tabuleiro

        for nome_a in tabuleiro.obter_nomes_das_regioes():
            regiao_a = tabuleiro.obter_regiao(nome_a)

            if regiao_a.esta_resolvida():
                continue

            for nome_b in tabuleiro.regioes_adjacentes(nome_a):
                regiao_b = tabuleiro.obter_regiao(nome_b)

                if regiao_b.esta_resolvida():
                    continue

                self._adicionar_trocas_superar_manobra(
                    parametros,
                    regiao_a,
                    regiao_b,
                    quantidade_destino,
                )

        if not parametros:
            return [{}]

        return parametros

    def _existe_troca_com_dois(self, estado):
        tabuleiro = estado.tabuleiro

        for nome_a in tabuleiro.obter_nomes_das_regioes():
            regiao_a = tabuleiro.obter_regiao(nome_a)

            if regiao_a.esta_resolvida():
                continue

            if regiao_a.total_de_seguidores() == 0:
                continue

            for nome_b in tabuleiro.regioes_adjacentes(nome_a):
                regiao_b = tabuleiro.obter_regiao(nome_b)

                if regiao_b.esta_resolvida():
                    continue

                for faccao in Faccao:
                    if regiao_b.quantidade_de_seguidores(faccao) >= 2:
                        return True

        return False

    def _adicionar_trocas_superar_manobra(
        self,
        parametros,
        regiao_a,
        regiao_b,
        quantidade_destino,
    ):
        for faccao_a in Faccao:
            if regiao_a.quantidade_de_seguidores(faccao_a) == 0:
                continue

            for faccao_b in Faccao:
                quantidade = regiao_b.quantidade_de_seguidores(faccao_b)

                if quantidade >= quantidade_destino:
                    parametros.append(
                        {
                            "regiao_a": regiao_a.nome,
                            "faccao_a": faccao_a,
                            "regiao_b": regiao_b.nome,
                            "faccao_b": faccao_b,
                        }
                    )

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
