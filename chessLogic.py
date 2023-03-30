import pygame
from classicalBitboard import Board
from moveGeneration import GenerateMoves
import numpy as np
from piece import Piece
from move import Move

class ChessLogic:
    def __init__(self, starting_fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.board = Board()
        self.ParseFen(starting_fen)
        self.board.FenToBitboards()
        self.board.SetUpBitboards()
        self.board.InitialiseBoard()

        self.moveGen = GenerateMoves(self.board)
        self.moveGen.PopulateAttackTables()
        self.moveGen.PopulateRayTable()

        self.is_checkmate = False
        self.is_stalemate = False
    
        self.clock = pygame.time.Clock()

        self.console_based_run = True

        self.previous_possible_moves = []
        self.attacked_squares = []

        # populate initial set of possible moves
        self.moveGen.GenerateAllPossibleMoves()

        # the piece that's being dragged by user
        self.drag_piece = None
        self.dragging = False
        self.drag_piece_moves = []

    def ParseFen(self, full_fen):
        self.board.position_fen, self.board.active_piece, self.board.castling_rights, self.board.en_passant, self.board.ply, self.board.moves = full_fen.split(' ')

        if self.board.en_passant != '-':
            x = ord(self.board.en_passant[0])-97
            y = 8 - int(self.board.en_passant[1])

            if y == 2:
                # last move by black pawn 2 down
                black_pawn = Piece('p', x + 8)
                self.board.move_history.append(Move(black_pawn, black_pawn.square, black_pawn.square + 16, 'EP'))

            elif y == 5:
                # last move by white pawn 2 up
                white_pawn = Piece('P', x + 48)
                self.board.move_history.append(Move(white_pawn, white_pawn.square, white_pawn.square - 16, 'EP'))

        self.board.ply = int(self.board.ply)
        self.board.moves = int(self.board.moves)


    def IsAllyPiece(self, piece_type):
        return (self.board.active_piece == 'w' and piece_type.isupper()) or (self.board.active_piece == 'b' and piece_type.islower())


    @staticmethod
    def NumbertoAlgebraic(s):
        x, y = s%8, s//8

        return f"{chr(x+97)}{8-y}"

    def IsCheckmate(self):
        king_can_move = len(list(filter(lambda move : move.piece == self.moveGen.ally_king, self.moveGen.possible_moves))) != 0
        attacker_attacked = all([sq in self.attacked_squares for sq in self.board.BBToSquares(self.board.attackers)])

        return (king_can_move == False and self.board.attackers != 0 and attacker_attacked == False and len(self.moveGen.possible_moves) == 0)

    def IsStalemate(self):
        return len(self.moveGen.possible_moves) == 0 and self.board.attackers == 0
    
    def SetAttackedSquares(self):
        self.attacked_squares = []

        for move in self.moveGen.possible_moves:
            self.attacked_squares.append(move.dest)

    def SwitchActivePiece(self):
        if self.board.active_piece == "w":
            self.board.active_piece = "b"
        else:
            self.board.active_piece = "w"

    def MakeMove(self, move):
        """
        move structure -> piece_name, initial_sq, final_sq, move_type

        P, 52, 36, _  (normal move)
        P, 13, 5, Q (promotion move to white queen)
        P, 18, 11, EP (pawn capture by en-passant)
        K, 60, 62, CK (white king kingside castle)
        K, 60, 57, CQ (white king queenside castle)

        move[3] will change from _ to piece object of captured piece if 
        captures happens
        """
        piece, initial_sq, final_sq, move_type = move.piece, move.initial, move.dest, move.type
        
        self.board.move_history.append(move)

        # remove piece from initial square
        drag_piece_bitboard = self.board.GetBitboard(piece.name)
        drag_piece_bitboard &= ~self.board.SquareToBB(initial_sq)
        self.board.SetBitboard(piece.name, drag_piece_bitboard)

        if self.board.IsSquareOccupied(final_sq) == True:
            # remove captured piece from final square
            captured_piece = self.board.GetPieceOnSquare(final_sq)
            captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
            captured_piece_bitboard &= ~self.board.SquareToBB(final_sq)
            self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

            self.board.pieces.remove(captured_piece)

            # set captured piece
            self.board.move_history[-1].captured_piece = captured_piece
            #self.board.move_history[-1] = self.board.move_history[-1][:3] + (captured_piece,)

        else:
            if move_type == 'EP' and piece.name in ['P', 'p']:
                # en-passant capture

                captured_piece = None
        
                if piece.name == 'P':
                    # white pawn performs EP capture, black pawn is below final square
                    captured_piece = self.board.GetPieceOnSquare(final_sq + 8)

                elif piece.name == 'p':
                    # black pawn performs EP capture, white pawn is above final square
                    captured_piece = self.board.GetPieceOnSquare(final_sq - 8)
                
                # remove captured piece from square
                captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
                captured_piece_bitboard &= ~self.board.SquareToBB(captured_piece.square)
                self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

                self.board.pieces.remove(captured_piece)

                self.board.move_history[-1].captured_piece = captured_piece

        if move_type != '_' and move_type != 'EP' and 'C' not in move_type:
            # promotion, set bitboard of move type parameter, which is the piece we want to promote to
            promotion_piece_bitboard = self.board.GetBitboard(move_type)
            promotion_piece_bitboard |= self.board.SquareToBB(final_sq)
            self.board.SetBitboard(move_type, promotion_piece_bitboard)

            # change piece's name and square, increased times moved
            piece.name = move_type
            piece.square = final_sq
            piece.times_moved += 1
            #piece.promoted = True
            self.board.move_history[-1].is_promotion_move = True
        
        else:
            # move piece to final square in its bitboard
            drag_piece_bitboard = self.board.GetBitboard(piece.name)
            drag_piece_bitboard |= self.board.SquareToBB(final_sq)
            self.board.SetBitboard(piece.name, drag_piece_bitboard)

            # change piece's square, set has moved to true
            piece.square = final_sq
            piece.times_moved += 1

            # perform rook movement for castling move
            if move_type == 'CK':
                rook = self.board.GetPieceOnSquare(63)
                new_rook_position = initial_sq + 1

                self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('K', '')             

            elif move_type == 'CQ':
                rook = self.board.GetPieceOnSquare(56)
                new_rook_position = initial_sq - 2

                self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('Q', '')

            elif move_type == 'Ck':
                rook = self.board.GetPieceOnSquare(7)
                new_rook_position = initial_sq + 1

                self.board.black_rooks &= ~self.ooard.SquareToBB(rook.square)
                self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('k', '')

            elif move_type == 'Cq':
                rook = self.board.GetPieceOnSquare(0)
                new_rook_position = initial_sq - 2

                self.board.black_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('q', '')
                            
        self.board.ply += 1
        self.board.moves = self.board.ply // 2

        # after move is made, bitboards have changed, so update all bitboard variables. 
        # update ascii board, this is used for rendering
        self.board.SetUpBitboards()
        self.board.UpdateBoard()

        self.SwitchActivePiece()

        self.previous_possible_moves.append(self.moveGen.possible_moves)
        self.moveGen.GenerateAllPossibleMoves()   

        self.SetAttackedSquares()

        if self.IsCheckmate():
            self.dragging = False
            self.is_checkmate = True

        if self.IsStalemate():
            self.dragging = False
            self.is_stalemate = True


    def UnmakeMove(self):
        """
        revert move at top of move history list
        
        - subtract ply and moves
        - if castling move, add castling type to castling rights 
        """
        if len(self.previous_possible_moves) >= 1:
            past_move = self.board.move_history.pop()
            piece, initial_sq, final_sq, move_type, is_promotion_move = past_move.piece, past_move.initial, past_move.dest, past_move.type, past_move.is_promotion_move

            if past_move.captured_piece != None:
                # remove from final square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard &= ~self.board.SquareToBB(final_sq)

                if is_promotion_move:
                    # set bitboard of the piece that was promoted to, to register
                    # removal of piece from final square
                    self.board.SetBitboard(piece.name, drag_piece_bitboard)

                    piece.name = 'P' if piece.name.isupper() else 'p'
                    piece.square = initial_sq
                    piece.times_moved -= 1
                    #piece.promoted = False

                    # set bitboard of pawn and set it with initial square
                    drag_piece_bitboard = self.board.GetBitboard(piece.name)
                    drag_piece_bitboard |= self.board.SquareToBB(initial_sq)
                else:
                    drag_piece_bitboard |= self.board.SquareToBB(initial_sq)

                # set bitboard of drag piece to be in initial square
                self.board.SetBitboard(piece.name, drag_piece_bitboard)

                # captures move happened, so restore captured piece
                captured_piece_bitboard = self.board.GetBitboard(past_move.captured_piece.name)
                captured_piece_bitboard |= self.board.SquareToBB(past_move.captured_piece.square)
                self.board.SetBitboard(past_move.captured_piece.name, captured_piece_bitboard)

                self.board.pieces.append(past_move.captured_piece)

                piece.square = initial_sq
                piece.times_moved -= 1

            elif move_type != '_' and move_type != 'EP' and 'C' not in move_type:
                # must be promotion move, without captures

                # remove promoted piece from final square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard &= ~self.board.SquareToBB(final_sq)

                # set bitboard of the piece that the pawn promoted to, to register
                # remove of piece from final square
                self.board.SetBitboard(piece.name, drag_piece_bitboard)

                piece.name = 'P' if piece.name.isupper() else 'p'
                piece.square = initial_sq
                piece.times_moved -= 1
                piece.promoted = False

                # set bitboard of pawn and set it with initial square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard |= self.board.SquareToBB(initial_sq)
                self.board.SetBitboard(piece.name, drag_piece_bitboard)

            else:
                # must be normal move, movement with no captures, or castling

                # move drag piece back to initial square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard |= self.board.SquareToBB(initial_sq)

                # remove drag piece from final square
                drag_piece_bitboard &= ~self.board.SquareToBB(final_sq)

                self.board.SetBitboard(piece.name, drag_piece_bitboard)

                piece.square = initial_sq
                piece.times_moved -= 1

                # if castling move, move rook back to where it has to be, and revert castlng rights

                if move_type == 'CK':
                    new_rook_position = initial_sq + 1
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.white_rooks |= self.board.SquareToBB(63)

                    rook.square = 63
                    rook.times_moved -= 1

                    self.board.castling_rights += 'K'            

                elif move_type == 'CQ':
                    new_rook_position = initial_sq - 2
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.white_rooks |= self.board.SquareToBB(56)

                    rook.square = 56
                    rook.times_moved -= 1

                    self.board.castling_rights += 'Q'       

                elif move_type == 'Ck':
                    new_rook_position = initial_sq + 1
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.black_rooks |= self.board.SquareToBB(7)

                    rook.square = 7
                    rook.times_moved -= 1

                    self.board.castling_rights += 'k'    

                elif move_type == 'Cq':
                    new_rook_position = initial_sq - 2
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.black_rooks |= self.board.SquareToBB(0)

                    rook.square = 0
                    rook.times_moved -= 1

                    self.board.castling_rights += 'q'    
                
            self.board.ply -= 1
            self.board.moves -= 1 # ?
            self.SwitchActivePiece()

            self.moveGen.ally_king = self.moveGen.GetAllyKing()
            self.moveGen.GetAttackers()

            self.is_checkmate = False
            self.is_stalemate = False
        
            self.board.SetUpBitboards()
            self.board.UpdateBoard()

            self.moveGen.possible_moves = self.previous_possible_moves.pop()

            self.SetAttackedSquares()
    

