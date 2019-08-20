import pygame
from pygame.locals import *
import sys

fps = 144

windowwidth = 600
windowheight = 400
linethickness = 10
paddlesize = 50
paddleoffset = 20

black = (0, 0, 0)
white = (255, 255, 255)


def draw_arena():
    displaysurface.fill((0, 0, 0))
    # Border
    pygame.draw.rect(displaysurface, white, ((0, 0), (windowwidth, windowheight)), linethickness)
    # Center line
    pygame.draw.line(displaysurface, white, (int(windowwidth/2), 0),
                     (int(windowwidth/2), windowheight), int(linethickness/4 + 1))


def draw_paddle(paddle):
    if paddle.bottom > windowheight - linethickness / 2:
        paddle.bottom = windowheight - linethickness / 2
    elif paddle.top < linethickness / 2:
        paddle.top = linethickness / 2
    pygame.draw.rect(displaysurface, white, paddle)


def draw_ball(ball):
    pygame.draw.rect(displaysurface, white, ball)


def display_score(score1, score2):
    score1_surf = basicfont.render(str(score1), True, white)
    score2_surf = basicfont.render(str(score2), True, white)
    score1_rect = score1_surf.get_rect()
    score2_rect = score2_surf.get_rect()
    score1_rect.topleft = (150, 25)
    score2_rect.topright = (windowwidth - 150, 25)
    displaysurface.blit(score1_surf, score1_rect)
    displaysurface.blit(score2_surf, score2_rect)


def move_ball(ball, ball_dir_x, ball_dir_y):
    ball.x += ball_dir_x
    ball.y += ball_dir_y
    return ball


def check_collision(ball, ball_dir_x, ball_dir_y):
    if ball.top == linethickness/2 or ball.bottom == (windowheight - linethickness/2):
        ball_dir_y = ball_dir_y * -1
    if ball.left == linethickness/2 or ball.right == (windowwidth - linethickness/2):
        ball_dir_x = ball_dir_x * -1
    return ball_dir_x, ball_dir_y


def check_ball_hit(ball, paddle1, paddle2, ball_dir_x):
    if ball_dir_x == -1 and paddle1.right == ball.left and paddle1.top < ball.bottom and paddle1.bottom > ball.top:
        return -1
    elif ball_dir_x == 1 and paddle2.left == ball.right and paddle2.top < ball.bottom and paddle2.bottom > ball.top:
        return -1
    else:
        return 1


def check_point_scored(paddle1, paddle2, score1, score2, ball, ball_dir_x):
    # reset points if left wall is hit
    if ball.left == linethickness/2:
        score1 = 0
        return score1, score2
    elif ball.right == windowwidth - linethickness/2:
        score2 = 0
        return score1, score2
    # 1 point for hitting the ball
    elif ball_dir_x == -1 and paddle1.right == ball.left and paddle1.top < ball.bottom and paddle1.bottom > ball.top:
        score1 += 1
        return score1, score2
    elif ball_dir_x == 1 and paddle2.left == ball.right and paddle2.top < ball.bottom and paddle2.bottom > ball.top:
        score2 += 1
        return score1, score2
    # if no points scored, return score unchanged
    else:
        return score1, score2


def move_player(paddle1):
    move_ticker = 0
    keys = pygame.key.get_pressed()
    if keys[K_UP]:
        if move_ticker == 0:
            move_ticker = 10
            paddle1.y -= 1
    if keys[K_DOWN]:
        if move_ticker == 0:
            move_ticker = 10
            paddle1.y += 1
    return paddle1, move_ticker


def move_computer(ball, ball_dir_x, paddle2):
    # If ball is moving away from paddle, center bat
    if ball_dir_x == -1:
        if paddle2.centery < (windowheight/2):
            paddle2.y += 1
        elif paddle2.centery > (windowheight/2):
            paddle2.y -= 1
    # if ball moving towards bat, track its movement.
    elif ball_dir_x == 1:
        if paddle2.centery < ball.centery:
            paddle2.y += 1
        else:
            paddle2.y -= 1
    return paddle2


def main():
    pygame.init()
    global displaysurface
    global basicfont, basicfontsize
    basicfontsize = 20
    basicfont = pygame.font.Font('freesansbold.ttf', basicfontsize)
    fpsclock = pygame.time.Clock()
    displaysurface = pygame.display.set_mode((windowwidth, windowheight))
    pygame.display.set_caption('Pong')

    ball_x = windowwidth / 2 - linethickness / 2
    ball_y = windowheight / 2 - linethickness / 2
    pos_player1 = windowheight / 2 - paddlesize / 2
    pos_player2 = windowheight / 2 - paddlesize / 2

    ball_dir_x = -1
    ball_dir_y = -1

    score1 = 0
    score2 = 0

    ball = pygame.Rect(ball_x, ball_y, linethickness, linethickness)
    paddle1 = pygame.Rect(paddleoffset, pos_player1, linethickness, paddlesize)
    paddle2 = pygame.Rect(windowwidth - paddleoffset - linethickness, pos_player2, linethickness, paddlesize)

    draw_arena()
    draw_paddle(paddle1)
    draw_paddle(paddle2)
    draw_ball(ball)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                                break

        paddle1, move_ticker = move_player(paddle1)
        paddle2 = move_computer(ball, ball_dir_x, paddle2)

        ball = move_ball(ball, ball_dir_x, ball_dir_y)
        ball_dir_x, ball_dir_y = check_collision(ball, ball_dir_x, ball_dir_y)

        score1, score2 = check_point_scored(paddle1, paddle2, score1, score2, ball, ball_dir_x)
        ball_dir_x = ball_dir_x * check_ball_hit(ball, paddle1, paddle2, ball_dir_x)

        draw_arena()
        draw_paddle(paddle1)
        draw_paddle(paddle2)
        draw_ball(ball)
        display_score(score1, score2)

        pygame.display.update()
        fpsclock.tick(fps)

        if move_ticker > 0:
            move_ticker -= 1


if __name__ == '__main__':
    main()
