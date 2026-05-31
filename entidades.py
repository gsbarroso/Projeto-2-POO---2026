import pygame
import random
from abc import ABC, abstractmethod
from configuracoes import *
# =====================================================================
# ARQUIVO: entidades.py (Sugestão de divisão futura)
# Objetivo: Conter todas as classes do jogo (Abstratas, Heranças, etc)
# =====================================================================

# 1. CLASSE ABSTRATA
class EntidadeDoJogo(ABC):
    def __init__(self, x, y, largura, altura, cor):
        # A hitbox principal no Pygame é o Rect
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
        self.hitbox = self.rect.copy()

    def atualizar_hitbox(self):
        self.hitbox.topleft = self.rect.topleft

    @abstractmethod
    def atualizar(self):
        """Método que deve ser implementado por todas as subclasses para lógica de movimento"""
        pass

    @abstractmethod
    def desenhar(self, tela):
        """Método que deve ser implementado para renderizar o objeto"""
        pass

    def checar_colisao(self, outra_entidade):
        return self.hitbox.colliderect(outra_entidade.hitbox)

# 2. CLASSE DO JOGADOR
class Dinossauro(EntidadeDoJogo):
    def __init__(self):
        self.image = carregar_sprite(random.choice(DINO_VARIANTS), 160, 160)
        largura, altura = self.image.get_size()
        chao_y = ALTURA_TELA - altura - 30
        super().__init__(50, chao_y, largura, altura, VERDE)
        self.rect = self.image.get_rect(topleft=(50, chao_y))
        self.hitbox = self.rect.inflate(-32, -32)
        self.vel_y = 0
        self.gravidade = 0.8
        self.forca_pulo = -15
        self.chao_y = chao_y
        self.no_chao = True

    def pular(self):
        if self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):
        # Aplica a gravidade
        self.vel_y += self.gravidade
        self.rect.y += self.vel_y

        # Colisão com o chão
        if self.rect.y >= self.chao_y:
            self.rect.y = self.chao_y
            self.no_chao = True
            self.vel_y = 0

        self.atualizar_hitbox()

    def desenhar(self, tela):
        if self.image:
            tela.blit(self.image, self.rect)
        else:
            pygame.draw.rect(tela, self.cor, self.rect)

# 3. HERANÇA E POLIMORFISMO: OBSTÁCULOS
class Obstaculo(EntidadeDoJogo):
    def __init__(self, x, y, largura, altura, cor, velocidade):
        super().__init__(x, y, largura, altura, cor)
        self.velocidade = velocidade

    def atualizar(self):
        # Movimento padrão para a esquerda
        self.rect.x -= self.velocidade
        self.atualizar_hitbox()

    def desenhar(self, tela):
        if hasattr(self, 'image') and self.image:
            tela.blit(self.image, self.rect)
        else:
            pygame.draw.rect(tela, self.cor, self.rect)

class Cacto(Obstaculo):
    def __init__(self, velocidade):
        self.image = carregar_sprite(CACTO_IMAGE, 90, 150)
        largura, altura = self.image.get_size()
        y = ALTURA_TELA - altura - 30
        super().__init__(LARGURA_TELA, y, largura, altura, VERMELHO, velocidade)
        self.rect = self.image.get_rect(topleft=(LARGURA_TELA, y))
        self.hitbox = self.rect.inflate(-16, -24)

class Pterodactilo(Obstaculo):
    def __init__(self, velocidade):
        self.image = carregar_sprite(PTERO_IMAGE, 180, 120)
        largura, altura = self.image.get_size()
        y = random.choice([ALTURA_TELA - 130, ALTURA_TELA - 170])
        super().__init__(LARGURA_TELA, y, largura, altura, AZUL, velocidade)
        self.rect = self.image.get_rect(topleft=(LARGURA_TELA, y))
        self.hitbox = self.rect.inflate(-32, -20)
        self.direcao_y = 1

    def atualizar(self):
        # POLIMORFISMO: Além de ir para a esquerda, oscila no eixo Y (voo)
        super().atualizar() # Chama o movimento para a esquerda da classe Pai
        self.rect.y += self.direcao_y
        if self.rect.y % 40 == 0: # Inverte a direção a cada 40 pixels
            self.direcao_y *= -1