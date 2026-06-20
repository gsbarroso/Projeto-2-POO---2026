import pygame
import os

# =====================================================================
# ARQUIVO: configuracoes.py
# Objetivo: Constantes globais e carregamento seguro de assets.
# =====================================================================
LARGURA_TELA = 800
ALTURA_TELA = 400
FPS = 60

# Cores (RGB)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (0, 0, 200)
AMARELO = (255, 215, 0)
CINZA_ESCURO = (44, 62, 80)
CINZA_CLARO = (236, 240, 241)

# GARANTIA DE CAMINHO ABSOLUTO (Resolve o bug de não achar as imagens)
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

def carregar_sprite(caminho, escala=1.0, largura_fallback=50, altura_fallback=50, max_largura=None, max_altura=None):
    """Carrega imagem de sprite do disco com segurança e limites de tamanho.
    
    Processo:
    1. Verifica se arquivo existe no caminho especificado
    2. Carrega imagem com transparência (convert_alpha)
    3. Aplica escala se fornecida
    4. Impõe limites máximos para evitar sprites gigantes
    5. Fallback: retorna retângulo vermelho se falhar
    
    Args:
        caminho (str): Caminho absoluto para arquivo PNG
        escala (float): Multiplicador de tamanho (padrão: 1.0)
        largura_fallback (int): Largura do retângulo fallback em pixels
        altura_fallback (int): Altura do retângulo fallback em pixels
        max_largura (int): Limite máximo de largura (None = auto)
        max_altura (int): Limite máximo de altura (None = auto)
        
    Returns:
        pygame.Surface: Superfície com imagem carregada ou fallback
        
    Raises:
        Exception: Capturada internamente e registrada em [ERRO]
    """
    if os.path.exists(caminho):
        try:
            # CARREGAMENTO: Abre PNG com suporte a transparência
            imagem = pygame.image.load(caminho).convert_alpha()

            # ESCALA: Aplica multiplicador se fornecido
            if escala != 1.0:
                nova_largura = max(1, int(imagem.get_width() * escala))
                nova_altura = max(1, int(imagem.get_height() * escala))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            # LIMITES: Usa parâmetros passados, ou fallback como base
            if max_largura is None:
                max_largura = max(largura_fallback * 4, 100)
            if max_altura is None:
                max_altura = max(altura_fallback * 4, 100)
            
            # ENFORÇA LIMITES: Se imagem ultrapassar, redimensiona mantendo proporção
            if imagem.get_width() > max_largura or imagem.get_height() > max_altura:
                fator = min(max_largura / imagem.get_width(), max_altura / imagem.get_height())
                nova_largura = max(1, int(imagem.get_width() * fator))
                nova_altura = max(1, int(imagem.get_height() * fator))
                imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

            # DEBUG: Registra carregamento bem-sucedido
            try:
                print(f"[INFO] Sprite carregado: '{caminho}' tamanho {imagem.get_width()}x{imagem.get_height()}")
            except Exception:
                print(f"[INFO] Sprite carregado: '{caminho}'")
            return imagem
        except Exception as e:
            # ERRO: Registra falha ao processar imagem
            print(f"[ERRO] Falha ao processar a imagem '{caminho}': {e}")
    else:
        # AVISO: Arquivo não encontrado no disco
        print(f"[AVISO] Imagem não encontrada: '{caminho}'. Verifique o nome e a pasta assets.")

    # FALLBACK: Retorna retângulo vermelho como placeholder
    superficie = pygame.Surface((largura_fallback, altura_fallback), pygame.SRCALPHA)
    pygame.draw.rect(superficie, VERMELHO, (0, 0, largura_fallback, altura_fallback), border_radius=4)
    return superficie