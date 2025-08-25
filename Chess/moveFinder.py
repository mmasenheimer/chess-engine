import random

# Rank the pieces by point value
pieceScores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
global counter

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

'''
Look at all possible moves and choose a random one-- LEVEL 1
'''
def findRandomMove(validMoves):
    print("random")
    return validMoves[random.randint(0, len(validMoves) - 1)]


'''
Find the best board position and maximizing the ai's score by material alone-- LEVEL 2
'''
def findBestMoveMinMaxNoRecursion(gs, validMoves):
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

'''
Helper method to call inital alpha beta function
'''
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(str(counter) + " Moves evaluated")
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

'''
MinMax AI algorithm setting the recursive depth based on how good the ai will be,
depth correlates to how many moves the ai will look forward
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
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
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
Recursive method to clean up minMax
'''
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    # 1 for white's turn, -1 for black
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undo_move()
    
    return maxScore

'''
AlphaBeta nega max AI with pruning for optomization
'''
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    # 1 for white's turn, -1 for black
    # Alpha upper-bound, beta lower-bound
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    # move ordering - implement later
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undo_move()
        if maxScore > alpha:
            # Pruning
            alpha = maxScore
        
        if alpha >= beta:
            break
    
    return maxScore
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
