import logging
import pygame
import sys
from src.controller.jogo_controller import JogoController

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=== Iniciando Dino Run MVC ===")
    try:
        controller = JogoController()
        controller.executar()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
    finally:
        logger.info("=== Jogo finalizado ===")
        pygame.quit()
