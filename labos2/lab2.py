import pygame
import sys
import random
from pygame.locals import *

width = 1000
height = 1000

class Square:
    def __init__(self, x_start=0, y_start=0):
        self.old = random.randint(2, 10)
        self.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.time = 0
        rand=random.randint(0, 1)
        if rand == 0:
            self.position_x = x_start
            self.position_y = y_start
        else:
            self.position_x = x_start - 250
            self.position_y = y_start
        self.velocity_x = random.randint(0, 40) / 20 - 1.5
        self.velocity_y = -1 * random.randint(20, 40) / 20 - 1.5                             

def main():

    mainClock = pygame.time.Clock()
    pygame.init()
    display = pygame.display.set_mode((width, height))

    x_start, y_start = 0, 0
    squares = []
    step_old = 0.03
    step_velocity = 0.03
    step_time = 0.03

    while True:

        display.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                x_start, y_start = pygame.mouse.get_pos()

        if x_start == 0 and y_start == 0:
            square = Square()
            rand=random.randint(0, 1)
            if rand == 0:
                square.position_x = int(width / 2) + 150
                square.position_y = int(height / 2)
            if rand == 1:
                square.position_x = int(width / 2) - 150
                square.position_y = int(height / 2)

        else:
            square = Square(x_start, y_start)

        squares.append(square)

        for square in squares:
            square.position_x += square.velocity_x * square.time
            square.position_y += square.velocity_y * square.time
            square.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            square.old -= step_old
            square.velocity_y += step_velocity
            square.time += step_time

            pygame.draw.rect(display, square.color, (int(square.position_x), int(square.position_y), int(square.old), int(square.old)), width=1)

            if square.old < 0:
                squares.remove(square)


        pygame.display.update()
        mainClock.tick(40)          

if __name__ == '__main__':
    main()
