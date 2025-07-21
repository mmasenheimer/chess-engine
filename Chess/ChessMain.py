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
    screen = p.display.set_mode((WIDTH, HEIGHT), p.NOFRAME, p.RESIZABLE)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    # Create the chess board

    valid_moves = gs.get_valid_moves()
    move_made = False
    # Flag for when a valid move is made

    load_images()

    running = True
    sqSelected = ()
    # This to keep track of the last square selected
    playerClicks = []
    # Keep track of clicks (2 tuples: [(6, 4), (4, 4)])

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            # Mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                # Get the xy position of the mouse click

                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sqSelected == (row, col):
                    # If the same square is clicked again, deselect it
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                
                if (len(playerClicks) == 2):
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())

                    for i in range(len(valid_moves)):

                        if move == valid_moves[i]:
                            gs.make_move(move)
                            move_made = True
                    
                            sqSelected = ()
                            # Reset the player clicks after a move is made
                            playerClicks = []
                    if not move_made:
                        playerClicks = [sqSelected]
            
            # Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # Undo move when z is pressed
                    gs.undo_move()
                    move_made = True
        
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)   
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs):
    draw_board(screen)  
    # Draw squares on the board

    draw_pieces(screen, gs.board)  
    # Draw pieces on top of those squares

def draw_board(screen):
    
    screen.fill(p.Color("white"))
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