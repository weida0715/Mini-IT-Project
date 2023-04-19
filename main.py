import pygame
import pyaudio
import numpy as np
from sys import exit
from random import randint, choice

threshold = 500


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        walk_1 = pygame.image.load("./graphics/Player/player_walk_1.png").convert_alpha()
        walk_1 = pygame.transform.rotozoom(walk_1, 0, 1.5)
        walk_2 = pygame.image.load("./graphics/Player/player_walk_2.png").convert_alpha()
        walk_2 = pygame.transform.rotozoom(walk_2, 0, 1.5)
        self.walk = [walk_1, walk_2]
        self.walk_index = 0
        self.jump = pygame.image.load("./graphics/Player/jump.png").convert_alpha()
        self.jump = pygame.transform.rotozoom(self.jump, 0, 1.5)

        self.image = self.walk[self.walk_index]
        self.rect = self.image.get_rect(midbottom=(WIDTH/5.5, HEIGHT/1.5))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound("./audio/jump.mp3")
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if self.rect.bottom >= HEIGHT/1.5:
            if keys[pygame.K_SPACE] or volume >= threshold:
                self.gravity = -23.5
                self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= HEIGHT/1.5:
            self.rect.bottom = HEIGHT/1.5

    def animation_state(self):
        if self.rect.bottom < HEIGHT/1.5:
            self.image = self.jump
        else:
            self.walk_index += 0.1
            if self.walk_index >= len(self.walk):
                self.walk_index = 0
            self.image = self.walk[int(self.walk_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()

        if obstacle_type == "fly":
            fly_1 = pygame.image.load("./graphics/Fly/Fly1.png").convert_alpha()
            fly_1 = pygame.transform.rotozoom(fly_1, 0, 1.5)
            fly_2 = pygame.image.load("./graphics/Fly/Fly2.png").convert_alpha()
            fly_2 = pygame.transform.rotozoom(fly_2, 0, 1.5)
            self.frames = [fly_1, fly_2]
            y_pos = HEIGHT/3
        else:
            snail_1 = pygame.image.load("./graphics/snail/snail1.png").convert_alpha()
            snail_1 = pygame.transform.rotozoom(snail_1, 0, 1.5)
            snail_2 = pygame.image.load("./graphics/snail/snail2.png").convert_alpha()
            snail_2 = pygame.transform.rotozoom(snail_2, 0, 1.5)
            self.frames = [snail_1, snail_2]
            y_pos = HEIGHT/1.5

        x_pos = WIDTH + randint(100, 150)
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def update(self):
        self.animation_state()
        self.rect.x -= OBSTACLE_SPEED
        self.destroy()


def display_score():
    score_font = pygame.font.Font("./font/Pixeltype.ttf", 70)
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = score_font.render(f"Score: {current_time}", False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(WIDTH/2, HEIGHT/8))
    screen.blit(score_surf, score_rect)
    return current_time


def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True


# ---------------------------Constants-------------------------------------
WIDTH = 1240
HEIGHT = 600
SCREEN_SIZE = (WIDTH, HEIGHT)
OBSTACLE_SPAWN_TIME = 2000
OBSTACLE_SPEED = 8
FPS = 60

# ---------------------------Game Interface-------------------------------------
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("V-DOG")
clock = pygame.time.Clock()
font = pygame.font.Font("./font/Pixeltype.ttf", 50)
start_time = 0
score = 0
bg_music = pygame.mixer.Sound("./audio/music.wav")
bg_music.set_volume(0.1)
bg_music.play(loops=-1)

# ---------------------------Set Audio Stream-------------------------------------
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
# threshold = threshold_thread()

# ---------------------------Intro Screen-------------------------------------
player_stand = pygame.image.load("./graphics/Player/player_stand.png").convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(WIDTH/2, HEIGHT/2))

game_logo = pygame.image.load("./graphics/logo.png")
game_logo = pygame.transform.scale(game_logo, (WIDTH/2, HEIGHT))
game_logo_rect = game_logo.get_rect(center=(WIDTH/2, HEIGHT/4))

game_message = font.render("SHOUT or Press SPACE to Run", False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(WIDTH/2, HEIGHT/1.3))

# ---------------------------Game Background-------------------------------------
sky_surf = pygame.image.load("./graphics/Sky.png").convert()
sky_surf = pygame.transform.scale(sky_surf, (WIDTH, HEIGHT))
ground_surf = pygame.image.load("./graphics/ground.png").convert()
ground_surf = pygame.transform.scale(ground_surf, (WIDTH, HEIGHT))
game_wallpaper = pygame.image.load("./graphics/game-wallpaper.jpg").convert()
game_wallpaper = pygame.transform.scale(game_wallpaper, (WIDTH, HEIGHT))

# # ---------------------------Object Position-------------------------------------
# OBJECT_Y = ground_surf.get_rect().centery
# print(OBJECT_Y)

# ---------------------------Groups-------------------------------------
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

# ---------------------------Timer-------------------------------------
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, OBSTACLE_SPAWN_TIME)

# ---------------------------Game Loop-------------------------------------
game_active = False

while True:
    audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)
    volume = np.abs(audio_data).mean()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            p.terminate()
            exit()
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["fly", "snail", "snail", "snail"])))
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

    if game_active:
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, HEIGHT/1.5))

        score = display_score()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        game_active = collision_sprite()

    else:
        # screen.fill((94, 129, 162))
        screen.blit(game_wallpaper, (0, 0))
        screen.blit(player_stand, player_stand_rect)
        screen.blit(game_logo, game_logo_rect)

        score_message = font.render(f"Your score: {score}", False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(WIDTH/2, HEIGHT/1.35))

        restart_message = font.render("SHOUT or click SPACE to Restart", False, (111, 196, 169))
        restart_message_rect = restart_message.get_rect(center=(WIDTH/2, HEIGHT/1.2))

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)
            screen.blit(restart_message, restart_message_rect)

        if volume >= threshold:
            game_active = True
            start_time = int(pygame.time.get_ticks() / 1000)

    pygame.display.update()
    clock.tick(FPS)
