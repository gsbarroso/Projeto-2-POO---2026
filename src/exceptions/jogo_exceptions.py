"""
Exceções customizadas do projeto Dino Run.
Seguindo princípios SOLID - cada exceção tem responsabilidade específica.
"""


class DinRunException(Exception):
    """Exceção base para todo o projeto."""
    pass


class SaldoInsuficienteError(DinRunException):
    """Raised quando o jogador tenta comprar item sem moedas suficientes."""
    pass


class ItemNaoDisponielError(DinRunException):
    """Raised quando tenta usar item que não está disponível."""
    pass


class ArquivoSaveInvalidoError(DinRunException):
    """Raised quando arquivo de save está corrompido."""
    pass


class EntidadeInvalidaError(DinRunException):
    """Raised quando entidade está em estado inválido."""
    pass


class ConfiguracaoInvalidaError(DinRunException):
    """Raised quando configurações são inválidas."""
    pass
