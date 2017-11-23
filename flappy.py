import pygame
from pygame.locals import *
import random
import sys

FPS = 60

WINDOW_HEIGHT = 700
WINDOW_WIDTH = 500
PLAYER_HEIGHT = 25
PLAYER_WIDTH = 25
# TODO calculate jump distance/frames to determine to pipe width (width = distance = frames*SPEED)
PIPE_WIDTH = 70

SPEED = 2.5
JUMP_SPEED = -7
GRAVITY = 0.4
JUMP_HEIGHT = (JUMP_SPEED ** 2) / (GRAVITY * 2)

# This area of the pipe will never have a gap
PIPE_SOLID_AREA = WINDOW_HEIGHT / 5


pipes = []
score = 0


class Bird:
    def __init__(self):
        self.x = (WINDOW_WIDTH / 2) - (PLAYER_WIDTH / 2)
        self.y = WINDOW_HEIGHT / 4
        self.fall_speed = 0

    def jump(self):
        self.fall_speed = JUMP_SPEED


class Pipe:
    def __init__(self, gap_height):
        self.x = WINDOW_WIDTH
        self.gap_height = gap_height
        self.gap = random.randrange(PIPE_SOLID_AREA, WINDOW_HEIGHT - PIPE_SOLID_AREA - int(self.gap_height))
        self.scored = False


def main():
    global DISPLAY_SURFACE, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Python")

    while True:
        play()
        game_over()


def play():
    global player, score, pipes
    pipes = []
    current_frame = 0
    last_pipe_frame = 0  # The frame when the last pipe spawned
    score = 0

    gap_height = JUMP_HEIGHT * 2.5

    player = Bird()

    while True:
        # ========= #
        # Get input #
        # ========= #
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

        # =============== #
        # Compute changes #
        # =============== #

        # Computer player position
        player.y += player.fall_speed
        player.fall_speed += GRAVITY

        # Spawn pipe
        min_distance_to_pipe = (WINDOW_WIDTH / 3) / SPEED
        frames_since_pipe = current_frame - last_pipe_frame
        if frames_since_pipe >= min_distance_to_pipe:
            # Chance of pipe spawning is 1/(FPS/2) or
            if random.randrange(FPS / 2) == 0 or frames_since_pipe > min_distance_to_pipe * 2:
                pipes.append(Pipe(gap_height))
                last_pipe_frame = current_frame
                if gap_height > JUMP_HEIGHT * 1.5:
                    gap_height -= JUMP_HEIGHT / 50

        # Compute pipe positions
        for index, pipe in enumerate(pipes):
            pipe.x -= SPEED
            if pipe.x + PIPE_WIDTH <= (WINDOW_WIDTH / 2) and not pipe.scored:
                score += 1
                pipe.scored = True
                print(score)

            if pipe.x < 0 - PIPE_WIDTH:
                del pipes[index]

        # Check for collisions
        GRACE_LENGTH = 2  # The amount of collision that won't count as collision
        if player.y + GRACE_LENGTH < 0 or player.y - GRACE_LENGTH > WINDOW_HEIGHT:
            return  # Game over

        for pipe in pipes:
            if pipe.x < player.x + PLAYER_WIDTH - GRACE_LENGTH and pipe.x + PIPE_WIDTH - GRACE_LENGTH > player.x:
                if player.y < pipe.gap - GRACE_LENGTH or player.y > pipe.gap + pipe.gap_height + GRACE_LENGTH:
                    return  # Game over

        # ============= #
        # Update screen #
        # ============= #
        draw_screen()

        # Tick
        current_frame += 1
        FPSCLOCK.tick(FPS)


def draw_screen():
    draw_background()
    draw_player()
    draw_pipes()
    pygame.display.update()


def draw_background():
    DISPLAY_SURFACE.fill((50, 50, 50))


def draw_player():
    player_rect = (player.x, player.y, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(DISPLAY_SURFACE, (255, 0, 0), player_rect)


def draw_pipes():
    for pipe in pipes:
        pipe_top = (pipe.x, 0, PIPE_WIDTH, pipe.gap)
        pipe_bottom_height = WINDOW_HEIGHT - pipe.gap + pipe.gap_height
        pipe_bottom = (pipe.x, pipe.gap + pipe.gap_height, PIPE_WIDTH, pipe_bottom_height)

        pygame.draw.rect(DISPLAY_SURFACE, (100, 250, 100), pipe_top)
        pygame.draw.rect(DISPLAY_SURFACE, (100, 250, 100), pipe_bottom)


def game_over():
    DISPLAY_SURFACE.fill((250, 50, 50))
    pygame.display.update()
    pygame.time.wait(500)


if __name__ == '__main__':
    main()
