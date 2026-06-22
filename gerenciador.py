import pygame
import sys
import random
import configuracoes as cfg
from entidades import Dinossauro, Cacto, Pterodactilo, Projetil
from persistencia import BancoDeDados

class SaldoInsuficienteError(Exception): pass

# =====================================================================
# 1. MODELO (M)
# =====================================================================
class JogoModel:
    def __init__(self):
        self.dados_jogador = BancoDeDados.carregar_dados()
        self.estado = "MENU"
        self.menu_opcao = 0
        self.mensagem_erro = ""
        
        self.loja_precos = {"classico": 0, "espadao": 100, "motoserra": 100, "shuriken": 175}
        self.loja_itens = {
            "vida": {"preco": 50, "nome": "Vida Extra"},
            "velocidade": {"preco": 75, "nome": "Veloc. Boost"},
            "pulo": {"preco": 75, "nome": "Pulo Boost"}
        }
        self.reiniciar_partida()

    def reiniciar_partida(self):
        self.dino = Dinossauro(self.dados_jogador["dinossauro_selecionado"])
        self.obstaculos = []
        self.projetil = None
        self.pontuacao = 0
        self.velocidade_jogo = cfg.VELOCIDADE_BASE_JOGO
        self.moedas_rodada = 0
        self.timer_spawn = 0
        self.ability_timer = 0
        self.ability_ready = False
        self.ability_mensagem = ""
        self.mensagem_erro = ""

    def comprar_item(self):
        self.mensagem_erro = ""
        dinos_nomes = list(self.loja_precos.keys())
        
        if self.menu_opcao < len(dinos_nomes):
            nome = dinos_nomes[self.menu_opcao]
            preco = self.loja_precos[nome]
            
            if nome in self.dados_jogador["dinossauros_desbloqueados"]:
                self.dados_jogador["dinossauro_selecionado"] = nome
            else:
                if self.dados_jogador["moedas"] < preco:
                    raise SaldoInsuficienteError(f"Faltam {preco - self.dados_jogador['moedas']} moedas!")
                self.dados_jogador["moedas"] -= preco
                self.dados_jogador["dinossauros_desbloqueados"].append(nome)
                self.dados_jogador["dinossauro_selecionado"] = nome
        else:
            idx_item = self.menu_opcao - len(dinos_nomes)
            item_id = list(self.loja_itens.keys())[idx_item]
            info = self.loja_itens[item_id]
            
            if self.dados_jogador["moedas"] < info["preco"]:
                raise SaldoInsuficienteError(f"Faltam {info['preco'] - self.dados_jogador['moedas']} moedas!")
            self.dados_jogador["moedas"] -= info["preco"]
            self.dados_jogador["itens_disponiveis"][item_id] += 1
            
        BancoDeDados.salvar_dados(self.dados_jogador)

    def usar_consumivel(self, tipo: str) -> None:
        if self.dados_jogador["itens_disponiveis"].get(tipo, 0) > 0:
            self.dados_jogador["itens_disponiveis"][tipo] -= 1
            if tipo == "vida": self.dino.vidas += 1
            elif tipo == "velocidade": 
                self.dino.velocidade_boost = 1.4
                self.ability_mensagem = "Velocidade Boost MAX!"
            elif tipo == "pulo": 
                self.dino.pulo_boost = 1.3
                self.ability_mensagem = "Super Pulo Ativado!"
            BancoDeDados.salvar_dados(self.dados_jogador)

    def usar_especial(self) -> None:
        if self.dino.variante != "shuriken" or not self.ability_ready or self.projetil is not None:
            return
        self.projetil = Projetil(self.dino.rect.right, self.dino.rect.centery)
        self.ability_ready = False
        self.ability_timer = 0
        self.ability_mensagem = "Shuriken lançada!"

# =====================================================================
# 2. VISÃO (V)
# =====================================================================
class JogoView:
    def __init__(self, tela):
        self.tela = tela
        pygame.font.init()
        self.fonte_grande = pygame.font.SysFont("courier", 48, bold=True)
        self.fonte = pygame.font.SysFont("courier", 24, bold=True)
        self.fonte_peq = pygame.font.SysFont("courier", 16, bold=True)

    def renderizar(self, m):
        is_night = (m.estado in ["JOGANDO", "GAME_OVER", "PAUSADO"]) and ((m.pontuacao // 600) % 2 != 0)
        bg_cor = cfg.CINZA_ESCURO if is_night else cfg.BRANCO
        txt_cor = cfg.CINZA_CLARO if is_night else cfg.PRETO

        self.tela.fill(bg_cor)

        if m.estado == "MENU":
            self._render_texto("DINO RUN MVC: EVOLUTION", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2 - 60, txt_cor, self.fonte_grande, center=True)
            self._render_texto("Pressione [ESPAÇO] para Iniciar", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2, cfg.VERDE, self.fonte, center=True)
            self._render_texto(f"Moedas: {m.dados_jogador['moedas']}", 20, 20, cfg.AMARELO, self.fonte)
            self._render_texto("Pressione 'L' para Loja", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA - 50, txt_cor, self.fonte, center=True)

        elif m.estado == "LOJA":
            self._render_texto("=== LOJA ===", cfg.LARGURA_TELA//2, 20, txt_cor, self.fonte_grande, center=True)
            self._render_texto(f"Moedas: {m.dados_jogador['moedas']}", 20, 20, cfg.AMARELO, self.fonte)
            
            if m.mensagem_erro:
                self._render_texto(f"⚠ {m.mensagem_erro}", 20, 60, cfg.VERMELHO, self.fonte_peq)

            y = 100
            for idx, (dino, preco) in enumerate(m.loja_precos.items()):
                possui = "✓" if dino in m.dados_jogador["dinossauros_desbloqueados"] else f"${preco}"
                if m.dados_jogador["dinossauro_selecionado"] == dino: possui = "[EQUIPADO]"
                cor = cfg.VERDE if idx == m.menu_opcao else txt_cor
                self._render_texto(f"{'▶' if idx == m.menu_opcao else ' '} {dino.upper()}: {possui}", 50, y, cor, self.fonte)
                y += 30
            
            y += 20
            self._render_texto("- CONSUMÍVEIS -", 50, y, txt_cor, self.fonte); y += 30
            for idx, (item, info) in enumerate(m.loja_itens.items()):
                qtd = m.dados_jogador["itens_disponiveis"].get(item, 0)
                global_idx = idx + len(m.loja_precos)
                cor = cfg.VERDE if global_idx == m.menu_opcao else txt_cor
                self._render_texto(f"{'▶' if global_idx == m.menu_opcao else ' '} {info['nome']}: ${info['preco']} (x{qtd})", 50, y, cor, self.fonte)
                y += 30

        elif m.estado in ["JOGANDO", "GAME_OVER", "PAUSADO"]:
            pygame.draw.line(self.tela, txt_cor, (0, cfg.LINHA_CHAO), (cfg.LARGURA_TELA, cfg.LINHA_CHAO), 2)
            
            if m.dino.image: self.tela.blit(m.dino.image, m.dino.rect)
            for obs in m.obstaculos:
                if hasattr(obs, 'image') and obs.image: self.tela.blit(obs.image, obs.rect)
            if m.projetil: self.tela.blit(m.projetil.image, m.projetil.rect)
            
            self._render_texto(f"Pontos: {m.pontuacao}", cfg.LARGURA_TELA - 200, 20, txt_cor, self.fonte)
            self._render_texto(f"Moedas: {m.moedas_rodada}", cfg.LARGURA_TELA - 200, 50, cfg.AMARELO, self.fonte)
            self._render_texto(f"Vidas: {m.dino.vidas}", 20, 20, cfg.VERMELHO, self.fonte)
            
            if m.dino.variante != "classico":
                porcentagem = min(100, (m.ability_timer / cfg.TEMPO_RECARGA_ESPECIAL) * 100)
                especial_txt = "Pronto (E)" if m.ability_ready else f"{porcentagem:.0f}%"
                self._render_texto(f"Especial: {especial_txt}", 20, 50, cfg.AZUL, self.fonte_peq)
                
            if m.ability_mensagem: 
                self._render_texto(m.ability_mensagem, 20, 70, txt_cor, self.fonte_peq)

            if m.estado == "PAUSADO":
                s = pygame.Surface((cfg.LARGURA_TELA, cfg.ALTURA_TELA), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                self.tela.blit(s, (0,0))
                self._render_texto("PAUSADO", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2, cfg.BRANCO, self.fonte_grande, center=True)

            elif m.estado == "GAME_OVER":
                s = pygame.Surface((cfg.LARGURA_TELA, cfg.ALTURA_TELA), pygame.SRCALPHA)
                s.fill((0, 0, 0, 200))
                self.tela.blit(s, (0,0))
                self._render_texto("GAME OVER", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2 - 60, cfg.VERMELHO, self.fonte_grande, center=True)
                self._render_texto("R: Reiniciar | L: Loja | M: Menu", cfg.LARGURA_TELA//2, cfg.ALTURA_TELA//2 + 40, cfg.BRANCO, self.fonte, center=True)

        pygame.display.flip()

    def _render_texto(self, texto, x, y, cor, fonte, center=False):
        surf = fonte.render(texto, True, cor)
        if center:
            rect = surf.get_rect(center=(x, y))
            self.tela.blit(surf, rect)
        else:
            self.tela.blit(surf, (x, y))

# =====================================================================
# 3. CONTROLADOR (C)
# =====================================================================
class JogoController:
    def __init__(self):
        pygame.init()
        tela = pygame.display.set_mode((cfg.LARGURA_TELA, cfg.ALTURA_TELA))
        pygame.display.set_caption("Dino Run MVC: Hardcore Edition")
        
        self.relogio = pygame.time.Clock()
        self.m = JogoModel()
        self.v = JogoView(tela)

    def _processar_inputs(self):
        keys = pygame.key.get_pressed()
        abaixar = keys[pygame.K_DOWN]
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                BancoDeDados.salvar_dados(self.m.dados_jogador)
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if self.m.estado == "MENU":
                    if evento.key == pygame.K_SPACE: self.m.estado = "JOGANDO"; self.m.reiniciar_partida()
                    elif evento.key == pygame.K_l: self.m.estado = "LOJA"; self.m.mensagem_erro = ""
                
                elif self.m.estado == "LOJA":
                    if evento.key == pygame.K_ESCAPE: self.m.estado = "MENU"
                    elif evento.key == pygame.K_UP: self.m.menu_opcao = max(0, self.m.menu_opcao - 1)
                    elif evento.key == pygame.K_DOWN: 
                        max_opt = len(self.m.loja_precos) + len(self.m.loja_itens) - 1
                        self.m.menu_opcao = min(max_opt, self.m.menu_opcao + 1)
                    elif evento.key == pygame.K_RETURN:
                        try:
                            self.m.comprar_item()
                        except SaldoInsuficienteError as erro:
                            self.m.mensagem_erro = str(erro)
                
                elif self.m.estado in ["JOGANDO", "PAUSADO"]:
                    if evento.key == pygame.K_p:
                        self.m.estado = "PAUSADO" if self.m.estado == "JOGANDO" else "JOGANDO"
                    
                    if self.m.estado == "JOGANDO":
                        if evento.key in [pygame.K_SPACE, pygame.K_UP]: self.m.dino.pular()
                        elif evento.key == pygame.K_e: self.m.usar_especial()
                        elif evento.key == pygame.K_1: self.m.usar_consumivel("vida")
                        elif evento.key == pygame.K_2: self.m.usar_consumivel("velocidade")
                        elif evento.key == pygame.K_3: self.m.usar_consumivel("pulo")
                
                elif self.m.estado == "GAME_OVER":
                    if evento.key == pygame.K_r: self.m.reiniciar_partida(); self.m.estado = "JOGANDO"
                    elif evento.key == pygame.K_l: self.m.estado = "LOJA"
                    elif evento.key == pygame.K_m: self.m.estado = "MENU"

        return abaixar

    def _atualizar_regras(self, abaixar):
        try:
            self.m.pontuacao += 1
            
            if self.m.pontuacao % cfg.PONTOS_PARA_ACELERAR == 0:
                self.m.velocidade_jogo += cfg.INCREMENTO_VELOCIDADE

            if self.m.dino.variante != "classico":
                self.m.ability_timer += 1
                if self.m.ability_timer >= cfg.TEMPO_RECARGA_ESPECIAL:
                    self.m.ability_ready = True

            self.m.dino.processar_entrada(abaixar)
            self.m.dino.atualizar()

            self.m.timer_spawn += 1
            rate = max(30, 90 - (self.m.velocidade_jogo * 3.5))
            if self.m.timer_spawn > rate:
                self.m.timer_spawn = 0
                if random.random() < 0.6:
                    qtd = 3 if random.random() > 0.85 else (2 if random.random() > 0.5 else 1)
                    for i in range(qtd):
                        novo_cacto = Cacto(self.m.velocidade_jogo * self.m.dino.velocidade_boost, i * 35)
                        self.m.obstaculos.append(novo_cacto)
                else:
                    novo_ptero = Pterodactilo(self.m.velocidade_jogo * self.m.dino.velocidade_boost)
                    self.m.obstaculos.append(novo_ptero)

            if self.m.projetil:
                self.m.projetil.atualizar()
                if self.m.projetil.x > cfg.LARGURA_TELA:
                    self.m.projetil = None
                else:
                    for obs in self.m.obstaculos[:]:
                        if self.m.projetil.checar_colisao(obs):
                            self.m.obstaculos.remove(obs)
                            self.m.projetil = None
                            self.m.ability_mensagem = "Alvo Eliminado!"
                            break

            for obs in self.m.obstaculos[:]:
                obs.atualizar()
                
                if obs.rect.right < 0:
                    self.m.obstaculos.remove(obs)
                    self.m.dados_jogador["moedas"] += 1
                    self.m.moedas_rodada += 1
                    continue
                
                if self.m.dino.checar_colisao(obs):
                    if self.m.dino.variante == "motoserra" and self.m.ability_ready and isinstance(obs, Cacto):
                        self.m.ability_ready = False
                        self.m.ability_timer = 0
                        self.m.ability_mensagem = "Motoserra rasgou o cacto!"
                        self.m.obstaculos.remove(obs)
                        continue
                    
                    if self.m.dino.variante == "espadao" and self.m.ability_ready and isinstance(obs, Pterodactilo):
                        self.m.ability_ready = False
                        self.m.ability_timer = 0
                        self.m.ability_mensagem = "Espadão fatiou o ptero!"
                        self.m.obstaculos.remove(obs)
                        continue

                    if self.m.dino.vidas > 1:
                        self.m.dino.vidas -= 1
                        self.m.obstaculos.remove(obs)
                    else:
                        self.m.estado = "GAME_OVER"
                        self.m.dados_jogador["pontos_acumulados"] += self.m.pontuacao
                        BancoDeDados.salvar_dados(self.m.dados_jogador)
                    
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha geral em _atualizar_regras: {e}")

    def executar(self):
        while True:
            try:
                abaixar = self._processar_inputs()
                if self.m.estado == "JOGANDO":
                    self._atualizar_regras(abaixar)
                self.v.renderizar(self.m)
                self.relogio.tick(cfg.FPS)
            except SystemExit:
                break
            except Exception as e:
                print(f"[ERRO] Exceção no loop principal: {e}")