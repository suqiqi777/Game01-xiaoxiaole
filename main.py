import pygame
import random
import sys
import asyncio
import os

# --- 1. 基础配置 ---
WIDTH, HEIGHT = 600, 750
GRID_SIZE = 5
CELL_SIZE = 100
FPS = 30 
GAME_TIME = 60 

# 颜色定义
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
DARK_BROWN = (90, 50, 30)
DEEP_RED = (200, 50, 50)
BLACK = (0, 0, 0)

class Game:
    def __init__(self):
        pygame.init()
        # 尝试初始化音效，网页版如果失败会自动跳过
        try:
            pygame.mixer.init()
        except:
            pass
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Photo Match-3")
        self.clock = pygame.time.Clock()
        
        self.load_assets()
        self.reset_game()

    def load_assets(self):
        """核心：加载照片逻辑，增加网页路径兼容性"""
        self.gem_images = []
        # 备选颜色（万一照片加载失败，用颜色代替，防止Loading卡死）
        fallback_colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]
        
        # 获取当前脚本所在文件夹的绝对路径
        base_path = os.path.dirname(os.path.abspath(__file__))

        for i in range(1, 5):
            img_name = f'gem{i}.png'
            full_path = os.path.join(base_path, img_name)
            
            try:
                # 尝试加载
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                self.gem_images.append(img)
                print(f"Successfully loaded: {img_name}")
            except Exception as e:
                # 容错：画一个彩色方块
                print(f"Load failed for {img_name}, using fallback color. Error: {e}")
                surf = pygame.Surface((80, 80))
                surf.fill(fallback_colors[i-1])
                self.gem_images.append(surf)

        # 加载字体
        try:
            self.font = pygame.font.SysFont("arial", 40, bold=True)
            self.big_font = pygame.font.SysFont("arial", 70, bold=True)
        except:
            self.font = pygame.font.Font(None, 40)
            self.big_font = pygame.font.Font(None, 70)

    def reset_game(self):
        """重置游戏状态"""
        self.board = [[random.randint(0, 3) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.score = 0
        self.game_over = False
        self.counting_down = True
        self.ready_timer = 4
        self.last_ready_tick = pygame.time.get_ticks()
        self.game_start_time = None
        
        # 消除初始的三连
        while self.find_matches():
            matches = self.find_matches()
            for r, c in matches: self.board[r][c] = -1
            self.drop_and_fill()

    def find_matches(self):
        """检查棋盘上的三连"""
        to_del = set()
        # 横向
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE - 2):
                if self.board[r][c] == self.board[r][c+1] == self.board[r][c+2] and self.board[r][c] != -1:
                    to_del.update([(r, c), (r, c+1), (r, c+2)])
        # 纵向
        for r in range(GRID_SIZE - 2):
            for c in range(GRID_SIZE):
                if self.board[r][c] == self.board[r+1][c] == self.board[r+2][c] and self.board[r][c] != -1:
                    to_del.update([(r, c), (r+1, c), (r+2, c)])
        return list(to_del)

    def drop_and_fill(self):
        """掉落并填充新照片"""
        for c in range(GRID_SIZE):
            col = [self.board[r][c] for r in range(GRID_SIZE) if self.board[r][c] != -1]
            while len(col) < GRID_SIZE:
                col.insert(0, random.randint(0, 3))
            for r in range(GRID_SIZE):
                self.board[r][c] = col[r]

    def draw(self):
        """绘制画面"""
        self.screen.fill(WHITE)
        now = pygame.time.get_ticks()
        
        # 计时逻辑
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

        # 画 UI
        t_txt = self.font.render(f"TIME: {seconds_left}s", True, DEEP_RED if seconds_left < 10 else (50, 50, 50))
        s_txt = self.font.render(f"SCORE: {self.score}", True, (50, 50, 50))
        self.screen.blit(t_txt, (30, 25))
        self.screen.blit(s_txt, s_txt.get_rect(topright=(WIDTH - 30, 25)))

        # 画棋盘
        off_x, off_y = (WIDTH - 500) // 2, 120
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(c*CELL_SIZE + off_x, r*CELL_SIZE + off_y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                # 绘制照片
                img_rect = self.gem_images[self.board[r][c]].get_rect(center=rect.center)
                self.screen.blit(self.gem_images[self.board[r][c]], img_rect)
                if self.selected == (r, c):
                    pygame.draw.rect(self.screen, BLACK, rect, 6)

        # 状态层
        if self.counting_down:
            self.draw_overlay("START" if self.ready_timer == 4 else str(self.ready_timer))
        elif self.game_over:
            self.draw_overlay("TIME UP!", DEEP_RED, f"Final: {self.score}")

        pygame.display.flip()

    def draw_overlay(self, main_txt, color=DARK_BROWN, sub_txt=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0,0))
        m_txt = self.big_font.render(str(main_txt), True, color)
        self.screen.blit(m_txt, m_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        if sub_txt:
            s_txt = self.font.render(str(sub_txt), True, BLACK)
            self.screen.blit(s_txt, s_txt.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))

    async def run(self):
        """异步主循环"""
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset_game()
                    elif not self.counting_down:
                        mx, my = pygame.mouse.get_pos()
                        off_x, off_y = (WIDTH - 500) // 2, 120
                        c, r = (mx - off_x) // CELL_SIZE, (my - off_y) // CELL_SIZE
                        if 0 <= r < 5 and 0 <= c < 5:
                            if self.selected is None:
                                self.selected = (r, c)
                            else:
                                r1, c1 = self.selected
                                if abs(r1-r) + abs(c1-c) == 1:
                                    self.board[r1][c1], self.board[r][c] = self.board[r][c], self.board[r1][c1]
                                    matches = self.find_matches()
                                    if matches:
                                        # 消除逻辑
                                        while matches:
                                            self.score += len(matches) * 10
                                            for mr, mc in matches: self.board[mr][mc] = -1
                                            self.drop_and_fill()
                                            matches = self.find_matches()
                                    else:
                                        # 换回来
                                        self.board[r1][c1], self.board[r][c] = self.board[r][c], self.board[r1][c1]
                                self.selected = None
            
            self.clock.tick(FPS)
            await asyncio.sleep(0) # 👈 关键：给浏览器喘息时间

if __name__ == "__main__":
    asyncio.run(Game().run())
