import pygame
import random
import sys

# Constants
RES = (1280, 740)
TILE_SIZE = 100
TILE = TILE_SIZE - 2
cols = RES[0] // TILE_SIZE
rows = RES[1] // TILE_SIZE

# Colors
WHITE = pygame.Color('white')

# import maze game
pygame.init()
sc = pygame.display.set_mode(RES)
pygame.display.set_caption('Maze Generator')
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load('megumin2.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE/2, TILE/2 - (TILE/2)/2500 * 300))
        self.rect = self.image.get_rect(center=(x, y))
        self.gold = 0
        self.speed = 3
        self.health = 1000
        self.alive = True

    def move(self):
        speed = self.speed
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if self.health <= 0:
            self.alive = False
        if self.alive:
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed

            # Check for collisions with walls
            if dx != 0 or dy != 0:
                new_rect = self.rect.move(dx, dy)
                if new_rect.left < 0:
                    dx = -self.rect.left
                if new_rect.right > int(RES[0] / TILE_SIZE) * TILE_SIZE:
                    dx = int(RES[0] / TILE_SIZE) * TILE_SIZE - self.rect.right
                if new_rect.top < 0:
                    dy = -self.rect.top
                if new_rect.bottom > int(RES[1] / TILE_SIZE) * TILE_SIZE:
                    dy = int(RES[1] / TILE_SIZE) * TILE_SIZE - self.rect.bottom
                for row in grid:
                    for cell in row:
                        if cell.walls[0] and new_rect.colliderect(pygame.Rect(cell.x, cell.y - 1, TILE_SIZE, 1)):
                            dy = 0 if dy > 0 else dy
                        if cell.walls[1] and new_rect.colliderect(pygame.Rect(cell.x + TILE_SIZE, cell.y, 1, TILE_SIZE)):
                            dx = 0 if dx < 0 else dx
                        if cell.walls[2] and new_rect.colliderect(pygame.Rect(cell.x, cell.y + TILE_SIZE, TILE_SIZE, 1)):
                            dy = 0 if dy < 0 else dy
                        if cell.walls[3] and new_rect.colliderect(pygame.Rect(cell.x - 1, cell.y, 1, TILE_SIZE)):
                            dx = 0 if dx > 0 else dx
                self.rect.move_ip(dx, dy)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Barrier:
    def __init__(self, x, y, passable, deal_dmg):
        self.passable = passable
        if self.passable:
            self.health = 100
        self.deal_dmg = deal_dmg
        if self.deal_dmg:
            self.image = pygame.transform.scale(pygame.image.load('spike_ball1.png').convert_alpha(), (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, TILE_SIZE/2, TILE_SIZE/2)

    def collision(self, player):
        bounce_back = 3
        acceleration = 2
        if self.rect.colliderect(player.rect):
            player.rect.y += bounce_back
            bounce_back += acceleration
            if self.deal_dmg:
                player.health -= 3

    def draw(self):
        if self.deal_dmg:
            sc.blit(self.image, self.rect)
        else:
            pygame.draw.rect(sc, (255, 0, 0), self.rect)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visited = False
        self.walls = [True, True, True, True]   #tương đương với top right bottom left
        self.x = col*TILE_SIZE
        self.y = row * TILE_SIZE

    def draw(self):
        x = self.col * TILE_SIZE
        y = self.row * TILE_SIZE

#vẽ những đường màu trắng trắng mà mình thấy trong cái mê cung
        if self.walls[0]:  #top
            pygame.draw.line(sc, WHITE, (x, y), (x + TILE_SIZE, y), 2)
        if self.walls[1]:  #right
            pygame.draw.line(sc, WHITE, (x + TILE_SIZE, y), (x + TILE_SIZE, y + TILE_SIZE), 2)
        if self.walls[2]:  #bottom
            pygame.draw.line(sc, WHITE, (x + TILE_SIZE, y + TILE_SIZE), (x, y + TILE_SIZE), 2)
        if self.walls[3]:  #left
            pygame.draw.line(sc, WHITE, (x, y + TILE_SIZE), (x, y), 2)

    def draw_current_cell(self):
        x = self.col * TILE_SIZE  # tính tọa đô của x
        y = self.row * TILE_SIZE  # tính tọa độ của y
        pygame.draw.rect(sc, pygame.Color('red'), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

    def check_neighbors(self):
        neighbors = []
        top = grid[self.row - 1][self.col] if self.row > 0 else None
        right = grid[self.row][self.col + 1] if self.col < cols - 1 else None
        bottom = grid[self.row + 1][self.col] if self.row < rows - 1 else None
        left = grid[self.row][self.col - 1] if self.col > 0 else None

        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)

        if neighbors:
            return random.choice(neighbors)
        else:
            return None


def remove_walls(current, next):
    dx = current.col - next.col
    if dx == 1:
        current.walls[3] = False
        next.walls[1] = False
    elif dx == -1:
        current.walls[1] = False
        next.walls[3] = False

    dy = current.row - next.row
    if dy == 1:
        current.walls[0] = False
        next.walls[2] = False
    elif dy == -1:
        current.walls[2] = False
        next.walls[0] = False


def draw_grid():
    for cell in grid_cells:
        cell.draw()


def get_font(size):
    return pygame.font.Font('font.ttf', size)


def draw_current():
    current_cell.draw_current_cell()


def draw_health_bar(health):
    ratio = health/1000
    white_bar = pygame.Rect(0, 0, 300, 24)
    red_bar = pygame.Rect(2, 2, 296*ratio, 20)
    pygame.draw.rect(sc, (120, 117, 108), white_bar)
    pygame.draw.rect(sc, (255, 0, 0), red_bar)


def remove_treasure(treasure):
    if treasure in treasure_rects:
        treasure_rects.remove(treasure)


def check_collision(treasure, walls):
    for wall in walls:
        if treasure.colliderect(wall):
            return True
    return False


def draw_gold_bar(gold, treasure_count):
    ratio = gold / (100 * treasure_count)
    gold_measure = pygame.Rect(100, 720, 1080 * ratio, 20)
    gold_original = pygame.Rect(100, 720, 1080, 20)
    pygame.draw.rect(sc, (255, 255, 255), gold_original)
    pygame.draw.rect(sc, (153, 98, 0), gold_measure)


grid = [[Cell(row, col) for col in range(cols)] for row in range(rows)]
current_cell = grid[0][0]  # Start from top-left corner
stack = []
colors, color = [], 40
grid_cells = [cell for row in grid for cell in row]  # Flattened list of all cells
adventurer1 = Player(25, 20)
treasure_numbers = random.randint(2, 5)
treasure_rects = []
barrier1 = Barrier(300, 300, False, True)
barrier2 = Barrier(500, 300, False, False)
for i in range(treasure_numbers):
    x = random.randint(100, int(RES[0] / TILE_SIZE) * TILE_SIZE - 30)
    y = random.randint(100, int(RES[1] / TILE_SIZE) * TILE_SIZE - 30)
    treasure_rects.append(pygame.Rect(x, y, 20, 20))

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    sc.fill(pygame.Color('black'))
    draw_grid()
    current_cell.visited = True
    [pygame.draw.rect(sc, colors[i], (cell.x * TILE + 5, cell.y * TILE + 5,
                                      TILE - 10, TILE - 10), border_radius=12) for i, cell in enumerate(stack)]
    next_cell = current_cell.check_neighbors()
    for treasure_rect in treasure_rects:
        pygame.draw.rect(sc, (240, 204, 5), treasure_rect)
        if adventurer1.rect.colliderect(treasure_rect):
            adventurer1.gold += 100
            remove_treasure(treasure_rect)
    draw_gold_bar(adventurer1.gold, treasure_numbers)
    if next_cell:
        next_cell.visited = True
        stack.append(current_cell)
        colors.append((min(color, 255), 10, 100))
        color += 1
        remove_walls(current_cell, next_cell)
        current_cell = next_cell
    elif stack:
        current_cell = stack.pop()
    draw_health_bar(adventurer1.health)
    adventurer1.draw(sc)
    adventurer1.move()
    barrier1.collision(adventurer1)
    barrier1.draw()
    barrier2.collision(adventurer1)
    barrier2.draw()
    if not adventurer1.alive:
        game_over_text = get_font(30).render('Game Over', True, (123, 200, 65))
        sc.blit(game_over_text, (RES[0]/2, RES[1]/2))
    pygame.display.flip()
    clock.tick(100)
    pygame.display.update()
