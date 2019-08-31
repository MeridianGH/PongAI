import pygame
from pygame.locals import *
import sys
import os
import random
import neat

fps = 288

windowwidth = 600
windowheight = 400
linethickness = 10
paddlesize = 50
paddleoffset = 20

black = (0, 0, 0)
white = (255, 255, 255)


class Ball:
    def __init__(self, x=windowwidth / 2 - linethickness / 2, y=windowheight / 2 - linethickness / 2,
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
    def check_collision(self):
        if self.ball.top == linethickness / 2 or self.ball.bottom == (windowheight - linethickness / 2):
            self.dir_y = self.dir_y * -1
        elif self.ball.left == linethickness / 2:
            self.dir_x = 0
            self.dir_y = 0
        elif self.ball.right == (windowwidth - linethickness / 2):
            self.dir_x = 0
            self.dir_y = 0

    # Check for hit on paddle and add score.
    def check_ball_hit(self, paddle):
        if self.dir_x == -1:
            if paddle.paddle.right == self.ball.left and \
                    paddle.paddle.top < self.ball.bottom and paddle.paddle.bottom > self.ball.top:
                self.dir_x = self.dir_x * -1
        elif self.dir_x == 1:
            if paddle.paddle.left == self.ball.right \
                    and paddle.paddle.top < self.ball.bottom and paddle.paddle.bottom > self.ball.top:
                self.dir_x = self.dir_x * -1


class Paddle:
    # Position for right paddle: x=windowwidth - linethickness - paddleoffset, y=windowheight / 2 - paddlesize / 2
    # Position for left  paddle: x=paddleoffset, y=windowheight / 2 - paddlesize / 2
    def __init__(self, position='right', auto_play=False):
        if position == 'left':
            x = paddleoffset
            y = windowheight / 2 - paddlesize / 2
        elif position == 'right':
            x = windowwidth - linethickness - paddleoffset
            y = windowheight / 2 - paddlesize / 2
        else:
            raise Exception('Position not defined!')
        self.position = position
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
        outline = pygame.Rect(self.paddle.x, self.paddle.y - 1, linethickness, linethickness + 2)
        pygame.draw.rect(disp, black, outline)
        pygame.draw.rect(disp, white, self.paddle)

    def check_game_over(self, ball):
        if self.position == 'left' and ball.ball.left == linethickness / 2:
            ball.dir_x = 0
            ball.dir_y = 0
            self.game_over = True
        elif self.position == 'right' and ball.ball.right == (windowwidth - linethickness / 2):
            ball.dir_x = 0
            ball.dir_y = 0
            self.game_over = True
            
    def check_score(self, ball):
        if self.position == 'left':
            if self.paddle.right == ball.ball.left and \
                    self.paddle.top < ball.ball.bottom and self.paddle.bottom > ball.ball.top:
                self.score += 1
        elif self.position == 'right':
            if self.paddle.left == ball.ball.right \
                    and self.paddle.top < ball.ball.bottom and self.paddle.bottom > ball.ball.top:
                self.score += 1
        
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


# Arena, draw background, scores and Game-Over-Screen.
class Arena:
    # Draw arena lines.
    @staticmethod
    def draw():
        disp.fill((0, 0, 0))
        # Border
        pygame.draw.rect(disp, white, ((0, 0), (windowwidth, windowheight)), linethickness)
        # Center line
        pygame.draw.line(disp, white, (int(windowwidth / 2), 0),
                         (int(windowwidth / 2), windowheight), int(linethickness / 4 + 1))

    # Draw scores.
    @staticmethod
    def display_score(paddle_left, paddle_ai):
        score1_surf = basicfont.render(str(paddle_left.score), True, white)
        score2_surf = basicfont.render(str(paddle_ai.score), True, white)
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


# Main game.
def pong(genomes, config):
    # Initialize NEAT
    nets = []
    ge = []
    paddles_ai = []
    balls = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        paddles_ai.append(Paddle())
        balls.append(Ball())
        g.fitness = 0
        ge.append(g)

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
    paddle_left = Paddle(position='left', auto_play=True)
    ball = Ball()

    # Draw all parts.
    arena.draw()
    paddle_left.draw()
    paddles_ai[0].draw()
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

        if len(paddles_ai) > 0:
            arena.draw()

            if paddle_left.auto_play:
                paddle_left.move_computer(balls[0])
            elif not paddle_left.game_over:
                paddle_left.move_player()
            paddle_left.draw()
            paddle_left.check_game_over(balls[0])
            paddle_left.check_score(balls[0])

            for x, paddle_ai in enumerate(paddles_ai):
                output = nets[x].activate((paddle_ai.paddle.y, ball.x, ball.y, ball.dir_x, ball.dir_y))
                if output[0] > 0.25:
                    # Go up
                    paddle_ai.paddle.y -= 1
                elif output[0] < -0.25:
                    # Go down
                    paddle_ai.paddle.y += 1
                elif -0.25 <= output[0] <= 0.25:
                    # Stay
                    paddle_ai.paddle.y += 0
                paddle_ai.draw()

                balls[x].check_ball_hit(paddle_ai)
                balls[x].check_ball_hit(paddle_left)
                paddle_ai.check_score(balls[x])
                paddle_ai.check_game_over(balls[x])
                ge[x].fitness = paddle_ai.score

                balls[x].check_collision()
                balls[x].move()
                balls[x].draw()

                arena.display_score(paddle_left, paddles_ai[0])

                if paddle_ai.game_over:
                    paddle_ai.score -= 1
                    ge[x].fitness = paddle_ai.score
                    paddles_ai.pop(x)
                    nets.pop(x)
                    balls.pop(x)
                    ge.pop(x)
                    continue
        else:
            paddle_left.score = 0
            break

        # Draw Game-Over-Screen.
        if paddle_left.game_over:
            arena.game_over_screen(1)

        # Update the screen and tick the clock once.
        pygame.display.update()
        fpsclock.tick(fps)


def run(config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config)

    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(pong, 50)
    print(winner)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)
