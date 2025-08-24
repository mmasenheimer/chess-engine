import random

# Rank the pieces by point value
pieceScores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

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
    # Shuffle the moves so the AI doesn't pick the top move every time
    random.shuffle(validMoves)

    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentsMoves = gs.get_valid_moves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE

        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE

        else:
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

# Helper method to make the first recursive call
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

'''
MinMax AI algorithm setting the recursive depth based on how good the ai will be,
deptch correlates to how many moves the ai will look foreward
'''
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, not whiteToMove)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return minScore

'''
A positive score is good for white, and a negative score is good for black
'''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
            # Black wins
        else:
            return CHECKMATE
            # White wins
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0]== "w":
                score += pieceScores[square[1]]
            elif square[0] == "b":
                score -= pieceScores[square[1]]
    return score

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
