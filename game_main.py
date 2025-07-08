import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game - Chọn chế độ")
clock = pygame.time.Clock()
font = pygame.font.Font("C:/Users/Admin/Downloads/UVNVan/UVNVan_B.TTF", 40)
small_font = pygame.font.Font("C:/Users/Admin/Downloads/UVNVan/UVNVan_B.TTF", 28)

MODES = ["DỄ (EASY)", "THƯỜNG (NORMAL)", "KHÓ (HARD)"]
MODE_COLORS = [(60,180,60), (255,185,30), (255,70,70)]

def show_menu(selected_idx):
    screen.fill((200, 220, 245))
    title = font.render("CHỌN CHẾ ĐỘ CHƠI", True, (30,60,140))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    for i, mode in enumerate(MODES):
        color = MODE_COLORS[i] if selected_idx == i else (100, 100, 100)
        txt = font.render(mode, True, color)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200 + 70*i))
    screen.blit(small_font.render("↑↓ hoặc 1-2-3: chọn, ENTER: bắt đầu", True, (0,0,0)), (45, 480))
    pygame.display.flip()

def main_menu():
    idx = 0
    while True:
        clock.tick(30)
        show_menu(idx)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]: idx = (idx+1)%3
                if event.key in [pygame.K_UP, pygame.K_w]: idx = (idx-1)%3
                if event.key == pygame.K_1: idx = 0
                if event.key == pygame.K_2: idx = 1
                if event.key == pygame.K_3: idx = 2
                if event.key == pygame.K_RETURN: return idx

# ------------ GAME LOGIC IMPORT OR DEFINE HERE -------------
def play_easy():
    import racing_ez   # hoặc: exec(open('racing_ez.py').read())
def play_normal():
    import racing_normal
def play_hard():
    import racing_hard

# ------------ MAIN -------------
if __name__ == '__main__':
    while True:
        mode = main_menu()
        if mode == 0:
            play_easy()
        elif mode == 1:
            play_normal()
        elif mode == 2:
            play_hard()
