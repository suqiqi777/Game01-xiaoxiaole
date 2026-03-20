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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.load_assets()
        self.reset_game()

    def load_assets(self):
        self.gem_images = []
        fallback_colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]
        base_path = os.path.dirname(os.path.abspath(__file__))

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

        self.font = pygame.font.SysFont("arial", 40, bold=True)
        self.big_font = pygame.font.SysFont("arial", 70, bold=True)

    def reset_game(self):
        self.board = [[random.randint(0, 3) for _ in range(5)] for _ in range(5)]
        self.selected, self.score, self.game_over = None, 0, False
        self.counting_down, self.ready_timer = True, 4
        self.last_ready_tick = pygame.time.get_ticks()
        self.game_start_time = None
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
        elif not self.game_over:
            passed = (now - self.game_start_time) // 1000
            seconds_left = max(0, GAME_TIME - passed)
            if seconds_left == 0: self.game_over = True

        t_txt = self.font.render(f"TIME: {seconds_left}s", True, DEEP_RED if seconds_left < 10 else (50,50,50))
        self.screen.blit(t_txt, (30, 25))
        off_x, off_y = (WIDTH - 500) // 2, 120
        for r in range(5):
            for c in range(5):
                rect = pygame.Rect(c*100 + off_x, r*100 + off_y, 100, 100)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                self.screen.blit(self.gem_images[self.board[r][c]], self.gem_images[self.board[r][c]].get_rect(center=rect.center))
                if self.selected == (r, c):
                    pygame.draw.rect(self.screen, BLACK, rect, 6)

        if self.counting_down:
            self.draw_overlay("START" if self.ready_timer == 4 else str(self.ready_timer))
        elif self.game_over:
            self.draw_overlay("TIME UP!", DEEP_RED, f"Score: {self.score}")
        pygame.display.flip()

    def draw_overlay(self, txt, color=DARK_BROWN, sub=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0,0))
        m_txt = self.big_font.render(str(txt), True, color)
        self.screen.blit(m_txt, m_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    async def run(self):
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset_game()
                    elif not self.counting_down:
                        # ✨ 关键：自动适配手机点击坐标
                        mx, my = pygame.mouse.get_pos()
                        mx = mx * WIDTH // self.screen.get_width()
                        my = my * HEIGHT // self.screen.get_height()
                        
                        off_x, off_y = (WIDTH - 500) // 2, 120
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
                                            self.score += len(matches) * 10
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
