import pygame
from classicalBitboard import Board
from moveGeneration import GenerateMoves, SPECIAL_MOVE_FLAGS, FLAG_MASK, TO_SQ_MASK, FROM_SQ_MASK, PROMOTION_MOVE_MASK, CAPTURE_MOVE_MASK
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

        self.captured_pieces = []

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
        king_can_move = len(list(filter(lambda move : self.board.GetPieceOnSquare((move & 0xfc0) >> 6) == self.moveGen.ally_king, self.moveGen.possible_moves))) != 0
        attacker_attacked = all([sq in self.attacked_squares for sq in self.board.BBToSquares(self.board.attackers)])

        return (king_can_move == False and self.board.attackers != 0 and attacker_attacked == False and len(self.moveGen.possible_moves) == 0)

    def IsStalemate(self):
        return len(self.moveGen.possible_moves) == 0 and self.board.attackers == 0
    
    def SetAttackedSquares(self):
        self.attacked_squares = []

        for move in self.moveGen.possible_moves:
            self.attacked_squares.append(move & 0x3f)

    def SwitchActivePiece(self):
        if self.board.active_piece == "w":
            self.board.active_piece = "b"
        else:
            self.board.active_piece = "w"

    def GetPromotionPiece(self, move_type, piece):

        if (move_type == SPECIAL_MOVE_FLAGS["npc"]) | (move_type == SPECIAL_MOVE_FLAGS["knight_promo"]):
            return 'N' if piece.colour == 'w' else 'n'

        elif (move_type == SPECIAL_MOVE_FLAGS["bpc"]) | (move_type == SPECIAL_MOVE_FLAGS["bishop_promo"]):
            return 'B' if piece.colour == 'w' else 'b'
        
        elif (move_type == SPECIAL_MOVE_FLAGS["rpc"]) | (move_type == SPECIAL_MOVE_FLAGS["rook_promo"]):
            return 'R' if piece.colour == 'w' else 'r'
        
        elif (move_type == SPECIAL_MOVE_FLAGS["qpc"]) | (move_type == SPECIAL_MOVE_FLAGS["queen_promo"]):
            return 'Q' if piece.colour == 'w' else 'q'
    
    def MakeMove(self, move):

        self.board.move_history.append(move)

        from_sq, to_sq, move_type = (move & FROM_SQ_MASK) >> 6, move & TO_SQ_MASK, (move & FLAG_MASK) 

        piece = self.board.GetPieceOnSquare(from_sq)

        """
        remove piece from initial square
        """
        drag_piece_bitboard = self.board.GetBitboard(piece.name)
        drag_piece_bitboard &= ~self.board.SquareToBB(from_sq)
        self.board.SetBitboard(piece.name, drag_piece_bitboard)

        """
        remove captured piece from final square if move is a type of capture move
        """
        if move_type & CAPTURE_MOVE_MASK != 0:
            # remove captured piece from final square if move is captures move of any kind

            captured_piece = None
        
            if move_type == SPECIAL_MOVE_FLAGS["ep_capture"] and piece.colour == 'w':
                # white pawn performs EP capture, black pawn is below final square
                captured_piece = self.board.GetPieceOnSquare(to_sq + 8)
            
            elif move_type == SPECIAL_MOVE_FLAGS["ep_capture"] and piece.colour == 'b':
                # black pawn performs EP capture, white pawn is above final square
                captured_piece = self.board.GetPieceOnSquare(to_sq - 8)
            
            else:
                # normal captures
                captured_piece = self.board.GetPieceOnSquare(to_sq)
            
            captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
            captured_piece_bitboard &= ~self.board.SquareToBB(to_sq)
            self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

            self.board.pieces.remove(captured_piece)
            self.captured_pieces.append(captured_piece)


        """
        move piece to final square in its bitboard if not a promotion move
        """
        if move_type & PROMOTION_MOVE_MASK == 0:
            
            drag_piece_bitboard = self.board.GetBitboard(piece.name)
            drag_piece_bitboard |= self.board.SquareToBB(to_sq)
            self.board.SetBitboard(piece.name, drag_piece_bitboard)

            # change piece's square, increase times moved
            piece.square = to_sq
            piece.times_moved += 1
        
        else:
            promo_piece = self.GetPromotionPiece(move_type, piece)
            
            promotion_piece_bitboard = self.board.GetBitboard(promo_piece)
            promotion_piece_bitboard |= self.board.SquareToBB(to_sq)
            self.board.SetBitboard(promo_piece, promotion_piece_bitboard)

            # change piece's name and square, increased times moved
            piece.name = promo_piece
            piece.square = to_sq
            piece.times_moved += 1


        """
        perform rook movement for castling moves
        """
        if move_type == SPECIAL_MOVE_FLAGS["king_castle"] and piece.colour == 'w':
            # kingside castle, white king

            rook = self.board.GetPieceOnSquare(63)
            new_rook_position = from_sq + 1

            self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
            self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

            rook.square = new_rook_position
            rook.times_moved += 1

            self.board.castling_rights = self.board.castling_rights.replace('K', '')

        elif move_type == SPECIAL_MOVE_FLAGS["king_castle"] and piece.colour == 'b':
            # kingside castle, black king

            rook = self.board.GetPieceOnSquare(7)
            new_rook_position = from_sq + 1

            self.board.black_rooks &= ~self.board.SquareToBB(rook.square)
            self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

            rook.square = new_rook_position
            rook.times_moved += 1

            self.board.castling_rights = self.board.castling_rights.replace('k', '')
        
        elif move_type == SPECIAL_MOVE_FLAGS["queen_castle"] and piece.colour == 'w':
            # queenside castle, white king
            rook = self.board.GetPieceOnSquare(56)
            new_rook_position = from_sq - 2

            self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
            self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

            rook.square = new_rook_position
            rook.times_moved += 1

            self.board.castling_rights = self.board.castling_rights.replace('Q', '')
        
        elif move_type == SPECIAL_MOVE_FLAGS["queen_castle"] and piece.colour == 'b':
            # queenside castle, black king
            rook = self.board.GetPieceOnSquare(0)
            new_rook_position = from_sq - 2

            self.board.black_rooks &= ~self.board.SquareToBB(rook.square)
            self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

            rook.square = new_rook_position
            rook.times_moved += 1

            self.board.castling_rights = self.board.castling_rights.replace('q', '')

        self.board.ply += 1
        self.board.moves = self.board.ply // 2

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
        get move at top of move list, revert it. 
        """
        
        if len(self.previous_possible_moves) >= 1:
            move = self.board.move_history.pop()

            from_sq, to_sq, move_type = (move & FROM_SQ_MASK) >> 6, move & TO_SQ_MASK, (move & FLAG_MASK)
            piece = self.board.GetPieceOnSquare(to_sq)

            if move_type & PROMOTION_MOVE_MASK != 0:
                # move is promotion move, change piece to pawn first
                piece.name = "P" if piece.name.isupper() else "p"

            drag_piece_bitboard = self.board.GetBitboard(piece.name)
            drag_piece_bitboard &= ~self.board.SquareToBB(to_sq)
            drag_piece_bitboard |= self.board.SquareToBB(from_sq)
            self.board.SetBitboard(piece.name, drag_piece_bitboard)

            piece.square = from_sq
            piece.times_moved -= 1

            if move_type & CAPTURE_MOVE_MASK != 0:
                # move is capture move
                captured_piece = self.captured_pieces.pop()

                captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
                captured_piece_bitboard |= self.board.SquareToBB(to_sq)
                self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

                self.board.pieces.append(captured_piece)

            """
            perform rook movement for castling moves
            """

            if move_type == SPECIAL_MOVE_FLAGS["king_castle"] and piece.colour == 'w':
                # kingside castle, white king

                new_rook_position = from_sq + 1
                rook = self.board.GetPieceOnSquare(new_rook_position)
            
                self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                self.board.white_rooks |= self.board.SquareToBB(63)

                rook.square = 63
                rook.times_moved -= 1

                self.board.castling_rights += 'K'   

            elif move_type == SPECIAL_MOVE_FLAGS["king_castle"] and piece.colour == 'b':
                # kingside castle, black king

                new_rook_position = from_sq + 1
                rook = self.board.GetPieceOnSquare(new_rook_position)
            
                self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                self.board.black_rooks |= self.board.SquareToBB(7)

                rook.square = 7
                rook.times_moved -= 1

                self.board.castling_rights += 'k'
        
            elif move_type == SPECIAL_MOVE_FLAGS["queen_castle"] and piece.colour == 'w':
                # queenside castle, white king

                new_rook_position = from_sq - 2
                rook = self.board.GetPieceOnSquare(new_rook_position)
            
                self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                self.board.white_rooks |= self.board.SquareToBB(56)

                rook.square = 56
                rook.times_moved -= 1

                self.board.castling_rights += 'Q'   

            elif move_type == SPECIAL_MOVE_FLAGS["queen_castle"] and piece.colour == 'b':
            # queenside castle, black king
                new_rook_position = from_sq - 2
                rook = self.board.GetPieceOnSquare(new_rook_position)
            
                self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                self.board.black_rooks |= self.board.SquareToBB(0)

                rook.square = 0
                rook.times_moved -= 1

                self.board.castling_rights += 'q'    

            self.board.ply -= 1
            self.board.moves -= 1 
            self.SwitchActivePiece()

            self.moveGen.ally_king = self.moveGen.GetAllyKing()
            self.moveGen.GetAttackers()

            self.is_checkmate = False
            self.is_stalemate = False
        
            self.board.SetUpBitboards()
            self.board.UpdateBoard()

            self.moveGen.possible_moves = self.previous_possible_moves.pop()

            self.SetAttackedSquares()

    