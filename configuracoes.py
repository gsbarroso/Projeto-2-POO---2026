import pygame
import os

# =====================================================================
# ARQUIVO: configuracoes.py (Sugestão de divisão futura)
# Objetivo: Guardar constantes globais do jogo.
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DINO_VARIANTS = [
    os.path.join(ASSETS_DIR, "Espadão.png"),
    os.path.join(ASSETS_DIR, "Motoserra.png"),
    os.path.join(ASSETS_DIR, "Shuriken.png"),
]
CACTO_IMAGE = os.path.join(ASSETS_DIR, "cacto.png")
PTERO_IMAGE = os.path.join(ASSETS_DIR, "pterodáctilo.png")
ARQUIVO_SAVE = 'save_dino.json'


def carregar_sprite(caminho, largura, altura):
    """Tenta carregar o sprite do arquivo; caso não exista, cria uma versão simples."""
    if os.path.exists(caminho):
        imagem = pygame.image.load(caminho).convert_alpha()
        largura_atual, altura_atual = imagem.get_size()
        escala = min(largura / largura_atual, altura / altura_atual)
        nova_largura = max(1, int(largura_atual * escala))
        nova_altura = max(1, int(altura_atual * escala))
        return pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))

    superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
    if caminho == CACTO_IMAGE:
        pygame.draw.rect(superficie, VERDE, (0, altura * 0.35, largura, altura * 0.65), border_radius=6)
        pygame.draw.rect(superficie, VERDE, (largura * 0.15, altura * 0.1, largura * 0.2, altura * 0.4), border_radius=4)
        pygame.draw.rect(superficie, VERDE, (largura * 0.55, altura * 0.15, largura * 0.2, altura * 0.35), border_radius=4)
    elif caminho == PTERO_IMAGE:
        pontos = [
            (0, altura * 0.5),
            (largura * 0.2, altura * 0.15),
            (largura * 0.4, altura * 0.4),
            (largura * 0.6, altura * 0.1),
            (largura, altura * 0.35),
            (largura * 0.85, altura * 0.65),
            (largura * 0.55, altura * 0.55),
            (largura * 0.35, altura * 0.85),
        ]
        pygame.draw.polygon(superficie, AZUL, pontos)
    else:
        pygame.draw.rect(superficie, VERDE, (0, altura * 0.25, largura, altura * 0.75), border_radius=8)
        pygame.draw.circle(superficie, PRETO, (largura // 2, altura // 3), largura // 8)

    return superficie
