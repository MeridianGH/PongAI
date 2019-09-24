import pygame
from pygame.locals import *
import sys
import os
import random
import neat

fps = 288

width = 600
height = 400
linethickness = 10
paddlesize = 50
paddleoffset = 20

black = (0, 0, 0)
white = (255, 255, 255)

gen = 0

auto_play_state = True


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
    def check_collision(self):
        if self.ball.top == linethickness / 2 or self.ball.bottom == (height - linethickness / 2):
            self.dir_y = self.dir_y * -1
        elif self.ball.left == linethickness / 2:
            self.dir_x = 0
            self.dir_y = 0
        elif self.ball.right == (width - linethickness / 2):
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
    def display_score(paddle_left, paddle_ai):
        score1_surf = basicfont.render(str(paddle_left.score), True, white)
        score2_surf = basicfont.render(str(paddle_ai.score), True, white)
        score1_rect = score1_surf.get_rect()
        score2_rect = score2_surf.get_rect()
        score1_rect.topright = (width / 2 - 50, 25)
        score2_rect.topleft = (width / 2 + 50, 25)
        disp.blit(score1_surf, score1_rect)
        disp.blit(score2_surf, score2_rect)

    @staticmethod
    def display_text(text, position, anchor):
        text = str(text)
        text_surf = basicfont.render(str(text), True, white)
        text_rect = text_surf.get_rect()
        setattr(text_rect, anchor, position)
        disp.blit(text_surf, text_rect)

    def display_best_fitness(self, fitness_list):
        fitness_list.sort()
        best_fitness = fitness_list[-1]
        if best_fitness < 0:
            best_fitness = str(best_fitness)
        else:
            best_fitness = ' ' + str(best_fitness)
        self.display_text('Best fitness: ' + best_fitness[:6],
                          (width / 2 + 50, height - linethickness / 2 - 25), 'bottomleft')

    # Draw Game-Over-Screen.
    @staticmethod
    def game_over_screen(player):
        game_over_font = pygame.font.Font(resource_path('freesansbold.ttf'), 90)
        lost_font = pygame.font.Font(resource_path('freesansbold.ttf'), 45)
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


# Main game.
def pong(genomes, config):
    # Increment generation counter
    global gen
    gen += 1

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
    global auto_play_state
    basicfontsize = 20
    basicfont = pygame.font.Font(resource_path('freesansbold.ttf'), basicfontsize)
    fpsclock = pygame.time.Clock()
    icon = pygame.image.load(resource_path('exe/icon.png'))
    pygame.display.set_icon(icon)
    disp = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Pong')
    run = True
    best_score = 0

    # Assign classes.
    arena = Arena()
    paddle_left = Paddle(position='left', auto_play=auto_play_state)

    # Draw all parts.
    arena.draw()
    paddle_left.draw()
    paddles_ai[0].draw()
    balls[0].draw()

    # Main game loop.
    while run:
        # PyGame events, used to get key-presses.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if paddle_left.game_over:
                        paddle_left.game_over = False
                        run = False
                    else:
                        while True:
                            event = pygame.event.wait()
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                break
                            if event.type == QUIT:
                                pygame.quit()
                                sys.exit()
                if event.key == pygame.K_SPACE:
                    if paddle_left.auto_play:
                        paddle_left.auto_play = False
                        auto_play_state = False
                    elif not paddle_left.auto_play:
                        paddle_left.auto_play = True
                        auto_play_state = True

        if len(paddles_ai) > 0 and not paddle_left.game_over:
            arena.draw()

            if paddle_left.auto_play:
                paddle_left.move_computer(balls[0])
            elif not paddle_left.game_over:
                paddle_left.move_player()
            paddle_left.draw()
            paddle_left.check_game_over(balls[0])
            paddle_left.check_score(balls[0])

            balls[0].draw()
            balls[-1].draw()

            fitness_list = []
            for x, paddle_ai in enumerate(paddles_ai):
                output = nets[x].activate((paddle_ai.paddle.y, balls[x].x, balls[x].y, balls[x].dir_x, balls[x].dir_y))
                if output[0] > 0.25:
                    # Go up
                    paddle_ai.paddle.y -= 1
                    ge[x].fitness -= 0.0013
                    ge[x].fitness = round(ge[x].fitness, 3)
                elif output[0] < -0.25:
                    # Go down
                    paddle_ai.paddle.y += 1
                    ge[x].fitness -= 0.0013
                    ge[x].fitness = round(ge[x].fitness, 3)
                elif -0.25 <= output[0] <= 0.25:
                    # Stay
                    paddle_ai.paddle.y += 0
                paddle_ai.draw()

                balls[x].check_ball_hit(paddle_ai)
                balls[x].check_ball_hit(paddle_left)
                if paddle_ai.check_score(balls[x]):
                    ge[x].fitness += 1
                paddle_ai.check_game_over(balls[x])

                balls[x].check_collision()
                balls[x].move()

                best_score = paddles_ai[0]
                fitness_list.append(ge[x].fitness)

                if paddle_ai.game_over:
                    ge[x].fitness -= 1
                    paddles_ai.pop(x)
                    nets.pop(x)
                    balls.pop(x)
                    ge.pop(x)
                    continue
                elif paddle_ai.score >= 10:
                    ge[x].fitness -= 1
                    paddles_ai.pop(x)
                    nets.pop(x)
                    balls.pop(x)
                    ge.pop(x)
                    continue

            arena.display_score(paddle_left, best_score)
            arena.display_best_fitness(fitness_list)
            arena.display_text('Gen: ' + str(gen), (50, 25), 'topleft')
            arena.display_text('Paddles: ' + str(len(paddles_ai)),
                               (50, height - linethickness/2 - 25), 'bottomleft')
        elif paddle_left.game_over:
            arena.game_over_screen(1)
        else:
            paddle_left.score = 0
            break

        # Update the screen and tick the clock once.
        pygame.display.update()
        fpsclock.tick(fps)


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


def start_ai(config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config)

    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(pong)
    print(winner)


if __name__ == '__main__':
    config_path = resource_path('neat-config.txt')
    start_ai(config_path)
