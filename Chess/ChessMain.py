'''
Main driver file, which is responsible for
handling user input and displaying the current game state.
'''

import pygame as p
import ChessEngine, moveFinder
from multiprocessing import Process, Queue, freeze_support

import sys
import os

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 175
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION  

def resource_path(relative_path):
    # Works for dev and PyInstaller exe
    try:
        base_path = sys._MEIPASS  # Temporary folder PyInstaller uses
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

IMAGES = {}
# Store images of pieces

def load_images():
    # Runs once before the game starts
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        path = resource_path("Chess/images/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(path), (SQ_SIZE, SQ_SIZE))
    # Can access an image by calling the IMAGES key

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.NOFRAME, p.RESIZABLE)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)

    gs = ChessEngine.GameState()
    # Create the chess board

    valid_moves = gs.get_valid_moves()
    move_made = False
    # Flag for when a valid move is made

    load_images()

    running = True
    sqSelected = ()

    playerClicks = []
    # Keep track of clicks (2 tuples: [(6, 4), (4, 4)])
    gameOver = False
    
    # *************************
    # False = AI player, True = human player
    playerOne = True
    playerTwo = True
    # *************************

    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()

                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col) or col >= 8:
                        # If the same square is clicked again or mouse log click, deselect it
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if (len(playerClicks) == 2) and humanTurn:
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
                    gs.undo_move()
                    move_made = True
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                
                if e.key == p.K_r:
                    # Reset the board if 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sqSelected = ()
                    playerClicks = []
                    move_made = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        
        # AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("loading...")
                returnQueue = Queue()
                # Used to pass data between threads

                moveFinderProcess = Process(target=moveFinder.findBestMove, args=(gs, valid_moves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                print("finished")
                result = returnQueue.get()
                if isinstance(result, tuple):
                    AIMove, moveFinder.counter = result
                else:
                    AIMove = result
                    moveFinder.counter = 0
                
                if AIMove is None:
                    AIMove = moveFinder.findRandomMove(valid_moves)
                gs.make_move(AIMove)
                move_made = True
                AIThinking = False

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
            moveUndone = False

        draw_game_state(screen, gs, valid_moves, sqSelected, moveLogFont)
        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                text = "Stalemate"
            else:
                text = "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate"
            drawEndGameText(screen, text)
       
        p.display.flip()
    print(str(moveFinder.counter) + " moves evaluated")
    #screen.blit(evalText, evalTextLocation)

def numMoves(counter):
    global evalText, evalTextLocation
    font = p.font.SysFont("Arial", 14, False, False)  # Need to define the font
    evalText = f"Moves Evaluated: {counter}"  # Use the parameter, not moveFinder.counter
    evalTextObject = font.render(evalText, True, p.Color("yellow"))

    # Need to define moveLogRect and padding since they're not available in this scope
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    padding = 5
    
    evalTextLocation = moveLogRect.move(
        padding, 
        MOVE_LOG_PANEL_HEIGHT - evalTextObject.get_height() - padding
    )
    

'''
Handles the graphics for current game state
'''
def draw_game_state(screen, gs, validMoves, sqSelected, moveLogFont):
    draw_board(screen)  
    # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, gs.board)  
    # Draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)


'''
Draw the squares on the board, where top left is always white
'''
def draw_board(screen):
    screen.fill(p.Color("white"))
    colors = [p.Color("white"), p.Color("gray")]

    for row in range(DIMENSION):

        for col in range(DIMENSION):

            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight the square selected and possible moves for the piece
'''
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

'''
Draw pieces on the board using the current gamestate
'''
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                # If the square is not empty
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draws the move log
'''
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            # Make sure black made a move
            moveString += str(moveLog[i+1]) + " "
        moveTexts.append(moveString)
    
    movesPerRow = 3
    padding = 5
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ''
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]

        #numMovesProcessed = 0 # GET NUM MOVES CALCULATED LATER...................
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + 1


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLoaction = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLoaction)

if __name__ == "__main__":
    freeze_support()
    main()
