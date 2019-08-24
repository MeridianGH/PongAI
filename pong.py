import pygame
from pygame.locals import *
import sys
import random

fps = 144

windowwidth = 600
windowheight = 400
linethickness = 10
paddlesize = 50
paddleoffset = 20

black = (0, 0, 0)
white = (255, 255, 255)


class Ball:
    def __init__(self, x=windowwidth/2-linethickness/2, y=windowheight/2-linethickness/2,
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
    def check_collision(self, paddle1, paddle2):
        if self.ball.top == linethickness / 2 or self.ball.bottom == (windowheight - linethickness / 2):
            self.dir_y = self.dir_y * -1
        elif self.ball.left == linethickness / 2:
            self.dir_x = 0
            self.dir_y = 0
            paddle1.game_over = True
        elif self.ball.right == (windowwidth - linethickness / 2):
            self.dir_x = 0
            self.dir_y = 0
            paddle2.game_over = True

    # Check for hit on paddle and add score.
    def check_ball_hit(self, paddle1, paddle2):
        if self.dir_x == -1 and paddle1.paddle.right == self.ball.left and paddle1.paddle.top < self.ball.bottom and \
                paddle1.paddle.bottom > self.ball.top:
            self.dir_x = self.dir_x * -1
            paddle1.score += 1
        elif self.dir_x == 1 and paddle2.paddle.left == self.ball.right and paddle2.paddle.top < self.ball.bottom and \
                paddle2.paddle.bottom > self.ball.top:
            self.dir_x = self.dir_x * -1
            paddle2.score += 1


# Left Paddle, Player or PC
class PaddlePC:
    def __init__(self, x=paddleoffset, y=windowheight/2-paddlesize/2, auto_play=True):
        self.paddle = pygame.Rect(x, y, linethickness, paddlesize)
        self.score = 0
        self.game_over = False
        self.auto_play = auto_play

    # Draw the paddle on the screen.
    def draw(self):
        if self.paddle.bottom > windowheight - linethickness / 2:
            self.paddle.bottom = windowheight - linethickness / 2
        elif self.paddle.top < linethickness / 2:
            self.paddle.top = linethickness / 2
        pygame.draw.rect(disp, white, self.paddle)

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
            if self.paddle.centery < (windowheight / 2):
                self.paddle.y += 1
            elif self.paddle.centery > (windowheight / 2):
                self.paddle.y -= 1
        elif ball.dir_x == -1:
            if self.paddle.centery < ball.ball.centery:
                self.paddle.y += 1
            else:
                self.paddle.y -= 1


# Right paddle, currently just Computer, soon to be controlled by AI
class PaddleAI:
    def __init__(self, x=windowwidth-linethickness-paddleoffset, y=windowheight/2-paddlesize/2):
        self.paddle = pygame.Rect(x, y, 10, 50)
        self.score = 0
        self.game_over = False

    # Draw the paddle to the screen.
    def draw(self):
        if self.paddle.bottom > windowheight - linethickness / 2:
            self.paddle.bottom = windowheight - linethickness / 2
        elif self.paddle.top < linethickness / 2:
            self.paddle.top = linethickness / 2
        pygame.draw.rect(disp, white, self.paddle)

    # Move the paddle to follow the ball.
    def move_ai(self, ball):
        if ball.dir_x == -1:
            if self.paddle.centery < (windowheight / 2):
                self.paddle.y += 1
            elif self.paddle.centery > (windowheight / 2):
                self.paddle.y -= 1
        elif ball.dir_x == 1:
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
        pygame.draw.rect(disp, white, ((0, 0), (windowwidth, windowheight)), linethickness)
        # Center line
        pygame.draw.line(disp, white, (int(windowwidth/2), 0),
                         (int(windowwidth/2), windowheight), int(linethickness/4 + 1))

    # Draw scores.
    @staticmethod
    def display_score(paddle1, paddle2):
        score1_surf = basicfont.render(str(paddle1.score), True, white)
        score2_surf = basicfont.render(str(paddle2.score), True, white)
        score1_rect = score1_surf.get_rect()
        score2_rect = score2_surf.get_rect()
        score1_rect.topleft = (150, 25)
        score2_rect.topright = (windowwidth - 150, 25)
        disp.blit(score1_surf, score1_rect)
        disp.blit(score2_surf, score2_rect)

    # Draw Game-Over-Screen.
    @staticmethod
    def game_over_screen(player):
        game_over_font = pygame.font.Font('freesansbold.ttf', 90)
        lost_font = pygame.font.Font('freesansbold.ttf', 45)
        box = pygame.Rect(0, 0, windowwidth / 2, windowheight / 2)
        box.center = (windowwidth / 2, windowheight / 2)
        game_surf = game_over_font.render('GAME', True, black)
        over_surf = game_over_font.render('OVER', True, black)
        lost_surf = lost_font.render('Player {0} lost!'.format(player), True, white)
        game_rect = game_surf.get_rect()
        over_rect = over_surf.get_rect()
        lost_rect = lost_surf.get_rect()
        game_rect.midbottom = (windowwidth / 2, windowheight / 2)
        over_rect.midtop = (windowwidth / 2, windowheight / 2)
        lost_rect.midtop = (windowwidth / 2, box.midbottom[1] + 10)
        pygame.draw.rect(disp, white, box)
        disp.blit(game_surf, game_rect)
        disp.blit(over_surf, over_rect)
        disp.blit(lost_surf, lost_rect)


# Main game, used for testing.
def main():
    # Initialize game.
    pygame.init()
    global disp
    global basicfont, basicfontsize
    basicfontsize = 20
    basicfont = pygame.font.Font('freesansbold.ttf', basicfontsize)
    fpsclock = pygame.time.Clock()
    disp = pygame.display.set_mode((windowwidth, windowheight))
    pygame.display.set_caption('Pong')

    # Assign classes.
    arena = Arena()
    paddle1 = PaddlePC()
    paddle2 = PaddleAI()
    ball = Ball()

    # Draw all parts.
    arena.draw()
    paddle1.draw()
    paddle2.draw()
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
                    if paddle1.auto_play:
                        paddle1.auto_play = False
                    else:
                        paddle1.auto_play = True

        # Move paddles.
        if paddle1.auto_play:
            paddle1.move_computer(ball)
        elif not paddle1.game_over:
            paddle1.move_player()
        paddle2.move_ai(ball)

        # Move ball and check for collisions or hits.
        ball.move()
        ball.check_collision(paddle1, paddle2)
        ball.check_ball_hit(paddle1, paddle2)

        # Draw all parts and display score.
        arena.draw()
        paddle1.draw()
        paddle2.draw()
        ball.draw()
        arena.display_score(paddle1, paddle2)

        # Draw Game-Over-Screen.
        if paddle1.game_over:
            arena.game_over_screen(1)

        # Update the screen and tick the clock once.
        pygame.display.update()
        fpsclock.tick(fps)


if __name__ == '__main__':
    main()
