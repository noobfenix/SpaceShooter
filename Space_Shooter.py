import pygame
import random
import os
import sys

# Initialize Pygame
pygame.init()

# Function to determine the base path
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load fonts
font_small = pygame.font.Font(resource_path("Font/kenvector_future_thin.ttf"), 24)
font_large = pygame.font.Font(resource_path("Font/kenvector_future.ttf"), 48)
font_medium = pygame.font.Font(resource_path("Font/kenvector_future_thin.ttf"), 36)

# Load background
backgrounds = [
    pygame.image.load(resource_path("BG/black.png")),
    pygame.image.load(resource_path("BG/blue.png")),
    pygame.image.load(resource_path("BG/darkPurple.png")),
    pygame.image.load(resource_path("BG/purple.png"))
]
current_background = random.choice(backgrounds)

class Player(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = pygame.image.load(resource_path(f"Player/player_{color}.png"))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        return Laser(self.rect.centerx, self.rect.top)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(resource_path("Laser/laser_red.png"))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.choice(["big", "medium", "small", "tiny"])
        color = random.choice(["brown", "grey"])
        self.image = pygame.image.load(resource_path(f"Meteor/meteor_{size}_{color}.png"))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(1, 5)
        self.speed_x = random.randint(-1, 1)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.player = Player("green")
        self.all_sprites = pygame.sprite.Group(self.player)
        self.lasers = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()

        self.score = 0
        self.lives = 5
        self.game_over = False
        self.running = False

        # Load sound effects
        self.zap_sound = pygame.mixer.Sound(resource_path("Sounds/zap.wav"))
        self.twotone_sound = pygame.mixer.Sound(resource_path("Sounds/twoTone.wav"))
        self.lose_sound = pygame.mixer.Sound(resource_path("Sounds/lose.wav"))
        self.laser_sound = pygame.mixer.Sound(resource_path("Sounds/laser1.wav"))

    def init(self):
        self.score = 0
        self.lives = 5
        self.game_over = False
        self.all_sprites = pygame.sprite.Group(self.player)
        self.lasers = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()

    def start(self):
        self.init()
        self.running = True

    def stop(self):
        self.running = False

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        surface.blit(text_obj, text_rect)

    def update(self):
        scaled_background = pygame.transform.scale(current_background, (WIDTH, HEIGHT))
        window.blit(scaled_background, (0, 0))

        if not self.game_over:
            self.all_sprites.update()
            self.meteors.update()
            self.lasers.update()

            # Spawn new meteors
            if random.randint(1, 60) == 1:
                self.meteors.add(Meteor())

            # Check for collisions
            for laser in self.lasers:
                hits = pygame.sprite.spritecollide(laser, self.meteors, True)
                for hit in hits:
                    self.score += 10
                    self.zap_sound.play()
                    laser.kill()

            hits = pygame.sprite.spritecollide(self.player, self.meteors, True)
            for hit in hits:
                self.lives -= 1
                self.twotone_sound.play()
                if self.lives <= 0:
                    self.game_over = True
                    self.lose_sound.play()

            # Draw everything
            self.all_sprites.draw(window)
            self.meteors.draw(window)
            self.lasers.draw(window)

            # Draw UI
            self.draw_text(f"Score: {self.score}", font_small, (255, 255, 255), window, 60, 20)

            for i in range(self.lives):
                life_image = pygame.image.load(resource_path(f"Life/life_{i+1}.png"))
                window.blit(life_image, (WIDTH - 30 * (i + 1), 10))

        if self.game_over:
            self.draw_text("GAME OVER", font_large, (255, 0, 0), window, WIDTH // 2, HEIGHT // 2 - 50)
            self.draw_text("Press 'S' to Restart", font_medium, (255, 255, 255), window, WIDTH // 2, HEIGHT // 2 + 10)
            self.draw_text("Press 'P' to Quit", font_medium, (255, 255, 255), window, WIDTH // 2, HEIGHT // 2 + 50)
            self.draw_text("Made By Noobfenix", font_small, (255, 255, 255), window, WIDTH // 2, HEIGHT - 30)

        pygame.display.flip()

    def show_start_screen(self):
        window.fill((0, 0, 0))
        self.draw_text("Space Shooter", font_large, (255, 255, 255), window, WIDTH // 2, HEIGHT // 2 - 100)
        self.draw_text("Press 'S' to Start", font_medium, (255, 255, 255), window, WIDTH // 2, HEIGHT // 2)
        self.draw_text("Press 'P' to Quit", font_medium, (255, 255, 255), window, WIDTH // 2, HEIGHT // 2 + 50)
        self.draw_text("Made By Noobfenix", font_small, (255, 255, 255), window, WIDTH // 2, HEIGHT - 30)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        waiting = False
                    if event.key == pygame.K_p:
                        pygame.quit()
                        sys.exit()

# Create a game instance
game = Game()

clock = pygame.time.Clock()

# Show the start screen
game.show_start_screen()

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.running:
                game.lasers.add(game.player.shoot())
                game.laser_sound.play()
            elif event.key == pygame.K_s:  # Start or restart the game
                game.start()
            elif event.key == pygame.K_p:  # Stop the game with 'P' key
                game.stop()

    if game.running:
        game.update()
