import pygame
import sys
import random

WIDTH, HEIGHT = 400, 600
FPS = 60
TRACK_LENGTH = 50000 # 50km
# Tính toán vị trí người chơi
PLAYER_START = HEIGHT - 120
CAR_W, CAR_H = 50, 100
NUM_AI = 3
AI_COLORS = [(255,0,0),(0,128,255),(180,180,0),(255,128,0)]

SPEED_MIN = 6
SPEED_MAX = 19
AISPEED_MIN = 5.5
AISPEED_MAX = 18
PENALTY_FRAMES = 35

LANE_POS = [int(WIDTH//(NUM_AI+1)*(i+1) - CAR_W//2) for i in range(NUM_AI)]

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
    ais = []
    for i in range(NUM_AI):
        x0 = LANE_POS[i]
        ais.append({
            'x': x0,
            'y': PLAYER_START,
            'target_x': x0,
            'speed': random.uniform(AISPEED_MIN, AISPEED_MAX-1),
            'progress': 0.0,
            'penalty': 0,
            'offset': 0,
            'lane_cd': 0,     # cooldown đổi làn
            'block_cd': 0,    # cooldown không ép người chơi liên tục
        })
    return {
        'car_x': LANE_POS[NUM_AI//2],
        'car_y': PLAYER_START,
        'car_speed': SPEED_MIN,
        'car_progress': 0.0,
        'car_penalty': 0,
        'bg_y': 0,
        'ais': ais,
        'finished': False,
        'winner': None
    }

def get_current_lane(x):
    # Tìm làn gần nhất (tính index làn)
    return min(range(NUM_AI), key=lambda i: abs(x - LANE_POS[i]))

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
        show_text("AI siêu khó!", 220, (0,0,128))
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

    # ----- AI logic -----
    for idx, ai in enumerate(data['ais']):
        # 1. Ngẫu nhiên chuyển làn (nếu không cooldown)
        if ai['lane_cd'] <= 0 and random.random() < 0.012:  # xác suất nhỏ
            # Đổi sang làn khác ngẫu nhiên (tránh đổi trùng làn xe bạn)
            my_lane = get_current_lane(data['car_x'])
            lanes = [i for i in range(NUM_AI) if i != get_current_lane(ai['x']) and abs(i-my_lane)>0]
            if lanes:
                ai['target_x'] = LANE_POS[random.choice(lanes)]
                ai['lane_cd'] = random.randint(80, 200)  # cooldown frame
        else:
            ai['lane_cd'] = max(0, ai['lane_cd']-1)

        # 2. Né tránh (người chơi hoặc AI khác)
        for jdx, aj in enumerate(data['ais']):
            if idx == jdx: continue
            if abs(ai['x'] - aj['x']) < CAR_W:
                progress_gap = ai['progress'] - aj['progress']
                if 0 < progress_gap < 140 and ai['lane_cd']<=0:
                    # Nếu sắp va vào xe trước (cùng làn), chuyển sang làn khác
                    cur_lane = get_current_lane(ai['x'])
                    other_lanes = [i for i in range(NUM_AI) if i != cur_lane]
                    # Tránh làn xe trước (ưu tiên trái/phải ngẫu nhiên)
                    random.shuffle(other_lanes)
                    for ln in other_lanes:
                        is_clear = True
                        for kdx, ak in enumerate(data['ais']):
                            if abs(LANE_POS[ln] - ak['x']) < CAR_W and abs(ai['progress']-ak['progress']) < 140:
                                is_clear = False
                        if abs(LANE_POS[ln] - data['car_x']) < CAR_W and abs(ai['progress']-data['car_progress']) < 140:
                            is_clear = False
                        if is_clear:
                            ai['target_x'] = LANE_POS[ln]
                            ai['lane_cd'] = random.randint(50, 150)
                            break
        # Né người chơi phía trước
        if abs(ai['x'] - data['car_x']) < CAR_W:
            progress_gap = ai['progress'] - data['car_progress']
            if 0 < progress_gap < 140 and ai['lane_cd']<=0:
                cur_lane = get_current_lane(ai['x'])
                lanes = [i for i in range(NUM_AI) if i != cur_lane and abs(LANE_POS[i] - data['car_x']) > CAR_W]
                if lanes:
                    ai['target_x'] = LANE_POS[random.choice(lanes)]
                    ai['lane_cd'] = random.randint(40, 110)

        # 3. Chủ động ép khi người chơi chuẩn bị vượt (block_cd để không ép liên tục)
        if ai['block_cd']<=0:
            if (ai['progress'] < data['car_progress'] and
                0 < data['car_progress'] - ai['progress'] < 160 and
                abs(ai['x'] - data['car_x']) > 10 and
                abs(get_current_lane(ai['x']) - get_current_lane(data['car_x'])) > 0):
                ai['target_x'] = data['car_x']
                ai['block_cd'] = random.randint(100, 200)
        else:
            ai['block_cd'] -= 1

        # Di chuyển về target_x mượt mà
        if abs(ai['x'] - ai['target_x']) > 2:
            ai['x'] += 4 if ai['x'] < ai['target_x'] else -4

        # Nếu bị penalty
        if ai['penalty'] > 0:
            ai['penalty'] -= 1
            ai['speed'] = max(ai['speed'] - 0.28, AISPEED_MIN)
        else:
            # Bình thường AI linh hoạt tốc độ như trước
            if data['car_progress'] > ai['progress'] and random.random() > 0.45:
                ai['speed'] = min(ai['speed'] + random.uniform(0.10, 0.22), AISPEED_MAX)
            elif ai['progress'] > data['car_progress'] and random.random() > 0.80:
                ai['speed'] = max(ai['speed'] - random.uniform(0.04, 0.12), AISPEED_MAX)
            else:
                if random.randint(0,10) > 6:
                    ai['speed'] = min(ai['speed'] + random.uniform(0.05, 0.11), AISPEED_MAX)
                if random.randint(0,10) < 4:
                    ai['speed'] = max(ai['speed'] - random.uniform(0.04, 0.10), AISPEED_MIN)
            # Giai đoạn cuối bứt phá
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
