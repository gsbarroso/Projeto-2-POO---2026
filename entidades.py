import pygame
import random
from abc import ABC, abstractmethod
from configuracoes import *

# =====================================================================
# ARQUIVO: entidades.py
# Objetivo: Modelos (Entities), garantindo POO e padronização.
# =====================================================================

class EntidadeDoJogo(ABC):
    def __init__(self, x, y, image, cor):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self._cor = cor
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def x(self): return self.rect.x
    @x.setter
    def x(self, valor): self.rect.x = valor

    @property
    def y(self): return self.rect.y
    @y.setter
    def y(self, valor): self.rect.y = valor

    def obter_altura_visual(self):
        """Retorna a altura real em pixels ignorando a transparência inferior da imagem."""
        bbox = self.mask.get_bounding_rects()
        if bbox:
            return max(r.bottom for r in bbox)
        return self.rect.height

    @abstractmethod
    def atualizar(self):
        """Método padrão obrigatório para toda entidade."""
        pass

    def checar_colisao(self, outra_entidade):
        padding = 8
        rect_reduzido_self = self.rect.inflate(-padding, -padding)
        rect_reduzido_outra = outra_entidade.rect.inflate(-padding, -padding)

        if not rect_reduzido_self.colliderect(rect_reduzido_outra):
            return False
        
        offset = (outra_entidade.x - self.x, outra_entidade.y - self.y)
        return self.mask.overlap(outra_entidade.mask, offset) is not None


class Dinossauro(EntidadeDoJogo):
    def __init__(self, variante="classico"):
        self.variante = variante
        dino_path = DINO_VARIANTS.get(variante, DINO_VARIANTS["classico"])
        
        self.image_base = carregar_sprite(dino_path, escala=0.043, largura_fallback=240, altura_fallback=240, max_largura=240, max_altura=240)
        self.largura_original = self.image_base.get_width()
        self.altura_original = self.image_base.get_height()
        
        # Inicia temporariamente com y=0 para podermos processar a máscara visual
        super().__init__(50, 0, self.image_base, VERDE)
        
        # Alinhamento perfeito do dino
        self.altura_visual_base = self.obter_altura_visual()
        self.chao_y = LINHA_CHAO - self.altura_visual_base
        self.y = self.chao_y  # Seta a posição Y definitiva
        
        self.vel_y = 0
        self.gravidade = 1.6
        self.forca_pulo = -21
        
        self.no_chao = True
        self._agachado = False
        self.vidas = 1
        self.velocidade_boost = 1.0
        self.pulo_boost = 1.0

    @property
    def is_agachado(self):
        return self._agachado

    def processar_entrada(self, input_abaixar):
        """Responsável apenas por reagir aos inputs (Separation of Concerns)."""
        if input_abaixar:
            self.agachar()
        else:
            self.levantar()

    def pular(self):
        if self.no_chao:
            self.vel_y = self.forca_pulo * self.pulo_boost
            self.no_chao = False

    def agachar(self):
        if not self._agachado and self.no_chao:
            self._agachado = True
            nova_altura = self.altura_original // 2
            nova_largura = int(self.largura_original * 1.2)
            
            self.image = pygame.transform.scale(self.image_base, (nova_largura, nova_altura))
            self.mask = pygame.mask.from_surface(self.image)
            
            # Re-alinha ao agachar para não flutuar nem afundar
            altura_visual_agachado = self.obter_altura_visual()
            self.rect = self.image.get_rect(topleft=(self.x, LINHA_CHAO - altura_visual_agachado))
            
        elif not self.no_chao:
            self.vel_y += 4

    def levantar(self):
        if self._agachado:
            self._agachado = False
            self.image = self.image_base
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect(topleft=(self.x, self.chao_y))

    def atualizar(self):
        """Responsável apenas por atualizar a física (respeitando Polimorfismo e LSP)."""
        self.vel_y += self.gravidade
        self.y += self.vel_y

        limite_chao = self.chao_y if not self._agachado else (LINHA_CHAO - self.obter_altura_visual())

        if self.y >= limite_chao:
            self.y = limite_chao
            self.no_chao = True
            self.vel_y = 0


class Obstaculo(EntidadeDoJogo):
    def __init__(self, x, y, imagem, cor, velocidade):
        super().__init__(x, y, imagem, cor)
        self.velocidade = velocidade

    def atualizar(self):
        self.x -= self.velocidade


class Cacto(Obstaculo):
    def __init__(self, velocidade, offset_x=0):
        escala_random = random.choice([0.035, 0.040, 0.045, 0.050])
        imagem_cacto = carregar_sprite(CACTO_IMAGE, escala=escala_random, largura_fallback=200, altura_fallback=240, max_largura=240, max_altura=240)
        
        super().__init__(LARGURA_TELA + offset_x, 0, imagem_cacto, VERMELHO, velocidade)
        
        # POO Correta: A própria entidade ajusta seus pés exatamente na linha
        self.y = LINHA_CHAO - self.obter_altura_visual()


class Pterodactilo(Obstaculo):
    def __init__(self, velocidade):
        imagem_ptero = carregar_sprite(PTERO_IMAGE, escala=0.042, largura_fallback=230, altura_fallback=230, max_largura=240, max_altura=240)
        
        super().__init__(LARGURA_TELA, 0, imagem_ptero, AZUL, velocidade * 1.35)
        
        # Alinha as patrulhas relativas ao visual real do pássaro
        h_visual = self.obter_altura_visual()
        alturas = [
            LINHA_CHAO - h_visual - 20,
            LINHA_CHAO - h_visual - 60,
            LINHA_CHAO - h_visual - 100
        ]
        self.y = random.choice(alturas)
        self.flap = 0

    def atualizar(self):
        super().atualizar()
        self.flap += 1
        if self.flap % 14 < 7:
            self.y -= 2
        else:
            self.y += 2


class Projetil(EntidadeDoJogo):
    def __init__(self, x, y):
        img_projetil = carregar_sprite(PROJETIL_IMAGE, escala=0.08, largura_fallback=20, altura_fallback=20, max_largura=30, max_altura=30)
        super().__init__(x, y, img_projetil, AMARELO)
        self.velocidade = 20

    def atualizar(self):
        self.x += self.velocidade