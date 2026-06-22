import json
import os
import configuracoes as cfg

# =====================================================================
# ARQUIVO: persistencia.py
# Objetivo: Lidar exclusivamente com a base de dados JSON e evitar corrupção.
# =====================================================================
class BancoDeDados:
    @staticmethod
    def carregar_dados():
        dados_padrao = {
            "moedas": 100, # Inicia com 100 para testes
            "pontos_acumulados": 0,
            "dinossauro_selecionado": "classico",
            "dinossauros_desbloqueados": ["classico"],
            "itens_disponiveis": {"vida": 0, "velocidade": 0, "pulo": 0}
        }

        if not os.path.exists(cfg.ARQUIVO_SAVE):
            BancoDeDados.salvar_dados(dados_padrao)
            return dados_padrao
        
        try:
            with open(cfg.ARQUIVO_SAVE, 'r') as f:
                dados = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("[AVISO] Arquivo de save corrompido ou não lido. Restaurando padrão.")
            return dados_padrao

        # Merge de chaves novas
        alterado = False
        for key, value in dados_padrao.items():
            if key not in dados:
                dados[key] = value
                alterado = True

        if alterado:
            BancoDeDados.salvar_dados(dados)

        return dados

    @staticmethod
    def salvar_dados(dados):
        try:
            with open(cfg.ARQUIVO_SAVE, 'w') as f:
                json.dump(dados, f, indent=4)
        except Exception as e:
            print(f"[ERRO] Não foi possível salvar o progresso: {e}")