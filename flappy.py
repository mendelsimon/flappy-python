import pygame
from pygame.locals import *
import random
import sys

FPS = 60

WINDOW_HEIGHT = 700
WINDOW_WIDTH = 500
GROUND_HEIGHT = 112
ground_offset = 0
PLAY_AREA_HEIGHT = WINDOW_HEIGHT - GROUND_HEIGHT
PLAYER_HEIGHT = 25
PLAYER_WIDTH = 25
# TODO calculate jump distance/frames to determine to pipe width (width = distance = frames*SPEED)
PIPE_WIDTH = 70
PIPE_HEAD_HEIGHT = 26

SPEED = 2.5
JUMP_SPEED = -7
GRAVITY = 0.4
JUMP_HEIGHT = (JUMP_SPEED ** 2) / (GRAVITY * 2)

# This area of the pipe will never have a gap
PIPE_SOLID_AREA = int(PLAY_AREA_HEIGHT / 5)
PIPE_GAP_STARTING_HEIGHT = JUMP_HEIGHT * 2.5
PIPE_GAP_MINIMUM_HEIGHT = JUMP_HEIGHT * 1.1 + PLAYER_HEIGHT

current_frame = 0
last_pipe_frame = 0  # The frame when the last pipe spawned
pipe_gap_height = PIPE_GAP_STARTING_HEIGHT

pipes = []
score = 0


class Bird:
    def __init__(self):
        self.x = (WINDOW_WIDTH / 2) - (PLAYER_WIDTH / 2)
        self.y = PLAY_AREA_HEIGHT / 4
        self.fall_speed = 0
        self.image = pygame.image.load('python.png')

    def jump(self):
        self.fall_speed = JUMP_SPEED

    def update_position(self):
        player.y += player.fall_speed
        player.fall_speed += GRAVITY


class Pipe:
    def __init__(self, gap_height):
        self.x = WINDOW_WIDTH
        self.gap_height = gap_height
        self.gap = random.randrange(PIPE_SOLID_AREA, PLAY_AREA_HEIGHT - PIPE_SOLID_AREA - int(self.gap_height))
        self.scored = False

        head_image = pygame.image.load('pipe_head.png')
        self.bottom_head_image = pygame.transform.scale(head_image, (PIPE_WIDTH, PIPE_HEAD_HEIGHT))
        self.top_head_image = pygame.transform.flip(self.bottom_head_image, False, True)
        self.body_image = pygame.image.load('pipe_body.png')

    def update_position(self):
        self.x -= SPEED


def main():
    global DISPLAY_SURFACE, FPSCLOCK, BACKGROUND_IMAGE, GROUND_IMAGE
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Python")
    BACKGROUND_IMAGE = pygame.image.load('background.png')
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WINDOW_WIDTH, PLAY_AREA_HEIGHT))
    GROUND_IMAGE = pygame.image.load('ground.png')
    GROUND_IMAGE = pygame.transform.scale(GROUND_IMAGE, (WINDOW_WIDTH, GROUND_HEIGHT))

    while True:
        play()
        game_over()


def play():
    global player, score, pipes, current_frame, pipe_gap_height
    # FIXME: reset gap height
    pipes = []
    pipe_gap_height = PIPE_GAP_STARTING_HEIGHT
    score = 0

    player = Bird()

    while True:
        # Get input
        get_input()

        # Compute changes
        player.update_position()
        spawn_pipe()
        compute_pipes()
        if check_collision():
            return  # Game over

        # Update screen
        draw_screen()

        # Tick
        current_frame += 1
        FPSCLOCK.tick(FPS)


def get_input():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key in (K_SPACE, K_UP):
                player.jump()


def spawn_pipe():
    global current_frame, last_pipe_frame, pipe_gap_height

    min_distance_to_pipe = (WINDOW_WIDTH / 3) / SPEED
    frames_since_pipe = current_frame - last_pipe_frame
    if frames_since_pipe >= min_distance_to_pipe:
        # Chance of pipe spawning is 1/(FPS), or 100% if it took too long
        if random.randrange(FPS) == 0 or frames_since_pipe > min_distance_to_pipe * 2:
            pipes.append(Pipe(pipe_gap_height))
            last_pipe_frame = current_frame

            # Make the gap smaller in future pipes
            if pipe_gap_height > PIPE_GAP_MINIMUM_HEIGHT:
                pipe_gap_height -= JUMP_HEIGHT / 50


def check_collision():
    GRACE_LENGTH = 5  # The amount of collision that won't count as collision

    # Check if player left window bounds
    if player.y + GRACE_LENGTH < 0 or player.y - GRACE_LENGTH > PLAY_AREA_HEIGHT:
        return True  # Game over

    # Check if player collided with a pipe
    for pipe in pipes:
        if pipe.x < player.x + PLAYER_WIDTH - GRACE_LENGTH and pipe.x + PIPE_WIDTH - GRACE_LENGTH > player.x:
            if player.y < pipe.gap - GRACE_LENGTH or player.y + PLAYER_HEIGHT > pipe.gap + pipe.gap_height + GRACE_LENGTH:
                return True  # Game over

    return False  # No collision


def compute_pipes():
    global score

    for index, pipe in enumerate(pipes):
        # Update position
        pipe.update_position()

        # Update score
        if pipe.x + PIPE_WIDTH <= (WINDOW_WIDTH / 2) and not pipe.scored:
            score += 1
            pipe.scored = True
            print(score)

        # Remove old pipes
        if pipe.x < 0 - PIPE_WIDTH:
            del pipes[index]


def draw_screen():
    draw_background()
    draw_player()
    draw_pipes()
    pygame.display.update()


def draw_background():
    global ground_offset
    DISPLAY_SURFACE.blit(BACKGROUND_IMAGE, (0, 0))
    DISPLAY_SURFACE.blit(GROUND_IMAGE, (-ground_offset, PLAY_AREA_HEIGHT))
    DISPLAY_SURFACE.blit(GROUND_IMAGE, (-ground_offset + WINDOW_WIDTH, PLAY_AREA_HEIGHT))
    ground_offset += SPEED
    ground_offset %= WINDOW_WIDTH


def draw_player():
    player_image = pygame.transform.scale(player.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
    DISPLAY_SURFACE.blit(player_image, (player.x, player.y))


def draw_pipes():
    for pipe in pipes:
        top_head_pos = (int(pipe.x), pipe.gap - PIPE_HEAD_HEIGHT)
        bottom_head_pos = (int(pipe.x), pipe.gap + pipe.gap_height)

        bottom_height = int(PLAY_AREA_HEIGHT - (pipe.gap + pipe.gap_height)) + 1

        top_body_pos = (int(pipe.x), 0)
        top_body_scale = (PIPE_WIDTH, pipe.gap - PIPE_HEAD_HEIGHT)
        bottom_body_pos = (int(pipe.x), pipe.gap + int(pipe.gap_height) + PIPE_HEAD_HEIGHT)
        bottom_body_scale = (PIPE_WIDTH, bottom_height - PIPE_HEAD_HEIGHT)

        top_body_image = pygame.transform.scale(pipe.body_image, top_body_scale)
        bottom_body_image = pygame.transform.scale(pipe.body_image, bottom_body_scale)

        DISPLAY_SURFACE.blit(top_body_image, top_body_pos)
        DISPLAY_SURFACE.blit(pipe.top_head_image, top_head_pos)
        DISPLAY_SURFACE.blit(pipe.bottom_head_image, bottom_head_pos)
        DISPLAY_SURFACE.blit(bottom_body_image, bottom_body_pos)


def game_over():
    DISPLAY_SURFACE.fill((250, 50, 50))
    pygame.display.update()
    pygame.time.wait(500)


if __name__ == '__main__':
    main()
