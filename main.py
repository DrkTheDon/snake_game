#!/usr/bin/env python3

#################################
# Game: Snake Game              #
# Purpose: School assignment.   #
# Author: Leonit Ajvazi         #
#################################

# Imports
from pygame import *
import sys
import random

# Constants/global vars
WIDTH, HEIGHT = 600, 400 # storleken på fönstret
BLOCK_SIZE = 20 # hur stora blocken är (pixel)
FPS = 10 # hur snabbt spelet går (frames per second)

# Colors
BLACK = (0, 0, 0) # bakgrundsfärg
GREEN = (0, 255, 0) #ormfärg
RED = (255, 0, 0) #matfärg

# Customizable variables
START_LENGTH = 3 # inte använd men kunde varit för startlängd på ormen (om spelet ska utvecklas)


# Classes
class Snake:
    def __init__(self): # startpositionen för ormen
        self.body = [(100, 50), (80, 50), (60, 50)]
        self.direction = 'RIGHT'

    def move(self): # flyttar ormen ett steg beroende på vart den ska
        x, y = self.body[0]
        if self.direction == 'UP':
            new_head = (x, y - BLOCK_SIZE)
        elif self.direction == 'DOWN':
            new_head = (x, y + BLOCK_SIZE)
        elif self.direction == 'LEFT':
            new_head = (x - BLOCK_SIZE, y)
        else:
            new_head = (x + BLOCK_SIZE, y)

        self.body.insert(0, new_head) # lägger till ny huvudposition

    def grow(self): # de här e bara sån automatik sak - om man är på samma pos som food är så kallar man inte shrink()
        pass

    def shrink(self): # tar bort sista biten av ormen så att den inte växer
        self.body.pop()

    def check_collision(self): # ser om vi kör in i oss själva eller väggen
        head = self.body[0]
        return (head in self.body[1:] or
                head[0] < 0 or head[0] >= WIDTH or
                head[1] < 0 or head[1] >= HEIGHT)

    def draw(self, surface): # ritar ormen på skärmen
        for segment in self.body:
            draw.rect(surface, GREEN, (*segment, BLOCK_SIZE, BLOCK_SIZE))


class Food:
    def __init__(self): # maten får en random plats direkt när den skapas
        self.position = self.random_position()

    def random_position(self): # slumpa fram en plats som är på rutnätet
        return (random.randrange(0, WIDTH, BLOCK_SIZE),
                random.randrange(0, HEIGHT, BLOCK_SIZE))

    def draw(self, surface): # ritar maten
        draw.rect(surface, RED, (*self.position, BLOCK_SIZE, BLOCK_SIZE))

class Game:
    def __init__(self): # startar pygame och skapar allt som behövs
        init()
        self.screen = display.set_mode((WIDTH, HEIGHT)) # skärmstorlek
        display.set_caption("Snake Game - Leonit Ajvazi") # titel på fönstret
        self.clock = time.Clock() # klocka för att styra FPS
        self.snake = Snake() # Skapar orm
        self.food = Food() # Skapar mat
        self.running = True # Spelet körs boolean

    def handle_input(self): # kollar vilken tangent man trycker på så ormen går åt rätt håll kommer att lägga till WASD också.
        keys = key.get_pressed()
        if keys[K_UP] and self.snake.direction != 'DOWN':
            self.snake.direction = 'UP'
        elif keys[K_DOWN] and self.snake.direction != 'UP':
            self.snake.direction = 'DOWN'
        elif keys[K_LEFT] and self.snake.direction != 'RIGHT':
            self.snake.direction = 'LEFT'
        elif keys[K_RIGHT] and self.snake.direction != 'LEFT':
            self.snake.direction = 'RIGHT'

    def update(self): # flyttar ormen framåt
        self.snake.move()

        if self.snake.body[0] == self.food.position: # Som beskriven på grow funktionen, omdu är på samma pos som mat så skippar vi shrink på så sätt växer man
            self.food.position = self.food.random_position()
        else:
            self.snake.shrink() # Själfförklarande

        if self.snake.check_collision(): # om ormen krockar med vägg eller sig själv så förlorar man
            self.running = False

    def draw(self): # rensar skärmen sen ritar om allting
        self.screen.fill(BLACK) 
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        display.update()

    def run(self): # här kör hela spelet i en loop
        while self.running:
            for e in event.get():# kollar om man klickar på krysset, då stänger man spelet
                if e.type == QUIT:
                    quit()
                    sys.exit()

            self.handle_input() # kollar input
            self.update() # uppdaterar spel
            self.draw() # ritar allt
            self.clock.tick(FPS) # pausar lite för att spelet inte ska gå 1000 fps och göra massa konstiga saker



# Functions
def main(): # Main funktionen, startar spelet.
    game = Game() 
    game.run()

if __name__ == "__main__":
    main()
