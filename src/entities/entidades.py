import pygame
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Optional

from src.config import configuracoes as cfg

logger = logging.getLogger(__name__)

class Entidade(ABC):
    """Interface base para todas as entidades do jogo."""
    
    @abstractmethod
    def atualizar(self) -> None:
        """Atualiza o estado da entidade a cada frame."""
        pass


class Colidivel(ABC):
    """Interface para entidades que podem colidir."""
    
    @abstractmethod
    def checar_colisao(self, outra: 'Colidivel') -> bool:
        """Verifica colisão com outra entidade."""
        pass


class PossuiVisual(ABC):
    """Interface para entidades que possuem representação visual."""
    
    @abstractmethod
    def obter_altura_visual(self) -> int:
        """Retorna a altura real em pixels ignorando transparência."""
        pass


class EntidadeDoJogo(Entidade, Colidivel, PossuiVisual):
    """Classe base para entidades do jogo com física e colisão."""
    
    def __init__(self, x: float, y: float, image: pygame.Surface, cor: Tuple[int, int, int]):
        """
        Inicializa uma entidade.
        
        Args:
            x: Posição X inicial
            y: Posição Y inicial
            image: Imagem da entidade
            cor: Cor RGB para debugging
        """
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self._cor = cor
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def x(self) -> float:
        """Posição X da entidade."""
        return self.rect.x
    
    @x.setter
    def x(self, valor: float) -> None:
        """Define a posição X."""
        self.rect.x = valor

    @property
    def y(self) -> float:
        """Posição Y da entidade."""
        return self.rect.y
    
    @y.setter
    def y(self, valor: float) -> None:
        """Define a posição Y."""
        self.rect.y = valor

    def obter_altura_visual(self) -> int:
        """Retorna a altura real em pixels ignorando a transparência inferior."""
        bbox = self.mask.get_bounding_rects()
        if bbox:
            return max(r.bottom for r in bbox)
        return self.rect.height

    @abstractmethod
    def atualizar(self) -> None:
        """Atualiza o estado da entidade."""
        pass

    def checar_colisao(self, outra_entidade: 'EntidadeDoJogo') -> bool:
        """
        Verifica colisão com outra entidade usando máscara de pixel.
        
        Args:
            outra_entidade: Outra entidade para verificar colisão
        
        Returns:
            True se houver colisão, False caso contrário
        """
        padding = cfg.PADDING_COLISAO
        rect_reduzido_self = self.rect.inflate(-padding, -padding)
        rect_reduzido_outra = outra_entidade.rect.inflate(-padding, -padding)

        if not rect_reduzido_self.colliderect(rect_reduzido_outra):
            return False
        
        offset = (outra_entidade.x - self.x, outra_entidade.y - self.y)
        return self.mask.overlap(outra_entidade.mask, offset) is not None


class Dinossauro(EntidadeDoJogo):
    def __init__(self, variante="classico"):
        self.variante = variante
        dino_path = cfg.DINO_VARIANTS.get(variante, cfg.DINO_VARIANTS["classico"])
        
        self.image_base = cfg.carregar_sprite(dino_path, escala=0.043, largura_fallback=240, altura_fallback=240, max_largura=240, max_altura=240)
        self.largura_original = self.image_base.get_width()
        self.altura_original = self.image_base.get_height()
        
        super().__init__(50, 0, self.image_base, cfg.VERDE)
        
        # Calcula quantos pixels de espaço vazio (transparente) existem na base da imagem
        self.padding_inferior = self.rect.height - self.obter_altura_visual()
        
        # Empurra o limite do chão para baixo na proporção exata da transparência
        self.chao_bottom = cfg.LINHA_CHAO + self.padding_inferior
        self.rect.bottom = self.chao_bottom
        
        self.vel_y = 0
        self.gravidade = cfg.GRAVIDADE
        self.forca_pulo = cfg.FORCA_PULO
        
        self.no_chao = True
        self._agachado = False
        self.vidas = 1
        self.velocidade_boost = 1.0
        self.pulo_boost = 1.0

    @property
    def is_agachado(self):
        return self._agachado

    def processar_entrada(self, input_abaixar):
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
            
            # Recalcula o espaço vazio para a nova imagem amassada
            self.padding_inferior = self.image.get_height() - self.obter_altura_visual()
            self.chao_bottom = cfg.LINHA_CHAO + self.padding_inferior
            self.rect = self.image.get_rect(bottomleft=(50, self.chao_bottom))
            
        elif not self.no_chao:
            self.vel_y += cfg.QUEDA_AGACHADO

    def levantar(self):
        if self._agachado:
            self._agachado = False
            self.image = self.image_base
            self.mask = pygame.mask.from_surface(self.image)
            
            # Restaura o espaço vazio da imagem original
            self.padding_inferior = self.image.get_height() - self.obter_altura_visual()
            self.chao_bottom = cfg.LINHA_CHAO + self.padding_inferior
            self.rect = self.image.get_rect(bottomleft=(50, self.chao_bottom))

    def atualizar(self):
        if not self.no_chao:
            self.vel_y += self.gravidade
            self.rect.y += int(self.vel_y)

            # Usa o limite calculado para parar a queda
            if self.rect.bottom >= self.chao_bottom:
                self.rect.bottom = self.chao_bottom
                self.no_chao = True
                self.vel_y = 0


Obstaculo = EntidadeDoJogo


class Cacto(Obstaculo):
    def __init__(self, velocidade, offset_x=0):
        self.velocidade = velocidade
        import random
        escala_random = random.choice([0.035, 0.040, 0.045, 0.050])
        imagem_cacto = cfg.carregar_sprite(cfg.CACTO_IMAGE, escala=escala_random, largura_fallback=200, altura_fallback=240, max_largura=240, max_altura=240)
        
        super().__init__(cfg.LARGURA_TELA + offset_x, 0, imagem_cacto, cfg.VERMELHO)
        
        # Desconta a transparência para os pixels VISÍVEIS grudarem no chão
        padding_inferior = self.rect.height - self.obter_altura_visual()
        self.rect.bottom = cfg.LINHA_CHAO + padding_inferior
        self.mask = pygame.mask.from_surface(self.image)

    def atualizar(self) -> None:
        self.rect.x -= int(self.velocidade)


class Pterodactilo(Obstaculo):
    def __init__(self, velocidade: float = 8.0):
        self.velocidade = velocidade
        
        caminho_ptero = cfg.ASSETS_DIR / "Pterodactilo.png"
        imagem = cfg.carregar_sprite(str(caminho_ptero), escala=0.045,
                                    largura_fallback=120, altura_fallback=80)
        
        super().__init__(cfg.LARGURA_TELA, 0, imagem, cfg.AZUL)
        
        import random
        altura_idx = random.randint(0, len(cfg.ALTURAS_PTERO) - 1)
        offset_y = cfg.ALTURAS_PTERO[altura_idx]
        
        # Desconta a transparência para ele voar na altura milimetricamente correta
        padding_inferior = self.rect.height - self.obter_altura_visual()
        self.rect.bottom = offset_y + padding_inferior
        self.mask = pygame.mask.from_surface(self.image)

    def atualizar(self) -> None:
        self.rect.x -= int(self.velocidade)

class Projetil(EntidadeDoJogo):
    """Projetil lançado pelo dinossauro shuriken."""
    
    def __init__(self, x: float, y: float):
        """
        Inicializa um projetil.
        
        Args:
            x: Posição X inicial
            y: Posição Y inicial
        """
        caminho_proj = cfg.ASSETS_DIR / "Shuriken_proj.png"
        imagem = cfg.carregar_sprite(str(caminho_proj), escala=0.03,
                                    largura_fallback=50, altura_fallback=50)
        
        super().__init__(x, y, imagem, cfg.AMARELO)
        self.velocidade = cfg.VELOCIDADE_PROJETIL

    def atualizar(self) -> None:
        """Atualiza posição do projetil (movimento para direita)."""
        self.x += self.velocidade
