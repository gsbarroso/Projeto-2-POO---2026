import random
import logging
from typing import Union
from src.entities.entidades import Cacto, Pterodactilo, Obstaculo
from src.utils.enums import TipoObstaculo

logger = logging.getLogger(__name__)

class FabricaObstaculos:
    """Factory para criação de obstáculos com padrão Strategy."""
    
    @staticmethod
    def criar_obstaculo(tipo: TipoObstaculo, velocidade: float, offset_x: float = 0) -> Obstaculo:
        """
        Cria um obstáculo específico.
        
        Args:
            tipo: Tipo de obstáculo (CACTO ou PTERODACTILO)
            velocidade: Velocidade do obstáculo
            offset_x: Offset horizontal (apenas para cactos)
        
        Returns:
            Obstáculo criado
        
        Raises:
            ValueError: Se tipo de obstáculo for inválido
        """
        if tipo == TipoObstaculo.CACTO:
            return Cacto(velocidade, offset_x)
        elif tipo == TipoObstaculo.PTERODACTILO:
            return Pterodactilo(velocidade)
        else:
            raise ValueError(f"Tipo de obstáculo inválido: {tipo}")
    
    @staticmethod
    def criar_aleatorio(velocidade: float) -> Obstaculo:
        """
        Cria um obstáculo aleatoriamente.
        
        Args:
            velocidade: Velocidade do obstáculo
        
        Returns:
            Obstáculo aleatório
        """
        if random.random() < 0.6:
            # 60% de chance de ser cacto
            qtd = 3 if random.random() > 0.85 else (2 if random.random() > 0.5 else 1)
            # Retorna o primeiro cacto (caller deve iterar se quiser múltiplos)
            return FabricaObstaculos.criar_obstaculo(TipoObstaculo.CACTO, velocidade, 0)
        else:
            # 40% de chance de ser pterodactilo
            return FabricaObstaculos.criar_obstaculo(TipoObstaculo.PTERODACTILO, velocidade)
    
    @staticmethod
    def criar_multiplos_cactos(velocidade: float, quantidade: int) -> list:
        """
        Cria múltiplos cactos com espaçamento.
        
        Args:
            velocidade: Velocidade dos cactos
            quantidade: Número de cactos a criar
        
        Returns:
            Lista de cactos criados
        """
        cactos = []
        for i in range(quantidade):
            offset = i * 35  # Espaçamento entre cactos
            cactos.append(FabricaObstaculos.criar_obstaculo(TipoObstaculo.CACTO, velocidade, offset))
        return cactos
