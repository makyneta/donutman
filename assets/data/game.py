import pygame
import sys
import math
import random

# --- CONFIGURAÇÕES GERAIS ---
pygame.init()
pygame.font.init()

# Cores (Estilo Dark Neon)
COLOR_BG = (10, 10, 18)
COLOR_WALL_FILL = (20, 20, 40)
COLOR_WALL_BORDER = (42, 42, 80)
COLOR_PLAYER = (255, 204, 0)  # Amarelo Neon
COLOR_BREAD = (255, 204, 0)
COLOR_DONUT = (255, 105, 180) # Rosa
COLOR_TEXT = (255, 255, 255)

# Dimensões
TILE_SIZE = 24
PLAYER_SPEED = 2
GHOST_SPEED = 1.4

# Mapa (Mesmo da versão Web)
LEVEL_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,2,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,2,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,9,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,9,1,9,1,1,1,0,1,1,1,1],
    [1,9,9,9,0,1,9,9,9,9,9,9,9,1,0,9,9,9,1],
    [1,1,1,1,0,1,9,1,1,9,1,1,9,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,2,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

ROWS = len(LEVEL_MAP)
COLS = len(LEVEL_MAP[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bread-Man Python Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 20, bold=True)
big_font = pygame.font.SysFont('arial', 40, bold=True)

class Game:
    def __init__(self):
        self.reset_game()
        self.state = "START" # START, PLAYING, GAMEOVER

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.reset_level()

    def reset_level(self):
        self.walls = []
        self.breads = []
        self.donuts = []
        self.ghosts = []

        # Parsear Mapa
        for r in range(ROWS):
            for c in range(COLS):
                tile = LEVEL_MAP[r][c]
                x, y = c * TILE_SIZE, r * TILE_SIZE
                if tile == 1:
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == 0:
                    self.breads.append({'x': x + 12, 'y': y + 12, 'active': True})
                elif tile == 2:
                    self.donuts.append({'x': x + 12, 'y': y + 12, 'active': True})

        # Adicionar Donuts Extras (3 aleatórios)
        for _ in range(3):
            if self.breads:
                target = random.choice(self.breads)
                self.donuts.append({'x': target['x'], 'y': target['y'], 'active': True})
                self.breads.remove(target)

        # Jogador
        self.player = {
            'rect': pygame.Rect(9 * TILE_SIZE, 8 * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            'dx': 0, 'dy': 0,
            'next_dx': 0, 'next_dy': 0,
            'angle': 0
        }

        # Fantasmas (2, em cantos opostos)
        self.ghosts = [
            {'rect': pygame.Rect(1 * TILE_SIZE, 1 * TILE_SIZE, TILE_SIZE, TILE_SIZE), 'color': (255, 50, 50), 'dx': 0, 'dy': 0},
            {'rect': pygame.Rect(16 * TILE_SIZE, 14 * TILE_SIZE, TILE_SIZE, TILE_SIZE), 'color': (255, 180, 50), 'dx': 0, 'dy': 0}
        ]
        self.change_ghost_directions()

    def check_wall_collision(self, rect):
        # Cria uma caixa de colisão menor para passar melhor nos cantos
        margin = 6
        test_rect = rect.inflate(-margin*2, -margin*2)
        
        # Checa 4 pontos da caixa
        points = [
            (test_rect.left, test_rect.top),
            (test_rect.right, test_rect.top),
            (test_rect.left, test_rect.bottom),
            (test_rect.right, test_rect.bottom)
        ]

        for px, py in points:
            c = px // TILE_SIZE
            r = py // TILE_SIZE
            if 0 <= r < ROWS and 0 <= c < COLS:
                if LEVEL_MAP[r][c] == 1:
                    return True
        return False

    def change_ghost_directions(self):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for g in self.ghosts:
            possible_dirs = []
            for dx, dy in dirs:
                test_rect = g['rect'].copy()
                test_rect.x += dx * GHOST_SPEED
                test_rect.y += dy * GHOST_SPEED
                if not self.check_wall_collision(test_rect):
                    # Evita voltar para trás imediatamente (opcional, mas bom)
                    if not (dx == -g['dx'] and dy == -g['dy']):
                        possible_dirs.append((dx, dy))
            
            if possible_dirs:
                # 30% de chance de perseguir, senão aleatório
                if random.random() < 0.3:
                    # Acha direção que minimiza distância ao player
                    best_dir = possible_dirs[0]
                    min_dist = 9999
                    for dx, dy in possible_dirs:
                        future_x = g['rect'].x + dx
                        future_y = g['rect'].y + dy
                        dist = math.hypot(future_x - self.player['rect'].x, future_y - self.player['rect'].y)
                        if dist < min_dist:
                            min_dist = dist
                            best_dir = (dx, dy)
                    g['dx'], g['dy'] = best_dir
                else:
                    g['dx'], g['dy'] = random.choice(possible_dirs)
            else:
                # Beco sem saída
                g['dx'] *= -1
                g['dy'] *= -1

    def handle_input(self, key):
        if self.state != "PLAYING":
            return
            
        if key == pygame.K_w: self.player['next_dx'], self.player['next_dy'] = 0, -1
        if key == pygame.K_s: self.player['next_dx'], self.player['next_dy'] = 0, 1
        if key == pygame.K_a: self.player['next_dx'], self.player['next_dy'] = -1, 0
        if key == pygame.K_d: self.player['next_dx'], self.player['next_dy'] = 1, 0
        
        # Suporte para setas também (caso queira)
        if key == pygame.K_UP: self.player['next_dx'], self.player['next_dy'] = 0, -1
        if key == pygame.K_DOWN: self.player['next_dx'], self.player['next_dy'] = 0, 1
        if key == pygame.K_LEFT: self.player['next_dx'], self.player['next_dy'] = -1, 0
        if key == pygame.K_RIGHT: self.player['next_dx'], self.player['next_dy'] = 1, 0

    def update(self):
        if self.state != "PLAYING":
            return

        p = self.player
        
        # Tentar mudar direção
        if p['next_dx'] != 0 or p['next_dy'] != 0:
            test_rect = p['rect'].copy()
            test_rect.x += p['next_dx'] * PLAYER_SPEED
            test_rect.y += p['next_dy'] * PLAYER_SPEED
            if not self.check_wall_collision(test_rect):
                p['dx'] = p['next_dx']
                p['dy'] = p['next_dy']

        # Mover X
        p['rect'].x += p['dx'] * PLAYER_SPEED
        if self.check_wall_collision(p['rect']):
            p['rect'].x -= p['dx'] * PLAYER_SPEED # Desfaz movimento
            p['dx'] = 0

        # Mover Y
        p['rect'].y += p['dy'] * PLAYER_SPEED
        if self.check_wall_collision(p['rect']):
            p['rect'].y -= p['dy'] * PLAYER_SPEED # Desfaz movimento
            p['dy'] = 0

        # Atualizar ângulo visual
        if p['dx'] == 1: p['angle'] = 0
        elif p['dx'] == -1: p['angle'] = 180
        elif p['dy'] == 1: p['angle'] = 90
        elif p['dy'] == -1: p['angle'] = 270

        # Mover Fantasmas
        for g in self.ghosts:
            g['rect'].x += g['dx'] * GHOST_SPEED
            g['rect'].y += g['dy'] * GHOST_SPEED
            
            if self.check_wall_collision(g['rect']) or random.random() < 0.015:
                # Colidiu ou decidiu virar
                g['rect'].x -= g['dx'] * GHOST_SPEED
                g['rect'].y -= g['dy'] * GHOST_SPEED
                self.change_ghost_directions()

            # Colisão com Jogador
            if p['rect'].colliderect(g['rect']):
                self.handle_death()

        # Coletar Pães (Pontos)
        center_p = (p['rect'].centerx, p['rect'].centery)
        for b in self.breads:
            if b['active'] and math.hypot(b['x'] - center_p[0], b['y'] - center_p[1]) < 10:
                b['active'] = False
                self.score += 10

        # Coletar Donuts (Vitória)
        for d in self.donuts:
            if d['active'] and math.hypot(d['x'] - center_p[0], d['y'] - center_p[1]) < 10:
                d['active'] = False
                self.score += 50
                self.check_win()

    def handle_death(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "GAMEOVER"
        else:
            # Respawn
            self.player['rect'].topleft = (9 * TILE_SIZE, 8 * TILE_SIZE)
            self.player['dx'] = 0; self.player['dy'] = 0
            self.player['next_dx'] = 0; self.player['next_dy'] = 0
            
            # Respawn Fantasmas
            self.ghosts[0]['rect'].topleft = (1 * TILE_SIZE, 1 * TILE_SIZE)
            self.ghosts[1]['rect'].topleft = (16 * TILE_SIZE, 14 * TILE_SIZE)
            self.change_ghost_directions()

    def check_win(self):
        # Apenas Donuts (como pedido)
        active_donuts = [d for d in self.donuts if d['active']]
        if len(active_donuts) == 0:
            self.level += 1
            self.score += 100
            self.reset_level()

    def draw(self):
        screen.fill(COLOR_BG)

        # Paredes
        for w in self.walls:
            pygame.draw.rect(screen, COLOR_WALL_FILL, w)
            pygame.draw.rect(screen, COLOR_WALL_BORDER, w, 1)

        # Pães
        for b in self.breads:
            if b['active']:
                pygame.draw.rect(screen, COLOR_BREAD, (b['x']-2, b['y']-2, 4, 4))

        # Donuts
        for d in self.donuts:
            if d['active']:
                # Desenhar donut geometricamente (Círculo rosa com buraco preto)
                pygame.draw.circle(screen, COLOR_DONUT, (int(d['x']), int(d['y'])), 7)
                pygame.draw.circle(screen, COLOR_BG, (int(d['x']), int(d['y'])), 3)

        # Jogador
        px, py = self.player['rect'].center
        # Desenhar "Cesta" / Pacman
        pygame.draw.circle(screen, COLOR_PLAYER, (px, py), 10)
        # Desenhar "boca" simples (triângulo preto apontando na direção)
        angle_rad = math.radians(self.player['angle'])
        end_x = px + math.cos(angle_rad) * 10
        end_y = py + math.sin(angle_rad) * 10
        pygame.draw.line(screen, COLOR_BG, (px, py), (end_x, end_y), 3)

        # Fantasmas
        for g in self.ghosts:
            gx, gy = g['rect'].center
            pygame.draw.circle(screen, g['color'], (gx, gy-2), 10) # Cabeça
            pygame.draw.rect(screen, g['color'], (gx-10, gy-2, 20, 10)) # Corpo
            # Olhos
            pygame.draw.rect(screen, (255, 255, 255), (gx-6, gy-6, 4, 4))
            pygame.draw.rect(screen, (255, 255, 255), (gx+2, gy-6, 4, 4))

        # UI
        score_text = font.render(f"Pontos: {self.score}", True, COLOR_TEXT)
        lives_text = font.render(f"Vidas: {'❤️' * self.lives}", True, COLOR_TEXT)
        level_text = font.render(f"Fase: {self.level}", True, COLOR_TEXT)
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH // 2 - 30, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))

        # Telas Overlay
        if self.state == "START":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0,0))
            
            title = big_font.render("BREAD-MAN", True, COLOR_PLAYER)
            instr = font.render("WASD para Mover | Colete os DONUTS", True, (200, 200, 200))
            press = font.render("Pressione ESPAÇO para iniciar", True, (255, 255, 255))
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT//2))
            screen.blit(press, (WIDTH//2 - press.get_width()//2, HEIGHT//2 + 50))

        elif self.state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0,0))
            
            title = big_font.render("GAME OVER", True, (255, 50, 50))
            pts = font.render(f"Pontos Finais: {self.score}", True, COLOR_TEXT)
            press = font.render("Pressione R para reiniciar", True, (255, 255, 255))
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
            screen.blit(pts, (WIDTH//2 - pts.get_width()//2, HEIGHT//2))
            screen.blit(press, (WIDTH//2 - press.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()

# --- LOOP PRINCIPAL ---
game = Game()
running = True

while running:
    clock.tick(60) # 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game.state == "PLAYING":
                game.handle_input(event.key)
            elif game.state == "START":
                if event.key == pygame.K_SPACE:
                    game.state = "PLAYING"
            elif game.state == "GAMEOVER":
                if event.key == pygame.K_r:
                    game.reset_game()
                    game.state = "PLAYING"

    game.update()
    game.draw()

pygame.quit()
sys.exit()