'''
This class is responsible for storing info about the current game state,
it's also responsible for determining the legality of moves and updating the game state.
It also keeps a move log.
'''

class GameState():

    def __init__(self):
        # Board representation is 8x8, char1 = color, char2 = piece type
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'P': self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
            "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)


    '''
    Takes a Move as a parameter and executes it 
    (will not work for castling, pawn promotion, and en-passant)
    '''

    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # Updating the king's location

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.startRow, move.endCol)

        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.startRow, move.endCol)



    '''
    Undo the last move made
    '''
    def undo_move(self):
        if len(self.moveLog) != 0:
            # Make sure there exists a move to undo

            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Switch turns back
    
    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        # Naive algorithm:
        # 1. Generate all possible moves
        moves = self.get_all_possible_moves()
        # 2. For each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
        # 3. Generate all oponent's moves
        # 4. For each oponents moves, see if they attack the king
        # 5. If they do attack the king, then it isn't a valid move
        return moves
    
    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if there is a square under attack
    '''
    def squareUnderAttack(self, row, col):
        pass



    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
                    
        return moves
    
    '''
    Get all of the pawn moves for a pawn at row, col, and add the moves to the list
    of valid moves
    '''

    def getPawnMoves(self, row, col, moves):

        if self.whiteToMove:
            if self.board[row - 1][col] == "--":
                # 1 square pawn advance
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":
                    # 2 square pawn advance
                    moves.append(Move((row, col), (row - 2, col), self.board))

            if col - 1 >= 0: # Captures to the left
                if self.board[row-1][col-1][0] == "b":
                    # Enemy piece exists here
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                
            if col + 1 <= 7: # Captures to the right
                if self.board[row-1][col+1][0] == "b":
                    moves.append(Move((row, col), (row-1, col+1), self.board))

        else: # Black to move
            if self.board[row+1][col] == "--":
                # 1 square pawn advance
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            
            if col - 1 >= 0: # Captures to the left
                if self.board[row + 1][col - 1][0] == "w":
                    # Enemy piece exists here
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                
            if col + 1 <= 7: # Captures to the right
                if self.board[row + 1][col+1][0] == "w":
                    moves.append(Move((row, col), (row-1, col+1), self.board))


        # Add pawn promotions later

    '''
    Get all of the rook moves for a rook at row, col, and add the moves to the list
    of valid moves
    '''
    def getRookMoves(self, row, col, moves):
        possibleDir = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for direction in possibleDir:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # On the board
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))

                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:
                        # Friendly piece invalid
                        break
                else:
                    # Off the board
                    break

    def getBishopMoves(self, row, col, moves):
        possibleDir = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for direction in possibleDir:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # On the board
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))

                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:
                        # Friendly piece invalid
                        break
                else:
                    # Off the board
                    break

    def getKnightMoves(self, row, col, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for aMove in knightMoves:
            endRow = row + aMove[0]
            endCol = col + aMove[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # Not an ally piece
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor:
                    # Not an ally piece
                    moves.append(Move((row, col), (endRow, endCol), self.board))


class Move ():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # Generating a unique ID for every move
        print(self.moveId)
    
    def __eq__(self, other):

        if isinstance(other, Move):
            return self.moveId == other.moveId
        
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]