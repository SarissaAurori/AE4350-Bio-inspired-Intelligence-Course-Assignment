import pygame
import random

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 400, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minimal Flappy Bird")

# Colors
LIGHT_GRAY = (211, 211, 211)
BURGUNDY = (128, 0, 32)
VIRIDIAN_BLUE = (0, 150, 152)

# Bird properties
bird_x = 100
bird_y = HEIGHT // 2
bird_radius = 15
gravity = 0.5
lift = -5   
velocity = 0

# Gates (obstacles)
gate_width = 40
gates = []
gate_speed = 3
spawn_timer = 0

# Gates
MIN_GATE_GAP = 120
MAX_GATE_GAP = 170
MIN_SPAWN_INTERVAL = 75
MAX_SPAWN_INTERVAL = 125
SPAWN_INTERVAL = random.randint(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)

# Game settings
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
score = 0
running = True

# Screenshot counter
screenshot_count = 1

def draw_window():
    win.fill(LIGHT_GRAY)

    # Draw bird
    pygame.draw.circle(win, BURGUNDY, (int(bird_x), int(bird_y)), bird_radius)

    # Draw gates
    for gate in gates:
        x = gate["x"]
        gap_y = gate["gap_y"]
        gap_height = gate["gap_height"]
        pygame.draw.rect(win, VIRIDIAN_BLUE, (x, 0, gate_width, gap_y))
        pygame.draw.rect(win, VIRIDIAN_BLUE, (x, gap_y + gap_height, gate_width, HEIGHT - (gap_y + gap_height)))

    # Draw score
    score_text = font.render(str(score), True, (50, 50, 50))
    win.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    pygame.display.update()

while running:
    clock.tick(60)
    spawn_timer += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Screenshot with 'S'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                filename = f"screenshot_{screenshot_count}.png"
                pygame.image.save(win, filename)
                print(f"Saved {filename}")
                screenshot_count += 1 

    # Bird controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        velocity = lift

    velocity += gravity
    bird_y += velocity

    # Spawn new gate
    if spawn_timer >= SPAWN_INTERVAL:
        gap_height = random.randint(MIN_GATE_GAP, MAX_GATE_GAP)
        gap_y = random.randint(100, HEIGHT - 100 - gap_height)
        gates.append({"x": WIDTH, "gap_y": gap_y, "gap_height": gap_height, "scored": False})
        spawn_timer = 0
        SPAWN_INTERVAL = random.randint(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)

    # Move gates
    for gate in gates:
        gate["x"] -= gate_speed

    gates = [g for g in gates if g["x"] + gate_width > 0]

    # Collision detection
    for gate in gates:
        gx = gate["x"]
        gap_y = gate["gap_y"]
        gap_height = gate["gap_height"]
        if gx < bird_x + bird_radius < gx + gate_width:
            if bird_y - bird_radius < gap_y or bird_y + bird_radius > gap_y + gap_height:
                running = False

    # Out-of-bounds check
    if bird_y - bird_radius < 0 or bird_y + bird_radius > HEIGHT:
        running = False

    # Scoring
    for gate in gates:
        if not gate["scored"] and gate["x"] + gate_width < bird_x:
            score += 1
            gate["scored"] = True

    draw_window()

pygame.quit()
  