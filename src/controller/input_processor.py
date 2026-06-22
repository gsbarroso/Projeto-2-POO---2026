import pygame
import logging
import sys
from src.utils.enums import EstadoJogo, TipoConsumivel

logger = logging.getLogger(__name__)


class InputProcessor:
    """Processador de entrada - lida com teclado e eventos."""
    
    def processar_eventos_menu(self, modelo) -> tuple:
        """
        Processa eventos no menu.
        
        Returns:
            (abaixar, deve_sair)
        """
        abaixar = False
        deve_sair = False
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                deve_sair = True
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    modelo.estado = EstadoJogo.JOGANDO
                elif evento.key == pygame.K_l:
                    modelo.estado = EstadoJogo.LOJA
        
        return abaixar, deve_sair
    
    def processar_eventos_loja(self, modelo) -> tuple:
        """Processa eventos na loja."""
        abaixar = False
        deve_sair = False
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                deve_sair = True
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    modelo.estado = EstadoJogo.MENU
                elif evento.key == pygame.K_UP:
                    modelo.menu_opcao = max(0, modelo.menu_opcao - 1)
                elif evento.key == pygame.K_DOWN:
                    total_opcoes = len(modelo.gerenciador_loja.PRECOS_DINOSSAURO) + len(TipoConsumivel)
                    modelo.menu_opcao = min(total_opcoes - 1, modelo.menu_opcao + 1)
                elif evento.key == pygame.K_RETURN:
                    modelo.comprar_item()
        
        return abaixar, deve_sair
    
    def processar_eventos_jogo(self, modelo) -> tuple:
        """
        Processa eventos durante o jogo.
        
        Returns:
            (abaixar, deve_sair)
        """
        keys = pygame.key.get_pressed()
        abaixar = keys[pygame.K_DOWN]
        deve_sair = False
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                deve_sair = True
            elif evento.type == pygame.KEYDOWN:
                # Pause/Unpause
                if evento.key == pygame.K_p:
                    modelo.estado = EstadoJogo.PAUSADO if modelo.estado == EstadoJogo.JOGANDO else EstadoJogo.JOGANDO
                
                # Apenas se estiver jogando (não pausado)
                if modelo.estado == EstadoJogo.JOGANDO:
                    if evento.key in [pygame.K_SPACE, pygame.K_UP]:
                        modelo.dino.pular()
                    elif evento.key == pygame.K_e:
                        modelo.usar_habilidade_especial()
                    elif evento.key == pygame.K_1:
                        modelo.usar_consumivel(TipoConsumivel.VIDA)
                    elif evento.key == pygame.K_2:
                        modelo.usar_consumivel(TipoConsumivel.VELOCIDADE)
                    elif evento.key == pygame.K_3:
                        modelo.usar_consumivel(TipoConsumivel.PULO)
        
        return abaixar, deve_sair
    
    def processar_eventos_game_over(self, modelo) -> tuple:
        """Processa eventos na tela de game over."""
        abaixar = False
        deve_sair = False
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                deve_sair = True
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    modelo.reiniciar_partida()
                    modelo.estado = EstadoJogo.JOGANDO
                elif evento.key == pygame.K_l:
                    modelo.estado = EstadoJogo.LOJA
                elif evento.key == pygame.K_m:
                    modelo.estado = EstadoJogo.MENU
        
        return abaixar, deve_sair
    
    def processar_eventos(self, modelo) -> tuple:
        """
        Processa eventos baseado no estado do jogo.
        
        Returns:
            (abaixar, deve_sair)
        """
        if modelo.estado == EstadoJogo.MENU:
            return self.processar_eventos_menu(modelo)
        elif modelo.estado == EstadoJogo.LOJA:
            return self.processar_eventos_loja(modelo)
        elif modelo.estado in [EstadoJogo.JOGANDO, EstadoJogo.PAUSADO]:
            return self.processar_eventos_jogo(modelo)
        elif modelo.estado == EstadoJogo.GAME_OVER:
            return self.processar_eventos_game_over(modelo)
        
        return False, False
