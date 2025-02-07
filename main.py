import pygame
import random
import sys
import time

pygame.init()

# Константы экрана и FPS
WIDTH, HEIGHT = 1024, 728
FPS = 60

# Настройка окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра Пианино")
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = {
    "Красный": (255, 0, 0),
    "Оранжевый": (255, 165, 0),
    "Желтый": (255, 255, 0),
    "Зеленый": (0, 255, 0),
    "Голубой": (0, 191, 255),
    "Синий": (0, 0, 255),
    "Фиолетовый": (128, 0, 128)
}

button_color = COLORS["Синий"]
text_color = BLACK

# Загрузка фонов и миниатюр
backgrounds = ["bg1.jpg", "bg2.jpg", "bg3.jpg"]
selected_background = pygame.image.load(backgrounds[0])
background_thumbnails = [pygame.transform.scale(pygame.image.load(bg), (100, 100)) for bg in backgrounds]

# Параметры кнопок
button_width = 100
button_height = 50
button_speed = 5
buttons = []

# Уровни и очки
levels = [f"Уровень {i + 1}" for i in range(10)]
unlocked_levels = 1
selected_level = None
score = 0
high_score = 0

# Флаги состояния игры
menu_open = True         # Показываем окно поражения/завершения уровня
start_menu_open = True   # Отображается стартовое меню

# Параметры музыки и тактов
bpm = 120
beat_interval = 60 / bpm
last_spawn_time = time.time()

# Список частиц для эффекта при нажатии
particles = []


def load_track(level_index):
    """
    Загружает и воспроизводит музыкальный трек в зависимости от номера уровня.
    Также задаёт BPM и интервал между появлением кнопок.
    """
    global bpm, beat_interval
    if level_index < 9:
        track_name = f"track{level_index + 1}.mp3"
        pygame.mixer.music.load(track_name)
        pygame.mixer.music.play(-1)
        bpm = 100 + level_index * 20
    else:
        track_name = f"track{random.randint(1, 9)}.mp3"
        pygame.mixer.music.load(track_name)
        pygame.mixer.music.play(-1)
        bpm = 200
    beat_interval = 60 / bpm


def draw_text(text, x, y, color, size=24):
    """
    Отрисовывает и выводит текст на экран по заданным координатам.
    """
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def spawn_button():
    """
    Создаёт новую кнопку (прямоугольник). Если выбран первый уровень,
    кнопка появляется в левом верхнем углу, иначе — в случайном месте сверху.
    """
    if selected_level == 0:
        x = 0
        y = 0
    else:
        x = random.randint(0, WIDTH - button_width)
        y = -button_height
    buttons.append(pygame.Rect(x, y, button_width, button_height))


def check_collision(mouse_pos):
    """
    Проверяет, попал ли клик мыши по кнопке.
    При попадании запускается анимация, эффект частиц и увеличивается счёт.
    Если клик не попал по кнопке, очки уменьшаются и открывается меню.
    """
    global score, menu_open
    collided = False
    for button in buttons[:]:
        if button.collidepoint(mouse_pos):
            buttons.remove(button)
            animate_button_split(button)
            spawn_particles(button.x + button_width // 2, button.y + button_height // 2)
            score += 1
            collided = True
            break

    if not collided:
        score = max(0, score - 5)
        menu_open = True


def animate_button_split(button):
    """
    Анимирует эффект «распада» кнопки.
    """
    for i in range(10):
        pygame.draw.rect(screen, button_color,
                         (button.x - i * 2, button.y - i * 2, button.width + i * 4, button.height + i * 4), 2)
        pygame.display.flip()
        pygame.time.delay(20)


def draw_menu():
    """
    Отрисовывает экран поражения.
    """
    screen.blit(selected_background, (0, 0))
    draw_text("Вы проиграли!", WIDTH // 2 - 120, HEIGHT // 2 - 100, text_color, 48)
    draw_text("Нажмите R, чтобы начать заново", WIDTH // 2 - 140, HEIGHT // 2 - 50, text_color, 32)
    pygame.display.flip()


def draw_win_menu():
    """
    Отрисовывает окно завершения уровня.
    """
    screen.blit(selected_background, (0, 0))
    draw_text("Уровень пройден!", WIDTH // 2 - 120, HEIGHT // 2 - 100, text_color, 48)
    draw_text("Нажмите N для следующего уровня", WIDTH // 2 - 160, HEIGHT // 2 - 50, text_color, 32)
    draw_text("Нажмите M для возврата в меню", WIDTH // 2 - 160, HEIGHT // 2, text_color, 32)
    pygame.display.flip()


def draw_start_menu():
    """
    Отрисовывает стартовое меню с выбором уровня, фона, цвета кнопки и шрифта.
    """
    screen.blit(selected_background, (0, 0))
    draw_text("Выберите уровень:", WIDTH // 2 - 80, HEIGHT // 2 - 220, text_color, 28)
    y_offset = 0
    for index, level in enumerate(levels[:unlocked_levels]):
        draw_text(f"{level}", WIDTH // 2 - 70, HEIGHT // 2 - 160 + y_offset, text_color, 28)
        y_offset += 50

    draw_text("Выберите фон:", WIDTH // 2 - 80, HEIGHT // 2, text_color, 28)
    for i, bg in enumerate(backgrounds):
        rect_x = WIDTH // 2 - 150 + i * 100
        rect_y = HEIGHT // 2 + 30
        screen.blit(background_thumbnails[i], (rect_x, rect_y))

    draw_text("Выберите цвет кнопки:", WIDTH // 2 - 100, HEIGHT // 2 + 150, text_color, 28)
    for i, (name, color) in enumerate(COLORS.items()):
        pygame.draw.rect(screen, color, (WIDTH // 2 - 120 + i * 80, HEIGHT // 2 + 180, 50, 50))

    draw_text("Выберите цвет шрифта:", WIDTH // 2 - 100, HEIGHT // 2 + 250, text_color, 28)
    for i, (name, color) in enumerate(COLORS.items()):
        pygame.draw.rect(screen, color, (WIDTH // 2 - 120 + i * 80, HEIGHT // 2 + 280, 50, 50))

    pygame.display.flip()


def draw_ui():
    """
    Отрисовывает игровой интерфейс (счёт и рекорд).
    """
    draw_text(f"Очки: {score}", 10, 10, text_color, 24)
    draw_text(f"Рекорд: {high_score}", 10, 40, text_color, 24)


def play_music():
    """
    Гарантирует непрерывное воспроизведение музыки.
    """
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


def update_buttons():
    """
    Обновляет позиции кнопок (перемещает их вниз) и отрисовывает.
    """
    for button in buttons:
        button.y += button_speed
        pygame.draw.rect(screen, button_color, button)


def remove_offscreen_buttons():
    """
    Удаляет кнопки, вышедшие за нижнюю границу экрана, и уменьшает очки.
    """
    global score
    for button in buttons[:]:
        if button.y > HEIGHT:
            buttons.remove(button)
            score = max(0, score - 5)


def update_difficulty():
    """
    Изменяет скорость кнопок в зависимости от текущего счёта.
    """
    global button_speed
    if score < 10:
        button_speed = 5
    elif score < 20:
        button_speed = 7
    elif score < 30:
        button_speed = 9
    else:
        button_speed = 12


def check_level_completion():
    """
    Проверяет, набраны ли необходимые очки для прохождения уровня.
    Для уровня 1 требуется 10 очков, для уровня 2 – 20, для уровня 3 – 30 и так далее.
    При достижении порога появляется окно с предложением перейти на следующий уровень.
    """
    global menu_open, unlocked_levels, selected_level, score
    if selected_level is None:
        return
    required_score = (selected_level + 1) * 10
    if score >= required_score:
        menu_open = True
        draw_win_menu()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        # Переход к следующему уровню (если он есть)
                        if selected_level + 1 < len(levels):
                            selected_level += 1
                        else:
                            selected_level = 0
                        load_track(selected_level)
                        score = 0
                        waiting = False
                        menu_open = False
                    if event.key == pygame.K_m:
                        waiting = False
                        menu_open = True
        buttons.clear()


def save_high_score_to_file(score_value, filename="highscore.txt"):
    """
    Сохраняет рекорд в файл.
    """
    with open(filename, "w") as file:
        file.write(str(score_value))


def load_high_score_from_file(filename="highscore.txt"):
    """
    Загружает рекорд из файла.
    """
    try:
        with open(filename, "r") as file:
            return int(file.read())
    except:
        return 0


def pause_game():
    """
    Ставит игру на паузу и отображает меню паузы.
    """
    paused = True
    draw_pause_menu()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
        clock.tick(FPS)


def draw_pause_menu():
    """
    Отрисовывает полупрозрачное оверлей-окно с сообщением о паузе.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    draw_text("Игра на паузе", WIDTH // 2 - 100, HEIGHT // 2 - 50, WHITE, 48)
    draw_text("Нажмите P чтобы продолжить", WIDTH // 2 - 150, HEIGHT // 2 + 10, WHITE, 32)
    pygame.display.flip()


def show_instructions():
    """
    Отображает экран с инструкциями перед началом игры.
    """
    instructions = [
        "Добро пожаловать в игру Пианино!",
        "Нажимайте на падающие кнопки, чтобы получать очки.",
        "Если вы нажмете не туда, то потеряете очки.",
        "Нажмите P чтобы поставить игру на паузу.",
        "Нажмите Q чтобы выйти из игры."
    ]
    screen.fill(BLACK)
    y_offset = 100
    for line in instructions:
        draw_text(line, 50, y_offset, WHITE, 32)
        y_offset += 50
    draw_text("Нажмите любую клавишу, чтобы начать", 50, y_offset + 20, WHITE, 28)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


def spawn_particles(x, y):
    """
    Создает эффект частиц в заданной точке (x, y).
    """
    for i in range(20):
        particle = {
            "pos": [x, y],
            "vel": [random.uniform(-2, 2), random.uniform(-2, 2)],
            "radius": random.randint(2, 5),
            "color": random.choice(list(COLORS.values()))
        }
        particles.append(particle)


def update_particles():
    """
    Обновляет положение и отрисовывает частицы.
    """
    for particle in particles[:]:
        particle["pos"][0] += particle["vel"][0]
        particle["pos"][1] += particle["vel"][1]
        particle["radius"] -= 0.1
        if particle["radius"] <= 0:
            particles.remove(particle)
        else:
            pygame.draw.circle(screen, particle["color"],
                               (int(particle["pos"][0]), int(particle["pos"][1])),
                               int(particle["radius"]))


# Загрузка рекорда из файла при старте игры
high_score = load_high_score_from_file()

# Опционально показываем инструкции перед запуском игры
show_instructions()

# Основной игровой цикл
running = True
while running:
    current_time = time.time()

    # Если открыто стартовое меню, обрабатываем его отдельно
    if start_menu_open:
        draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Выбор уровня
                for index in range(unlocked_levels):
                    button_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 160 + index * 50, 140, 30)
                    if button_rect.collidepoint(event.pos):
                        selected_level = index
                        load_track(index)
                        start_menu_open = False
                        menu_open = False
                        score = 0
                        buttons.clear()
                # Выбор фона
                for i in range(len(backgrounds)):
                    rect_x = WIDTH // 2 - 150 + i * 100
                    rect_y = HEIGHT // 2 + 30
                    if pygame.Rect(rect_x, rect_y, 100, 100).collidepoint(event.pos):
                        selected_background = pygame.image.load(backgrounds[i])
                        background_thumbnails = [pygame.transform.scale(pygame.image.load(bg), (100, 100)) for bg in backgrounds]
                # Выбор цвета кнопки и шрифта
                for name, color in COLORS.items():
                    idx = list(COLORS.keys()).index(name)
                    if pygame.Rect(WIDTH // 2 - 120 + idx * 80, HEIGHT // 2 + 180, 50, 50).collidepoint(event.pos):
                        button_color = color
                    if pygame.Rect(WIDTH // 2 - 120 + idx * 80, HEIGHT // 2 + 280, 50, 50).collidepoint(event.pos):
                        text_color = color
        clock.tick(FPS)
        continue

    # Глобальная обработка событий во время игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause_game()
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_r and menu_open:
                # Перезапуск игры
                score = 0
                buttons.clear()
                load_track(selected_level if selected_level is not None else 0)
                menu_open = False
            if event.key == pygame.K_h:
                show_instructions()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not menu_open:
                check_collision(event.pos)

    # Игровая логика, когда меню не активно
    if not menu_open:
        screen.blit(selected_background, (0, 0))
        draw_ui()
        play_music()

        # Появление кнопок в такт музыке
        if current_time - last_spawn_time > beat_interval:
            spawn_button()
            last_spawn_time = current_time

        update_difficulty()
        update_buttons()
        remove_offscreen_buttons()
        check_level_completion()
    else:
        draw_menu()

    update_particles()

    # Обновление рекорда, если текущий счёт выше, и сохранение в файл
    if score > high_score:
        high_score = score
        save_high_score_to_file(high_score)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
