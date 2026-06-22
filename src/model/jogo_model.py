import logging
import random
from typing import Dict, List, Any, Optional
from src.utils.enums import EstadoJogo, TipoObstaculo, TipoDinossauro, TipoConsumivel
from src.entities.entidades import Dinossauro, Projetil
from src.services.fabrica_obstaculos import FabricaObstaculos
from src.repository.repositorio_dados import RepositorioDados
from src.exceptions import SaldoInsuficienteError, ItemInvalidoError, PersistenciaError
import configuracoes as cfg

logger = logging.getLogger(__name__)


class GerenciadorConsumivel:
    """Gerencia consumíveis do jogador."""
    
    PRECOS_CONSUMIVEL = {
        TipoConsumivel.VIDA: 50,
        TipoConsumivel.VELOCIDADE: 75,
        TipoConsumivel.PULO: 75
    }
    
    NOMES_CONSUMIVEL = {
        TipoConsumivel.VIDA: "Vida Extra",
        TipoConsumivel.VELOCIDADE: "Veloc. Boost",
        TipoConsumivel.PULO: "Pulo Boost"
    }
    
    def __init__(self, dados_jogador: Dict[str, Any]):
        """
        Inicializa o gerenciador de consumíveis.
        
        Args:
            dados_jogador: Dicionário de dados do jogador
        """
        self.dados = dados_jogador
    
    def obter_quantidade(self, tipo: TipoConsumivel) -> int:
        """Obtém quantidade de consumível."""
        if tipo not in TipoConsumivel:
            raise ItemInvalidoError(f"Consumível inválido: {tipo}")
        return self.dados["itens_disponiveis"].get(tipo.value, 0)
    
    def usar_consumivel(self, tipo: TipoConsumivel) -> None:
        """Usa um consumível."""
        if self.obter_quantidade(tipo) <= 0:
            raise SaldoInsuficienteError(f"Sem consumível: {tipo.value}")
        self.dados["itens_disponiveis"][tipo.value] -= 1
    
    def comprar_consumivel(self, tipo: TipoConsumivel) -> None:
        """Compra um consumível."""
        if tipo not in TipoConsumivel:
            raise ItemInvalidoError(f"Consumível inválido: {tipo}")
        
        preco = self.PRECOS_CONSUMIVEL[tipo]
        if self.dados["moedas"] < preco:
            faltam = preco - self.dados["moedas"]
            raise SaldoInsuficienteError(f"Faltam {faltam} moedas!")
        
        self.dados["moedas"] -= preco
        self.dados["itens_disponiveis"][tipo.value] += 1
        logger.info(f"Consumível comprado: {tipo.value}")


class GerenciadorLoja:
    """Gerencia a loja e compra de dinossauros."""
    
    PRECOS_DINOSSAURO = {
        TipoDinossauro.CLASSICO: 0,
        TipoDinossauro.ESPADAO: 100,
        TipoDinossauro.MOTOSERRA: 100,
        TipoDinossauro.SHURIKEN: 175
    }
    
    def __init__(self, dados_jogador: Dict[str, Any]):
        """
        Inicializa o gerenciador de loja.
        
        Args:
            dados_jogador: Dicionário de dados do jogador
        """
        self.dados = dados_jogador
        self.gerenciador_consumivel = GerenciadorConsumivel(dados_jogador)
    
    def obter_preço_dinossauro(self, tipo: TipoDinossauro) -> int:
        """Obtém preço de um dinossauro."""
        return self.PRECOS_DINOSSAURO.get(tipo, 0)
    
    def dinossauro_desbloqueado(self, tipo: TipoDinossauro) -> bool:
        """Verifica se um dinossauro foi desbloqueado."""
        return tipo.value in self.dados["dinossauros_desbloqueados"]
    
    def comprar_dinossauro(self, tipo: TipoDinossauro) -> None:
        """
        Compra um dinossauro.
        
        Args:
            tipo: Tipo de dinossauro
        
        Raises:
            SaldoInsuficienteError: Se não tiver saldo
        """
        if self.dinossauro_desbloqueado(tipo):
            self.dados["dinossauro_selecionado"] = tipo.value
            logger.info(f"Dinossauro selecionado: {tipo.value}")
            return
        
        preco = self.obter_preço_dinossauro(tipo)
        if self.dados["moedas"] < preco:
            faltam = preco - self.dados["moedas"]
            raise SaldoInsuficienteError(f"Faltam {faltam} moedas!")
        
        self.dados["moedas"] -= preco
        self.dados["dinossauros_desbloqueados"].append(tipo.value)
        self.dados["dinossauro_selecionado"] = tipo.value
        logger.info(f"Dinossauro desbloqueado e selecionado: {tipo.value}")


class JogoModel:
    """Modelo do jogo - contém lógica e estado."""
    
    def __init__(self, repositorio: RepositorioDados):
        """
        Inicializa o modelo do jogo.
        
        Args:
            repositorio: Repositório para persistência de dados
        """
        self.repositorio = repositorio
        self.dados_jogador = repositorio.carregar_dados()
        
        self.estado = EstadoJogo.MENU
        self.menu_opcao = 0
        self.mensagem_erro = ""
        
        # Gerenciadores de negócio
        self.gerenciador_loja = GerenciadorLoja(self.dados_jogador)
        self.gerenciador_consumivel = GerenciadorConsumivel(self.dados_jogador)
        
        self.reiniciar_partida()
    
    def reiniciar_partida(self) -> None:
        """Reinicia uma partida."""
        self.dino = Dinossauro(self.dados_jogador["dinossauro_selecionado"])
        self.obstaculos = []
        self.projetil: Optional[Projetil] = None
        self.pontuacao = 0
        self.velocidade_jogo = cfg.VELOCIDADE_BASE_JOGO
        self.moedas_rodada = 0
        self.timer_spawn = 0
        self.ability_timer = 0
        self.ability_ready = False
        self.ability_mensagem = ""
        logger.info("Partida reiniciada")
    
    # ========== LÓGICA DE LOJA ==========
    def comprar_item(self) -> None:
        """Compra um item na loja (dinossauro ou consumível)."""
        self.mensagem_erro = ""
        try:
            dinos = list(self.gerenciador_loja.PRECOS_DINOSSAURO.keys())
            consumiveis = list(TipoConsumivel)
            
            if self.menu_opcao < len(dinos):
                tipo_dino = dinos[self.menu_opcao]
                self.gerenciador_loja.comprar_dinossauro(tipo_dino)
            else:
                idx_consumivel = self.menu_opcao - len(dinos)
                tipo_cons = consumiveis[idx_consumivel]
                self.gerenciador_consumivel.comprar_consumivel(tipo_cons)
            
            self.salvar_progresso()
        except SaldoInsuficienteError as e:
            self.mensagem_erro = str(e)
        except ItemInvalidoError as e:
            self.mensagem_erro = str(e)
    
    def usar_consumivel(self, tipo: TipoConsumivel) -> None:
        """
        Usa um consumível durante o jogo.
        
        Args:
            tipo: Tipo de consumível
        """
        try:
            self.gerenciador_consumivel.usar_consumivel(tipo)
            
            if tipo == TipoConsumivel.VIDA:
                self.dino.vidas += 1
            elif tipo == TipoConsumivel.VELOCIDADE:
                self.dino.velocidade_boost = 1.4
                self.ability_mensagem = "Velocidade Boost MAX!"
            elif tipo == TipoConsumivel.PULO:
                self.dino.pulo_boost = 1.3
                self.ability_mensagem = "Super Pulo Ativado!"
            
            self.salvar_progresso()
        except SaldoInsuficienteError as e:
            logger.warning(f"Consumível não disponível: {e}")
    
    # ========== LÓGICA DE HABILIDADES ==========
    def usar_habilidade_especial(self) -> None:
        """Usa a habilidade especial do dinossauro."""
        if self.dino.variante == "shuriken" and self.ability_ready and self.projetil is None:
            self.projetil = Projetil(self.dino.rect.right, self.dino.rect.centery)
            self.ability_ready = False
            self.ability_timer = 0
            self.ability_mensagem = "Shuriken lançada!"
    
    # ========== LÓGICA DE JOGO ==========
    def atualizar_jogo(self, abaixar: bool) -> None:
        """
        Atualiza toda a lógica do jogo a cada frame.
        
        Args:
            abaixar: Se True, dinossauro agacha
        """
        try:
            self.pontuacao += 1
            
            # Aumenta velocidade periodicamente
            if self.pontuacao % cfg.PONTOS_PARA_ACELERAR == 0:
                self.velocidade_jogo += cfg.INCREMENTO_VELOCIDADE

            # Atualiza timer de habilidade especial
            if self.dino.variante != "classico":
                self.ability_timer += 1
                if self.ability_timer >= cfg.TEMPO_RECARGA_ESPECIAL:
                    self.ability_ready = True

            # Atualiza dinossauro
            self.dino.processar_entrada(abaixar)
            self.dino.atualizar()

            # Spawna obstáculos
            self._atualizar_spawn_obstaculos()

            # Atualiza projetil
            self._atualizar_projetil()

            # Atualiza obstáculos e colisões
            self._atualizar_obstaculos()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar jogo: {e}", exc_info=True)
    
    def _atualizar_spawn_obstaculos(self) -> None:
        """Gerencia spawn de obstáculos."""
        self.timer_spawn += 1
        rate = max(30, 90 - (self.velocidade_jogo * 3.5))
        
        if self.timer_spawn > rate:
            self.timer_spawn = 0
            
            if random.random() < 0.6:
                # Spawna cacto(s)
                qtd = 3 if random.random() > 0.85 else (2 if random.random() > 0.5 else 1)
                for i in range(qtd):
                    velocidade = self.velocidade_jogo * self.dino.velocidade_boost
                    novo_obs = FabricaObstaculos.criar_obstaculo(
                        TipoObstaculo.CACTO, velocidade, i * 35
                    )
                    self.obstaculos.append(novo_obs)
            else:
                # Spawna pterodactilo
                velocidade = self.velocidade_jogo * self.dino.velocidade_boost
                novo_obs = FabricaObstaculos.criar_obstaculo(
                    TipoObstaculo.PTERODACTILO, velocidade
                )
                self.obstaculos.append(novo_obs)
    
    def _atualizar_projetil(self) -> None:
        """Atualiza projetil e verifica colisões com obstáculos."""
        if not self.projetil:
            return
        
        self.projetil.atualizar()
        
        if self.projetil.x > cfg.LARGURA_TELA:
            self.projetil = None
            return
        
        for obs in self.obstaculos[:]:
            if self.projetil.checar_colisao(obs):
                if obs in self.obstaculos:
                    self.obstaculos.remove(obs)
                self.projetil = None
                self.ability_mensagem = "Alvo Eliminado!"
                break
    
    def _atualizar_obstaculos(self) -> None:
        """Atualiza obstáculos e verifica colisões com dinossauro."""
        for obs in self.obstaculos[:]:
            obs.atualizar()
            
            # Remove obstáculo que saiu da tela e adiciona moeda
            if obs.rect.right < 0:
                self.obstaculos.remove(obs)
                self.dados_jogador["moedas"] += 1
                self.moedas_rodada += 1
                continue
            
            # Verifica colisão com dinossauro
            if self.dino.checar_colisao(obs):
                # Habilidades especiais que destroem obstáculos
                if self.ability_ready:
                    # Motoserra vs Cacto
                    if self.dino.variante == "motoserra" and obs.__class__.__name__ == "Cacto":
                        self.ability_ready = False
                        self.ability_timer = 0
                        self.ability_mensagem = "Motoserra rasgou o cacto!"
                        self.obstaculos.remove(obs)
                        continue
                    
                    # Espadão vs Pterodactilo
                    if self.dino.variante == "espadao" and obs.__class__.__name__ == "Pterodactilo":
                        self.ability_ready = False
                        self.ability_timer = 0
                        self.ability_mensagem = "Espadão fatiou o ptero!"
                        self.obstaculos.remove(obs)
                        continue
                
                # Dano ao dinossauro
                if self.dino.vidas > 1:
                    self.dino.vidas -= 1
                    self.obstaculos.remove(obs)
                else:
                    # Game Over
                    self.estado = EstadoJogo.GAME_OVER
                    self.dados_jogador["pontos_acumulados"] += self.pontuacao
                    self.salvar_progresso()
    
    def salvar_progresso(self) -> None:
        """Salva progresso do jogador."""
        try:
            self.repositorio.salvar_dados(self.dados_jogador)
            logger.info("Progresso salvo")
        except PersistenciaError as e:
            logger.error(f"Erro ao salvar: {e}")
            self.mensagem_erro = "Erro ao salvar progresso"
    
    # ========== GETTERS PARA VIEW ==========
    def obter_moedas(self) -> int:
        """Obtém quantidade de moedas."""
        return self.dados_jogador["moedas"]
    
    def obter_pontos(self) -> int:
        """Obtém pontos da rodada atual."""
        return self.pontuacao
    
    def obter_pontos_totais(self) -> int:
        """Obtém pontos acumulados totais."""
        return self.dados_jogador["pontos_acumulados"]
    
    def obter_dino_selecionado(self) -> str:
        """Obtém nome do dinossauro selecionado."""
        return self.dados_jogador["dinossauro_selecionado"]
