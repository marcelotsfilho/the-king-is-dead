def validar_quantidade_de_seguidores(quantidade):
    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        raise TypeError("A quantidade deve ser um número inteiro.")

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
