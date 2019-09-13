import pygame
from pygame.locals import *
import sys
import random

fps = 144

width = 600
height = 400
linethickness = 10
paddlesize = 50
paddleoffset = 20

black = (0, 0, 0)
white = (255, 255, 255)


class Ball:
    def __init__(self, x=width / 2 - linethickness / 2, y=height / 2 - linethickness / 2,
                 dir_x=1, dir_y=random.choice((-1, 1))):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.ball = pygame.Rect(self.x, self.y, linethickness, linethickness)

    # Move the Ball in the current direction.
    def move(self):
        self.x += self.dir_x
        self.y += self.dir_y
        self.ball = pygame.Rect(self.x, self.y, linethickness, linethickness)

    # Draw the Ball on the screen.
    def draw(self):
        pygame.draw.rect(disp, white, self.ball)

    # Check for collisions with walls and set paddle-state.
    def check_collision(self, paddle_left, paddle_right):
        if self.ball.top == linethickness / 2 or self.ball.bottom == (height - linethickness / 2):
            self.dir_y = self.dir_y * -1
        elif self.ball.left == linethickness / 2:
            self.dir_x = 0
            self.dir_y = 0
            paddle_left.game_over = True
        elif self.ball.right == (width - linethickness / 2):
            self.dir_x = 0
            self.dir_y = 0
            paddle_right.game_over = True

    # Check for hit on paddle and add score.
    def check_ball_hit(self, paddle_left, paddle_right):
        if self.dir_x == -1 and paddle_left.paddle.right == self.ball.left and \
                paddle_left.paddle.top < self.ball.bottom and paddle_left.paddle.bottom > self.ball.top:
            self.dir_x = self.dir_x * -1
            paddle_left.score += 1
        elif self.dir_x == 1 and paddle_right.paddle.left == self.ball.right and paddle_right.paddle.top < self.ball.bottom and \
                paddle_right.paddle.bottom > self.ball.top:
            self.dir_x = self.dir_x * -1
            paddle_right.score += 1


class Paddle:
    # Position for right paddle: x=width - linethickness - paddleoffset, y=height / 2 - paddlesize / 2
    # Position for left  paddle: x=paddleoffset, y=height / 2 - paddlesize / 2
    def __init__(self, position='right', auto_play=False):
        if position == 'left':
            x = paddleoffset
            y = height / 2 - paddlesize / 2
        elif position == 'right':
            x = width - linethickness - paddleoffset
            y = height / 2 - paddlesize / 2
        else:
            raise Exception('Position not defined!')
        self.position = position
        self.paddle = pygame.Rect(x, y, linethickness, paddlesize)
        self.score = 0
        self.game_over = False
        self.auto_play = auto_play

    # Draw the paddle on the screen.
    def draw(self):
        if self.paddle.bottom > height - linethickness / 2:
            self.paddle.bottom = height - linethickness / 2
        elif self.paddle.top < linethickness / 2:
            self.paddle.top = linethickness / 2
        outline = pygame.Rect(self.paddle.x, self.paddle.y - 1, linethickness, linethickness + 2)
        pygame.draw.rect(disp, black, outline)
        pygame.draw.rect(disp, white, self.paddle)

    def check_game_over(self, ball):
        if self.position == 'left' and ball.ball.left == linethickness / 2:
            ball.dir_x = 0
            ball.dir_y = 0
            self.game_over = True
        elif self.position == 'right' and ball.ball.right == (width - linethickness / 2):
            ball.dir_x = 0
            ball.dir_y = 0
            self.game_over = True

    def check_score(self, ball):
        if self.position == 'left':
            if self.paddle.right == ball.ball.left and \
                    self.paddle.top < ball.ball.bottom and self.paddle.bottom > ball.ball.top:
                self.score += 1
                return True
        elif self.position == 'right':
            if self.paddle.left == ball.ball.right \
                    and self.paddle.top < ball.ball.bottom and self.paddle.bottom > ball.ball.top:
                self.score += 1
                return True
        else:
            return False

    # Move player with arrow keys.
    def move_player(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            self.paddle.y -= 1
        if keys[K_DOWN]:
            self.paddle.y += 1

    # Computer, that follows the ball on the y-axis.
    def move_computer(self, ball):
        if ball.dir_x == 1:
            if self.paddle.centery < (height / 2):
                self.paddle.y += 1
            elif self.paddle.centery > (height / 2):
                self.paddle.y -= 1
        elif ball.dir_x == -1:
            if self.paddle.centery < ball.ball.centery:
                self.paddle.y += 1
            else:
                self.paddle.y -= 1


# Arena, draw background, scores and Game-Over-Screen.
class Arena:
    # Draw arena lines.
    @staticmethod
    def draw():
        disp.fill((0, 0, 0))
        # Border
        pygame.draw.rect(disp, white, ((0, 0), (width, height)), linethickness)
        # Center line
        pygame.draw.line(disp, white, (int(width / 2), 0),
                         (int(width / 2), height), int(linethickness / 4 + 1))

    # Draw scores.
    @staticmethod
    def display_score(paddle_left, paddle_right):
        score1_surf = basicfont.render(str(paddle_left.score), True, white)
        score2_surf = basicfont.render(str(paddle_right.score), True, white)
        score1_rect = score1_surf.get_rect()
        score2_rect = score2_surf.get_rect()
        score1_rect.topleft = (150, 25)
        score2_rect.topright = (width - 150, 25)
        disp.blit(score1_surf, score1_rect)
        disp.blit(score2_surf, score2_rect)

    # Draw Game-Over-Screen.
    @staticmethod
    def game_over_screen(player):
        game_over_font = pygame.font.Font('freesansbold.ttf', 90)
        lost_font = pygame.font.Font('freesansbold.ttf', 45)
        box = pygame.Rect(0, 0, width / 2, height / 2)
        box.center = (width / 2, height / 2)
        game_surf = game_over_font.render('GAME', True, black)
        over_surf = game_over_font.render('OVER', True, black)
        lost_surf = lost_font.render('Player {0} lost!'.format(player), True, white)
        game_rect = game_surf.get_rect()
        over_rect = over_surf.get_rect()
        lost_rect = lost_surf.get_rect()
        game_rect.midbottom = (width / 2, height / 2)
        over_rect.midtop = (width / 2, height / 2)
        lost_rect.midtop = (width / 2, box.midbottom[1] + 10)
        pygame.draw.rect(disp, white, box)
        disp.blit(game_surf, game_rect)
        disp.blit(over_surf, over_rect)
        disp.blit(lost_surf, lost_rect)


# Main game, used for testing.
def pong():
    # Initialize game.
    pygame.init()
    global disp
    global basicfont, basicfontsize
    basicfontsize = 20
    basicfont = pygame.font.Font('freesansbold.ttf', basicfontsize)
    fpsclock = pygame.time.Clock()
    disp = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Pong')

    # Assign classes.
    arena = Arena()
    paddle_left = Paddle(position='left', auto_play=False)
    paddle_right = Paddle(position='right', auto_play=True)
    ball = Ball()

    # Draw all parts.
    arena.draw()
    paddle_left.draw()
    paddle_right.draw()
    ball.draw()

    # Main game loop.
    while True:
        # PyGame events, used to get key-presses.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            break
                if event.key == pygame.K_SPACE:
                    if paddle_left.auto_play:
                        paddle_left.auto_play = False
                    else:
                        paddle_left.auto_play = True

        # Move paddles.
        if paddle_left.auto_play:
            paddle_left.move_computer(ball)
        elif not paddle_left.game_over:
            paddle_left.move_player()
        paddle_right.move_computer(ball)

        # Move ball and check for collisions or hits.
        ball.move()
        ball.check_collision(paddle_left, paddle_right)
        ball.check_ball_hit(paddle_left, paddle_right)

        # Draw all parts and display score.
        arena.draw()
        paddle_left.draw()
        paddle_right.draw()
        ball.draw()
        arena.display_score(paddle_left, paddle_right)

        # Draw Game-Over-Screen.
        if paddle_left.game_over:
            arena.game_over_screen(1)
        elif paddle_right.game_over:
            arena.game_over_screen(2)

        # Update the screen and tick the clock once.
        pygame.display.update()
        fpsclock.tick(fps)


if __name__ == '__main__':
    pong()
