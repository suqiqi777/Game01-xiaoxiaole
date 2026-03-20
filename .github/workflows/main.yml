import pygame
import random
import sys
import asyncio

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
        for i in range(1, 5):
            img = pygame.image.load(f'gem{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (80, 80))
            self.gem_images.append(img)
        self.font = pygame.font.SysFont("arial", 40, bold=True)
        self.big_font = pygame.font.SysFont("arial", 70, bold=True)

    def reset_game(self):
        self.board = [[random.randint(0, 3) for _ in range(5)] for _ in range(5)]
        self.selected, self.score, self.game_over = None, 0, False
        self.counting_down, self.ready_timer = True, 4
        self.last_ready_tick = pygame.time.get_ticks()
        self.game_start_time = None

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

        # 画文字和棋盘
        t_txt = self.font.render(f"TIME: {seconds_left}s", True, DEEP_RED if seconds_left < 10 else (50,50,50))
        self.screen.blit(t_txt, (30, 25))
        for r in range(5):
            for c in range(5):
                rect = pygame.Rect(c*100+50, r*100+120, 100, 100)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                self.screen.blit(self.gem_images[self.board[r][c]], self.gem_images[self.board[r][c]].get_rect(center=rect.center))

        if self.counting_down:
            self.draw_overlay("START" if self.ready_timer==4 else str(self.ready_timer))
        elif self.game_over:
            self.draw_overlay("TIME UP!", DEEP_RED, f"Final: {self.score}")
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
                if event.type == pygame.MOUSEBUTTONDOWN and self.game_over: self.reset_game()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(Game().run())
