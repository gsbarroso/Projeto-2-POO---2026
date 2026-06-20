import pygame
import random
from abc import ABC, abstractmethod
from configuracoes import *

# =====================================================================
# ARQUIVO: entidades.py
# Objetivo: Conter os modelos (Entities) e a física (Dificuldade Aumentada).
# =====================================================================

class EntidadeDoJogo(ABC):
    """Classe abstrata base para todas as entidades do jogo.
    
    Define a interface comum para dinossauros, obstáculos e projéteis,
    garantindo que todas implementem método de atualização e suportem
    colisões pixel-perfect com máscara de transparência.
    """
    
    def __init__(self, x, y, image, cor):
        """Inicializa uma entidade com posição, imagem e cor.
        
        Args:
            x (int): Posição X inicial
            y (int): Posição Y inicial
            image (pygame.Surface): Imagem/sprite da entidade
            cor (tuple): Cor RGB para fallback se imagem falhar
        """
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self._cor = cor
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def x(self):
        """Getter para posição X do retângulo da entidade."""
        return self.rect.x
    
    @x.setter
    def x(self, valor):
        """Setter para posição X do retângulo da entidade."""
        self.rect.x = valor

    @property
    def y(self):
        """Getter para posição Y do retângulo da entidade."""
        return self.rect.y
    
    @y.setter
    def y(self, valor):
        """Setter para posição Y do retângulo da entidade."""
        self.rect.y = valor

    @abstractmethod
    def atualizar(self):
        """Método abstrato que deve ser implementado por todas as subclasses.
        
        Cada entidade define sua própria lógica de atualização (movimento, física, etc).
        
        Raises:
            NotImplementedError: Se a subclasse não implementar este método
        """
        pass

    def checar_colisao(self, outra_entidade):
        """Verifica colisão pixel-perfect entre duas entidades usando máscara de transparência.
        
        Utiliza dois níveis de validação:
        1. Colisão de retângulos com padding reduzido (mais permissivo para gameplay justo)
        2. Colisão pixel-perfect usando máscara de transparência (preciso)
        
        Args:
            outra_entidade (EntidadeDoJogo): Outra entidade para testar colisão
            
        Returns:
            bool: True se há colisão, False caso contrário
        """
        # NÍVEL 1: Hitbox com padding para não ser muito restritivo no modo Hardcore
        padding = 8  # pixels de tolerância (8px em cada lado)
        rect_reduzido_self = self.rect.inflate(-padding, -padding)
        rect_reduzido_outra = outra_entidade.rect.inflate(-padding, -padding)

        # Se os retângulos não se sobrepõem, não há colisão
        if not rect_reduzido_self.colliderect(rect_reduzido_outra):
            return False
        
        # NÍVEL 2: Colisão pixel-perfect usando máscara (área não-transparente da imagem)
        offset = (outra_entidade.x - self.x, outra_entidade.y - self.y)
        return self.mask.overlap(outra_entidade.mask, offset) is not None


class Dinossauro(EntidadeDoJogo):
    """Dinossauro jogável com mecânicas de pulo, agachamento e poderes especiais.
    
    O dinossauro é a entidade controlada pelo jogador. Suporta múltiplas variantes
    (clássico, espadão, motosserra, shuriken) cada uma com habilidades únicas.
    """
    
    def __init__(self, variante="classico"):
        """Inicializa dinossauro com variante e física.
        
        Args:
            variante (str): Tipo de dinossauro ('classico', 'espadao', 'motoserra', 'shuriken')
        """
        self.variante = variante
        dino_path = DINO_VARIANTS.get(variante, DINO_VARIANTS["classico"])
        
        # CARREGAMENTO: Dino em 240x240px - grande e proporcionado ao mapa 800x400
        self.image_base = carregar_sprite(
            dino_path,
            escala=0.043,
            largura_fallback=240,
            altura_fallback=240,
            max_largura=240,
            max_altura=240,
        )
        
        self.largura_original = self.image_base.get_width()
        self.altura_original = self.image_base.get_height()
        
        # POSICIONAMENTO: Chão está em ALTURA_TELA - 30 (linha de colisão visual)
        # Dino posiciona-se imediatamente acima deste ponto
        chao_y = ALTURA_TELA - 30 - self.altura_original
        super().__init__(50, chao_y, self.image_base, VERDE)
        
        # FÍSICA: Sistema de velocidade vertical para pulo e gravidade
        self.vel_y = 0
        self.gravidade = 1.6  # DIFICULDADE: Gravidade alta exige reflexos rápidos
        self.forca_pulo = -21  # Força inicial do pulo (negativo = para cima)
        self.chao_y = chao_y
        
        # ESTADO: Controle de movimento e colisões
        self.no_chao = True
        self._agachado = False
        self.vidas = 1
        self.velocidade_boost = 1.0  # Multiplicador de velocidade (consumível)
        self.pulo_boost = 1.0  # Multiplicador de altura de pulo (consumível)

    @property
    def is_agachado(self):
        """Getter que indica se o dinossauro está agachado."""
        return self._agachado

    def pular(self):
        """Realiza um pulo se o dinossauro está no chão.
        
        Aplica força inicial vertical (vel_y negativo) e marca como "no_chao=False"
        para que a gravidade atue no próximo frame.
        """
        if self.no_chao:
            self.vel_y = self.forca_pulo * self.pulo_boost
            self.no_chao = False

    def agachar(self):
        """Abaixa o dinossauro para evitar obstáculos ou acelera queda se em ar.
        
        Quando no chão: reduz altura para 50% e expande largura para 120% (mais baixo, mais largo)
        Quando em ar: acelera queda (4 px/frame) para rapidez tática
        """
        if not self._agachado and self.no_chao:
            # AGACHAMENTO: Reduz altura, aumenta largura, mantém proporções realistas
            self._agachado = True
            nova_altura = self.altura_original // 2
            nova_largura = int(self.largura_original * 1.2)
            
            self.image = pygame.transform.scale(self.image_base, (nova_largura, nova_altura))
            self.rect = self.image.get_rect(topleft=(self.x, ALTURA_TELA - 30 - nova_altura))
            self.mask = pygame.mask.from_surface(self.image)  # Atualiza máscara de colisão
            
        elif not self.no_chao:
            # QUEDA RÁPIDA: Força extra aplicada quando em ar (fast fall)
            self.vel_y += 4  # Fast fall bem agressivo (4px/frame extra)

    def levantar(self):
        """Levanta o dinossauro de volta à posição normal.
        
        Restaura imagem original e posição no chão (chao_y).
        Máscara de colisão é recalculada automaticamente.
        """
        if self._agachado:
            self._agachado = False
            self.image = self.image_base
            self.rect = self.image.get_rect(topleft=(self.x, self.chao_y))
            self.mask = pygame.mask.from_surface(self.image)

    def atualizar(self, input_abaixar=False):
        """Atualiza física e posição do dinossauro a cada frame.
        
        Processo:
        1. Processa entrada de agachamento (alto/baixo)
        2. Aplica gravidade à velocidade vertical
        3. Atualiza posição Y
        4. Valida limite do chão e reseta velocidade se pousar
        
        Args:
            input_abaixar (bool): True se jogador pressionou tecla DOWN
        """
        # ENTRADA: Processa agachamento ou levantamento
        if input_abaixar:
            self.agachar()
        else:
            self.levantar()

        # FÍSICA: Aplica gravidade à velocidade vertical
        self.vel_y += self.gravidade
        self.y += self.vel_y

        # COLISÃO CHÃO: Define limite baseado no estado (agachado ou não)
        limite_chao = self.chao_y if not self._agachado else (ALTURA_TELA - 30 - self.rect.height)

        # ATERRISSAGEM: Se passou do chão, volta e reseta velocidade
        if self.y >= limite_chao:
            self.y = limite_chao
            self.no_chao = True
            self.vel_y = 0  # Zera velocidade ao aterrissar


class Obstaculo(EntidadeDoJogo):
    """Classe abstrata para obstáculos (cactos, pterodáctilos) que se movem da direita para esquerda.
    
    Todos os obstáculos herdam movimento horizontal baseado em velocidade do jogo.
    """
    
    def __init__(self, x, y, imagem, cor, velocidade):
        """Inicializa um obstáculo com posição e velocidade.
        
        Args:
            x (int): Posição X inicial (sempre LARGURA_TELA para spawnar na direita)
            y (int): Posição Y inicial (chão ou altura variável)
            imagem (pygame.Surface): Sprite do obstáculo
            cor (tuple): Cor RGB para fallback
            velocidade (float): Velocidade de movimento horizontal (pixels/frame)
        """
        super().__init__(x, y, imagem, cor)
        self.velocidade = velocidade

    def atualizar(self):
        """Move o obstáculo para a esquerda a cada frame.
        
        A velocidade aumenta conforme a dificuldade sobe durante o jogo.
        """
        self.x -= self.velocidade  # Movimento: esquerda (x decresce)


class Cacto(Obstaculo):
    """Obstáculo cacto que spawna no chão com tamanho aleatório variado.
    
    Pode spawnar em grupos (até 3 juntos) com offset horizontal para criar padrões.
    Tamanho varia para aumentar dificuldade visual (alguns cactos maiores, outros menores).
    """
    
    def __init__(self, velocidade, offset_x=0):
        """Inicializa um cacto com tamanho aleatório.
        
        Args:
            velocidade (float): Velocidade de movimento (aumenta com dificuldade)
            offset_x (int): Offset horizontal se spawnar em grupo (padrão: 0)
        """
        # VARIAÇÃO: Cactos de tamanhos variados (72-101px) para aumentar dificuldade visual
        # Escala aleatória entre 0.035 e 0.05 = 3.5% a 5% da imagem original (5541x5541)
        escala_random = random.uniform(0.035, 0.05)
        imagem_cacto = carregar_sprite(
            CACTO_IMAGE,
            escala=escala_random,
            largura_fallback=200,
            altura_fallback=240,
            max_largura=240,
            max_altura=240,
        )
        
        # POSICIONAMENTO: Cacto no chão, com margem de 40px do limite visual
        h = imagem_cacto.get_height()
        y = ALTURA_TELA - h - 40
        super().__init__(LARGURA_TELA + offset_x, y, imagem_cacto, VERMELHO, velocidade)


class Pterodactilo(Obstaculo):
    """Obstáculo pterodáctilo voador que patrulha em 3 alturas diferentes.
    
    Mais rápido que cactos (1.35x velocidade), voa em padrão oscilatório (up/down).
    Pode spawnar em 3 alturas diferentes: baixa, média e alta.
    """
    
    def __init__(self, velocidade):
        """Inicializa pterodáctilo em altura aleatória com padrão de voo.
        
        Args:
            velocidade (float): Velocidade base (será multiplicada por 1.35)
        """
        # CARREGAMENTO: Pterodáctilo em ~139-140px (proporcional ao mapa)
        imagem_ptero = carregar_sprite(
            PTERO_IMAGE,
            escala=0.042,
            largura_fallback=230,
            altura_fallback=230,
            max_largura=240,
            max_altura=240,
        )
        h = imagem_ptero.get_height()
        
        # ALTURAS: Pterodáctilo spawna em 3 níveis para variar dificuldade
        # Cálculo: linha_chao(370) - altura_sprite - offset_altura
        alturas = [
            ALTURA_TELA - 30 - h - 20,    # BAIXA: próximo ao chão (evitar pulos normais)
            ALTURA_TELA - 30 - h - 60,    # MÉDIA: altura media (exige pulos altos)
            ALTURA_TELA - 30 - h - 100    # ALTA: próximo ao topo (exige agachamento)
        ]
        y = random.choice(alturas)
        
        # MOVIMENTO: Pterodáctilos são 1.35x mais rápidos que cactos
        super().__init__(LARGURA_TELA, y, imagem_ptero, AZUL, velocidade * 1.35)
        self.flap = 0  # Contador para oscilação de voo

    def atualizar(self):
        """Atualiza posição com movimento horizontal + oscilação vertical de voo.
        
        Padrão de voo: oscila ±2 pixels a cada 7 frames (período de 14 frames total).
        """
        # MOVIMENTO HORIZONTAL: Chama método pai (movimento para esquerda)
        super().atualizar()
        
        # MOVIMENTO VERTICAL: Oscila para simular batida de asas
        self.flap += 1
        if self.flap % 14 < 7:
            self.y -= 2  # Primeira metade: voa para cima
        else:
            self.y += 2  # Segunda metade: voa para baixo


class Projetil(EntidadeDoJogo):
    """Projétil disparado pelo dinossauro variante 'shuriken'.
    
    Move-se horizontalmente para a direita com velocidade fixa (20px/frame).
    Desaparece quando sai da tela ou atinge um obstáculo.
    """
    
    def __init__(self, x, y):
        """Inicializa projétil na posição do dino.
        
        Args:
            x (int): Posição X inicial (geralmente rect.right do dino)
            y (int): Posição Y inicial (geralmente rect.centery do dino)
        """
        # CARREGAMENTO: Projétil pequeno (~20-30px)
        img_projetil = carregar_sprite(
            PROJETIL_IMAGE,
            escala=0.08,
            largura_fallback=20,
            altura_fallback=20,
            max_largura=30,
            max_altura=30,
        )
        super().__init__(x, y, img_projetil, AMARELO)
        self.velocidade = 20  # Velocidade fixa muito rápida (20px/frame)

    def atualizar(self):
        """Move o projétil para a direita (em direção aos obstáculos).
        
        Controle: Controller remove projétil quando sai da tela ou acerta algo.
        """
        self.x += self.velocidade  # Movimento: direita (x aumenta)