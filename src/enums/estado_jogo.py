from enum import Enum


class EstadoJogo(Enum):
    """Enum para estados possíveis do jogo seguindo Liskov Substitution."""
    MENU = "MENU"
    LOJA = "LOJA"
    JOGANDO = "JOGANDO"
    PAUSADO = "PAUSADO"
    GAME_OVER = "GAME_OVER"
