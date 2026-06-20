# =====================================================================
# ARQUIVO: main.py
# Objetivo: Ponto de entrada (Entry Point) da aplicação MVC
# =====================================================================
import pygame
import sys
from gerenciador import JogoController

if __name__ == "__main__":
    try:
        # Inicializa o controlador principal que amarra o Model e a View
        controller = JogoController()
        controller.executar()
        
    except Exception as e:
        # Captura erros não previstos e exibe no console para debug
        print(f"\n[ERRO FATAL] Ocorreu um problema durante a execução do jogo:")
        print(f"Detalhes: {e}\n")
        
    finally:
        # Garante que os processos do Pygame sejam encerrados com segurança
        pygame.quit()
        sys.exit()