from model.action_card import CartaAcao
from model.board import Tabuleiro
from model.dispute_track import TrilhaDisputas
from model.enums import Faccao, FaseTurno, TipoCartaAcao
from model.game_state import EstadoJogo
from model.player import Jogador
from model.supply import ReservaSeguidores


_VERSAO_DO_FORMATO = 1


class SerializadorEstadoJogo:
    """Transforma o estado do jogo em dados simples e faz o caminho inverso."""

    def serializar(self, estado):
        """Retorna uma fotografia independente e serializável do estado."""
        if not isinstance(estado, EstadoJogo):
            raise TypeError("O estado deve ser uma instância de EstadoJogo.")

        jogadores = estado.obter_jogadores()

        return {
            "versao": _VERSAO_DO_FORMATO,
            "tabuleiro": self._serializar_tabuleiro(estado.tabuleiro),
            "trilha_disputas": self._serializar_trilha(
                estado.trilha_disputas
            ),
            "jogadores": self._serializar_jogadores(jogadores),
            "reserva": self._serializar_reserva(estado.reserva),
            "indice_jogador_atual": estado.indice_jogador_atual,
            "passes_consecutivos": estado.passes_consecutivos,
            "historico_vitorias_faccoes": self._serializar_faccoes(
                estado.historico_vitorias_faccoes
            ),
            "ultima_acao": self._serializar_ultima_acao(
                estado.ultima_acao,
                jogadores,
            ),
            "ultimo_jogador_que_agiu": self._obter_indice_jogador(
                estado.ultimo_jogador_que_agiu,
                jogadores,
            ),
            "ordem_jogadores_sem_cartas": self._serializar_ordem_jogadores(
                estado.ordem_jogadores_sem_cartas,
                jogadores,
            ),
            "fase_turno": estado.fase_turno.name,
            "carta_em_execucao": self._serializar_carta_em_execucao(
                estado.carta_em_execucao
            ),
            "finalizado": estado.finalizado,
            "vencedor": self._obter_indice_jogador(
                estado.vencedor,
                jogadores,
            ),
            "faccao_vencedora": self._serializar_faccao_opcional(
                estado.faccao_vencedora
            ),
            "motivo_encerramento": estado.motivo_encerramento,
            "ultima_mensagem": estado.ultima_mensagem,
        }

    def restaurar(self, dados):
        """Reconstrói um EstadoJogo a partir de uma fotografia serializada."""
        self._validar_dados(dados)

        tabuleiro = self._restaurar_tabuleiro(dados["tabuleiro"])
        trilha = self._restaurar_trilha(dados["trilha_disputas"])
        jogadores = self._restaurar_jogadores(dados["jogadores"])
        reserva = self._restaurar_reserva(dados["reserva"])
        estado = EstadoJogo(tabuleiro, trilha, jogadores, reserva)

        estado.indice_jogador_atual = dados["indice_jogador_atual"]
        estado.passes_consecutivos = dados["passes_consecutivos"]
        estado.historico_vitorias_faccoes = self._restaurar_faccoes(
            dados["historico_vitorias_faccoes"]
        )
        estado.ultima_acao = self._restaurar_ultima_acao(
            dados["ultima_acao"],
            jogadores,
        )
        estado.ultimo_jogador_que_agiu = self._obter_jogador_por_indice(
            dados["ultimo_jogador_que_agiu"],
            jogadores,
        )
        estado.ordem_jogadores_sem_cartas = self._restaurar_ordem_jogadores(
            dados["ordem_jogadores_sem_cartas"],
            jogadores,
        )
        estado.fase_turno = FaseTurno[dados["fase_turno"]]
        estado.carta_em_execucao = self._restaurar_carta_em_execucao(
            dados["carta_em_execucao"],
            jogadores,
            estado.indice_jogador_atual,
        )
        estado.finalizado = dados["finalizado"]
        estado.vencedor = self._obter_jogador_por_indice(
            dados["vencedor"],
            jogadores,
        )
        estado.faccao_vencedora = self._restaurar_faccao_opcional(
            dados["faccao_vencedora"]
        )
        estado.motivo_encerramento = dados["motivo_encerramento"]
        estado.ultima_mensagem = dados["ultima_mensagem"]

        return estado

    def copiar(self, estado):
        """Cria uma cópia independente do estado atual."""
        dados = self.serializar(estado)
        return self.restaurar(dados)

    def _validar_dados(self, dados):
        if not isinstance(dados, dict):
            raise TypeError("Os dados do estado devem estar em um dicionário.")

        if dados.get("versao") != _VERSAO_DO_FORMATO:
            raise ValueError("A versão dos dados do estado não é suportada.")

    def _serializar_tabuleiro(self, tabuleiro):
        regioes = []

        for nome in tabuleiro.obter_nomes_das_regioes():
            regiao = tabuleiro.obter_regiao(nome)
            regioes.append(
                {
                    "nome": regiao.nome,
                    "seguidores": self._serializar_quantidades_por_faccao(
                        regiao.obter_seguidores()
                    ),
                    "controlador": self._serializar_faccao_opcional(
                        regiao.controlador
                    ),
                    "instavel": regiao.instavel,
                }
            )

        return {"regioes": regioes}

    def _restaurar_tabuleiro(self, dados):
        tabuleiro = Tabuleiro()

        for dados_regiao in dados["regioes"]:
            regiao = tabuleiro.obter_regiao(dados_regiao["nome"])

            for nome_faccao in dados_regiao["seguidores"]:
                quantidade = dados_regiao["seguidores"][nome_faccao]

                if quantidade > 0:
                    faccao = Faccao[nome_faccao]
                    regiao.adicionar_seguidores(faccao, quantidade)

            controlador = dados_regiao["controlador"]

            if controlador is not None:
                regiao.definir_controlador(Faccao[controlador])
            elif dados_regiao["instavel"]:
                regiao.marcar_como_instavel()

        return tabuleiro

    def _serializar_trilha(self, trilha):
        cartas = []

        for carta in trilha.obter_cartas():
            cartas.append(
                {
                    "nome_regiao": carta.nome_regiao,
                    "virada_para_cima": carta.virada_para_cima,
                    "possui_disco_negociacao": (
                        carta.possui_disco_negociacao
                    ),
                }
            )

        return {"cartas": cartas}

    def _restaurar_trilha(self, dados):
        nomes_regioes = []

        for dados_carta in dados["cartas"]:
            nomes_regioes.append(dados_carta["nome_regiao"])

        trilha = TrilhaDisputas(nomes_regioes)

        for posicao in range(1, len(dados["cartas"]) + 1):
            dados_carta = dados["cartas"][posicao - 1]
            carta = trilha.obter_carta(posicao)

            if dados_carta["possui_disco_negociacao"]:
                carta.colocar_disco_negociacao()

            if not dados_carta["virada_para_cima"]:
                carta.virar_para_baixo()

        return trilha

    def _serializar_jogadores(self, jogadores):
        dados_jogadores = []

        for jogador in jogadores:
            dados_jogadores.append(
                {
                    "nome": jogador.nome,
                    "mao": self._serializar_cartas(jogador.obter_mao()),
                    "descarte": self._serializar_cartas(
                        jogador.obter_descarte_mao()
                    ),
                    "corte": self._serializar_quantidades_por_faccao(
                        jogador.obter_corte()
                    ),
                    "disco_negociacao_disponivel": (
                        jogador.disco_negociacao_disponivel
                    ),
                }
            )

        return dados_jogadores

    def _restaurar_jogadores(self, dados_jogadores):
        jogadores = []

        for dados_jogador in dados_jogadores:
            jogador = Jogador(dados_jogador["nome"])

            for nome_tipo in dados_jogador["mao"]:
                jogador.adicionar_carta_mao(
                    CartaAcao(TipoCartaAcao[nome_tipo])
                )

            for nome_tipo in dados_jogador["descarte"]:
                carta = CartaAcao(TipoCartaAcao[nome_tipo])
                jogador.adicionar_carta_mao(carta)
                jogador.usar_carta(carta)

            for nome_faccao in dados_jogador["corte"]:
                quantidade = dados_jogador["corte"][nome_faccao]
                faccao = Faccao[nome_faccao]

                for _ in range(quantidade):
                    jogador.adicionar_seguidor_na_corte(faccao)

            if not dados_jogador["disco_negociacao_disponivel"]:
                jogador.usar_disco_negociacao()

            jogadores.append(jogador)

        return jogadores

    def _serializar_reserva(self, reserva):
        return self._serializar_quantidades_por_faccao(
            reserva.obter_quantidades()
        )

    def _restaurar_reserva(self, dados):
        reserva = ReservaSeguidores(0)

        for nome_faccao in dados:
            quantidade = dados[nome_faccao]

            if quantidade > 0:
                reserva.devolver(Faccao[nome_faccao], quantidade)

        return reserva

    def _serializar_cartas(self, cartas):
        tipos = []

        for carta in cartas:
            tipos.append(carta.tipo.name)

        return tipos

    def _serializar_quantidades_por_faccao(self, quantidades):
        resultado = {}

        for faccao in Faccao:
            resultado[faccao.name] = quantidades[faccao]

        return resultado

    def _serializar_faccoes(self, faccoes):
        nomes = []

        for faccao in faccoes:
            nomes.append(faccao.name)

        return nomes

    def _restaurar_faccoes(self, nomes):
        faccoes = []

        for nome in nomes:
            faccoes.append(Faccao[nome])

        return faccoes

    def _serializar_faccao_opcional(self, faccao):
        if faccao is None:
            return None

        return faccao.name

    def _restaurar_faccao_opcional(self, nome_faccao):
        if nome_faccao is None:
            return None

        return Faccao[nome_faccao]

    def _obter_indice_jogador(self, jogador, jogadores):
        if jogador is None:
            return None

        for indice in range(len(jogadores)):
            if jogadores[indice] is jogador:
                return indice

        raise ValueError("O jogador informado não pertence ao estado.")

    def _obter_jogador_por_indice(self, indice, jogadores):
        if indice is None:
            return None

        return jogadores[indice]

    def _serializar_ordem_jogadores(self, ordem, jogadores):
        indices = []

        for jogador in ordem:
            indices.append(self._obter_indice_jogador(jogador, jogadores))

        return indices

    def _restaurar_ordem_jogadores(self, indices, jogadores):
        ordem = []

        for indice in indices:
            ordem.append(jogadores[indice])

        return ordem

    def _serializar_carta_em_execucao(self, carta):
        if carta is None:
            return None

        return carta.tipo.name

    def _restaurar_carta_em_execucao(
        self,
        nome_tipo,
        jogadores,
        indice_jogador_atual,
    ):
        if nome_tipo is None:
            return None

        jogador = jogadores[indice_jogador_atual]
        descarte = jogador.obter_descarte_mao()

        for carta in reversed(descarte):
            if carta.tipo == TipoCartaAcao[nome_tipo]:
                return carta

        raise ValueError("A carta em execução não foi encontrada no descarte.")

    def _serializar_ultima_acao(self, acao, jogadores):
        if acao is None:
            return None

        return {
            "jogador": self._obter_indice_jogador(
                acao["jogador"],
                jogadores,
            ),
            "tipo": acao["tipo"].name,
            "detalhes": self._serializar_detalhes_acao(
                acao["tipo"],
                acao["detalhes"],
            ),
            "convocacao": self._serializar_convocacao(
                acao["convocacao"]
            ),
        }

    def _restaurar_ultima_acao(self, acao, jogadores):
        if acao is None:
            return None

        tipo = TipoCartaAcao[acao["tipo"]]

        return {
            "jogador": jogadores[acao["jogador"]],
            "tipo": tipo,
            "detalhes": self._restaurar_detalhes_acao(
                tipo,
                acao["detalhes"],
            ),
            "convocacao": self._restaurar_convocacao(
                acao["convocacao"]
            ),
        }

    def _serializar_detalhes_acao(self, tipo, detalhes):
        resultado = detalhes.copy()

        if tipo == TipoCartaAcao.REUNIR and "destinos" in resultado:
            destinos = {}

            for faccao in resultado["destinos"]:
                destinos[faccao.name] = resultado["destinos"][faccao]

            resultado["destinos"] = destinos

        chaves_de_faccao = ["faccao", "faccao_a", "faccao_b"]

        for chave in chaves_de_faccao:
            if chave in resultado and isinstance(resultado[chave], Faccao):
                resultado[chave] = resultado[chave].name

        return resultado

    def _restaurar_detalhes_acao(self, tipo, detalhes):
        resultado = detalhes.copy()

        if tipo == TipoCartaAcao.REUNIR and "destinos" in resultado:
            destinos = {}

            for nome_faccao in resultado["destinos"]:
                destinos[Faccao[nome_faccao]] = resultado["destinos"][
                    nome_faccao
                ]

            resultado["destinos"] = destinos

        chaves_de_faccao = ["faccao", "faccao_a", "faccao_b"]

        for chave in chaves_de_faccao:
            if chave in resultado and resultado[chave] is not None:
                resultado[chave] = Faccao[resultado[chave]]

        return resultado

    def _serializar_convocacao(self, convocacao):
        if convocacao is None:
            return None

        return {
            "regiao": convocacao["regiao"],
            "faccao": convocacao["faccao"].name,
        }

    def _restaurar_convocacao(self, convocacao):
        if convocacao is None:
            return None

        return {
            "regiao": convocacao["regiao"],
            "faccao": Faccao[convocacao["faccao"]],
        }
