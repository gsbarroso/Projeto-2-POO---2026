"""
Configurações globais e constantes do jogo.
Seguindo SOLID: responsabilidade única = armazenar constantes.
Usa pathlib para ser cross-platform.
"""
import pygame
from pathlib import Path


# =====================================================================
# TELA E DISPLAY
# =====================================================================
LARGURA_TELA: int = 800
ALTURA_TELA: int = 400
FPS: int = 60
TITULO_JANELA: str = "Dino Run MVC: Hardcore Edition"

# =====================================================================
# FÍSICA E GAMEPLAY
# =====================================================================
LINHA_CHAO: int = ALTURA_TELA - 30
GRAVIDADE: float = 1.6
FORCA_PULO: float = -21
QUEDA_AGACHADO: float = 4
VELOCIDADE_BASE_JOGO: float = 8.0
INCREMENTO_VELOCIDADE: float = 1.2
PONTOS_PARA_ACELERAR: int = 350
TEMPO_RECARGA_ESPECIAL: int = 250
VELOCIDADE_PROJETIL: int = 20
# ALTURAS BASEADAS NA ESTRATÉGIA DE JOGABILIDADE TRADICIONAL
# [0] Alto: passa por cima do dino em pé (pular causa colisão)
# [1] Médio: exige que o dino agache para desviar
# [2] Baixo: exige que o dino pule por cima (mesma dinâmica do cacto)
ALTURAS_PTERO: list = [LINHA_CHAO - 130, LINHA_CHAO - 85, LINHA_CHAO - 45]
PADDING_COLISAO: int = 10

# =====================================================================
# CORES (RGB)
# =====================================================================
BRANCO: tuple = (255, 255, 255)
PRETO: tuple = (0, 0, 0)
VERDE: tuple = (0, 200, 0)
VERMELHO: tuple = (200, 0, 0)
AZUL: tuple = (0, 0, 200)
AMARELO: tuple = (255, 215, 0)
CINZA_ESCURO: tuple = (44, 62, 80)
CINZA_CLARO: tuple = (236, 240, 241)

# =====================================================================
# CAMINHOS (usando pathlib para cross-platform)
# =====================================================================
BASE_DIR: Path = Path(__file__).parent.parent.parent
ASSETS_DIR: Path = BASE_DIR / "assets"
ARQUIVO_SAVE: Path = BASE_DIR / "save_dino.json"

# Variantes de dinossauros
DINO_VARIANTS: dict = {
    "classico": ASSETS_DIR / "Classico.png",
    "espadao": ASSETS_DIR / "Espadão.png",
    "motoserra": ASSETS_DIR / "Motoserra.png",
    "shuriken": ASSETS_DIR / "Shuriken.png",
}

# Assets de obstáculos e projetil
PROJETIL_IMAGE: Path = ASSETS_DIR / "Projetil.png"
CACTO_IMAGE: Path = ASSETS_DIR / "Cacto.png"
PTERO_IMAGE: Path = ASSETS_DIR / "Pterodáctilo.png"

# =====================================================================
# PREÇOS DA LOJA
# =====================================================================
LOJA_PRECOS_DINOS: dict = {
    "classico": 0,
    "espadao": 100,
    "motoserra": 100,
    "shuriken": 175
}

LOJA_ITENS_CONSUMIVEIS: dict = {
    "vida": {"preco": 50, "nome": "Vida Extra"},
    "velocidade": {"preco": 75, "nome": "Veloc. Boost"},
    "pulo": {"preco": 75, "nome": "Pulo Boost"}
}

# =====================================================================
# DADOS DO JOGADOR (PADRÃO)
# =====================================================================
DADOS_JOGADOR_PADRAO: dict = {
    "moedas": 100,
    "pontos_acumulados": 0,
    "dinossauro_selecionado": "classico",
    "dinossauros_desbloqueados": ["classico"],
    "itens_disponiveis": {"vida": 0, "velocidade": 0, "pulo": 0}
}

# =====================================================================
# CACHE DE IMAGENS
# =====================================================================
_CACHE_IMAGENS: dict = {}


def carregar_sprite(
    caminho: str | Path,
    escala: float = 1.0,
    largura_fallback: int = 50,
    altura_fallback: int = 50,
    max_largura: int | None = None,
    max_altura: int | None = None
) -> pygame.Surface:
    """
    Carrega imagem de sprite com sistema de cache para evitar lag I/O.
    
    Args:
        caminho: Caminho para a imagem.
        escala: Fator de escala (padrão 1.0).
        largura_fallback: Largura padrão se imagem não existir.
        altura_fallback: Altura padrão se imagem não existir.
        max_largura: Largura máxima permitida.
        max_altura: Altura máxima permitida.
    
    Returns:
        pygame.Surface: Imagem carregada do cache ou disco.
    
    Raises:
        Nenhuma - retorna fallback em caso de erro.
    """
    # Converter Path para string se necessário
    caminho_str = str(caminho) if isinstance(caminho, Path) else caminho
    chave_cache = (caminho_str, escala, max_largura, max_altura)
    
    if chave_cache in _CACHE_IMAGENS:
        return _CACHE_IMAGENS[chave_cache]
        
    if Path(caminho_str).exists():
        try:
            imagem = pygame.image.load(caminho_str).convert_alpha()

            if escala != 1.0:
                nova_largura = max(1, int(imagem.get_width() * escala))
                nova_altura = max(1, int(imagem.get_height() * escala))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            if max_largura is None:
                max_largura = max(largura_fallback * 4, 100)
            if max_altura is None:
                max_altura = max(altura_fallback * 4, 100)
            
            if imagem.get_width() > max_largura or imagem.get_height() > max_altura:
                fator = min(
                    max_largura / imagem.get_width(),
                    max_altura / imagem.get_height()
                )
                nova_largura = max(1, int(imagem.get_width() * fator))
                nova_altura = max(1, int(imagem.get_height() * fator))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            _CACHE_IMAGENS[chave_cache] = imagem
            return imagem
        except Exception as e:
            print(f"[AVISO] Falha ao processar a imagem '{caminho_str}': {e}")
    else:
        print(f"[AVISO] Imagem não encontrada: '{caminho_str}'.")

    # Retornar fallback
    superficie = pygame.Surface((largura_fallback, altura_fallback), pygame.SRCALPHA)
    pygame.draw.rect(
        superficie, VERMELHO, (0, 0, largura_fallback, altura_fallback), border_radius=4
    )
    _CACHE_IMAGENS[chave_cache] = superficie
    return superficie


def limpar_cache_imagens() -> None:
    """Limpa o cache de imagens (útil ao reiniciar jogo)."""
    global _CACHE_IMAGENS
    _CACHE_IMAGENS.clear()
