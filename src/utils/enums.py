from enum import Enum

class EstadoJogo(Enum):
    """Estados possíveis do jogo."""
    MENU = "menu"
    LOJA = "loja"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    GAME_OVER = "game_over"

class TipoObstaculo(Enum):
    """Tipos de obstáculos."""
    CACTO = "cacto"
    PTERODACTILO = "pterodactilo"

class TipoDinossauro(Enum):
    """Variantes disponíveis de dinossauros."""
    CLASSICO = "classico"
    ESPADAO = "espadao"
    MOTOSERRA = "motoserra"
    SHURIKEN = "shuriken"

class TipoConsumivel(Enum):
    """Tipos de consumíveis."""
    VIDA = "vida"
    VELOCIDADE = "velocidade"
    PULO = "pulo"
