# Exceções customizadas
class JogoException(Exception):
    pass

class SaldoInsuficienteError(JogoException):
    pass

class ItemInvalidoError(JogoException):
    pass

class EstadoInvalidoError(JogoException):
    pass

class PersistenciaError(JogoException):
    pass

class DinosaurInvalidoError(JogoException):
    pass
