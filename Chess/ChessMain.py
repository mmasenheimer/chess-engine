'''
This is the main driver file, which is responsible for
handling user input and displaying the current game state.
'''

import pygame as p
import ChessEngine

WIDTH = 512
HEIGHT = 512
DIMENSION = 8

SQ_SIZE = HEIGHT // DIMENSION  
# Size of each square on the chess board

MAX_FPS = 15  
# For animations

IMAGES = {}
# Store images of pieces

def load_images():
    # Runs once before the game starts
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Can access an image by calling the IMAGES key

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    # Create the chess board

    load_images()

    running = True

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            draw_game_state(screen, gs)    
            
            clock.tick(MAX_FPS)
            p.display.flip()

def draw_game_state(screen, gs):
    draw_board(screen, )  
    # Draw squares on the board

    draw_pieces(screen, gs.board)  
    # Draw pieces on top of those squares


def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]

    for row in range(DIMENSION):

        for col in range(DIMENSION):

            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for row in range(DIMENSION):

        for col in range(DIMENSION):

            piece = board[row][col]
            if piece != "--":
                # If the square is not empty
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    


if __name__ == "__main__":
    main()



