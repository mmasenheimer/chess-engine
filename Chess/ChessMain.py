'''
This is the main driver file, which is responsible for
handling user input and displaying the current game state.
'''

import pygame as p
import ChessEngine, moveFinder

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
    gameOver = False
    # If human is playing white, then this is true, if AI is playing, false
    playerOne = True
    # Same for above but for black
    playerTwo = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            # Mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
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
                        print("...")

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
                    gameOver = False
                
                if e.key == p.K_r:
                    # Reset the board if 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sqSelected = ()
                    playerClicks = []
                    move_made = False
                    gameOver = False
        
        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = moveFinder.findBestMove(gs, valid_moves)

            if AIMove is None:
                AIMove = moveFinder.findRandomMove(valid_moves)

            gs.make_move(AIMove)
            move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Game over: stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()
    print(str(moveFinder.counter) + " moves evaluated")

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected

        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"):
            # Square selected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def draw_game_state(screen, gs, validMoves, sqSelected):
    draw_board(screen)  
    # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)

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

def drawText(screen, text):
    font = p.font.SysFont("Helvetca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLoaction = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLoaction)

if __name__ == "__main__":
    main()
