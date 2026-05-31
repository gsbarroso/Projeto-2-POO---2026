import pygame
import sys
import json
import os
import random
from abc import ABC, abstractmethod
from configuracoes import ARQUIVO_SAVE
# =====================================================================
# ARQUIVO: persistencia.py (Sugestão de divisão futura)
# Objetivo: Lidar exclusivamente com a base de dados JSON.
# =====================================================================
class BancoDeDados:
    @staticmethod
    def carregar_dados():
        if not os.path.exists(ARQUIVO_SAVE):
            # Dados padrão se o jogador for novo
            dados = {"moedas": 0, "habilidades": {"pulo_duplo": False}}
            BancoDeDados.salvar_dados(dados)
            return dados
        
        with open(ARQUIVO_SAVE, 'r') as f:
            return json.load(f)

    @staticmethod
    def salvar_dados(dados):
        with open(ARQUIVO_SAVE, 'w') as f:
            json.dump(dados, f, indent=4)
