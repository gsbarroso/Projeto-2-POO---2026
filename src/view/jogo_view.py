import pygame
import logging
from typing import TYPE_CHECKING
from src.utils.enums import EstadoJogo
from src.config import configuracoes as cfg

if TYPE_CHECKING:
    from src.model.jogo_model import JogoModel

logger = logging.getLogger(__name__)


class JogoView:
    """View do jogo - renderiza apenas, sem lógica."""
    
    def __init__(self, tela: pygame.Surface):
        """
        Inicializa a view.
        
        Args:
            tela: Surface do Pygame para renderização
        """
        self.tela = tela
        pygame.font.init()
        self.fonte_grande = pygame.font.SysFont("courier", 48, bold=True)
        self.fonte = pygame.font.SysFont("courier", 24, bold=True)
        self.fonte_peq = pygame.font.SysFont("courier", 16, bold=True)

    def renderizar(self, modelo: 'JogoModel') -> None:
        """
        Renderiza o jogo baseado no estado do modelo.
        
        Args:
            modelo: Modelo do jogo
        """
        is_night = (modelo.estado in [EstadoJogo.JOGANDO, EstadoJogo.GAME_OVER, EstadoJogo.PAUSADO]) \
                   and ((modelo.pontuacao // 600) % 2 != 0)
        bg_cor = cfg.CINZA_ESCURO if is_night else cfg.BRANCO
        txt_cor = cfg.CINZA_CLARO if is_night else cfg.PRETO

        self.tela.fill(bg_cor)

        if modelo.estado == EstadoJogo.MENU:
            self._renderizar_menu(modelo, txt_cor)
        elif modelo.estado == EstadoJogo.LOJA:
            self._renderizar_loja(modelo, txt_cor)
        elif modelo.estado in [EstadoJogo.JOGANDO, EstadoJogo.GAME_OVER, EstadoJogo.PAUSADO]:
            self._renderizar_jogo(modelo, txt_cor)

        pygame.display.flip()

    def _renderizar_menu(self, modelo: 'JogoModel', cor: tuple) -> None:
        """Renderiza tela de menu."""
        self._render_texto("DINO RUN MVC: EVOLUTION", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2 - 60, 
                          cor, self.fonte_grande, center=True)
        self._render_texto("Pressione [ESPAÇO] para Iniciar", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2, 
                          cfg.VERDE, self.fonte, center=True)
        self._render_texto(f"Moedas: {modelo.obter_moedas()}", 20, 20, cfg.AMARELO, self.fonte)
        self._render_texto("Pressione 'L' para Loja", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA - 50, 
                          cor, self.fonte, center=True)

    def _renderizar_loja(self, modelo: 'JogoModel', cor: tuple) -> None:
        """Renderiza tela de loja."""
        self._render_texto("=== LOJA ===", cfg.LARGURA_TELA//2, 20, cor, self.fonte_grande, center=True)
        self._render_texto(f"Moedas: {modelo.obter_moedas()}", 20, 20, cfg.AMARELO, self.fonte)
        
        if modelo.mensagem_erro:
            self._render_texto(f"⚠ {modelo.mensagem_erro}", 20, 60, cfg.VERMELHO, self.fonte_peq)

        y = 100
        precos = modelo.gerenciador_loja.PRECOS_DINOSSAURO
        for idx, (dino, preco) in enumerate(precos.items()):
            # Se já possui o dino mostra '✓', senão mostra o preço
            status = "✓" if modelo.gerenciador_loja.dinossauro_desbloqueado(dino) else f"${preco}"
            
            if modelo.obter_dino_selecionado() == dino.value:
                status = "[EQUIPADO]"
                
            cor_item = cfg.VERDE if idx == modelo.menu_opcao else cor
            self._render_texto(f"{'▶' if idx == modelo.menu_opcao else ' '} {dino.value.upper()}: {status}", 
                             50, y, cor_item, self.fonte)
            y += 30
        
        y += 20
        self._render_texto("- CONSUMÍVEIS -", 50, y, cor, self.fonte)
        y += 30
        
        from src.utils.enums import TipoConsumivel
        for idx, tipo in enumerate(TipoConsumivel):
            qtd = modelo.gerenciador_consumivel.obter_quantidade(tipo)
            preco = modelo.gerenciador_consumivel.PRECOS_CONSUMIVEL[tipo]
            nomes = modelo.gerenciador_consumivel.NOMES_CONSUMIVEL[tipo]
            global_idx = idx + len(precos)
            cor_item = cfg.VERDE if global_idx == modelo.menu_opcao else cor
            
            #${preco} na string do texto
            self._render_texto(f"{'▶' if global_idx == modelo.menu_opcao else ' '} {nomes} (${preco}) - Possui: {qtd}", 
                             50, y, cor_item, self.fonte)
            y += 30

    def _renderizar_jogo(self, modelo: 'JogoModel', cor: tuple) -> None:
        """Renderiza tela de jogo."""
        pygame.draw.line(self.tela, cor, (0, cfg.LINHA_CHAO - 4), (cfg.LARGURA_TELA, cfg.LINHA_CHAO - 4), 2)
        
        # Renderiza entidades
        if modelo.dino.image:
            self.tela.blit(modelo.dino.image, modelo.dino.rect)
        for obs in modelo.obstaculos:
            if hasattr(obs, 'image') and obs.image:
                self.tela.blit(obs.image, obs.rect)
        if modelo.projetil:
            self.tela.blit(modelo.projetil.image, modelo.projetil.rect)
        
        # HUD
        self._render_texto(f"Pontos: {modelo.obter_pontos()}", cfg.LARGURA_TELA - 200, 20, cor, self.fonte)
        self._render_texto(f"Moedas: {modelo.moedas_rodada}", cfg.LARGURA_TELA - 200, 50, cfg.AMARELO, self.fonte)
        self._render_texto(f"Vidas: {modelo.dino.vidas}", 20, 20, cfg.VERMELHO, self.fonte)
        
        # Habilidade especial
        if modelo.dino.variante != "classico":
            porcentagem = min(100, (modelo.ability_timer / cfg.TEMPO_RECARGA_ESPECIAL) * 100)
            especial_txt = "Pronto (E)" if modelo.ability_ready else f"{porcentagem:.0f}%"
            self._render_texto(f"Especial: {especial_txt}", 20, 50, cfg.AZUL, self.fonte_peq)
        
        # Mensagem de habilidade
        if modelo.ability_mensagem:
            self._render_texto(modelo.ability_mensagem, 20, 70, cor, self.fonte_peq)

        # Estados especiais
        if modelo.estado == EstadoJogo.PAUSADO:
            s = pygame.Surface((cfg.LARGURA_TELA, cfg.ALTURA_TELA), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.tela.blit(s, (0, 0))
            self._render_texto("PAUSADO", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2, 
                             cfg.BRANCO, self.fonte_grande, center=True)

        elif modelo.estado == EstadoJogo.GAME_OVER:
            s = pygame.Surface((cfg.LARGURA_TELA, cfg.ALTURA_TELA), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.tela.blit(s, (0, 0))
            self._render_texto("GAME OVER", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2 - 60, 
                             cfg.VERMELHO, self.fonte_grande, center=True)
            self._render_texto("R: Reiniciar | L: Loja | M: Menu", cfg.LARGURA_TELA//2, 
                             cfg.ALTURA_TELA//2 + 40, cfg.BRANCO, self.fonte, center=True)

    def _render_texto(self, texto: str, x: int, y: int, cor: tuple, fonte: pygame.font.Font, 
                     center: bool = False) -> None:
        """
        Renderiza texto na tela.
        
        Args:
            texto: Texto a renderizar
            x: Posição X
            y: Posição Y
            cor: Cor RGB
            fonte: Font do Pygame
            center: Se True, centraliza o texto
        """
        surf = fonte.render(texto, True, cor)
        if center:
            rect = surf.get_rect(center=(x, y))
            self.tela.blit(surf, rect)
        else:
            self.tela.blit(surf, (x, y))
