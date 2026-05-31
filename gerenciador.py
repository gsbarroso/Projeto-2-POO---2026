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
        
        self.fonte = pygame.font.SysFont(None, 36)
        self.estado = "MENU" # Estados: MENU, JOGANDO, GAME_OVER
        self.reiniciar_partida()

    def reiniciar_partida(self):
        self.dino = Dinossauro()
        self.obstaculos = []
        self.pontuacao = 0
        self.velocidade_jogo = 5
        self.timer_spawn = 0

    def desenhar_texto(self, texto, x, y, cor=PRETO):
        superficie = self.fonte.render(texto, True, cor)
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
                elif self.estado == "JOGANDO":
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                        self.dino.pular()
                elif self.estado == "GAME_OVER":
                    if evento.key == pygame.K_r:
                        self.reiniciar_partida()
                        self.estado = "JOGANDO"
                    if evento.key == pygame.K_m:
                        self.estado = "MENU"

    def atualizar_jogando(self):
        self.dino.atualizar()

        # Aumentar pontuação e dificuldade com o tempo
        self.pontuacao += 1
        if self.pontuacao % 500 == 0:
            self.velocidade_jogo += 1

        # Sistema de Spawn (Geração de obstáculos)
        self.timer_spawn += 1
        if self.timer_spawn > max(30, 100 - self.velocidade_jogo * 2): # Fica mais rápido
            self.timer_spawn = 0
            # Escolhe aleatoriamente entre Cacto e Pterodáctilo
            if random.random() < 0.7:
                self.obstaculos.append(Cacto(self.velocidade_jogo))
            else:
                self.obstaculos.append(Pterodactilo(self.velocidade_jogo))

        # Atualiza obstáculos e checa colisões (Polimorfismo em ação no for)
        for obstaculo in self.obstaculos[:]:
            obstaculo.atualizar()
            
            # Checa se saiu da tela para remover da memória
            if obstaculo.rect.x < -50:
                self.obstaculos.remove(obstaculo)
                self.dados_jogador["moedas"] += 1 # Ganha 1 moeda por desvio
            
            # Checa colisão
            if self.dino.checar_colisao(obstaculo):
                self.estado = "GAME_OVER"
                BancoDeDados.salvar_dados(self.dados_jogador) # Salva as moedas ganhas

    def renderizar(self):
        self.tela.fill(BRANCO)

        if self.estado == "MENU":
            self.desenhar_texto("DINO RUN: EVOLUTION", LARGURA_TELA//2 - 120, ALTURA_TELA//2 - 50)
            self.desenhar_texto("Pressione ESPAÇO para Iniciar", LARGURA_TELA//2 - 150, ALTURA_TELA//2)
            self.desenhar_texto(f"Moedas Acumuladas: {self.dados_jogador['moedas']}", 20, 20)
            
        elif self.estado == "JOGANDO":
            # Desenha uma linha simulando o chão
            pygame.draw.line(self.tela, PRETO, (0, ALTURA_TELA - 40), (LARGURA_TELA, ALTURA_TELA - 40), 2)
            
            self.dino.desenhar(self.tela)
            for obstaculo in self.obstaculos:
                obstaculo.desenhar(self.tela)
                
            self.desenhar_texto(f"Pontos: {self.pontuacao}", LARGURA_TELA - 150, 20)

        elif self.estado == "GAME_OVER":
            self.desenhar_texto("GAME OVER", LARGURA_TELA//2 - 80, ALTURA_TELA//2 - 50, VERMELHO)
            self.desenhar_texto(f"Pontuação Final: {self.pontuacao}", LARGURA_TELA//2 - 100, ALTURA_TELA//2)
            self.desenhar_texto("Pressione 'R' para Reiniciar ou 'M' para Menu", LARGURA_TELA//2 - 200, ALTURA_TELA//2 + 50)

        pygame.display.flip()

    def executar(self):
        # Game Loop Principal
        while True:
            self.processar_eventos()
            
            if self.estado == "JOGANDO":
                self.atualizar_jogando()
                
            self.renderizar()
            self.relogio.tick(FPS)