# Estas são as dimensões lógicas usadas para desenhar o jogo.
# A janela real é calculada de acordo com a resolução do monitor.
LARGURA_JANELA = 1200
ALTURA_JANELA = 1030
TITULO_JANELA = "The King is Dead"
COR_DE_FUNDO = (230, 217, 191)
COR_TEXTO = (35, 32, 28)
COR_PAINEL = (245, 238, 220)
COR_BORDA = (90, 75, 55)
COR_FRONTEIRA = (135, 112, 78)
COR_BOTAO = (126, 70, 52)
COR_BOTAO_DESATIVADO = (150, 145, 135)
COR_BRANCA = (255, 255, 255)
COR_INSTABILIDADE = (90, 90, 90)

CORES_FACCOES = {
    "escoceses": (49, 105, 183),
    "galeses": (196, 54, 54),
    "ingleses": (227, 183, 50),
}

POSICOES_REGIOES = {
    "Moray": (40, 100),
    "Strathclyde": (260, 100),
    "Northumbria": (480, 100),
    "Lancaster": (700, 100),
    "Gwynedd": (40, 280),
    "Warwick": (260, 280),
    "Essex": (480, 280),
    "Devon": (700, 280),
}

# Algumas fronteiras longas precisam passar pelos corredores entre as caixas.
# Estes pontos alteram apenas o desenho; as regras continuam em model/board.py.
ROTAS_FRONTEIRAS = {
    frozenset(["Moray", "Northumbria"]): [(135, 82), (575, 82)],
    frozenset(["Strathclyde", "Lancaster"]): [(355, 72), (795, 72)],
    frozenset(["Gwynedd", "Lancaster"]): [(240, 255), (680, 255)],
    frozenset(["Gwynedd", "Devon"]): [(135, 432), (795, 432)],
    frozenset(["Warwick", "Devon"]): [(355, 422), (795, 422)],
}

LARGURA_REGIAO = 190
ALTURA_REGIAO = 130

LARGURA_CARTA_ACAO = 132
ALTURA_CARTA_ACAO = 78
ESPACO_ENTRE_CARTAS = 8
POSICAO_X_MAO = 40
POSICAO_Y_MAO = 815
