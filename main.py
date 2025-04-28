#!/usr/bin/env python3

#################################
# Game: Snake Game              #
# Purpose: School assignment.   #
# Author: Leonit Ajvazi         #
#################################

# Imports
import pygame
from pygame import display  # För att visa och uppdatera fönstret
from pygame import font  # För att skriva text och använda typsnitt
from pygame import time  # För att kolla tid typ FPS
from pygame.locals import *  # För att läsa knapptryckningar och sånt
import random  # För att skapa random tal (t.ex. för att slumpla fram matens plats)
import os  # För att jobba med filer och sånt
import requests  # För att göra HTTP-anrop (men vi använder det inte än)

# Constants
WIDTH, HEIGHT = 600, 480  # storleken på fönstret
GRID_SIZE = 20  # Hur stor varje block är på spelplanen
FPS = 15  # hur många gånger per sekund spelet uppdateras
SCOREBOARD_HEIGHT = 40  # Höjden på poängtavlan
CHEAT_BUTTON_WIDTH = 120  # bredden på fusk-knappen
CHEAT_BUTTON_HEIGHT = 30  # höjden på fusk-knappen

# Colors
BLACK = (0, 0, 0)  # bakgrundsfärg
WHITE = (255, 255, 255)  # färg för text och andra grejer
GREEN = (0, 255, 0)  # orm
RED = (255, 0, 0)  # mat
BLUE = (0, 0, 255)  # För Bosnien bakgrund
GOLD = (255, 215, 0)  # Guld färg för Posnia titel

class Snake:
    def __init__(self, start_length=3):
        # Ensure initial position is grid-aligned, below the scoreboard
        start_x = (WIDTH // (2 * GRID_SIZE)) * GRID_SIZE
        start_y = ((HEIGHT - SCOREBOARD_HEIGHT - GRID_SIZE) // (2 * GRID_SIZE)) * GRID_SIZE + SCOREBOARD_HEIGHT
        self.body = [(start_x - i * GRID_SIZE, start_y) for i in range(start_length)]
        self.direction = (1, 0)

    def move(self):
        head = (self.body[0][0] + self.direction[0] * GRID_SIZE,
                self.body[0][1] + self.direction[1] * GRID_SIZE)
        self.body = [head] + self.body[:-1]

    def grow(self):
        tail = self.body[-1]
        self.body.append(tail)

    def check_collision(self):
        head = self.body[0]
        if not (0 <= head[0] < WIDTH and SCOREBOARD_HEIGHT <= head[1] < HEIGHT):
            return True  # Collision with wall
        if head in self.body[1:]:
            return True  # Collision with self
        return False # No collision

    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))

class Food:
    def __init__(self, snake_body):
        # skapar mat på en plats som inte är där ormen är
        self.position = self.generate_food(snake_body)

    def generate_food(self, snake_body):
        # här slumpar vi fram en matposition tills den inte är där ormen är
        while True:
            x = random.randrange(0, WIDTH // GRID_SIZE) * GRID_SIZE
            y = random.randrange(SCOREBOARD_HEIGHT // GRID_SIZE, HEIGHT // GRID_SIZE) * GRID_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, screen):
        # ritar ut maten på skärmen
        pygame.draw.rect(screen, RED, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

class Game:
    def __init__(self):
        pygame.init()
        # skapar skärm med rätt storlek
        self.screen = display.set_mode((WIDTH, HEIGHT))
        display.set_caption("Snake Game")
        self.clock = time.Clock()  # skapar en klocka för FPS
        self.settings = self.load_settings()  # hämtar inställningar från fil
        self.snake = Snake(self.settings['start_length'])  # skapar ormen
        self.food = Food(self.snake.body)  # skapar maten
        self.score = 0  # startscroren är 0
        self.high_score = self.load_high_score()  # kollar om det finns en highscore sparad
        self.game_state = "main_menu"  # startar på main_menu
        self.button_rects = {}  # för knapparna, just nu tomt
        self.last_move = None  # lagrar senaste rörelse
        self.clear_console()  # rensar konsolen i början
        self.posnia_enabled = self.settings['posnia_enabled']  # kollar om Posnia är på
        self.wasd_controls = self.settings['wasd_controls']  # kollar om WASD kontroller är på
        self.posnia_background = self.load_posnia_background()  # laddar bakgrund om Posnia är på

    def draw_title(self):
        font_obj = font.SysFont("Arial", 20)  # skapar fonten för titeln
        if self.posnia_enabled:
            # om Posnia är på, rita titeln med gul färg
            title_text = font_obj.render("snake_game - POSNIA LIMITED", True, GOLD)
        else:
            # annars skriv en annan titel
            title_text = font_obj.render("snake_game - Av Leonit", True, WHITE)
        self.screen.blit(title_text, (10, 10))  # ritar titeln på skärmen

    def clear_console(self):
        # rensar konsolen när spelet startar
        os.system('cls' if os.name == 'nt' else 'clear')  # för Windows och Linux

    def log_move(self, move):
        # skriver ut i konsolen när spelaren gör en rörelse
        print(f"- USER MOVED {move.upper()}")

    def load_high_score(self):
        try:
            # försöker läsa highscore från fil
            with open("highscore.txt", "r") as file:
                return int(file.read())  # returnera highscore
        except FileNotFoundError:
            # om filen inte finns, sätt highscore till 0
            return 0

    def save_high_score(self, score):
        # sparar highscore till fil
        with open("highscore.txt", "w") as file:
            file.write(str(score))

    def load_settings(self):
        # default inställningar om vi inte kan läsa från fil
        default_settings = {'start_length': 3, 'posnia_enabled': False, 'wasd_controls': False}
        try:
            # försöker läsa inställningar från fil
            with open("settings.txt", "r") as file:
                lines = file.readlines()
                settings = {}  # tom inställnings-dict

                if len(lines) > 0:
                    try:
                        settings['start_length'] = int(lines[0].split('=')[1].strip())
                    except (IndexError, ValueError):
                        settings['start_length'] = default_settings['start_length']
                else:
                    settings['start_length'] = default_settings['start_length']

                if len(lines) > 1:
                    try:
                        settings['posnia_enabled'] = lines[1].split('=')[1].strip().lower() == 'true'
                    except (IndexError, ValueError):
                        settings['posnia_enabled'] = default_settings['posnia_enabled']
                else:
                    settings['posnia_enabled'] = default_settings['posnia_enabled']

                if len(lines) > 2:
                    try:
                        settings['wasd_controls'] = lines[2].split('=')[1].strip().lower() == 'true'
                    except (IndexError, ValueError):
                        settings['wasd_controls'] = default_settings['wasd_controls']
                else:
                    settings['wasd_controls'] = default_settings['wasd_controls']

                return settings
        except FileNotFoundError:
            # om inställningsfilen inte finns, använd default inställningar
            return default_settings

    def save_settings(self):
        # sparar inställningarna till fil
        with open("settings.txt", "w") as file:
            file.write(f"start_length={self.settings['start_length']}\n")
            file.write(f"posnia_enabled={self.settings['posnia_enabled']}\n")
            file.write(f"wasd_controls={self.settings['wasd_controls']}\n")

    def load_posnia_background(self):
        # URL för att ladda ner Posnia bakgrund
        image_url = "https://media.discordapp.net/attachments/1365774256859775068/1366396291675984027/Screenshot_20250428_145053_Gallery.jpg?ex=6810cb36&is=680f79b6&hm=2ca66fddd3f2d0a3b64617f72aad16bb1cd0dac129ca930b0999dfc3ed51aebb&=&format=webp&width=2086&height=1174"
        filename = "posnia.jpg"

        try:
            # Försök ladda bakgrunden från fil först
            background = pygame.image.load(filename)
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            return background
        except FileNotFoundError:
            # Om filen inte finns, ladda ner bakgrunden
            print("posnia.jpg not found, downloading...")
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()  # om något går fel vid nedladdning

                with open(filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                background = pygame.image.load(filename)
                background = pygame.transform.scale(background, (WIDTH, HEIGHT))
                print("posnia.jpg downloaded successfully!")
                return background
            except requests.exceptions.RequestException as e:
                # om det är något fel med nedladdningen
                print(f"Error downloading posnia.jpg: {e}")
                return None
            except Exception as e:
                # om något annat går fel
                print(f"Error loading/scaling posnia.jpg: {e}")
                return None

    def draw_grid(self):
        # ritar rutnätet på skärmen
        for x in range(0, WIDTH, GRID_SIZE):
            for y in range(SCOREBOARD_HEIGHT, HEIGHT, GRID_SIZE):
                # ritar linjer för vertikalt rutnät
                pygame.draw.line(self.screen, (40, 40, 40), (x, SCOREBOARD_HEIGHT), (x, HEIGHT))
                # ritar linjer för horisontellt rutnät
                pygame.draw.line(self.screen, (40, 40, 40), (0, y), (WIDTH, y))

    def draw_score(self):
        # skapar font för att rita poängen
        font_obj = font.SysFont("Arial", 20)
        # ritar text för nuvarande och högsta poäng
        score_text = font_obj.render(f"Score: {self.score} High Score: {self.high_score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    def display_main_menu(self):
        # om Posnia är på, ritar Posnia bakgrund
        if self.posnia_enabled and self.posnia_background:
            self.screen.blit(self.posnia_background, (0, 0))
        else:
            # annars rita svart bakgrund
            self.screen.fill(BLACK)

        # skapar font för huvudmenyn
        font_title = font.SysFont("Arial", 40)
        # ritar titeltexten på skärmen
        title_text = font_title.render("Snake Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title_text, title_rect)

        # knappar för Start, Options och Quit
        button_font = font.SysFont("Arial", 24)
        button_names = ["Start", "Options", "Quit"]
        self.button_rects = {}
        button_height = HEIGHT // 2 - 60
        # ritar alla knappar
        for button_name in button_names:
            button_text = button_font.render(button_name, True, WHITE)
            button_rect = self.draw_button(button_name, (WIDTH // 2 - button_text.get_width() // 2 - 10, button_height), button_font)
            self.button_rects[button_name] = button_rect
            button_height += 80

        display.update()

        # väntar på att användaren ska trycka på någon knapp
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    # om Start-knappen trycks på
                    if self.button_rects["Start"].collidepoint(event.pos):
                        self.game_state = "playing"
                        waiting_for_input = False
                    # om Options-knappen trycks på
                    elif self.button_rects["Options"].collidepoint(event.pos):
                        self.game_state = "options_menu"
                        waiting_for_input = False
                    # om Quit-knappen trycks på
                    elif self.button_rects["Quit"].collidepoint(event.pos):
                        pygame.quit()
                        exit()
            self.clock.tick(FPS)

    def display_options_menu(self):
        # om Posnia är på, ritar Posnia bakgrund
        if self.posnia_enabled and self.posnia_background:
            self.screen.blit(self.posnia_background, (0, 0))
        else:
            # annars rita svart bakgrund
            self.screen.fill(BLACK)

        self.draw_title()  # ritar titeln i options-menyn

        # skapar font för titel i options-menyn
        font_title = font.SysFont("Arial", 30)
        title_text = font_title.render("Options", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        self.screen.blit(title_text, title_rect)

        # knapp för att aktivera fusk
        cheat_button_font = font.SysFont("Arial", 16)
        cheat_button_text = cheat_button_font.render("Cheat Codes", True, WHITE)
        cheat_button_rect = self.draw_button("Cheat Codes", (WIDTH - CHEAT_BUTTON_WIDTH - 10, 50), cheat_button_font,
                                            width=CHEAT_BUTTON_WIDTH, height=CHEAT_BUTTON_HEIGHT)
        self.button_rects["Cheat Codes"] = cheat_button_rect

        # knapp för att aktivera WASD-kontroller
        wasd_button_font = font.SysFont("Arial", 24)
        wasd_button_text = wasd_button_font.render(f"WASD: {'On' if self.wasd_controls else 'Off'}", True,
                                                GREEN if self.wasd_controls else RED)
        wasd_button_rect = self.draw_button("WASD", (WIDTH // 2 - wasd_button_text.get_width() // 2 - 10, HEIGHT // 2 - 40),
                                            wasd_button_font, color=GREEN if self.wasd_controls else RED)
        self.button_rects["WASD"] = wasd_button_rect

        # beskrivning för WASD-knappen
        wasd_desc_font = font.SysFont("Arial", 16)
        wasd_desc_text = wasd_desc_font.render("Enables WASD keys" if self.wasd_controls == False else "Disables WASD keys",
                                            True, WHITE)
        wasd_desc_rect = wasd_desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(wasd_desc_text, wasd_desc_rect)

        # knapp för att gå tillbaka
        back_button_font = font.SysFont("Arial", 24)
        back_button_text = back_button_font.render("Back", True, WHITE)
        back_button_rect = self.draw_button("Back", (WIDTH // 2 - back_button_text.get_width() // 2 - 10, HEIGHT // 2 + 80),
                                            back_button_font)
        self.button_rects["Back"] = back_button_rect

        display.update()

        # hanterar knapptryckningar
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    # om fusk-koder knapp trycks
                    if self.button_rects.get("Cheat Codes") and self.button_rects["Cheat Codes"].collidepoint(event.pos):
                        code = self.get_user_input("Enter Cheat Code:")  # ber om input från användaren
                        self.handle_cheat_code(code)  # hantera den inskrivna koden
                        waiting_for_input = False  # Rendera om options-menyn efter fusk-kod
                        self.game_state = "options_menu"
                    # om WASD knapp trycks
                    elif self.button_rects.get("WASD") and self.button_rects["WASD"].collidepoint(event.pos):
                        self.wasd_controls = not self.wasd_controls  # Växla WASD kontroll
                        self.settings['wasd_controls'] = self.wasd_controls  # uppdatera inställningarna
                        self.save_settings()  # spara inställningar
                        self.display_options_menu()  # rendera om options-menyn för att uppdatera texten
                        waiting_for_input = False
                    # om Back knapp trycks
                    elif self.button_rects.get("Back") and self.button_rects["Back"].collidepoint(event.pos):
                        self.game_state = "main_menu"  # gå till huvudmenyn
                        waiting_for_input = False
            self.clock.tick(FPS)

    def get_user_input(self, prompt):
        # Skapar en input box för användaren
        input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 30)
        color_inactive = WHITE  # färg när boxen inte är aktiv
        color_active = GREEN    # färg när boxen är aktiv
        color = color_inactive
        active = True
        text = ''
        font_obj = font.SysFont("Arial", 20)

        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text  # returnera texten när Enter trycks
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # ta bort senaste tecknet om Backspace trycks
                    else:
                        text += event.unicode  # lägg till tecken från användaren

            # ritar bakgrund om Posnia är aktiverat
            if self.posnia_enabled and self.posnia_background:
                self.screen.blit(self.posnia_background, (0, 0))
            else:
                self.screen.fill(BLACK)

            prompt_text = font_obj.render(prompt, True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            self.screen.blit(prompt_text, prompt_rect)

            # ritar texten i inputboxen
            txt_surface = font_obj.render(text, True, color)
            width = max(200, txt_surface.get_width()+10)  # bredd på inputboxen beroende på textens längd
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(self.screen, color, input_box, 2)  # ritar själva boxen

            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_cheat_code(self, code):
        # hanterar fusk-koder
        if code == "irene":
            self.display_message("Code Valid: Customize snake length")  # giltig kod för att anpassa längd
            length_str = self.get_user_input("Enter desired snake length:")  # ber om längd från användaren
            try:
                length = int(length_str)
                if 1 <= length <= 20:  # Begränsa längden för att undvika problem
                    self.settings['start_length'] = length
                    self.save_settings()  # spara den nya längden
                    self.display_message(f"Snake length set to {length}")  # visar resultatet
                else:
                    self.display_message("Invalid length. Must be between 1 and 20.")  # ogiltig längd
            except ValueError:
                self.display_message("Invalid input. Please enter a number.")  # om användaren skriver något annat än ett nummer
        elif code == "posnia":
            self.display_message("Code Valid: Posnia mode toggled!")  # Posnia-läge aktiverat eller avaktiverat
            self.posnia_enabled = not self.posnia_enabled
            self.settings['posnia_enabled'] = self.posnia_enabled
            self.save_settings()  # spara inställningar
            if self.posnia_enabled:
                pygame.mixer.music.load("posnia_music.mp3") # spela musik om posnia aktiverat
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.stop() # stoppa musik om posnia mode inte är på
        elif code == "wasd":
            self.display_message("Code Valid: WASD controls toggled!")  # WASD kontroll aktiverad/avaktiverad
            self.wasd_controls = not self.wasd_controls
            self.settings['wasd_controls'] = self.wasd_controls
            self.save_settings()  # spara inställningar
        else:
            self.display_message("Code Invalid")  # ogiltig kod


    def display_message(self, message):
        # Visar ett meddelande på skärmen
        font_obj = font.SysFont("Arial", 24)
        message_text = font_obj.render(message, True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(message_text, message_rect)
        pygame.display.update()
        pygame.time.delay(1500)  # Visa meddelandet i 1.5 sekunder

    def display_game_over(self, is_new_high_score):
        # Visar Game Over-skärmen
        if self.posnia_enabled and self.posnia_background:
            self.screen.blit(self.posnia_background, (0, 0))
        else:
            self.screen.fill(BLACK)

        font_obj = font.SysFont("Arial", 30)
        game_over_text = font_obj.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)

        # Färgar poängen grön om det är en ny high score, annars röd
        score_color = GREEN if is_new_high_score else RED
        score_text = font_obj.render(f"Score: {self.score}", True, score_color)
        text_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(score_text, text_rect)

        if is_new_high_score:
            high_score_text = font_obj.render("NEW HIGH SCORE!", True, GOLD)
        else:
            high_score_text = font_obj.render(f"High Score: {self.high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(high_score_text, high_score_rect)

        # Retry- och Main Menu-knappar
        font_obj_button = font.SysFont("Arial", 20)  # Använd en separat font för knappar
        button_names = ["Retry", "Main Menu"]
        self.button_rects = {}
        button_height = HEIGHT // 2 + 40
        for button_name in button_names:
            button_text = font_obj_button.render(button_name, True, WHITE)
            button_rect = self.draw_button(button_name, (WIDTH // 2 - button_text.get_width() // 2 - 10, button_height),
                                        font_obj_button)
            self.button_rects[button_name] = button_rect
            button_height += 60

        display.update()

        # Hantera knapptryckningar
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    # Om Retry-knappen trycks, starta om spelet
                    if self.button_rects["Retry"].collidepoint(event.pos):
                        self.game_state = "playing"
                        waiting_for_input = False
                    # Om Main Menu-knappen trycks, gå till huvudmenyn
                    elif self.button_rects["Main Menu"].collidepoint(event.pos):
                        self.game_state = "main_menu"
                        waiting_for_input = False
            self.clock.tick(FPS)

    def draw_button(self, text, position, font_obj, color=WHITE, width=None, height=None):
        # Ritar en knapp på skärmen
        button_text = font_obj.render(text, True, color)
        button_rect = button_text.get_rect(topleft=position)

        if width is not None:
            button_rect.width = width
        if height is not None:
            button_rect.height = height

        # Rita knappramen
        pygame.draw.rect(self.screen, color, button_rect.inflate(10, 5), 2)  # Ram med padding

        # Rita knappens text
        self.screen.blit(button_text, position)
        return button_rect

    def run(self):
        # Huvudspel-loop som kör alla spelets tillstånd
        while True:
            if self.game_state == "main_menu":
                self.display_main_menu()
            elif self.game_state == "options_menu":
                self.display_options_menu()
            elif self.game_state == "playing":
                self.play()
            elif self.game_state == "game_over":
                self.display_game_over(self.score > self.high_score)

            self.clock.tick(FPS)

    def play(self):
        # Starta ett nytt spel
        self.clear_console()  # Rensa konsolen när ett nytt spel startas
        self.snake = Snake(self.settings['start_length'])  # Återställ ormen
        self.food = Food(self.snake.body)  # Återställ maten
        self.score = 0  # Återställ poängen
        self.last_move = None  # Återställ senaste rörelsen

        while self.game_state == "playing":
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    # Hantera kontroll beroende på WASD-inställningarna
                    if self.wasd_controls:
                        if event.key == K_w and self.last_move != "down":
                            self.snake.direction = (0, -1)
                            self.log_move("up")
                            self.last_move = "up"
                        elif event.key == K_s and self.last_move != "up":
                            self.snake.direction = (0, 1)
                            self.log_move("down")
                            self.last_move = "down"
                        elif event.key == K_a and self.last_move != "right":
                            self.snake.direction = (-1, 0)
                            self.log_move("left")
                            self.last_move = "left"
                        elif event.key == K_d and self.last_move != "left":
                            self.snake.direction = (1, 0)
                            self.log_move("right")
                            self.last_move = "right"
                    else:
                        if event.key == K_UP and self.last_move != "down":
                            self.snake.direction = (0, -1)
                            self.log_move("up")
                            self.last_move = "up"
                        elif event.key == K_DOWN and self.last_move != "up":
                            self.snake.direction = (0, 1)
                            self.log_move("down")
                            self.last_move = "down"
                        elif event.key == K_LEFT and self.last_move != "right":
                            self.snake.direction = (-1, 0)
                            self.log_move("left")
                            self.last_move = "left"
                        elif event.key == K_RIGHT and self.last_move != "left":
                            self.snake.direction = (1, 0)
                            self.log_move("right")
                            self.last_move = "right"

            self.snake.move()

            # Kolla om ormen äter maten
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.food = Food(self.snake.body)
                self.score += 1

            # Kolla om ormen kolliderar med sig själv
            if self.snake.check_collision():
                self.high_score = max(self.score, self.high_score)
                self.save_high_score(self.high_score)
                self.game_state = "game_over"

            # Rita bakgrunden och andra element på skärmen
            if self.posnia_enabled and self.posnia_background:
                self.screen.blit(self.posnia_background, (0, SCOREBOARD_HEIGHT))
            else:
                self.screen.fill(BLACK)

            # Rita en svart rektangel för titel- och poängområdet (över delningslinjen)
            pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SCOREBOARD_HEIGHT))

            # Rita delningslinjen
            pygame.draw.line(self.screen, WHITE, (0, SCOREBOARD_HEIGHT), (WIDTH, SCOREBOARD_HEIGHT), 2)

            # Rita rutnät, ormen och maten
            self.draw_grid()
            self.snake.draw(self.screen)
            self.food.draw(self.screen)

            # Rita titeln och poäng (över delningslinjen)
            self.draw_title()
            self.draw_score()

            display.update()
            self.clock.tick(FPS)

# main skit
if __name__ == "__main__":
    game = Game()  # Skapa en instans av spelet
    game.run()  # Kör spelet
