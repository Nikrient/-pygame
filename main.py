import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра Пианино")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

lanes = [WIDTH // 4 - 50, WIDTH // 2 - 50, WIDTH * 3 // 4 - 50]
button_width = 100
button_height = 50
button_speed = 5
buttons = []

levels = ["Уровень 1", "Уровень 2", "Уровень 3", "Уровень 4", "Уровень 5"]
selected_level = None
score = 0
menu_open = True
start_menu_open = True
spawn_rate = 50
high_score = 0


def load_track(level_index):
    track_name = f"track{level_index + 1}.mp3"
    pygame.mixer.music.load(track_name)
    pygame.mixer.music.play(-1)


def draw_text(text, x, y, color, size=24):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def spawn_button():
    lane = random.choice(lanes)
    y = -button_height
    buttons.append(pygame.Rect(lane, y, button_width, button_height))


def check_collision(mouse_pos):
    global score, menu_open, high_score
    for button in buttons:
        if button.collidepoint(mouse_pos):
            buttons.remove(button)
            score += 1
            return
    if score > high_score:
        high_score = score
    menu_open = True


def draw_menu():
    global high_score
    screen.fill(GRAY)
    draw_text("Игра окончена", WIDTH // 2 - 80, HEIGHT // 2 - 100, RED, 48)
    draw_text("Нажмите R, чтобы начать заново", WIDTH // 2 - 140, HEIGHT // 2, BLACK, 32)
    draw_text("Нажмите M, чтобы вернуться в меню", WIDTH // 2 - 160, HEIGHT // 2 + 50, BLACK, 32)
    draw_text(f"Рекорд: {high_score}", WIDTH // 2 - 100, HEIGHT // 2 + 100, BLACK, 32)
    pygame.display.flip()


def draw_start_menu():
    screen.fill(GRAY)
    draw_text("Выберите уровень:", WIDTH // 2 - 80, HEIGHT // 2 - 120, RED, 28)

    y_offset = 0
    for index, level in enumerate(levels):
        draw_text(f"{level}", WIDTH // 2 - 70, HEIGHT // 2 - 60 + y_offset, BLACK, 28)
        y_offset += 50

    pygame.display.flip()


running = True
while running:
    if start_menu_open:
        draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for index, level in enumerate(levels):
                    button_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 60 + index * 50, 140, 30)
                    if button_rect.collidepoint(event.pos):
                        selected_level = level
                        load_track(index)
                        start_menu_open = False
                        menu_open = False
        continue

    if menu_open:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    menu_open = False
                    buttons.clear()
                    score = 0
                    button_speed = 5
                    spawn_rate = 50
                if event.key == pygame.K_m:
                    menu_open = False
                    buttons.clear()
                    selected_level = None
                    start_menu_open = True
        continue
    screen.fill(WHITE)
    draw_text(f"Счёт: {score}", 10, 10, BLACK, 24)
    draw_text(f"Рекорд: {high_score}", WIDTH - 150, 10, BLACK, 24)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            check_collision(event.pos)

    if random.randint(1, spawn_rate) == 1:
        spawn_button()

    button_speed += 0.002
    for button in buttons:
        button.y += button_speed
        if button.y > HEIGHT:
            if score > high_score:
                high_score = score
            menu_open = True

    for button in buttons:
        pygame.draw.rect(screen, BLUE, button)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
