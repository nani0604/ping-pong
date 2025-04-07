import pygame
import random
import sys
import os
import json

# --- Constants ---
SCREEN_WIDTH    = 960
SCREEN_HEIGHT   = 720
FPS             = 60
SCORE_LIMIT     = 10
POWERUP_INTERVAL= 10000  # ms
POWERUP_DURATION= 5000   # ms
HIGH_SCORE_FILE = 'highscore.json'

# --- Colors ---
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREY   = (100, 100, 100)
RED    = (255,  50,  50)
GREEN  = (50,  255,  50)
BLUE   = (50,   50, 255)
YELLOW = (255, 255,  50)

# --- Utility Managers ---
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        for name in ('hit','score','powerup','wall'):
            path = os.path.join('sounds', f'{name}.wav')
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except FileNotFoundError:
                print(f"[WARNING] Missing sound: {path}")
                self.sounds[name] = None
    def play(self, name):
        snd = self.sounds.get(name)
        if snd:
            snd.play()

class HighScoreManager:
    def __init__(self, path=HIGH_SCORE_FILE):
        self.path = path
        self.high_score = 0
        self.load()
    def load(self):
        if os.path.exists(self.path):
            with open(self.path,'r') as f:
                data = json.load(f)
                self.high_score = data.get('high_score',0)
    def save(self):
        with open(self.path,'w') as f:
            json.dump({'high_score':self.high_score}, f)
    def update(self, score):
        if score > self.high_score:
            self.high_score = score
            self.save()

# --- Game Objects ---
class Paddle:
    def __init__(self, x, y, width=10, height=100, speed=0.5, is_ai=False, difficulty='medium'):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_speed = speed
        self.velocity = 0
        self.is_ai = is_ai
        self.difficulty = difficulty

    def move(self, direction):
        """direction: -1 up, +1 down, 0 stop"""
        self.velocity = direction * self.base_speed

    def ai_move(self, ball):
        diff_map = {'easy':0.3,'medium':0.5,'hard':0.8}
        factor = diff_map.get(self.difficulty,0.5)
        if self.rect.centery < ball.rect.centery:
            self.velocity = self.base_speed * factor
        elif self.rect.centery > ball.rect.centery:
            self.velocity = -self.base_speed * factor
        else:
            self.velocity = 0

    def update(self, dt, ball=None):
        if self.is_ai and ball:
            self.ai_move(ball)
        self.rect.y += self.velocity * dt
        # keep on screen
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)

class Ball:
    def __init__(self, size=20, speed=0.4, accel=1.05):
        self.size, self.speed, self.accel = size, speed, accel
        self.rect = pygame.Rect(0,0,size,size)
        self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        vx = random.choice([-1,1]) * random.uniform(2,4) * self.speed
        vy = random.choice([-1,1]) * random.uniform(2,4) * self.speed
        self.vel = pygame.Vector2(vx, vy)

    def update(self, dt, paddles, sounds, scoreboard):
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt

        # wall bounce
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vel.y *= -1
            sounds.play('wall')

        # paddle bounce
        for p in paddles:
            if self.rect.colliderect(p.rect):
                self.vel.x *= -1 * self.accel
                offset = (self.rect.centery - p.rect.centery) / (p.rect.height/2)
                self.vel.y += offset * 0.2 * self.speed
                sounds.play('hit')
                break

        # scoring
        if self.rect.left <= 0:
            sounds.play('score')
            scoreboard.add_point(2)
            self.reset()
        elif self.rect.right >= SCREEN_WIDTH:
            sounds.play('score')
            scoreboard.add_point(1)
            self.reset()

    def draw(self, surf):
        pygame.draw.ellipse(surf, WHITE, self.rect)

class PowerUp:
    TYPES = ['expand','shrink','speed','multiball']
    def __init__(self):
        self.type = random.choice(PowerUp.TYPES)
        self.rect = pygame.Rect(
            random.randint(200,SCREEN_WIDTH-200),
            random.randint(50, SCREEN_HEIGHT-50),
            20,20
        )
        self.active = True

    def apply(self, game):
        if self.type == 'expand':
            game.paddle2.rect.height += 50
        elif self.type == 'shrink':
            game.paddle2.rect.height = max(20, game.paddle2.rect.height - 50)
        elif self.type == 'speed':
            game.ball.speed *= 1.2
        elif self.type == 'multiball':
            game.extra_balls.append(Ball())
        game.sounds.play('powerup')
        self.active = False

    def draw(self, surf):
        color_map = {'expand':GREEN,'shrink':RED,'speed':YELLOW,'multiball':BLUE}
        if self.active:
            pygame.draw.rect(surf, color_map[self.type], self.rect)

class Scoreboard:
    def __init__(self):
        self.score = {1:0, 2:0}
        self.font  = pygame.font.SysFont('Consolas', 40)

    def add_point(self, player):
        self.score[player] += 1

    def draw(self, surf):
        txt = f"{self.score[1]}    {self.score[2]}"
        img = self.font.render(txt, True, WHITE)
        surf.blit(img, (SCREEN_WIDTH//2 - 50, 10))

class Net:
    def draw(self, surf):
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.line(surf, GREY,
                             (SCREEN_WIDTH//2, y),
                             (SCREEN_WIDTH//2, y+15), 4)

# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultimate Pong")
        self.clock    = pygame.time.Clock()
        self.sounds   = SoundManager()
        self.hs_mgr   = HighScoreManager()
        self.font     = pygame.font.SysFont('Consolas', 30)

        # LEFT = AI, RIGHT = HUMAN
        self.paddle1 = Paddle(30,  (SCREEN_HEIGHT-100)//2, is_ai=True,  difficulty='medium')
        self.paddle2 = Paddle(SCREEN_WIDTH-40, (SCREEN_HEIGHT-100)//2, is_ai=False)

        self.ball        = Ball()
        self.extra_balls = []
        self.powerups    = []
        self.scoreboard  = Scoreboard()
        self.net         = Net()

        self.running = True
        self.started = False
        self.paused  = False

        pygame.time.set_timer(pygame.USEREVENT+1, POWERUP_INTERVAL)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.started = True
                elif e.key == pygame.K_p:
                    self.paused = not self.paused
                elif e.key == pygame.K_r:
                    self.reset()
                # RIGHT paddle controls
                elif e.key == pygame.K_UP:
                    self.paddle2.move(-1)
                elif e.key == pygame.K_DOWN:
                    self.paddle2.move(1)

            elif e.type == pygame.KEYUP:
                if e.key in (pygame.K_UP, pygame.K_DOWN):
                    self.paddle2.move(0)

            elif e.type == pygame.USEREVENT+1:
                self.powerups.append(PowerUp())

    def reset(self):
        self.started = False
        self.paused  = False
        self.ball.reset()
        self.extra_balls.clear()
        self.scoreboard = Scoreboard()
        # restore paddle sizes
        self.paddle1.rect.height = 100
        self.paddle2.rect.height = 100

    def update(self, dt):
        if not self.started or self.paused:
            return

        self.paddle1.update(dt, self.ball)
        self.paddle2.update(dt)

        self.ball.update(dt, [self.paddle1, self.paddle2], self.sounds, self.scoreboard)
        for b in list(self.extra_balls):
            b.update(dt, [self.paddle1, self.paddle2], self.sounds, self.scoreboard)

        # power‑up pickup
        for pu in self.powerups:
            if pu.active and self.ball.rect.colliderect(pu.rect):
                pu.apply(self)

        # check for game over
        if (self.scoreboard.score[1] >= SCORE_LIMIT or
            self.scoreboard.score[2] >= SCORE_LIMIT):
            self.hs_mgr.update(max(self.scoreboard.score.values()))
            self.paused = True

    def draw(self):
        self.screen.fill(BLACK)
        self.net.draw(self.screen)

        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)

        self.ball.draw(self.screen)
        for b in self.extra_balls:
            b.draw(self.screen)

        for pu in self.powerups:
            pu.draw(self.screen)

        self.scoreboard.draw(self.screen)

        if not self.started:
            self._draw_center("Press SPACE to start")
        if self.paused:
            msg = f"Game Over! High Score: {self.hs_mgr.high_score}"
            self._draw_center(msg)

        pygame.display.flip()

    def _draw_center(self, text):
        img = self.font.render(text, True, WHITE)
        r   = img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        pygame.draw.rect(self.screen, BLACK, r.inflate(20,20))
        pygame.draw.rect(self.screen, WHITE, r.inflate(20,20), 2)
        self.screen.blit(img, r)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Game().run()
