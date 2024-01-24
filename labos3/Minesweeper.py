import pygame
import random
import time
import sys

# Constants
WIDTH, HEIGHT = 600, 650 #visina i sirina ploče
ROWS = 15               #broj polja za matricu rows*rows
CELL_SIZE = WIDTH // ROWS   #veličina svakog polja
MINES_COUNT =   20          # broj mina

WHITE = (255, 255, 255)     #definirali boje
GRAY = (192, 192, 192)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
MAROON = (128, 0, 0)

pygame.init()       #inicijalizacija Pygame biblioteke

win = pygame.display.set_mode((WIDTH, HEIGHT))  #stvaranje prozora igre 
pygame.display.set_caption("Minesweeper")

start_time = time.time()    # deklaracija start_time 

# varijable za definiranje slike zastavica
original_flag_images = []
for i in range(4):
    original_flag_images.append(pygame.image.load(f'flag_{i}.png'))  
scaled_flag_images = [pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE)) for img in original_flag_images] #skaliranje slike zastavica

explosion_image = pygame.image.load('explosion.png')  # slika 'explosion.jpg' 
explosion_image = pygame.transform.scale(explosion_image, (CELL_SIZE , CELL_SIZE))  # skaliraj veličinu


def calculate_remaining_mines(mines_count, flagged):    #racunamo broj preostalih mina
    flagged_count = sum(row.count(True) for row in flagged)
    remaining_mines = mines_count - flagged_count
    return remaining_mines

def draw_grid(remaining_mines, elapsed_time, mines, revealed, game_over, pressed_mine):
    win.fill(WHITE)
    font = pygame.font.Font(None, 24)

    # ispis broja neoznacenih mina
    text = font.render(f"Remaining Mines: {remaining_mines}", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 4, 10))
    win.blit(text, text_rect)

    # ispis proteklog vremena
    elapsed_time = int(time.time() - start_time)
    text = font.render(f"Time: {elapsed_time} seconds", True, BLACK)
    text_rect = text.get_rect(center=(3 * WIDTH // 4, 10))
    win.blit(text, text_rect)

    # Draw the grid
    for row in range(ROWS):
        for col in range(ROWS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)

            if game_over and (row, col) in mines:
                if pressed_mine and (row, col) == pressed_mine:
                    win.blit(explosion_image, rect) # prikaži eksploziju na pritisnutom polju
                else:
                    pygame.draw.rect(win, RED, rect)    #ostale nepritisnute mine obojaj crveno
                    pygame.draw.rect(win, WHITE, rect, 1)
            else:
                pygame.draw.rect(win, GRAY, rect, 1)    #ostale obojaj u sivo

def initialize_mines(): #postavljamo mine
    mines = set()
    while len(mines) < MINES_COUNT:
        mine = (random.randint(0, ROWS - 1), random.randint(0, ROWS - 1))
        mines.add(mine)
    return mines

def reveal_empty_neighbors(row, col, mines, revealed):  #otkrij susjedne prazne blokove ako kliknemo na prazni blok
    if revealed[row][col]:
        return
    revealed[row][col] = True

    if count_neighbors(row, col, mines) == 0:
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_row, neighbor_col = row + i, col + j
                if 0 <= neighbor_row < ROWS and 0 <= neighbor_col < ROWS:
                    reveal_empty_neighbors(neighbor_row, neighbor_col, mines, revealed) #poziv funkcije za susjede

def draw_mines_and_flags(mines, revealed, flagged, pressed_mine):   #crtanje mina i zastavica
    for row in range(ROWS):
        for col in range(ROWS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)

            if (row, col) in mines:
                if revealed[row][col]:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= row + i < ROWS and 0 <= col + j < ROWS:
                                explosion_rect = pygame.Rect((col + j) * CELL_SIZE, (row + i) * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)
                                win.blit(explosion_image, explosion_rect) #pritisnuli minu-->eksplozija
                elif flagged[row][col]:
                    flag_animation_index = (int(time.time() * 7) % 4)  # brzina animacije
                    flag_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)
                    win.blit(scaled_flag_images[flag_animation_index], flag_rect) #oznacili minu-->zastavica
            else:
                if flagged[row][col]:
                    flag_animation_index = (int(time.time() * 7) % 4)  # brzina animacije
                    flag_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)
                    win.blit(scaled_flag_images[flag_animation_index], flag_rect) #oznacili minu-->zastavica
                elif revealed[row][col]:
                    count = count_neighbors(row, col, mines)
                    if count == 0:
                        pygame.draw.rect(win, WHITE, rect)  #otkrili prazno polje -->bijela
                    else:
                        draw_numbers(mines, revealed)   #prikazi broj susjednih mina

def draw_numbers(mines, revealed):
    font = pygame.font.Font(None, 36)
    for row in range(ROWS):
        for col in range(ROWS):
            if (row, col) not in mines and revealed[row][col]:
                count = count_neighbors(row, col, mines)
                if count > 0:
                    color = get_number_color(count)
                    text = font.render(str(count), True, color)
                    text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2 + 50))
                    win.blit(text, text_rect)   #prikazi broj susjednih mina

def count_neighbors(row, col, mines):   #izbroji susjedne mine
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbor_row, neighbor_col = row + i, col + j
            if (neighbor_row, neighbor_col) in mines:
                count += 1
    return count

def get_number_color(number):   #razlicite brojeve oboji razlicitim bojama
    colors = [BLUE, GREEN, RED, PURPLE, CYAN, YELLOW, MAROON, MAGENTA, WHITE]
    return colors[number - 1] if 1 <= number <= 8 else BLACK

def check_victory(mines, revealed): #provjeravamo pobjedu
    for row in range(ROWS):
        for col in range(ROWS):
            if (row, col) not in mines and not revealed[row][col]:
                return False
    return True

def restart_game():
    global start_time          
    start_time = time.time()  # Resetirajte start_time
    return initialize_mines(), [[False] * ROWS for _ in range(ROWS)], [[False] * ROWS for _ in range(ROWS)] #inicijaliziraj mine

def game_loop():
    mines, revealed, flagged = initialize_mines(), [[False] * ROWS for _ in range(ROWS)], [[False] * ROWS for _ in range(ROWS)]  #pocetni uvjeti
    game_over = False
    waiting_for_restart = False
    pressed_mine = None

    while not game_over:
        for event in pygame.event.get():    #provjeri zahtjev za zatvaranje prozora
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  #odredi koja je celija odabrana
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // CELL_SIZE
                row = (mouse_y - 50) // CELL_SIZE

                if 0 <= row < ROWS and 0 <= col < ROWS:
                    if event.button == 1:   # Left-click
                        if (row, col) in mines:
                            if not flagged[row][col]:   #ako smo lijevim klikom odabrali celiju s minama onda gubimo
                                game_over = True
                                pressed_mine = (row, col)
                                draw_grid(calculate_remaining_mines(MINES_COUNT, flagged), int(time.time() - start_time), mines, revealed, game_over, pressed_mine)
                                draw_mines_and_flags(mines, revealed, flagged, pressed_mine)
                                font = pygame.font.Font(None, 32)
                                text = font.render("Game over! You lost. Press 'R' to restart.", True, BLACK)
                                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                                win.blit(text, text_rect)
                                pygame.display.flip()
                                waiting_for_restart = True
                                while waiting_for_restart:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  #ako je pritisnuto R resetiraj igru
                                            mines, revealed, flagged = restart_game()
                                            game_over = False
                                            pressed_mine = None
                                            waiting_for_restart = False
                        else:
                            if not flagged[row][col]:   #otkrij odabrano polje koje nije mina
                                reveal_empty_neighbors(row, col, mines, revealed)
                    elif event.button == 3 and revealed[row][col] == False: # Right-click
                        flagged[row][col] = not flagged[row][col]   #dodaj zastavicu

        draw_grid(calculate_remaining_mines(MINES_COUNT, flagged), int(time.time() - start_time), mines, revealed, game_over, pressed_mine)
        draw_mines_and_flags(mines, revealed, flagged, pressed_mine)
        draw_numbers(mines, revealed)

        pygame.display.flip()

        if check_victory(mines, revealed):  #provjeri pobjedu
            game_over = True    #resetiraj varijable
            draw_grid(0, int(time.time() - start_time), mines, revealed, game_over, pressed_mine)
            font = pygame.font.Font(None, 32)
            text = font.render("Congratulations! You win! Press 'R' to restart.", True, BLACK)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(text, text_rect)
            pygame.display.flip()
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  #ako je pritisnuto R pokreni novu igru
                        mines, revealed, flagged = restart_game()
                        game_over = False
                        pressed_mine = None
                        waiting_for_restart = False

# Pokreni igru
game_loop()
pygame.quit()
sys.exit()
