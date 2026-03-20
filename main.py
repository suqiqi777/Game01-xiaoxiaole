# pygame-ce
import pygame
import random
import sys
import asyncio
import os

# --- 基础配置 ---
WIDTH, HEIGHT = 600, 750
GRID_SIZE = 5
CELL_SIZE = 100
FPS = 30 
GAME_TIME = 60 

WHITE, GRAY, BLACK = (255, 255, 255), (220, 220, 220), (0, 0, 0)
DARK_BROWN, DEEP_RED = (90, 50, 30), (200, 50, 50)
GOLD = (255, 215, 0)

class Game:
    def __init__(self):
        pygame.init()
        # 初始化音频混合器
        try:
            pygame.mixer.init()
        except:
            print("Audio mixer could not be initialized")
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.load_assets()
        self.reset_game()

    def load_assets(self):
        self.gem_images = []
        fallback_colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]
        base_path = os.path.dirname(os.path.abspath(__file__))

        # 加载照片
        for i in range(1, 5):
            img_name = f'gem{i}.png'
            full_path = os.path.join(base_path, img_name)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                self.gem_images.append(img)
            except:
                surf = pygame.Surface((80, 80))
                surf.fill(fallback_colors[i-1])
                self.gem_images.append(surf)

        # 加载背景音乐
        self.bgm_path = os.path.join(base_path, 'bgm.mp3')
        self.music_playing = False

        # 加载字体（确保计分功能可见）
        self.font = pygame.font.SysFont("arial", 35, bold=True)
        self.big_font = pygame.font.SysFont("arial", 70, bold=True)

    def reset_game(self):
        self.board = [[random.randint(0, 3) for _ in range(5)] for _ in range(5)]
        self.selected, self.score, self.game_over = None, 0, False
        self.counting_down, self.ready_timer = True, 4
        self.last_ready_tick = pygame.time.get_ticks()
        self.game_start_time = None
        # 停止之前的音乐重新开始
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.music_playing = False
        
        while self.find_matches():
            matches = self.find_matches()
            for r, c in matches: self.board[r][c] = -1
            self.drop_and_fill()

    def find_matches(self):
        to_del = set()
        for r in range(5):
            for c in range(3):
                if self.board[r][c] == self.board[r][c+1] == self.board[r][c+2] and self.board[r][c] != -1:
                    to_del.update([(r, c), (r, c+1), (r, c+2)])
        for r in range(3):
            for c in range(5):
                if self.board[r][c] == self.board[r+1][c] == self.board[r+2][c] and self.board[r][c] != -1:
                    to_del.update([(r, c), (r+1, c), (r+2, c)])
        return list(to_del)

    def drop_and_fill(self):
        for c in range(5):
            col = [self.board[r][c] for r in range(5) if self.board[r][c] != -1]
            while len(col) < 5: col.insert(0, random.randint(0, 3))
            for r in range(5): self.board[r][c] = col[r]

    def draw(self):
        self.screen.fill(WHITE)
        now = pygame.time.get_ticks()
        
        seconds_left = GAME_TIME
        if self.counting_down:
            if now - self.last_ready_tick > 1000:
                self.ready_timer -= 1
                self.last_ready_tick = now
                if self.ready_timer <= 0:
                    self.counting_down = False
                    self.game_start_time = pygame.time.get_ticks()
                    # ✨ 游戏正式开始，播放背景音乐
                    self.play_music()
        elif not self.game_over:
            passed = (now - self.game_start_time) // 1000
            seconds_left = max(0, GAME_TIME - passed)
            if seconds_left == 0: 
                self.game_over = True
                if pygame.mixer.get_init(): pygame.mixer.music.fadeout(2000)

        # --- 绘制计分和时间 ---
        # 时间显示
        t_txt = self.font.render(f"TIME: {seconds_left}s", True, DEEP_RED if seconds_left < 10 else (50,50,50))
        self.screen.blit(t_txt, (30, 30))
        
        # 🌟 计分显示（放在右上角）
        s_txt = self.font.render(f"SCORE: {self.score}", True, (30, 120, 30))
        s_rect = s_txt.get_rect(topright=(WIDTH - 30, 30))
        self.screen.blit(s_txt, s_rect)

        # 绘制棋盘
        off_x, off_y = (WIDTH - 500) // 2, 130
        for r in range(5):
            for c in range(5):
                rect = pygame.Rect(c*100 + off_x, r*100 + off_y, 100, 100)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                self.screen.blit(self.gem_images[self.board[r][c]], self.gem_images[self.board[r][c]].get_rect(center=rect.center))
                if self.selected == (r, c):
                    pygame.draw.rect(self.screen, BLACK, rect, 4)

        if self.counting_down:
            self.draw_overlay("READY?" if self.ready_timer == 4 else str(self.ready_timer))
        elif self.game_over:
            self.draw_overlay("FINISH!", DEEP_RED, f"Total Score: {self.score}")
            
        pygame.display.flip()

    def play_music(self):
        if not self.music_playing and pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.play(-1) # -1 表示循环播放
                self.music_playing = True
            except:
                print("Music file not found or format error")

    def draw_overlay(self, txt, color=DARK_BROWN, sub=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))
        self.screen.blit(overlay, (0,0))
        m_txt = self.big_font.render(str(txt), True, color)
        self.screen.blit(m_txt, m_txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
        if sub:
            sub_t = self.font.render(sub, True, BLACK)
            self.screen.blit(sub_t, sub_t.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

    async def run(self):
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                
                # 点击逻辑
                click_detected, mx, my = False, 0, 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    mx = mx * WIDTH // self.screen.get_width()
                    my = my * HEIGHT // self.screen.get_height()
                    click_detected = True
                elif event.type == pygame.FINGERDOWN:
                    mx, my = int(event.x * WIDTH), int(event.y * HEIGHT)
                    click_detected = True

                if click_detected:
                    if self.game_over:
                        self.reset_game()
                    elif not self.counting_down:
                        off_x, off_y = (WIDTH - 500) // 2, 130
                        c, r = (mx - off_x) // CELL_SIZE, (my - off_y) // CELL_SIZE
                        if 0 <= r < 5 and 0 <= c < 5:
                            if self.selected is None: self.selected = (r, c)
                            else:
                                r1, c1 = self.selected
                                if abs(r1-r) + abs(c1-c) == 1:
                                    self.board[r1][c1], self.board[r][c] = self.board[r][c], self.board[r1][c1]
                                    matches = self.find_matches()
                                    if matches:
                                        while matches:
                                            self.score += len(matches) * 10 # ✨ 计分逻辑
                                            for mr, mc in matches: self.board[mr][mc] = -1
                                            self.drop_and_fill()
                                            matches = self.find_matches()
                                    else:
                                        self.board[r1][c1], self.board[r][c] = self.board[r][c], self.board[r1][c1]
                                self.selected = None
            
            self.clock.tick(FPS)
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(Game().run())
