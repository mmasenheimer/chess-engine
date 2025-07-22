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
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        # Coordinates for the square where en passant capture is possible

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
            self.whiteKingLocation = (move.endRow, move.endCol)

        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        # Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            # Grab the color of the pawn and then make it a queen
        
        if move.isEnpassantMove:
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            # Remove the pawn being captured (it's on the previous row, same col as end)
            if move.pieceMoved[0] == 'w':
                self.board[move.endRow + 1][move.endCol] = '--'
            else:
                self.board[move.endRow - 1][move.endCol] = '--'

        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            # Only on two square pawn advances
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()


    """Undo the last move made"""
    def undo_move(self):
        if len(self.moveLog) != 0:
            # Make sure there exists a move to undo

            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Switch turns back

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            
            if move.isEnpassantMove:
                # Undo en passant move
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                # Undo 2-square pawn advance
                self.enpassantPossible = ()

    """All moves considering checks"""
    def get_valid_moves(self):
        # # ----Naive algorithm (First iteration, slower):----
        # # 1. Generate all possible moves
        # # 2. For each move, make the move
        # # 3. Generate all oponent's moves
        # # 4. For each oponents moves, see if they attack the king
        # ----Faster algorithm----
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]

        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        # Getting which king
        
        if self.inCheck:
            if len(self.checks) == 1:
                # Only one check--block check or move the king
                moves = self.get_all_possible_moves()
                # To block a check, need to move a piece between the attacker piece and the king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                # Location of the enemy piece causing the check
                validSquares = []
                # Valid squares that pieces can move to
                if pieceChecking[1] == "N":
                    # If attacking is a knight, the player must capture the knight or move king
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        # Where check[2] and check[3] are the check directions
                        validSquares.append(validSquare)

                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) -1, -1, -1):
                    # Getting rid of moves that don't block check or move king
                    if moves[i].pieceMoved[1] != "K":
                        # Move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            # Move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:
                # 2X check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            # Not in check so all moves are fine
            moves = self.get_all_possible_moves()

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
        self.whiteToMove = not self.whiteToMove
        # Switch to opponent's turn
        oppMoves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                # Square is under attack
                self.whiteToMove = not self.whiteToMove
                return True
            
        self.whiteToMove = not self.whiteToMove
        return False

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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            # Single move forward
            if self.board[row - 1][col] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == "--":
                        moves.append(Move((row, col), (row - 2, col), self.board))
            
            # Captures to the left
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                # En passant to the left
                if (row - 1, col - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))

            # Captures to the right
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
                # En passant to the right
                if (row - 1, col + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))

        else:  # Black to move
            # Single move forward
            if self.board[row + 1][col] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))

            # Captures to the left
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                # En passant to the left
                if (row + 1, col - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))

            # Captures to the right
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                # En passant to the right
                if (row + 1, col + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True))



    '''
    Get all of the rook moves for a rook at row, col, and add the moves to the list
    of valid moves
    '''
    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    # Can't remove the queen from pin on rook moves
                    self.pins.remove(self.pins[i])
                    break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for dir in directions:
            for i in range(1, 8):
                endRow = row + dir[0] * i
                endCol = col + dir[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # On the board
                    if not piecePinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
                        # Should be able to move the piece towards or away from the pin
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            # Valid empty space
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            # Valid enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            # Invalid friendly piece
                            break
                else:
                    # Off the board
                    break

    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for dir in directions:
            for i in range(1, 8):
                endRow = row + dir[0] * i
                endCol = col + dir[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
                        # On the board
                        endPiece = self.board[endRow][endCol]

                        if endPiece == "--":
                            # Valid empty space
                            moves.append(Move((row, col), (endRow, endCol), self.board))

                        elif endPiece[0] == enemyColor:
                            # Valid enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            # Friendly piece invalid
                            break
                else:
                    # Off the board
                    break

    def getKnightMoves(self, row, col, moves):
        # Note that the pin direction does not matter for a knight
        piecePinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"

        for aMove in knightMoves:
            endRow = row + aMove[0]
            endCol = col + aMove[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:  
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        # Not an ally piece, either empty or enemy
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"

        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # Not an ally piece
                    # Place king on end square and check for checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    
                    # Place the king back on the original location
                    if allyColor == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
                    
    '''
    This function generates a list of all the pieces that are pinned,
    all the squares that are causing a check, and whether or not the
    king is currently in check
    '''
    def checkForPinsAndChecks(self):
        pins = []
        # Squares where the allied pinned piece is and direction pinned from
        checks = []
        # Squares where enemy is applying a check
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        # Directions for checking outward from king for checks

        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            # Reset the possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                # A square that is i away from a given direction
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            # First allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            # Second allied piece, therefore no possible check in the i direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        '''
                        There are 5 possibilities in this conditional:
                        1) orthogonally away from king and piece is a rook
                        2) diagonally away from king and piece is a bishop
                        3) 1 square away diagonally from king and piece is a bishop
                        4) any direction and piece is a queen
                        5) any direction 1 square away and piece is a king (to prevent king move to a square controlled by another king)
                        '''
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            
                            if possiblePin == ():
                                # No piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                # Piece blocking the check so it's a pin
                                pins.append(possiblePin)
                                break
                        else:
                            # Enemy piece not applying check
                            break
                else:
                    # Off the board
                    break

        # Check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    # Enemy knight is attacking the king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

class Move ():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # Generating a unique ID for every move

        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True
        
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        
        print(self.moveId)
    
    def __eq__(self, other):

        if isinstance(other, Move):
            return self.moveId == other.moveId
        
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]