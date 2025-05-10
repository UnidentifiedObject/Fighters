import pygame
import random
import math

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 900
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 350
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Big Ball vs Small Balls")

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (1, 255, 1)
YELLOW = (200, 200, 1)
BIG_BALL_COLOR = (100, 200, 255)
SMALL_BALL_COLORS = [(255, 100, 100), (100, 255, 100), (255, 255, 100), (255, 150, 255)]

# --- Game Parameters ---
FPS = 60
BIG_RADIUS = 25
SMALL_RADIUS = 10
PROJECTILE_LIMIT = 4  # Maximum projectiles allowed
COOLDOWN_TIME = 120  # Cooldown time in frames (3 seconds at 60 FPS)
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)

# --- Ball Classes ---
class Ball:
    def __init__(self, x, y, vx, vy, radius, color):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vx, vy)
        self.radius = radius
        self.color = color
        self.spawn_cooldown = 0
        self.spawn_count = 0

    def move(self):
        self.pos += self.vel

    def bounce_off_wall(self):
        dist_to_center = self.pos.distance_to(CENTER)
        if dist_to_center + self.radius >= RADIUS:
            to_center = (self.pos - pygame.math.Vector2(CENTER)).normalize()
            self.vel = self.vel.reflect(to_center)
            self.pos = pygame.math.Vector2(CENTER) + to_center * (RADIUS - self.radius)
            if self.spawn_cooldown == 0:
                self.spawn_cooldown = 90
                if random.random() < 0.65:
                    return True
        return False

    def reset_spawn_cooldown(self):
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1

    def is_colliding(self, other):
        return self.pos.distance_to(other.pos) < self.radius + other.radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

# --- Projectile Ball ---
class ProjectileBall(Ball):
    def __init__(self, x, y, vx, vy, radius, color):
        super().__init__(x, y, vx, vy, radius, color)
        self.bounced = False

    def bounce_off_wall(self):
        dist_to_center = self.pos.distance_to(CENTER)
        if dist_to_center + self.radius >= RADIUS:
            return True  # Remove on first bounce
        return False

# --- Big Ball with Controls ---
class PlayerBall(Ball):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, 0, 0, radius, color)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        acceleration = pygame.math.Vector2(0, 0)
        speed = 0.4

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            acceleration.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            acceleration.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            acceleration.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            acceleration.y += speed

        self.vel += acceleration

    def apply_friction(self):
        self.vel *= 0.95

# --- Initialize Main Menu ---
def main_menu():
    running = True
    selected_ball_count = 200  # Default value for the number of small balls

    while running:
        WIN.fill((0, 0, 0))
        title_font = pygame.font.SysFont(None, 64)
        title_text = title_font.render("Big Ball vs Small Balls", True, WHITE)
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

        # Instructions for quick selection
        quick_select_text = font.render("Use +/- to increase/decrease by 50", True, WHITE)
        WIN.blit(quick_select_text, (WIDTH // 2 - quick_select_text.get_width() // 2, HEIGHT // 2 - 40))

        # Instructions for player to select max small balls
        select_text = font.render(f"Select Max Small Balls: {selected_ball_count}", True, YELLOW)
        WIN.blit(select_text, (WIDTH // 2 - select_text.get_width() // 2, HEIGHT // 2))

        # Instructions to confirm and start the game
        start_text = font.render("Press Enter to Start", True, GREEN)
        WIN.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 1.5))

        # New Spacebar instruction
        spacebar_text = font.render("Press Space to Shoot!", True, WHITE)
        WIN.blit(spacebar_text, (WIDTH // 2 - spacebar_text.get_width() // 2, HEIGHT // 1.1))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:  # Increase by 50
                    selected_ball_count = min(1000, selected_ball_count + 50)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:  # Decrease by 50
                    selected_ball_count = max(100, selected_ball_count - 50)
                elif event.key == pygame.K_RETURN:  # Start game
                    return selected_ball_count

# --- Start Game with User Selection ---
MAX_SMALL_BALLS = main_menu()  # Get user-selected ball count
if MAX_SMALL_BALLS is None:
    pygame.quit()

# --- Initialize Balls ---
CENTER = (WIDTH // 2, HEIGHT // 2)
big_ball = PlayerBall(CENTER[0], CENTER[1], BIG_RADIUS, BIG_BALL_COLOR)

small_balls = []
for i in range(5):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(4, 6)
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    offset_radius = random.uniform(30, 60)
    x = CENTER[0] + math.cos(angle) * offset_radius
    y = CENTER[1] + math.sin(angle) * offset_radius
    small_balls.append(Ball(x, y, vx, vy, SMALL_RADIUS, random.choice(SMALL_BALL_COLORS)))

# --- Projectiles List ---
projectiles = []
projectile_count = PROJECTILE_LIMIT
cooldown_counter = 0  # Track the cooldown for reloading projectiles

# --- Main Loop ---
clock = pygame.time.Clock()
running = True
winner = None

while running:
    clock.tick(FPS)
    WIN.fill((0, 0, 0))
    pygame.draw.circle(WIN, WHITE, CENTER, RADIUS, 2)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if projectile_count > 0 and cooldown_counter == 0 and big_ball.vel.length() != 0:
                dir_vec = big_ball.vel.normalize()
                proj_speed = 6
                proj = ProjectileBall(
                    big_ball.pos.x, big_ball.pos.y,
                    dir_vec.x * proj_speed, dir_vec.y * proj_speed,
                    BIG_RADIUS, (255, 1, 1)
                )
                projectiles.append(proj)
                projectile_count -= 1

    # --- Big Ball Logic ---
    big_ball.handle_input()
    big_ball.apply_friction()
    big_ball.move()
    big_ball.bounce_off_wall()

    # --- Small Balls Logic ---
    new_small_balls = []
    for ball in small_balls:
        ball.move()
        if ball.bounce_off_wall():
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            new_ball = Ball(ball.pos.x, ball.pos.y, vx, vy, SMALL_RADIUS, random.choice(SMALL_BALL_COLORS))
            new_small_balls.append(new_ball)
        ball.reset_spawn_cooldown()
    small_balls.extend(new_small_balls)

    # --- Projectile Logic ---
    updated_projectiles = []
    for proj in projectiles:
        proj.move()
        if not proj.bounce_off_wall():
            updated_projectiles.append(proj)
        # Eat small balls
        small_balls = [b for b in small_balls if not proj.is_colliding(b)]
    projectiles = updated_projectiles

    # --- Check Cooldown for Projectiles ---
    if projectile_count == 0:
        cooldown_counter += 1
        if cooldown_counter >= COOLDOWN_TIME:
            projectile_count = PROJECTILE_LIMIT  # Reload projectiles after cooldown
            cooldown_counter = 0  # Reset cooldown

    # --- Collision Detection ---
    small_balls = [b for b in small_balls if not big_ball.is_colliding(b)]

    # --- Win Conditions ---
    if len(small_balls) == 0:
        winner = "Big Ball Wins!"
        # Draw final frame
        WIN.fill((0, 0, 0))
        pygame.draw.circle(WIN, WHITE, CENTER, RADIUS, 2)
        ball_count_text = font.render(f"Small Balls: {len(small_balls)}", True, WHITE)
        WIN.blit(ball_count_text, (WIDTH // 2 - ball_count_text.get_width() // 2, 10))
        proj_text = font.render(f"Projectiles: {projectile_count}", True, WHITE)
        WIN.blit(proj_text, (10, 10))
        if projectile_count == 0:
            cooldown_text = font.render(f"Cooldown: {cooldown_counter // 60}s", True, WHITE)
            WIN.blit(cooldown_text, (10, 40))
        big_ball.draw(WIN)
        for ball in small_balls:
            ball.draw(WIN)
        for proj in projectiles:
            proj.draw(WIN)
        pygame.display.update()
        pygame.time.delay(2000)
        running = False

    elif len(small_balls) >= MAX_SMALL_BALLS:
        winner = "Small Balls Win!"
        # Draw final frame
        WIN.fill((0, 0, 0))
        pygame.draw.circle(WIN, WHITE, CENTER, RADIUS, 2)
        ball_count_text = font.render(f"Small Balls: {len(small_balls)}", True, WHITE)
        WIN.blit(ball_count_text, (WIDTH // 2 - ball_count_text.get_width() // 2, 10))
        proj_text = font.render(f"Projectiles: {projectile_count}", True, WHITE)
        WIN.blit(proj_text, (10, 10))
        if projectile_count == 0:
            cooldown_text = font.render(f"Cooldown: {cooldown_counter // 60}s", True, WHITE)
            WIN.blit(cooldown_text, (10, 40))
        big_ball.draw(WIN)
        for ball in small_balls:
            ball.draw(WIN)
        for proj in projectiles:
            proj.draw(WIN)
        pygame.display.update()
        pygame.time.delay(2000)
        running = False

    # --- Draw Everything ---
    ball_count_text = font.render(f"Small Balls: {len(small_balls)}", True, WHITE)
    WIN.blit(ball_count_text, (WIDTH // 2 - ball_count_text.get_width() // 2, 10))

    # Display available projectiles and cooldown
    proj_text = font.render(f"Projectiles: {projectile_count}", True, WHITE)
    WIN.blit(proj_text, (10, 10))
    if projectile_count == 0:
        cooldown_text = font.render(f"Cooldown: {cooldown_counter // 60}s", True, WHITE)
        WIN.blit(cooldown_text, (10, 40))

    big_ball.draw(WIN)
    for ball in small_balls:
        ball.draw(WIN)
    for proj in projectiles:
        proj.draw(WIN)

    pygame.display.update()

# --- Game Over ---
WIN.fill((0, 0, 0))
font = pygame.font.SysFont(None, 64)
text = font.render(winner, True, WHITE)
WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))

# exit instruction message with "Q" for exit
exit_font = pygame.font.SysFont(None, 30)  # Smaller font size
exit_text = exit_font.render("Press Q to exit", True, WHITE)
WIN.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 40))

pygame.display.update()

# Wait for the player to press Q to exit
waiting_for_input = True
while waiting_for_input:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting_for_input = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            waiting_for_input = False

pygame.quit()
