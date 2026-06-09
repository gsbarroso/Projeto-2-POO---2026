import pygame
import sys
import json
import os
import random
from abc import ABC, abstractmethod
from configuracoes import *
from entidades import *
from persistencia import BancoDeDados
# =====================================================================
# ARQUIVO: gerenciador.py (Sugestão de divisão futura)
# Objetivo: Controlar os estados do jogo e o laço principal (Game Loop)
# =====================================================================
class GerenciadorDeJogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Dino Run: Evolution")
        self.relogio = pygame.time.Clock()
        
        # Carrega dados do Banco
        self.dados_jogador = BancoDeDados.carregar_dados()
        
        self.fonte_grande = pygame.font.SysFont(None, 48)
        self.fonte = pygame.font.SysFont(None, 36)
        self.fonte_pequena = pygame.font.SysFont(None, 28)
        self.estado = "MENU" # Estados: MENU, LOJA, JOGANDO, GAME_OVER
        self.menu_opcao = 0  # Para navegação de menu
        
        self.reiniciar_partida()

    def reiniciar_partida(self):
        variante = self.dados_jogador.get("dinossauro_selecionado", "classico")
        self.dino = Dinossauro(variante)
        self.dino.vidas = 1  # Vidas base
        self.obstaculos = []
        self.pontuacao = 0
        self.velocidade_jogo = 5
        self.timer_spawn = 0
        self.moedas_rodada = 0
        self.ability_timer = 0
        self.ability_ready = False
        self.ability_mensagem = ""
        self.projetil = None

    def desenhar_texto(self, texto, x, y, cor=PRETO, fonte=None):
        if fonte is None:
            fonte = self.fonte
        superficie = fonte.render(texto, True, cor)
        self.tela.blit(superficie, (x, y))

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                BancoDeDados.salvar_dados(self.dados_jogador)
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if self.estado == "MENU":
                    if evento.key == pygame.K_SPACE:
                        self.estado = "JOGANDO"
                    elif evento.key == pygame.K_l:
                        self.estado = "LOJA"
                elif self.estado == "LOJA":
                    if evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU"
                    elif evento.key == pygame.K_UP:
                        self.menu_opcao = max(0, self.menu_opcao - 1)
                    elif evento.key == pygame.K_DOWN:
                        self.menu_opcao = min(7, self.menu_opcao + 1)  # 4 dinossauros + 3 itens + 1
                    elif evento.key == pygame.K_RETURN:
                        self.comprar_item()
                elif self.estado == "JOGANDO":
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                        self.dino.pular()
                    elif evento.key == pygame.K_e:
                        self.usar_shuriken()
                    elif evento.key == pygame.K_1:  # Usar vida
                        self.usar_item("vida")
                    elif evento.key == pygame.K_2:  # Usar velocidade
                        self.usar_item("velocidade")
                    elif evento.key == pygame.K_3:  # Usar pulo
                        self.usar_item("pulo")
                elif self.estado == "GAME_OVER":
                    if evento.key == pygame.K_r:
                        self.reiniciar_partida()
                        self.estado = "JOGANDO"
                    elif evento.key == pygame.K_l:
                        self.estado = "LOJA"
                    elif evento.key == pygame.K_m:
                        self.estado = "MENU"

    def comprar_item(self):
        """Lógica de compra na loja"""
        itens_lista = list(DINO_PRECOS.items()) + list(LOJA_ITENS.items())
        
        if self.menu_opcao < len(DINO_PRECOS):
            # Comprando dinossauro
            dino_nome, preco = list(DINO_PRECOS.items())[self.menu_opcao]
            if dino_nome in self.dados_jogador["dinossauros_desbloqueados"]:
                # Já possui, seleciona
                self.dados_jogador["dinossauro_selecionado"] = dino_nome
                BancoDeDados.salvar_dados(self.dados_jogador)
            elif self.dados_jogador["moedas"] >= preco:
                # Compra
                self.dados_jogador["moedas"] -= preco
                self.dados_jogador["dinossauros_desbloqueados"].append(dino_nome)
                self.dados_jogador["dinossauro_selecionado"] = dino_nome
                BancoDeDados.salvar_dados(self.dados_jogador)
        else:
            # Comprando item
            idx = self.menu_opcao - len(DINO_PRECOS)
            item_nome, info = list(LOJA_ITENS.items())[idx]
            if self.dados_jogador["moedas"] >= info["preco"]:
                self.dados_jogador["moedas"] -= info["preco"]
                self.dados_jogador["itens_disponiveis"][item_nome] += 1
                BancoDeDados.salvar_dados(self.dados_jogador)

    def usar_item(self, tipo):
        """Usa item durante a gameplay"""
        if self.dados_jogador["itens_disponiveis"].get(tipo, 0) > 0:
            self.dados_jogador["itens_disponiveis"][tipo] -= 1
            if tipo == "vida":
                self.dino.vidas += 1
            elif tipo == "velocidade":
                self.dino.velocidade_boost = 1.5
            elif tipo == "pulo":
                self.dino.pulo_boost = 1.3
            BancoDeDados.salvar_dados(self.dados_jogador)

    def usar_shuriken(self):
        """Dispara a shuriken quando a habilidade estiver pronta."""
        if self.dino.variante != "shuriken":
            return
        if not self.ability_ready:
            self.ability_mensagem = "Especial ainda não está pronta."
            return
        if self.projetil is not None:
            self.ability_mensagem = "Projétil já em voo."
            return
        self.projetil = Projetil(self.dino.rect.right, self.dino.rect.centery)
        self.ability_ready = False
        self.ability_mensagem = "Shuriken lançada!"

    def atualizar_jogando(self):
        self.dino.atualizar()

        # Aumentar pontuação e dificuldade com o tempo
        self.pontuacao += 1
        if self.pontuacao % 500 == 0:
            self.velocidade_jogo += 1

        self.ability_timer += 1
        if self.ability_timer >= FPS * 5:
            self.ability_timer -= FPS * 5
            self.ability_ready = True
            self.ability_mensagem = "Especial pronto! Pressione E"

        # Sistema de Spawn (Geração de obstáculos)
        self.timer_spawn += 1
        if self.timer_spawn > max(30, 100 - self.velocidade_jogo * 2):
            self.timer_spawn = 0
            if random.random() < 0.7:
                self.obstaculos.append(Cacto(self.velocidade_jogo * self.dino.velocidade_boost))
            else:
                self.obstaculos.append(Pterodactilo(self.velocidade_jogo * self.dino.velocidade_boost))

        if self.projetil:
            self.projetil.atualizar()
            if self.projetil.rect.x > LARGURA_TELA:
                self.projetil = None
            else:
                for obstaculo in self.obstaculos[:]:
                    if self.projetil.checar_colisao(obstaculo):
                        self.obstaculos.remove(obstaculo)
                        self.projetil = None
                        self.ability_mensagem = "Shuriken acertou um obstáculo!"
                        break

        # Atualiza obstáculos e checa colisões
        for obstaculo in self.obstaculos[:]:
            obstaculo.atualizar()
            
            if obstaculo.rect.x < -50:
                self.obstaculos.remove(obstaculo)
                self.dados_jogador["moedas"] += 1
                self.moedas_rodada += 1
            
            if self.dino.checar_colisao(obstaculo):
                if self.dino.variante == "motoserra" and self.ability_ready and isinstance(obstaculo, Cacto):
                    self.ability_ready = False
                    self.ability_mensagem = "Motoserra ignorou um cacto!"
                    self.obstaculos.remove(obstaculo)
                    continue
                if self.dino.variante == "espadao" and self.ability_ready and isinstance(obstaculo, Pterodactilo):
                    self.ability_ready = False
                    self.ability_mensagem = "Espadão ignorou um pterodáctilo!"
                    self.obstaculos.remove(obstaculo)
                    continue
                if self.dino.vidas > 1:
                    self.dino.vidas -= 1
                    self.obstaculos.remove(obstaculo)
                else:
                    self.estado = "GAME_OVER"
                    self.dados_jogador["pontos_acumulados"] += self.pontuacao
                    BancoDeDados.salvar_dados(self.dados_jogador)
                    break

    def renderizar_menu(self):
        self.tela.fill(BRANCO)
        self.desenhar_texto("DINO RUN: EVOLUTION", LARGURA_TELA//2 - 140, ALTURA_TELA//2 - 80, fonte=self.fonte_grande)
        self.desenhar_texto("Pressione ESPAÇO para Iniciar", LARGURA_TELA//2 - 160, ALTURA_TELA//2)
        self.desenhar_texto(f"Moedas: {self.dados_jogador['moedas']}", 20, 20)
        self.desenhar_texto(f"Pontos Totais: {self.dados_jogador['pontos_acumulados']}", 20, 50)
        self.desenhar_texto("Pressione 'L' para Loja", LARGURA_TELA//2 - 140, ALTURA_TELA//2 + 50)

    def renderizar_loja(self):
        self.tela.fill(BRANCO)
        self.desenhar_texto("LOJA", LARGURA_TELA//2 - 50, 20, fonte=self.fonte_grande)
        self.desenhar_texto(f"Moedas: {self.dados_jogador['moedas']}", 20, 20)
        
        y = 80
        # Dinossauros
        self.desenhar_texto("=== DINOSSAUROS ===", 50, y)
        y += 40
        
        for idx, (dino, preco) in enumerate(DINO_PRECOS.items()):
            possui = "✓" if dino in self.dados_jogador["dinossauros_desbloqueados"] else f"${preco}"
            cor = VERDE if idx == self.menu_opcao else PRETO
            self.desenhar_texto(f"{dino.capitalize()}: {possui}", 70, y, cor=cor, fonte=self.fonte_pequena)
            y += 30
        
        # Itens
        self.desenhar_texto("=== ITENS ===", 50, y)
        y += 40
        
        for idx, (item, info) in enumerate(LOJA_ITENS.items()):
            qtd = self.dados_jogador["itens_disponiveis"].get(item, 0)
            cor = VERDE if idx + len(DINO_PRECOS) == self.menu_opcao else PRETO
            self.desenhar_texto(f"{info['nome']}: ${info['preco']} (x{qtd})", 70, y, cor=cor, fonte=self.fonte_pequena)
            y += 30
        
        self.desenhar_texto("ENTER: Comprar/Selecionar | ESC: Voltar", 20, ALTURA_TELA - 40, fonte=self.fonte_pequena)

    def renderizar_jogo(self):
        self.tela.fill(BRANCO)
        pygame.draw.line(self.tela, PRETO, (0, ALTURA_TELA - 40), (LARGURA_TELA, ALTURA_TELA - 40), 2)
        
        self.dino.desenhar(self.tela)
        for obstaculo in self.obstaculos:
            obstaculo.desenhar(self.tela)
        if self.projetil:
            self.projetil.desenhar(self.tela)
        
        self.desenhar_texto(f"Pontos: {self.pontuacao}", LARGURA_TELA - 150, 20)
        self.desenhar_texto(f"Vidas: {self.dino.vidas}", 20, 20)
        self.desenhar_texto(f"Moedas: {self.moedas_rodada}", 20, 50)
        if self.ability_ready:
            self.desenhar_texto(f"Especial: Pronto (E)", 20, 80, cor=AZUL, fonte=self.fonte_pequena)
        else:
            tempo = max(0, (FPS * 5 - self.ability_timer) // FPS + 1)
            self.desenhar_texto(f"Especial em: {tempo}s", 20, 80, cor=AZUL, fonte=self.fonte_pequena)
        if self.ability_mensagem:
            self.desenhar_texto(self.ability_mensagem, 20, 110, cor=PRETO, fonte=self.fonte_pequena)
            y = 140
        else:
            y = 110

        # Mostrar itens disponíveis
        if self.dados_jogador["itens_disponiveis"]["vida"] > 0:
            self.desenhar_texto(f"Vida (1): x{self.dados_jogador['itens_disponiveis']['vida']}", 20, y, fonte=self.fonte_pequena)
            y += 25
        if self.dados_jogador["itens_disponiveis"]["velocidade"] > 0:
            self.desenhar_texto(f"Velocidade (2): x{self.dados_jogador['itens_disponiveis']['velocidade']}", 20, y, fonte=self.fonte_pequena)
            y += 25
        if self.dados_jogador["itens_disponiveis"]["pulo"] > 0:
            self.desenhar_texto(f"Pulo (3): x{self.dados_jogador['itens_disponiveis']['pulo']}", 20, y, fonte=self.fonte_pequena)

    def renderizar_game_over(self):
        self.tela.fill(BRANCO)
        self.desenhar_texto("GAME OVER", LARGURA_TELA//2 - 100, ALTURA_TELA//2 - 80, VERMELHO, self.fonte_grande)
        self.desenhar_texto(f"Pontuação: {self.pontuacao}", LARGURA_TELA//2 - 100, ALTURA_TELA//2)
        self.desenhar_texto(f"Moedas Ganhas: {self.moedas_rodada}", LARGURA_TELA//2 - 120, ALTURA_TELA//2 + 40)
        self.desenhar_texto("R: Reiniciar | L: Loja | M: Menu", LARGURA_TELA//2 - 160, ALTURA_TELA//2 + 100)

    def renderizar(self):
        if self.estado == "MENU":
            self.renderizar_menu()
        elif self.estado == "LOJA":
            self.renderizar_loja()
        elif self.estado == "JOGANDO":
            self.renderizar_jogo()
        elif self.estado == "GAME_OVER":
            self.renderizar_game_over()
        
        pygame.display.flip()

    def executar(self):
        while True:
            self.processar_eventos()
            
            if self.estado == "JOGANDO":
                self.atualizar_jogando()
            
            self.renderizar()
            self.relogio.tick(FPS)