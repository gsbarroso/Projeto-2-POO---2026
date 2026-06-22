import json
import logging
from pathlib import Path
from typing import Dict, Any
from src.exceptions import PersistenciaError

logger = logging.getLogger(__name__)

class RepositorioDados:
    """Abstração para persistência de dados do jogo."""
    
    def carregar_dados(self) -> Dict[str, Any]:
        """Carrega dados do jogador."""
        raise NotImplementedError
    
    def salvar_dados(self, dados: Dict[str, Any]) -> None:
        """Salva dados do jogador."""
        raise NotImplementedError


class RepositorioDadosJSON(RepositorioDados):
    """Implementação de repositório usando arquivo JSON."""
    
    def __init__(self, caminho_arquivo: str = "save_dino.json"):
        self.caminho = Path(caminho_arquivo)
        self._dados_padrao = {
            "moedas": 100,
            "pontos_acumulados": 0,
            "dinossauro_selecionado": "classico",
            "dinossauros_desbloqueados": ["classico"],
            "itens_disponiveis": {"vida": 0, "velocidade": 0, "pulo": 0}
        }
    
    def carregar_dados(self) -> Dict[str, Any]:
        """Carrega dados do jogador do arquivo JSON."""
        if not self.caminho.exists():
            logger.info("Arquivo de save não existe. Criando padrão.")
            self.salvar_dados(self._dados_padrao)
            return self._dados_padrao.copy()
        
        try:
            with open(self.caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Merge com dados padrão
            alterado = False
            for chave, valor in self._dados_padrao.items():
                if chave not in dados:
                    dados[chave] = valor
                    alterado = True
            
            if alterado:
                self.salvar_dados(dados)
            
            return dados
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise PersistenciaError("Arquivo de save corrompido")
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            raise PersistenciaError(f"Erro ao carregar dados: {e}")
    
    def salvar_dados(self, dados: Dict[str, Any]) -> None:
        """Salva dados do jogador no arquivo JSON."""
        try:
            with open(self.caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            logger.info("Dados salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            raise PersistenciaError(f"Não foi possível salvar o progresso: {e}")
