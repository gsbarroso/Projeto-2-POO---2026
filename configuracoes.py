import pygame
import os

# =====================================================================
# ARQUIVO: configuracoes.py
# Objetivo: Constantes globais, balanceamento de física e cache de assets.
# =====================================================================

# Configurações de Tela
LARGURA_TELA = 800
ALTURA_TELA = 400
FPS = 60

# =====================================================================
# GAMEPLAY E FÍSICA (Remoção de Magic Numbers)
# =====================================================================
LINHA_CHAO = ALTURA_TELA - 30
GRAVIDADE = 1.6
FORCA_PULO = -21
QUEDA_AGACHADO = 4
VELOCIDADE_BASE_JOGO = 8.0
INCREMENTO_VELOCIDADE = 1.2
PONTOS_PARA_ACELERAR = 350
TEMPO_RECARGA_ESPECIAL = 250
VELOCIDADE_PROJETIL = 20

# Offsets ajustados: 15 (força pular) e 50 (força agachar)
# Removemos a altura de 100 para que o jogador nunca possa "passar direto"
ALTURAS_PTERO = [15, 50]  

# Cores (RGB)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (0, 0, 200)
AMARELO = (255, 215, 0)
CINZA_ESCURO = (44, 62, 80)
CINZA_CLARO = (236, 240, 241)

# Caminhos Absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DINO_VARIANTS = {
    "classico": os.path.join(ASSETS_DIR, "Classico.png"),
    "espadao": os.path.join(ASSETS_DIR, "Espadão.png"),
    "motoserra": os.path.join(ASSETS_DIR, "Motoserra.png"),
    "shuriken": os.path.join(ASSETS_DIR, "Shuriken.png"),
}
PROJETIL_IMAGE = os.path.join(ASSETS_DIR, "Projetil.png")
CACTO_IMAGE = os.path.join(ASSETS_DIR, "Cacto.png")
PTERO_IMAGE = os.path.join(ASSETS_DIR, "Pterodáctilo.png")
ARQUIVO_SAVE = os.path.join(BASE_DIR, 'save_dino.json')

# =====================================================================
# CACHE DE IMAGENS
# =====================================================================
_CACHE_IMAGENS = {}

def carregar_sprite(caminho, escala=1.0, largura_fallback=50, altura_fallback=50, max_largura=None, max_altura=None):
    """Carrega imagem de sprite com sistema de cache para evitar lag I/O."""
    chave_cache = (caminho, escala, max_largura, max_altura)
    
    if chave_cache in _CACHE_IMAGENS:
        return _CACHE_IMAGENS[chave_cache]
        
    if os.path.exists(caminho):
        try:
            imagem = pygame.image.load(caminho).convert_alpha()

            if escala != 1.0:
                nova_largura = max(1, int(imagem.get_width() * escala))
                nova_altura = max(1, int(imagem.get_height() * escala))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            if max_largura is None: max_largura = max(largura_fallback * 4, 100)
            if max_altura is None: max_altura = max(altura_fallback * 4, 100)
            
            if imagem.get_width() > max_largura or imagem.get_height() > max_altura:
                fator = min(max_largura / imagem.get_width(), max_altura / imagem.get_height())
                nova_largura = max(1, int(imagem.get_width() * fator))
                nova_altura = max(1, int(imagem.get_height() * fator))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            _CACHE_IMAGENS[chave_cache] = imagem
            return imagem
        except Exception as e:
            print(f"[ERRO] Falha ao processar a imagem '{caminho}': {e}")
    else:
        print(f"[AVISO] Imagem não encontrada: '{caminho}'.")

    # Fallback
    superficie = pygame.Surface((largura_fallback, altura_fallback), pygame.SRCALPHA)
    pygame.draw.rect(superficie, VERMELHO, (0, 0, largura_fallback, altura_fallback), border_radius=4)
    _CACHE_IMAGENS[chave_cache] = superficie
    return superficie