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
            dados = {
                "moedas": 0,
                "pontos_acumulados": 0,
                "dinossauro_selecionado": "classico",
                "dinossauros_desbloqueados": ["classico"],
                "itens_disponiveis": {"vida": 0, "velocidade": 0, "pulo": 0}
            }
            BancoDeDados.salvar_dados(dados)
            return dados
        
        with open(ARQUIVO_SAVE, 'r') as f:
            dados = json.load(f)

        alterado = False
        if "dinossauro_selecionado" not in dados:
            dados["dinossauro_selecionado"] = "classico"
            alterado = True
        if "dinossauros_desbloqueados" not in dados:
            dados["dinossauros_desbloqueados"] = ["classico"]
            alterado = True
        if "itens_disponiveis" not in dados:
            dados["itens_disponiveis"] = {"vida": 0, "velocidade": 0, "pulo": 0}
            alterado = True
        if alterado:
            BancoDeDados.salvar_dados(dados)

        return dados

    @staticmethod
    def salvar_dados(dados):
        with open(ARQUIVO_SAVE, 'w') as f:
            json.dump(dados, f, indent=4)
