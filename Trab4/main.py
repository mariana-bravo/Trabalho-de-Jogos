import pygame

pygame.init()

LARGURA = 400
ALTURA = 600

screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bolinha Saltitante!")
clock = pygame.time.Clock()

fonte = pygame.font.SysFont(None, 30)
fonte_grande = pygame.font.SysFont(None, 56)

# Estado da bolinha
pos = [200, 50]  # posição em x e y
vel = [60, 0]    # velocidade em x e y

# ---------- CONSTANTES ----------
GRAVIDADE = 300
RAIO = 10
VEL_MAXIMA = 800  # limite pra bolinha não ficar rápida demais
RAQUETE_LARGURA = 80
RAQUETE_ALTURA = 15
RAQUETE_Y = 560
RAQUETE_VELOCIDADE = 650
PONTOS_POR_ALVO = 1

# ---------- OBSTÁCULOS (REFLETEM A BOLINHA) ----------
obstaculos = [
    [(80, 200), (220, 170), (180, 260)],
    [(250, 320), (350, 300), (330, 380), (260, 390)],
    [(60, 420), (150, 400), (120, 470)],
]

# ---------- ALVOS (SOMAM PONTOS E SOMEM; NÃO REFLETEM) ----------
def losango(cx, cy, r):
    return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]

alvos = [
    {"pontos": losango(60, 100, 18), "coletado": False},
    {"pontos": losango(200, 90, 18), "coletado": False},
    {"pontos": losango(340, 110, 18), "coletado": False},
    {"pontos": losango(320, 240, 18), "coletado": False},
    {"pontos": losango(40, 320, 18), "coletado": False},
    {"pontos": losango(190, 340, 18), "coletado": False},
    {"pontos": losango(300, 450, 18), "coletado": False},
]

# ---------- FUNÇÕES AUXILIARES ----------
def dist_ponto_segmento(p, a, b):
    # ponto mais próximo do segmento a-b em relação a p
    ax, ay = a; bx, by = b; px, py = p
    abx, aby = bx - ax, by - ay
    t = ((px - ax) * abx + (py - ay) * aby) / (abx**2 + aby**2)
    t = max(0, min(1, t))
    closest = (ax + t * abx, ay + t * aby)
    dx, dy = px - closest[0], py - closest[1]
    return (dx**2 + dy**2) ** 0.5, closest

def refletir(vel, normal):
    vx, vy = vel
    nx, ny = normal
    dot = vx * nx + vy * ny
    return [vx - 2 * dot * nx, vy - 2 * dot * ny]

def ponto_dentro_poligono(p, poly):
    x, y = p
    dentro = False
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        if (ay > y) != (by > y):
            x_int = (bx - ax) * (y - ay) / (by - ay) + ax
            if x < x_int:
                dentro = not dentro
    return dentro

def colidir_com_poligono(pos, vel, poly):
    # testa a bolinha contra cada aresta e reflete se estiver batendo.
    # retorna (vel nova, True/False se colidiu)
    colidiu = False
    n = len(poly)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        dist, closest = dist_ponto_segmento(pos, a, b)
        if dist < RAIO:
            nx, ny = pos[0] - closest[0], pos[1] - closest[1]
            comprimento = (nx**2 + ny**2) ** 0.5
            if comprimento > 0:
                nx, ny = nx / comprimento, ny / comprimento
                # só reflete se a bolinha está indo CONTRA a parede
                if vel[0] * nx + vel[1] * ny < 0:
                    vel = refletir(vel, (nx, ny))
                # empurra pra fora pra não grudar
                pos[0] = closest[0] + nx * RAIO
                pos[1] = closest[1] + ny * RAIO
                colidiu = True
    return vel, colidiu

def limitar_velocidade(vel):
    velocidade = (vel[0]**2 + vel[1]**2) ** 0.5
    if velocidade > VEL_MAXIMA:
        fator = VEL_MAXIMA / velocidade
        return [vel[0] * fator, vel[1] * fator]
    return vel

def prender_bola():
    # bolinha parada em cima da raquete, esperando o lançamento
    global pos, vel
    pos = [raquete_x + RAQUETE_LARGURA / 2, RAQUETE_Y - RAIO - 1]
    vel = [0, 0]

def novo_jogo():
    # coloca tudo no estado inicial (usado no começo e no reset)
    global pontos, vidas, estado, raquete_x
    pontos = 0
    vidas = 3
    estado = "parada"   # estados: instrucoes, parada, jogando, venceu, perdeu
    raquete_x = (LARGURA - RAQUETE_LARGURA) / 2
    for alvo in alvos:
        alvo["coletado"] = False
    prender_bola()

def desenhar_texto_centro(texto, y, fnt, cor=(255, 255, 255)):
    img = fnt.render(texto, True, cor)
    screen.blit(img, (LARGURA / 2 - img.get_width() / 2, y))

novo_jogo()

estado = "instrucoes"
tempo_instrucoes = 5.0

# ---------- LOOP PRINCIPAL (roda a cada frame) ----------
running = True
while running:
    dt = clock.tick(60) / 1000  # segundos desde o último frame

    # INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and estado == "instrucoes":
                estado = "parada"
            elif event.key == pygame.K_SPACE and estado == "parada":
                estado = "jogando"
                vel = [120, -550]
            if event.key == pygame.K_r:
                novo_jogo()

    teclas = pygame.key.get_pressed()

    if estado in ("parada", "jogando"):
        if teclas[pygame.K_LEFT]:
            raquete_x -= RAQUETE_VELOCIDADE * dt
        if teclas[pygame.K_RIGHT]:
            raquete_x += RAQUETE_VELOCIDADE * dt
        raquete_x = max(0, min(LARGURA - RAQUETE_LARGURA, raquete_x))

    raquete_poligono = [
        (raquete_x, RAQUETE_Y),
        (raquete_x + RAQUETE_LARGURA, RAQUETE_Y),
        (raquete_x + RAQUETE_LARGURA, RAQUETE_Y + RAQUETE_ALTURA),
        (raquete_x, RAQUETE_Y + RAQUETE_ALTURA),
    ]

    # UPDATE
    if estado == "instrucoes":
        tempo_instrucoes -= dt
        if tempo_instrucoes <= 0:
            estado = "parada"

    elif estado == "parada":
        prender_bola()  # a bolinha acompanha a raquete

    elif estado == "jogando":
        # física
        vel[1] += GRAVIDADE * dt
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt

        # paredes laterais e teto (o chão NÃO reflete: cair = perder vida)
        if pos[0] - RAIO < 0:
            pos[0] = RAIO
            vel[0] = abs(vel[0])
        if pos[0] + RAIO > LARGURA:
            pos[0] = LARGURA - RAIO
            vel[0] = -abs(vel[0])
        if pos[1] - RAIO < 0:
            pos[1] = RAIO
            vel[1] = abs(vel[1])

        # obstáculos
        for obstaculo in obstaculos:
            vel, _ = colidir_com_poligono(pos, vel, obstaculo)

        # raquete (o ponto de impacto muda o ângulo da bolinha)
        vel, bateu = colidir_com_poligono(pos, vel, raquete_poligono)
        if bateu and vel[1] < 0:
            centro = raquete_x + RAQUETE_LARGURA / 2
            deslocamento = (pos[0] - centro) / (RAQUETE_LARGURA / 2)
            vel[0] += deslocamento * 150

        # alvos: coleta ao passar por dentro
        for alvo in alvos:
            if not alvo["coletado"] and ponto_dentro_poligono(pos, alvo["pontos"]):
                alvo["coletado"] = True
                pontos += PONTOS_POR_ALVO

        vel = limitar_velocidade(vel)

        # vitória
        if all(alvo["coletado"] for alvo in alvos):
            estado = "venceu"

        # caiu no fundo
        elif pos[1] - RAIO > ALTURA:
            vidas -= 1
            if vidas <= 0:
                estado = "perdeu"
            else:
                estado = "parada"
                prender_bola()

    # DRAW
    screen.fill((30, 30, 30))

    for obstaculo in obstaculos:
        pygame.draw.polygon(screen, (100, 180, 100), obstaculo)

    for alvo in alvos:
        if not alvo["coletado"]:
            pygame.draw.polygon(screen, (220, 200, 60), alvo["pontos"])

    pygame.draw.polygon(screen, (200, 200, 200), raquete_poligono)
    pygame.draw.circle(screen, (255, 255, 255), pos, RAIO)

    # HUD
    restantes = sum(1 for a in alvos if not a["coletado"])
    screen.blit(fonte.render(f"Pontos: {pontos}", True, (255, 255, 255)), (10, 10))
    screen.blit(fonte.render(f"Vidas: {vidas}", True, (255, 255, 255)), (150, 10))
    screen.blit(fonte.render(f"Alvos: {restantes}", True, (255, 255, 255)), (290, 10))

    if estado == "parada":
        desenhar_texto_centro("ESPAÇO para lançar", 300, fonte)

    if estado in ("venceu", "perdeu"):
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 170))
        screen.blit(camada, (0, 0))
        if estado == "venceu":
            desenhar_texto_centro("VOCÊ VENCEU!", 230, fonte_grande, (120, 255, 120))
        else:
            desenhar_texto_centro("GAME OVER", 230, fonte_grande, (255, 100, 100))
        desenhar_texto_centro(f"Pontos: {pontos}", 300, fonte)
        desenhar_texto_centro("Aperte R para jogar de novo", 340, fonte)

    if estado == "instrucoes":
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 200))
        screen.blit(camada, (0, 0))
        desenhar_texto_centro("COMO JOGAR", 150, fonte_grande)
        desenhar_texto_centro("Colete todos os losangos amarelos!", 230, fonte, (255, 220, 80))
        desenhar_texto_centro("SETAS <- e -> movem a raquete", 275, fonte)
        desenhar_texto_centro("ESPAÇO lança a bolinha", 305, fonte)
        desenhar_texto_centro("Obstáculos verdes rebatem a bolinha", 345, fonte)
        desenhar_texto_centro("Não deixe a bolinha cair! (3 vidas)", 375, fonte)
        desenhar_texto_centro("R reinicia o jogo", 405, fonte)
        desenhar_texto_centro(f"Começando em {int(tempo_instrucoes) + 1}...", 470, fonte, (180, 180, 180))

    pygame.display.flip()

pygame.quit()