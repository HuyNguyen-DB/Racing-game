import pygame
import sys
import random

WIDTH, HEIGHT = 400, 600
FPS = 60
TRACK_LENGTH = 50000
PLAYER_START = HEIGHT - 120
CAR_W, CAR_H = 50, 100
NUM_AI = 4
AI_COLORS = [(255,0,0),(0,128,255),(180,180,0),(255,128,0)]

SPEED_MIN = 6
SPEED_MAX = 19
AISPEED_MIN = 5.2     # AI nhanh hơn một chút
AISPEED_MAX = 17.5
PENALTY_FRAMES = 35

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game Python - Đua xe 5 người!")
clock = pygame.time.Clock()

bg = pygame.image.load("background.png")
car_img = pygame.image.load("car.png")
enemy_img = pygame.image.load("enemy.png")
car_img = pygame.transform.scale(car_img, (CAR_W, CAR_H))
enemy_img = pygame.transform.scale(enemy_img, (CAR_W, CAR_H))

font = pygame.font.Font("C:/Users/Admin/Downloads/UVNVan/UVNVan_B.TTF", 48)
small_font = pygame.font.Font("C:/Users/Admin/Downloads/UVNVan/UVNVan_B.TTF", 26)

def show_text(text, y, color=(255,0,0), size='big'):
    f = font if size=='big' else small_font
    s = f.render(text, True, color)
    r = s.get_rect(center=(WIDTH//2, y))
    screen.blit(s, r)

def reset():
    lane_w = WIDTH//(NUM_AI+1)
    ais = []
    for i in range(NUM_AI):
        ais.append({
            'x': lane_w*(i+1) - CAR_W//2,
            'y': PLAYER_START,
            'speed': random.uniform(AISPEED_MIN, AISPEED_MAX-1),
            'progress': 0.0,
            'penalty': 0,
            'offset': 0,
        })
    return {
        'car_x': lane_w*0 - CAR_W//2 + WIDTH//2,
        'car_y': PLAYER_START,
        'car_speed': SPEED_MIN,
        'car_progress': 0.0,
        'car_penalty': 0,
        'bg_y': 0,
        'ais': ais,
        'finished': False,
        'winner': None
    }

game_state = 'start'
data = reset()

while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if game_state == 'start' and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_state = 'play'
            data = reset()
        if game_state == 'gameover' and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state = 'play'
                data = reset()
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

    if game_state == 'start':
        screen.blit(bg, (0,0))
        show_text("RACING", 180)
        show_text("Bạn vs 4 AI!", 220, (0,0,128))
        show_text('WASD để lái - SPACE để bắt đầu', 350, color=(0,0,0), size='small')
        pygame.display.flip()
        continue

    if game_state == 'gameover':
        screen.blit(bg, (0,0))
        color = (0,180,0) if data['winner']=='player' else (180,0,0)
        msg = "YOU WIN!" if data['winner']=='player' else f"{data['winner']} WIN!"
        show_text(msg, 220, color)
        show_text('SPACE: replay   ESC: exit', 350, (0,0,0), 'small')
        pygame.display.flip()
        continue

    # --- PLAY MODE ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and data['car_x'] > 0:
        data['car_x'] -= 7
    if keys[pygame.K_d] and data['car_x'] < WIDTH-CAR_W:
        data['car_x'] += 7
    if keys[pygame.K_w]:
        data['car_speed'] = min(data['car_speed'] + 0.12, SPEED_MAX)
    if keys[pygame.K_s]:
        data['car_speed'] = max(data['car_speed'] - 0.15, SPEED_MIN)
    if data['car_penalty'] > 0:
        data['car_penalty'] -= 1
        data['car_speed'] = max(data['car_speed'] - 0.35, SPEED_MIN)
    data['car_progress'] += data['car_speed']

    # AI logic
    for idx, ai in enumerate(data['ais']):
        # Nếu bị phạt
        if ai['penalty'] > 0:
            ai['penalty'] -= 1
            ai['speed'] = max(ai['speed'] - 0.28, AISPEED_MIN)
        else:
            # Nếu bạn vượt lên, AI tăng tốc mạnh hơn
            if data['car_progress'] > ai['progress'] and random.random() > 0.45:
                ai['speed'] = min(ai['speed'] + random.uniform(0.10, 0.22), AISPEED_MAX)
            # Nếu AI vượt bạn, AI vẫn cố giữ tốc độ
            elif ai['progress'] > data['car_progress'] and random.random() > 0.80:
                ai['speed'] = max(ai['speed'] - random.uniform(0.04, 0.12), AISPEED_MAX)
            else:
                # Bình thường AI tăng giảm nhẹ
                if random.randint(0,10) > 6:
                    ai['speed'] = min(ai['speed'] + random.uniform(0.05, 0.11), AISPEED_MAX)
                if random.randint(0,10) < 4:
                    ai['speed'] = max(ai['speed'] - random.uniform(0.04, 0.10), AISPEED_MIN)

        # Giai đoạn cuối (bứt phá)
        if (TRACK_LENGTH - ai['progress'] < 500) and ai['speed'] < AISPEED_MAX:
            ai['speed'] = min(ai['speed'] + 0.18, AISPEED_MAX + 1.5)

        ai['progress'] += ai['speed']
        if abs(ai['offset']) > 0:
            ai['x'] += int(ai['offset'])
            ai['offset'] = 0

    # Vẽ nền cuộn
    data['bg_y'] = int(data['car_progress']) % HEIGHT
    screen.blit(bg, (0, data['bg_y']-HEIGHT))
    screen.blit(bg, (0, data['bg_y']))

    # Vẽ AI
    lane_w = WIDTH//(NUM_AI+1)
    for idx, ai in enumerate(data['ais']):
        ai_offset = int(PLAYER_START - (ai['progress'] - data['car_progress']))
        if 0 < ai_offset < HEIGHT:
            color = AI_COLORS[idx]
            ai_surface = enemy_img.copy()
            ai_surface.fill(color, special_flags=pygame.BLEND_ADD)
            screen.blit(ai_surface, (ai['x'], ai_offset))
        if not data['finished'] and ai['progress'] >= TRACK_LENGTH:
            data['finished'] = True
            data['winner'] = f"AI#{idx+1}"
            game_state = 'gameover'

    # Vẽ xe người chơi
    player_y = PLAYER_START
    screen.blit(car_img, (data['car_x'], player_y))

    # Kiểm tra về đích người chơi
    if not data['finished'] and data['car_progress'] >= TRACK_LENGTH:
        data['finished'] = True
        data['winner'] = "player"
        game_state = 'gameover'

    # Va chạm hai chiều
    for idx, ai in enumerate(data['ais']):
        ai_offset = int(PLAYER_START - (ai['progress'] - data['car_progress']))
        # Người chơi tông vào AI
        if (player_y < ai_offset + CAR_H < player_y + 30 and
            abs(data['car_x'] - ai['x']) < CAR_W and
            ai['progress'] > data['car_progress'] and
            not ai['penalty'] and not data['car_penalty']):
            data['car_penalty'] = PENALTY_FRAMES
            ai['penalty'] = PENALTY_FRAMES
            ai['offset'] = random.choice([-15, 15])
        # AI tông vào đuôi người chơi
        if (ai_offset < player_y + CAR_H < ai_offset + 30 and
            abs(data['car_x'] - ai['x']) < CAR_W and
            data['car_progress'] > ai['progress'] and
            not ai['penalty'] and not data['car_penalty']):
            data['car_penalty'] = PENALTY_FRAMES
            ai['penalty'] = PENALTY_FRAMES
            ai['offset'] = random.choice([-15, 15])

    # HUD
    show_text(f"Tốc độ: {int(data['car_speed']*10)} km/h", 30, (0,0,0), 'small')
    show_text("WASD để lái | Đua tốc độ!", 570, (0,0,0), 'small')
    show_text(f"Đường đua: {int(min(data['car_progress'], TRACK_LENGTH))}/{TRACK_LENGTH}m", 60, (0,0,0), 'small')
    pygame.display.flip()
