import random

# Rank the pieces by point value
pieceScores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}

CHECKMATE = 1000
STALEMATE = 0

'''
Look at all possible moves and choose a random one-- LEVEL 1
'''
def findRandomMove(validMoves):
    print("random")
    return validMoves[random.randint(0, len(validMoves) - 1)]

'''
Find the best board position and maximizing the ai's score by material alone-- LEVEL 2
'''
def findBestMove(gs, validMoves):
    print("Greedy")
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)

    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentsMoves = gs.get_valid_moves()
    
        opponentMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.make_move(opponentsMove)

            if gs.checkMate:
                score = -turnMultiplier * CHECKMATE

            elif gs.staleMate:
                score = 0

            else:
                score = -turnMultiplier * scoreMaterial(gs.board)

            if score > opponentMaxScore:
                opponentMaxScore = score

            gs.undo_move()

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undo_move()

    return bestPlayerMove

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
