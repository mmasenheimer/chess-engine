import random

# Rank the pieces by point value
pieceScores = {"K": 0, "Q": 10, "R": 5, "B": 3, "K": 3, "P": 1}

CHECKMATE = 1000
STALEMATE = 0

'''
Look at all possible moves and choose a random one-- LEVEL 1
'''
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

'''
Find the best board position and maximizing the ai's score by material alone-- LEVEL 2
'''
def findBestMove():
    pass



'''
Score the board based on material
'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0]== "w":
                score += pieceScores[square[1]]
            elif square[0] == "b":
                score -= pieceScores[square[1]]
    return score
