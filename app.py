# IMPORTAÇÕES E CONFIGURAÇÃO INICIAL
import sys
import pygame
from pygame.locals import *
from random import randint

pygame.init()
fundo = pygame.image.load('fundo.jpg')
pygame.mixer_music.load('musica.mp3')
pygame.mixer.music.play(-1)
barulho = pygame.mixer.Sound('coin.wav')

largura_tela, altura_tela = 640, 480
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Snake Attack")
placar = pygame.font.Font(None, 36)
relogio = pygame.time.Clock()

maças_com_poder = [
    {"tipo": "vermelha", "cor": (200, 0, 0)},
    {"tipo": "roxa", "cor": (128, 0, 128)},
    {"tipo": "verde", "cor": (0, 255, 0)},
    {"tipo": "amarela", "cor": (255, 255, 0)},
    {"tipo": "branca", "cor": (255, 255, 255)},
    {"tipo": "preta", "cor": (0, 0, 0)}  # MAÇÃ PRETA
]

modo_jogo = None
pausado = False

# FUNÇÕES
def cria_maca(tipo):
    maca = next(m for m in maças_com_poder if m["tipo"] == tipo)
    return {"tipo": maca["tipo"], "cor": maca["cor"], "x": randint(40, 600), "y": randint(50, 430)}

def desenha_cobra(cobra, cor):
    for seg in cobra:
        pygame.draw.rect(tela, cor, (seg[0], seg[1], 20, 20))

def menu():
    global modo_jogo
    tela.blit(fundo, (0, 0))
    titulo = placar.render("SNAKE ATTACK", True, (0, 255, 0))
    texto1 = placar.render("1: Modo Solo", True, (255, 255, 255))
    texto2 = placar.render("2: Modo Multiplayer", True, (255, 255, 255))
    texto3 = placar.render("Controles Jogador 1: W A S D", True, (100, 255, 100))
    texto4 = placar.render("Controles Jogador 2: Setas", True, (255, 100, 100))
    texto5 = placar.render("Tecla P: Pausar | Tecla M: Menu | Tecla R: Reiniciar", True, (255, 255, 0))

    tela.blit(titulo, (220, 100))
    tela.blit(texto1, (200, 160))
    tela.blit(texto2, (200, 200))
    tela.blit(texto3, (150, 250))
    tela.blit(texto4, (150, 280))
    tela.blit(texto5, (50, 320))
    pygame.display.update()

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_1:
                    modo_jogo = "solo"
                    restart_game()
                    return
                if e.key == K_2:
                    modo_jogo = "multiplayer"
                    restart_game()
                    return

def restart_game():
    global x1, y1, vx1, vy1, tamanho1, cobra1, pontos1
    global x2, y2, vx2, vy2, tamanho2, cobra2, pontos2
    global maças, spawn_timers, efeitos, game_over, pausado

    x1, y1, vx1, vy1 = 0, 0, 10, 0
    tamanho1, cobra1, pontos1 = 5, [], 0
    x2, y2, vx2, vy2 = largura_tela - 20, altura_tela - 20, -10, 0
    tamanho2, cobra2, pontos2 = 5, [], 0
    efeitos = {"j1": {}, "j2": {}}
    maças = {}
    spawn_timers = {}
    for maca in maças_com_poder:
        tipo = maca["tipo"]
        maças[tipo] = cria_maca(tipo) if tipo == "vermelha" else None
        spawn_timers[tipo] = pygame.time.get_ticks()
    game_over = False
    pausado = False

def aplicar_efeitos(jogador, maca):
    j = jogador[-1]
    e = efeitos[jogador]
    now = pygame.time.get_ticks()

    if maca["tipo"] == "vermelha":
        globals()[f"tamanho{j}"] += 1
        globals()[f"pontos{j}"] += 1
    elif maca["tipo"] == "roxa":
        global game_over
        game_over = True
    elif maca["tipo"] == "verde":
        e["velocidade"] = now
        globals()[f"tamanho{j}"] += 1
        globals()[f"pontos{j}"] += 2
        globals()[f"vx{j}"] *= 1.5
        globals()[f"vy{j}"] *= 1.5
    elif maca["tipo"] == "amarela":
        # REMOVE O VENENO SE EXISTIR
        if "veneno" in e:
            e.pop("veneno", None)
            e.pop("veneno_tick", None)
        globals()[f"tamanho{j}"] += 1
        globals()[f"pontos{j}"] += 5
    elif maca["tipo"] == "branca":
        e["invencivel"] = now
        globals()[f"pontos{j}"] += 5
    elif maca["tipo"] == "preta":
        e["veneno"] = now
        e["veneno_tick"] = now

def checar_efeitos(jogador):
    now = pygame.time.get_ticks()
    j = jogador[-1]
    e = efeitos[jogador]

    if "veneno" in e:
        if now - e["veneno_tick"] >= 5000:  # A CADA 5 SEGUNDOS
            e["veneno_tick"] = now
            globals()[f"pontos{j}"] = max(0, globals()[f"pontos{j}"] - 1)
            globals()[f"vx{j}"] *= 0.9
            globals()[f"vy{j}"] *= 0.9

    if "velocidade" in e and now - e["velocidade"] > 30000:
        e.pop("velocidade")
        globals()[f"vx{j}"] = 10 if globals()[f"vx{j}"] >= 0 else -10
        globals()[f"vy{j}"] = 10 if globals()[f"vy{j}"] >= 0 else -10

    if "invencivel" in e and now - e["invencivel"] > 10000:
        e.pop("invencivel")

def mostrar_efeitos(jogador, y):
    e = efeitos[jogador]
    now = pygame.time.get_ticks()
    if "veneno" in e:
        tela.blit(placar.render(f"VENENO ATIVO", True, (255, 0, 255)), (10, y))
    if "velocidade" in e:
        t = max(0, 30 - (now - e["velocidade"]) // 1000)
        tela.blit(placar.render(f"Speed: {t}s", True, (0, 255, 0)), (10, y + 30))
    if "invencivel" in e:
        t = max(0, 10 - (now - e["invencivel"]) // 1000)
        tela.blit(placar.render(f"Invencível: {t}s", True, (255, 255, 255)), (10, y + 60))

def verificar_colisoes():
    global game_over
    inv1 = "invencivel" in efeitos["j1"]
    inv2 = "invencivel" in efeitos["j2"]
    if cobra1[0] in cobra1[1:] and not inv1:
        game_over = True
    if modo_jogo == "multiplayer":
        if cobra2[0] in cobra2[1:] and not inv2:
            game_over = True
        if cobra1[0] in cobra2 and not inv1:
            game_over = True
        if cobra2[0] in cobra1 and not inv2:
            game_over = True

# LOOP PRINCIPAL
while True:
    if modo_jogo is None:
        menu()
    else:
        relogio.tick(30)
        tela.blit(fundo, (0, 0))

        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_p:
                    pausado = not pausado
                if e.key == K_m:
                    modo_jogo = None
                if not game_over and not pausado:
                    if e.key == K_w and vy1 == 0: vx1, vy1 = 0, -10
                    if e.key == K_s and vy1 == 0: vx1, vy1 = 0, 10
                    if e.key == K_a and vx1 == 0: vx1, vy1 = -10, 0
                    if e.key == K_d and vx1 == 0: vx1, vy1 = 10, 0
                    if modo_jogo == "multiplayer":
                        if e.key == K_UP and vy2 == 0: vx2, vy2 = 0, -10
                        if e.key == K_DOWN and vy2 == 0: vx2, vy2 = 0, 10
                        if e.key == K_LEFT and vx2 == 0: vx2, vy2 = -10, 0
                        if e.key == K_RIGHT and vx2 == 0: vx2, vy2 = 10, 0
                if game_over and e.key == K_r:
                    restart_game()

        if pausado:
            tela.blit(placar.render("JOGO PAUSADO", True, (255, 255, 0)), (200, 220))
            tela.blit(placar.render("Pressione 'P' para continuar", True, (255, 255, 255)), (140, 260))
            tela.blit(placar.render("Pressione 'M' para voltar ao menu", True, (255, 255, 255)), (120, 300))
            pygame.display.update()
            continue

        if not game_over:
            x1 = (x1 + int(vx1)) % largura_tela
            y1 = (y1 + int(vy1)) % altura_tela
            checar_efeitos("j1")
            if modo_jogo == "multiplayer":
                x2 = (x2 + int(vx2)) % largura_tela
                y2 = (y2 + int(vy2)) % altura_tela
                checar_efeitos("j2")

            now = pygame.time.get_ticks()
            for tipo, maca in list(maças.items()):
                if maca is None:
                    tempo_espera = now - spawn_timers[tipo]
                    if tipo == "vermelha" and tempo_espera > 5000:
                        maças[tipo] = cria_maca(tipo)
                        spawn_timers[tipo] = now
                    elif tipo != "vermelha" and tempo_espera > 15000:
                        maças[tipo] = cria_maca(tipo)
                        spawn_timers[tipo] = now
                else:
                    if abs(maca["x"] - x1) < 20 and abs(maca["y"] - y1) < 20:
                        aplicar_efeitos("j1", maca)
                        maças[tipo] = None
                        spawn_timers[tipo] = now
                        barulho.play()
                    if modo_jogo == "multiplayer" and abs(maca["x"] - x2) < 20 and abs(maca["y"] - y2) < 20:
                        aplicar_efeitos("j2", maca)
                        maças[tipo] = None
                        spawn_timers[tipo] = now
                        barulho.play()

            cobra1.insert(0, (x1, y1))
            while len(cobra1) > tamanho1:
                cobra1.pop()

            if modo_jogo == "multiplayer":
                cobra2.insert(0, (x2, y2))
                while len(cobra2) > tamanho2:
                    cobra2.pop()

            verificar_colisoes()

            for maca in maças.values():
                if maca:
                    pygame.draw.rect(tela, maca["cor"], (maca["x"], maca["y"], 20, 20))

            desenha_cobra(cobra1, (0, 100, 0))
            if modo_jogo == "multiplayer":
                desenha_cobra(cobra2, (100, 0, 0))

            tela.blit(placar.render(f"Pontos J1: {pontos1}", True, (255, 255, 255)), (10, 10))
            mostrar_efeitos("j1", 40)
            if modo_jogo == "multiplayer":
                tela.blit(placar.render(f"Pontos J2: {pontos2}", True, (255, 255, 255)), (400, 10))
                mostrar_efeitos("j2", 300)

        else:
            tela.blit(placar.render("FIM DE JOGO! Pressione R para reiniciar.", True, (255, 0, 0)), (100, 220))
            tela.blit(placar.render("Pressione M para voltar ao menu", True, (255, 255, 255)), (140, 260))

        pygame.display.update()

