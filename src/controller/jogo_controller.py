import pygame
import sys
import logging
from src.model.jogo_model import JogoModel
from src.view.jogo_view import JogoView
from src.controller.input_processor import InputProcessor
from src.repository.repositorio_dados import RepositorioDadosJSON
from src.utils.enums import EstadoJogo
import configuracoes as cfg

logger = logging.getLogger(__name__)


class JogoController:
    """Controller do jogo - orquestra Model, View e Input."""
    
    def __init__(self):
        """Inicializa o controlador com Dependency Injection."""
        pygame.init()
        self.tela = pygame.display.set_mode((cfg.LARGURA_TELA, cfg.ALTURA_TELA))
        pygame.display.set_caption("Dino Run MVC: Refactored Edition")
        
        self.relogio = pygame.time.Clock()
        
        # Dependency Injection
        repositorio = RepositorioDadosJSON("save_dino.json")
        self.modelo = JogoModel(repositorio)
        self.view = JogoView(self.tela)
        self.input_processor = InputProcessor()
        
        logger.info("JogoController inicializado")
    
    def executar(self) -> None:
        """Loop principal do jogo."""
        try:
            while True:
                # Processar entrada
                abaixar, deve_sair = self.input_processor.processar_eventos(self.modelo)
                
                if deve_sair:
                    break
                
                # Atualizar lógica (apenas durante jogo)
                if self.modelo.estado == EstadoJogo.JOGANDO:
                    self.modelo.atualizar_jogo(abaixar)
                
                # Renderizar
                self.view.renderizar(self.modelo)
                
                # FPS
                self.relogio.tick(cfg.FPS)
        
        except KeyboardInterrupt:
            logger.info("Jogo interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro não tratado no loop principal: {e}", exc_info=True)
        finally:
            self._limpar()
    
    def _limpar(self) -> None:
        """Limpa recursos antes de sair."""
        try:
            self.modelo.salvar_progresso()
            logger.info("Progresso salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar progresso: {e}")
        finally:
            pygame.quit()
            sys.exit()
