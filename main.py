#!/usr/bin/env python3

#################################
# Game: Snake Game              #
# Purpose: School assignment.   #
# Author: Leonit Ajvazi         #
#################################

# Imports
from tkinter import * # Importing a lib for    
import random # Importing the random library

# Constants/global vars
GAME_WIDTH = 700
GAME_HEIGHT = 700
SPEED = 50
SPACE_SIZE = 50
BODY_PARTS = 1
FOOD_COLOR = "#FF0000"

# Customizable variables
snake_color = "#00FF00" # Not a const, this will be customizable!
background_color = "#000000"


# Classes
class snake:
    pass
class apple:
    pass




# Functions
def options():
    pass

def next_turn():
    pass

def change_direction(new_direciton):
    pass

def chack_collision():
    pass

def game_over():
    pass

window = Tk()
window.title("Snake Game - Leonit Ajvazi")
window.resizable(False, False)

score = 0
direction = 'down'

label = Label(window, text="Score:{}".format(score), font=('consolas', 40))
label.pack()

canvas = Canvas(window, bg=background_color, height=GAME_HEIGHT, width=GAME_WIDTH)

window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.mainloop()
