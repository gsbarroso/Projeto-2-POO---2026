import pygame
import sys
import json
import os
import random
from abc import ABC, abstractmethod
from gerenciador import GerenciadorDeJogo
# =====================================================================
# ARQUIVO: main.py
# Objetivo: Ponto de entrada (Entry Point) da aplicação
# =====================================================================
if __name__ == "__main__":
    jogo = GerenciadorDeJogo()
    jogo.executar()