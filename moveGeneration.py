import numpy as np
from typing import Any

class GenerateMoves:
    def __init__(self, board_object):
        self.possible_moves = [] # stores moves for all pieces expect kings

        self.ally_king = None
        self.enemy_king = None
                     
        self.board = board_object

        """
        Kings, pawns* and knights move in very predictable ways. These lookup tables are pre-calculated with each square and possible squares piece can land on.
        Finding actual moves is a matter of making 
        """
        self.KING_TABLE : dict[int, Any] = {}
        self.KNIGHT_TABLE : dict[int, Any] = {}
        self.RAYS : dict[str, dict[int, Any]] = {}
        for sq in range(0, 64):
            # each square key stores bitboard of attack set
            self.KING_TABLE[sq] = 0
            self.KNIGHT_TABLE[sq] = 0

        # legal move filtration
        self.capture_mask = 0 # bitboard of all squares we can possibly capture to
        self.push_mask = 0 # bitboard of all squares we can popssibly move to
        self.number_of_attackers = 0

        self.opposite_dir = {'N': 'S', 'E': 'W', 'NE': 'SW', 'NW': 'SE', 'SE': 'NW', 'SW': 'NE', 'S': 'N', 'W':'E'}

        self.CASTLING_MASKS = {'CQ': {'R': np.uint64(128), 'd': np.uint64(120)}, 'CK': {'R': np.uint64(1), 'd': np.uint64(14)}, 'Ck': {'r': np.uint(2**56), 'd': np.uint64(2**59 + 2**58 + 2**57)}, 'Cq': {'r': np.uint64(2**63), 'd': np.uint64(2**62 + 2**61 + 2**59 + 2**60)}}
        self.get_castling_masks = lambda type, *k: [self.CASTLING_MASKS[type][i] for i in k]


    def PossibleWhitePawnMoves(self):
        rank_8 = self.board.RANKS(8)
        rank_4 = self.board.RANKS(4)
        rank_5 = self.board.RANKS(5)

        # right captures
        r_captures = (self.board.white_pawns << np.uint64(7)) & ~rank_8 & ~self.board.A_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= r_captures

        else:
            dest_squares = self.board.BBToSquares(r_captures & self.board.all_blacks & self.capture_mask)

            for sq in dest_squares:
                white_pawn = self.board.GetPieceOnSquare(sq + 7)
                self.possible_moves.append((white_pawn, white_pawn.square, sq, '_'))

        # left_captures
        l_captures = (self.board.white_pawns << np.uint64(9)) & ~rank_8 & ~self.board.H_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= l_captures

        else:
            dest_squares = self.board.BBToSquares(l_captures & self.board.all_blacks & self.capture_mask)

            for sq in dest_squares:
                white_pawn = self.board.GetPieceOnSquare(sq + 9)
                self.possible_moves.append((white_pawn, white_pawn.square, sq, '_'))

        # forward by 1
        if self.board.active_piece == 'w':
            forward_1 = (self.board.white_pawns << np.uint(8)) & self.board.empty & ~rank_8 & self.push_mask

            dest_squares = self.board.BBToSquares(forward_1)

            for sq in dest_squares:
                white_pawn = self.board.GetPieceOnSquare(sq + 8)
                self.possible_moves.append((white_pawn, white_pawn.square, sq, '_'))

        # forward by 2
        if self.board.active_piece == 'w':
            forward_2 = (self.board.white_pawns << np.uint64(16)) & self.board.empty & (self.board.empty << np.uint64(8)) & ~rank_8 & rank_4 & self.push_mask 
            dest_squares = self.board.BBToSquares(forward_2)

            for sq in dest_squares:
                white_pawn = self.board.GetPieceOnSquare(sq + 16)
                self.possible_moves.append((white_pawn, white_pawn.square, sq, '_'))

        # promotion by right captures
        promo_r_captures = (self.board.white_pawns << np.uint64(7)) & rank_8 & ~self.board.A_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= promo_r_captures
        else:
            dest_squares = self.board.BBToSquares(promo_r_captures & self.board.all_blacks & self.capture_mask)

            for sq in dest_squares:
                for promotes_to in ['Q', 'N', 'R', 'B']:
                    white_pawn = self.board.GetPieceOnSquare(sq + 7)
                    self.possible_moves.append((white_pawn, white_pawn.square, sq, promotes_to))

        # promotion by left captures
        promo_l_captures = (self.board.white_pawns << np.uint64(9)) & rank_8 & ~self.board.H_FILE 

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= promo_l_captures
        else:
            dest_squares = self.board.BBToSquares(promo_l_captures & self.board.all_blacks & self.capture_mask)

            for sq in dest_squares:
                for promotes_to in ['Q', 'N', 'R', 'B']:
                    white_pawn = self.board.GetPieceOnSquare(sq + 9)
                    self.possible_moves.append((white_pawn, white_pawn.square, sq, promotes_to))

        # promotion by forward 1
        if self.board.active_piece == 'w':
            promo_forward_1 = (self.board.white_pawns << np.uint(8)) & self.board.empty & rank_8 & self.push_mask

            dest_squares = self.board.BBToSquares(promo_forward_1)

            for sq in dest_squares:
                for promotes_to in ['Q', 'N', 'R', 'B']:
                    white_pawn = self.board.GetPieceOnSquare(sq + 8)
                    self.possible_moves.append((white_pawn, white_pawn.square, sq, promotes_to))

        # en-passant
        if len(self.board.move_history) >= 1:
            last_move = self.board.move_history[-1]

            piece, initial_square, final_sq, _ = last_move

            if piece.name == 'p' and abs(initial_square-final_sq) == 2*8:
                ep_file = final_sq%8 + 1
                # move by black pawn 2 up

                # en-passant right
                if (self.board.white_pawns >> np.uint64(1)) & self.board.black_pawns & self.board.FILES[ep_file] & ~self.board.A_FILE & rank_5 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_right = (self.board.white_pawns << np.uint64(7))  & ~self.board.A_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'b':
                        self.board.king_danger_squares |= ep_right
                    else:
                        captured_piece = (self.board.white_pawns >> np.uint64(1)) & self.board.black_pawns & self.board.FILES[ep_file] & ~self.board.A_FILE & rank_5
                        
                        if ep_right & self.push_mask != 0 or captured_piece & self.capture_mask != 0:
                            dest_squares = self.board.BBToSquares(ep_right)

                            for sq in dest_squares:
                                white_pawn = self.board.GetPieceOnSquare(sq + 7)
                                self.possible_moves.append((white_pawn, white_pawn.square, sq, 'EP'))

                # en-passant left
                if (self.board.white_pawns << np.uint64(1)) & self.board.black_pawns & self.board.FILES[ep_file] & ~self.board.H_FILE & rank_5 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_left = (self.board.white_pawns << np.uint64(9))  & ~self.board.H_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'b':
                        self.board.king_danger_squares |= ep_left
                    else:
                        captured_piece = (self.board.white_pawns << np.uint64(1)) & self.board.black_pawns & self.board.FILES[ep_file] & ~self.board.H_FILE & rank_5

                        if ep_left & self.push_mask != 0 or captured_piece & self.capture_mask != 0:
                            dest_squares = self.board.BBToSquares(ep_left)

                            for sq in dest_squares:
                                white_pawn = self.board.GetPieceOnSquare(sq + 9)
                                self.possible_moves.append((white_pawn, white_pawn.square, sq, 'EP'))
                    
    def PossibleBlackPawnMoves(self):
        rank_1 = self.board.RANKS(1)
        rank_5 = self.board.RANKS(5)
        rank_4 = self.board.RANKS(4)

        # right captures
        r_captures = (self.board.black_pawns >> np.uint64(9)) & ~rank_1 & ~self.board.A_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= r_captures
        else:
            dest_squares = self.board.BBToSquares(r_captures & self.board.all_whites & self.capture_mask)

            for sq in dest_squares:
                black_pawn = self.board.GetPieceOnSquare(sq - 9)
                self.possible_moves.append((black_pawn, black_pawn.square, sq, '_'))

        # left_captures
        l_captures = (self.board.black_pawns >> np.uint64(7)) & ~rank_1 & ~self.board.H_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= l_captures
        else:
        
            dest_squares = self.board.BBToSquares(l_captures & self.board.all_whites & self.capture_mask)

            for sq in dest_squares:
                black_pawn = self.board.GetPieceOnSquare(sq - 7)
                self.possible_moves.append((black_pawn, black_pawn.square, sq, '_'))

        # forward by 1
        if self.board.active_piece == 'b':
            forward_1 = (self.board.black_pawns >> np.uint(8)) & self.board.empty & ~rank_1 & self.push_mask 

            dest_squares = self.board.BBToSquares(forward_1)

            for sq in dest_squares:
                black_pawn = self.board.GetPieceOnSquare(sq - 8)
                self.possible_moves.append((black_pawn, black_pawn.square, sq, '_'))

        # forward by 2
        if self.board.active_piece == 'b':
            forward_2 = (self.board.black_pawns >> np.uint64(16)) & self.board.empty & (
                        self.board.empty >> np.uint64(8)) & ~rank_1 & rank_5 & self.push_mask 

            dest_squares = self.board.BBToSquares(forward_2)

            for sq in dest_squares:
                black_pawn = self.board.GetPieceOnSquare(sq - 16)
                self.possible_moves.append((black_pawn, black_pawn.square, sq, '_'))

        # promotion by right captures
        promo_r_captures = (self.board.black_pawns >> np.uint64(9)) & rank_1 & ~self.board.A_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= promo_r_captures
        else:

            dest_squares = self.board.BBToSquares(promo_r_captures & self.board.all_whites & self.capture_mask)

            for sq in dest_squares:
                for promotes_to in ['q', 'n', 'r', 'b']:
                    black_pawn = self.board.GetPieceOnSquare(sq - 9)
                    self.possible_moves.append((black_pawn, black_pawn.square, sq, promotes_to))

        # promotion by left captures
        promo_l_captures = (self.board.black_pawns >> np.uint64(7)) & rank_1 & ~self.board.H_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= promo_l_captures
        else:

            dest_squares = self.board.BBToSquares(promo_l_captures & self.board.all_whites & self.capture_mask)

            for sq in dest_squares:
                for promotes_to in ['q', 'n', 'r', 'b']:
                    black_pawn = self.board.GetPieceOnSquare(sq - 7)
                    self.possible_moves.append((black_pawn, black_pawn.square, sq, promotes_to))

        # promotion by forward 1
        if self.board.active_piece == 'b':
            promo_forward_1 = (self.board.black_pawns >> np.uint(8)) & self.board.empty & rank_1 & self.push_mask 

            dest_squares = self.board.BBToSquares(promo_forward_1)

            for sq in dest_squares:
                for promotes_to in ['q', 'n', 'r', 'b']:
                    black_pawn = self.board.GetPieceOnSquare(sq - 8)
                    self.possible_moves.append((black_pawn, black_pawn.square, sq, promotes_to))

        # en-passant
        if len(self.board.move_history) >= 1:
            last_move = self.board.move_history[-1]

            piece, initial_square, final_sq, _ = last_move

            if piece.name == 'P' and abs(initial_square - final_sq) == 2 * 8:
                ep_file = final_sq % 8 + 1
                # move by white pawn 2 up

                # en-passant right
                if (self.board.black_pawns >> np.uint64(1)) & self.board.white_pawns & self.board.FILES[
                    ep_file] & ~self.board.A_FILE & rank_4 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_right = (self.board.black_pawns >> np.uint64(9)) & ~self.board.A_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'w':
                        self.board.king_danger_squares |= ep_right
                    else:
                        captured_piece = (self.board.black_pawns >> np.uint64(1)) & self.board.white_pawns & self.board.FILES[
                    ep_file] & ~self.board.A_FILE & rank_4
                        
                        if ep_right & self.push_mask != 0 or captured_piece & self.capture_mask != 0:
                            dest_squares = self.board.BBToSquares(ep_right)

                            for sq in dest_squares:
                                black_pawn = self.board.GetPieceOnSquare(sq - 9)
                                self.possible_moves.append((black_pawn, black_pawn.square, sq, 'EP'))

                # en-passant left
                if (self.board.black_pawns << np.uint64(1)) & self.board.white_pawns & self.board.FILES[
                    ep_file] & ~self.board.H_FILE & rank_4 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_left = (self.board.black_pawns >> np.uint64(7)) & ~self.board.H_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'w':
                        self.board.king_danger_squares |= ep_left
                    else:
                        captured_piece = (self.board.black_pawns << np.uint64(1)) & self.board.white_pawns & self.board.FILES[
                    ep_file] & ~self.board.H_FILE & rank_4

                        if ep_left & self.push_mask != 0 or captured_piece & self.capture_mask != 0:
                            dest_squares = self.board.BBToSquares(ep_left)

                            for sq in dest_squares:
                                black_pawn = self.board.GetPieceOnSquare(sq - 7)
                                self.possible_moves.append((black_pawn, black_pawn.square, sq, 'EP'))
        
    def PossibleWhitePawnKingAttacks(self, square):
        """
        get possible attacks for a white pawn at a given square

        this function checks specifically for possible captures moves of a given pawn
        """
        pawn_bitboard = self.board.SquareToBB(square)
        result = np.uint64(0)

        rank_8 = self.board.RANKS(8)
  
        # right captures
        r_captures = ((self.board.white_pawns & pawn_bitboard) << np.uint64(7)) & ~rank_8 & ~self.board.A_FILE

        result |= (r_captures & self.board.black_king)

        # left_captures
        l_captures = ((self.board.white_pawns & pawn_bitboard) << np.uint64(9)) & ~rank_8 & ~self.board.H_FILE

        result |= (l_captures & self.board.black_king)

        # promotion by right captures
        promo_r_captures = ((self.board.white_pawns & pawn_bitboard) << np.uint64(7)) & rank_8 & ~self.board.A_FILE

        result |= (promo_r_captures & self.board.black_king)

        # promotion by left captures
        promo_l_captures = ((self.board.white_pawns & pawn_bitboard) << np.uint64(9)) & rank_8 & ~self.board.H_FILE

        result |= (promo_l_captures & self.board.black_king)
    
        return result

    def PossibleBlackPawnKingAttacks(self, square):
        """
        get possible attacks for a white pawn at a given square

        this function checks specifically for possible captures moves of a given pawn
        """
        pawn_bitboard = self.board.SquareToBB(square)
        result = np.uint64(0)

        rank_1 = self.board.RANKS(1)
    
        # right captures
        r_captures = ((self.board.black_pawns & pawn_bitboard) >> np.uint64(9)) & ~rank_1 & ~self.board.A_FILE

        result |= (r_captures & self.board.white_king)

        # left_captures
        l_captures = ((self.board.black_pawns & pawn_bitboard) >> np.uint64(7)) & ~rank_1 & ~self.board.H_FILE

        result |= (l_captures & self.board.white_king)

        # promotion by right captures
        promo_r_captures = ((self.board.black_pawns & pawn_bitboard) >> np.uint64(9)) & rank_1 & ~self.board.A_FILE

        result |= (promo_r_captures & self.board.white_king)

        # promotion by left captures
        promo_l_captures = ((self.board.black_pawns & pawn_bitboard) >> np.uint64(7)) & rank_1 & ~self.board.H_FILE

        result |= (promo_l_captures & self.board.white_king)

        return result

    def GetKnightAttackSet(self, bitboard):
        rank_8 = self.board.RANKS(8)
        rank_7 =  self.board.RANKS(7)
        rank_1 = self.board.RANKS(1)
        rank_2 = self.board.RANKS(2)
        rank_78 = rank_7 | rank_8
        rank_12 = rank_1 | rank_2

        knight_attack_set = np.uint64(0)
        
        nne = (bitboard & ~(self.board.H_FILE | rank_78)) << np.uint64(15)

        knight_attack_set |= nne

        ne = (bitboard & ~(self.board.GH_FILE | rank_8)) << np.uint64(6)
        
        knight_attack_set |= ne

        nnw = (bitboard & ~(self.board.A_FILE | rank_78)) << np.uint64(17)

        knight_attack_set |= nnw

        nw = (bitboard & ~(self.board.AB_FILE | rank_8)) << np.uint64(10)

        knight_attack_set |= nw

        sse = (bitboard & ~(self.board.H_FILE | rank_12)) >> np.uint64(17)

        knight_attack_set |= sse

        se = (bitboard & ~(self.board.GH_FILE | rank_1)) >> np.uint64(10)

        knight_attack_set |= se
        
        ssw = (bitboard & ~(self.board.A_FILE | rank_12)) >> np.uint64(15)

        knight_attack_set |= ssw

        sw = (bitboard & ~(self.board.AB_FILE | rank_1)) >> np.uint64(6)

        knight_attack_set |= sw

        return knight_attack_set

    def GetKingAttackSet(self, bitboard):
        rank_8 = self.board.RANKS(8)
        rank_1 = self.board.RANKS(1)
    
        king_attack_set = np.uint64(0)

        n = (bitboard & ~rank_8) << np.uint64(8)
        king_attack_set |= n

        e = (bitboard & ~self.board.H_FILE) >> np.uint64(1)
        king_attack_set |= e

        w = (bitboard & ~self.board.A_FILE) << np.uint64(1)
        king_attack_set |= w

        s = (bitboard & ~rank_1) >> np.uint(8)
        king_attack_set |= s

        ne = (bitboard & ~(rank_8 | self.board.H_FILE)) << np.uint64(7)
        king_attack_set |= ne

        nw = (bitboard & ~(rank_8 | self.board.A_FILE)) << np.uint64(9)
        king_attack_set |= nw

        se = (bitboard & ~(rank_1 | self.board.H_FILE)) >> np.uint64(9)
        king_attack_set |= se

        sw = (bitboard & ~(rank_1 | self.board.A_FILE)) >> np.uint64(7)
        king_attack_set |= sw

        return king_attack_set

    def PopulateAttackTables(self):
        for sq, _ in self.KNIGHT_TABLE.items():
            initial_bitboard = self.board.SquareToBB(sq)

            self.KNIGHT_TABLE[sq] = self.GetKnightAttackSet(initial_bitboard)

        for sq, _ in self.KING_TABLE.items():
            initial_bitboard = self.board.SquareToBB(sq)

            self.KING_TABLE[sq] = self.GetKingAttackSet(initial_bitboard)
    
    @staticmethod
    def GreaterThanDiagonal(square, dir):
        x, y  = square % 8, square // 8

        if dir == 'NE' or dir == 'SW':
            return (x + y) >= 7

        elif dir == 'NW' or dir == 'SE':
            return (x - y) >= 0 

    def GetNumberOfShifts(self, square, dir):
        x, y  = square % 8, square // 8

        if dir == 'NE':
            if self.GreaterThanDiagonal(square, 'NE'):
                return 7 - x
            else:
                return y

        elif dir == 'SW':
            if self.GreaterThanDiagonal(square, 'SW'):
                return 7 - y
            else:
                return x

        elif dir == 'NW':
            if self.GreaterThanDiagonal(square, 'NW'):
                return y
            else:
                return x

        elif dir == 'SE':
            if self.GreaterThanDiagonal(square, 'SE'):
                return 7 - x
            else:
                return 7 - y

        elif dir == 'N':
            return  y

        elif dir == 'E':
            return 7 - x

        elif dir == 'W':
            return x

        elif dir == 'S':
            return 7 - y

    def PopulateRayTable(self):
        shift_by = {'N':8, 'E':1, 'W':1, 'S':8, 'NE':7, 'NW':9, 'SE':9, 'SW':7}
        #restrictions = {'N':self.board.RANKS(8), 'E':self.board.H_FILE, 'W':self.board.A_FILE, 'S':self.board.RANKS(1), 'NE':self.board.RANKS(8), 'NW':self.board.RANKS(8), 'SE':self.board.RANKS(1), 'SW':self.board.RANKS(1)}

        for dir in ['N','E','W','S','NE','NW','SE','SW']:
            self.RAYS[dir] = {}

            for sq in range(64):
                ray = np.uint64(0)
                sq_bitboard = self.board.SquareToBB(sq)

                for shift in range(self.GetNumberOfShifts(sq, dir)):
                    if dir in ['NE', 'NW', 'W', 'N']:
                        # left shift
                        ray |= sq_bitboard << np.uint64((shift + 1) * shift_by[dir])

                    else:
                        # right shift
                        ray |= sq_bitboard >> np.uint64((shift + 1) * shift_by[dir])

                self.RAYS[dir][sq] = ray
    
    @staticmethod
    def BitscanForward(n):
        return np.uint64(int(np.binary_repr(n & -n), 2))

    @staticmethod
    def BitscanReverse(n):
        binary = bin(n)[2:][::-1]
        index = binary.rindex('1')

        return np.uint64(1) << np.uint64(index)

    def PossibleBishopMoves(self, piece_type, square):
        # blockers is all other pieces except itself
        blockers = self.board.occupied & ~self.board.SquareToBB(square)

        #setup result
        result = np.uint64(0)

        # NE
        ray = self.RAYS['NE'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray

            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray
                
        else:
            n = self.BitscanForward(masked_blockers)

            r = ray & ~self.RAYS['NE'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['NE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['NE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        # NW        
        ray = self.RAYS['NW'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray

        else:
            n = self.BitscanForward(masked_blockers)

            r = ray & ~self.RAYS['NW'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['NW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type  == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['NW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #SE
        ray = self.RAYS['SE'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray

        else:
            n = self.BitscanReverse(masked_blockers)

            r = ray & ~self.RAYS['SE'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['SE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares|= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['SE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #SW
        ray = self.RAYS['SW'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray


        else:
            n = self.BitscanReverse(masked_blockers)

            r = ray & ~self.RAYS['SW'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['SW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['SW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        return result
        

    def PossibleRookMoves(self, piece_type, square):
        # blockers is all other pieces except itself
        blockers = self.board.occupied & ~self.board.SquareToBB(square)

        #setup result
        result = np.uint64(0)

        # N
        ray = self.RAYS['N'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray
            
        else:
            n = self.BitscanForward(masked_blockers)

            r = ray & ~self.RAYS['N'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['N'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
   
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['N'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        # E        
        ray = self.RAYS['E'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray
            
        else:
            n = self.BitscanReverse(masked_blockers)

            r = ray & ~self.RAYS['E'][self.board.BBToSquares(n)[0]]
            
            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['E'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['E'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #W
        ray = self.RAYS['W'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray

            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray

        else:
            n = self.BitscanForward(masked_blockers)

            r = ray & ~self.RAYS['W'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['W'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = self.BitscanForward(msbs_without_king)
                r_prime = ray & ~self.RAYS['W'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #S
        ray = self.RAYS['S'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0 :
            result |= ray
            
            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray

        elif ((piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w')) and (masked_blockers & ~(self.board.black_king | self.board.white_king) == 0):
            self.board.king_danger_squares |= ray

        else:
            n = self.BitscanReverse(masked_blockers)

            r = ray & ~self.RAYS['S'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['S'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king

                n_prime = self.BitscanReverse(msbs_without_king)
                r_prime = ray & ~self.RAYS['S'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        return result


    def GetPossibleMoves(self, piece):
        """
        For a given piece type and square, the function appends to the list of all possible moves, all moves for given piece at given square
        Attacked squares bitboard is also calculated
        """ 
        if piece.name  == 'N':
            attack_set = self.KNIGHT_TABLE[piece.square] & (self.board.all_blacks | self.board.empty)

            if self.board.active_piece == 'b':
                self.board.king_danger_squares |= attack_set

            elif self.board.active_piece == 'w' and self.number_of_attackers <= 1:
                # filter ally move
                attack_set = attack_set & (self.capture_mask | self.push_mask)

                for dest_sq in self.board.BBToSquares(attack_set):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))

        elif piece.name == 'n':
            attack_set = self.KNIGHT_TABLE[piece.square] & (self.board.all_whites | self.board.empty)

            if self.board.active_piece == 'w':
                self.board.king_danger_squares |= attack_set
            elif self.board.active_piece == 'b' and self.number_of_attackers <= 1:
                # filter ally move
                attack_set = attack_set & (self.capture_mask | self.push_mask)

                for dest_sq in self.board.BBToSquares(attack_set):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))

        elif piece.name == 'K':
            attack_set = self.KING_TABLE[piece.square] & (self.board.all_blacks | self.board.empty)

            if self.board.active_piece == 'w':
                self.king_pseudo_legal_bitboard = attack_set
            
            else:
                self.board.king_danger_squares |= self.KING_TABLE[piece.square]

        elif piece.name == 'k':
            attack_set = self.KING_TABLE[piece.square] & (self.board.all_whites | self.board.empty)

            if self.board.active_piece == 'b':
                self.king_pseudo_legal_bitboard = attack_set
            else:
                self.board.king_danger_squares |= self.KING_TABLE[piece.square]
        
        elif piece.name == 'B':
            result = self.PossibleBishopMoves(piece.name, piece.square)

            if self.board.active_piece == 'w' and self.number_of_attackers <= 1:
                result &= (self.board.all_blacks | self.board.empty)

                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask
         
                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))

        elif piece.name == 'b':
            result = self.PossibleBishopMoves(piece.name, piece.square)

            if self.board.active_piece == 'b' and self.number_of_attackers <= 1:
                result &= (self.board.all_whites | self.board.empty)
                
                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask

                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))
            
        elif piece.name == 'R':
            result = self.PossibleRookMoves(piece.name, piece.square)

            if self.board.active_piece == 'w' and self.number_of_attackers <= 1:
                result &= (self.board.all_blacks | self.board.empty)

                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask

                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))

        elif piece.name == 'r':
            result = self.PossibleRookMoves(piece.name, piece.square)

            if self.board.active_piece == 'b' and self.number_of_attackers <= 1:
                # check that there's 1 or less attackers,  beacuse then no moves are possible, except king moves out of check
                result &= (self.board.all_whites | self.board.empty)
                
                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask

                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))
            
        elif piece.name == 'Q':
            result = self.PossibleBishopMoves('B', piece.square) | self.PossibleRookMoves('R', piece.square)

            if self.board.active_piece == 'w' and self.number_of_attackers <= 1:
                result &= (self.board.all_blacks | self.board.empty)
                
                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask

                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))

        elif piece.name == 'q':
            result = self.PossibleBishopMoves('b', piece.square) | self.PossibleRookMoves('r', piece.square)

            if self.board.active_piece == 'b' and self.number_of_attackers <= 1:
                result &= (self.board.all_whites | self.board.empty)

                if self.capture_mask != (2**64) - 1:
                    result &= (self.capture_mask | (self.push_mask & piece.pinned_mask))
                else:
                    # push mask will also be all 1s, but pinned mask has area between enemy slider and ally king and enemy piece, which is what we want
                    result &= piece.pinned_mask

                for dest_sq in self.board.BBToSquares(result):
                    self.possible_moves.append((piece, piece.square, dest_sq, '_'))
    

    def FilterKingMoves(self):
        filtered = self.king_pseudo_legal_bitboard & ~self.board.king_danger_squares

        for dest_sq in self.board.BBToSquares(filtered):
            self.possible_moves.append((self.ally_king, self.ally_king.square, dest_sq, '_'))

    def IsEnemyPiece(self, piece):
        return piece.colour != self.board.active_piece

    def IsAllyPiece(self, piece):
        return piece.colour == self.board.active_piece

    def GetAttackers(self):
        ally_king_square = self.ally_king.square
        self.board.attackers = np.uint64(0)

        for piece in self.board.pieces:
            if self.IsEnemyPiece(piece) and (piece.name != 'K' or piece.name != 'k'):
                # is enemy piece and not king

                if piece.name == 'N':
                    self.board.attackers |= (self.KNIGHT_TABLE[ally_king_square] & self.board.white_knights)
                
                elif piece.name == 'n':
                    self.board.attackers |= (self.KNIGHT_TABLE[ally_king_square] & self.board.black_knights)

                elif piece.name == 'B':
                    self.board.attackers |= (self.PossibleBishopMoves('B', ally_king_square) & self.board.white_bishops)

                elif piece.name == 'b':
                    self.board.attackers |= (self.PossibleBishopMoves('b', ally_king_square) & self.board.black_bishops)

                elif piece.name == 'R':
                    self.board.attackers |= (self.PossibleRookMoves('R', ally_king_square) & self.board.white_rooks)

                elif piece.name == 'r':
                    self.board.attackers |= (self.PossibleRookMoves('r', ally_king_square) & self.board.black_rooks)

                elif piece.name == 'Q':
                    queen_moves = self.PossibleBishopMoves('B', ally_king_square) | self.PossibleRookMoves('R', ally_king_square)
                    self.board.attackers |= (queen_moves & self.board.white_queen)
                
                elif piece.name == 'q':
                    queen_moves = self.PossibleBishopMoves('b', ally_king_square) | self.PossibleRookMoves('r', ally_king_square)
                    self.board.attackers |= (queen_moves & self.board.black_queen)

                elif piece.name == 'P':
                    if (self.PossibleWhitePawnKingAttacks(piece.square) & self.board.black_king) != 0:
                        self.board.attackers |= self.board.SquareToBB(piece.square)

                elif piece.name == 'p':
                    if (self.PossibleBlackPawnKingAttacks(piece.square) & self.board.white_king) != 0:
                        self.board.attackers |= self.board.SquareToBB(piece.square)
        
        if self.board.attackers in (2**np.arange(64)):
            self.number_of_attackers = 1
        
        elif self.board.attackers == 0:
            self.number_of_attackers = 0

        else:
            self.number_of_attackers = 2 # set to arbitrary number > 1

    def GetPushMask(self, king_square, attacker):
        blocker = self.board.SquareToBB(king_square)

        if attacker.name == 'R' or attacker.name == 'r':
            dirs = ['N', 'E', 'W', 'S']
            
        elif attacker.name == 'B' or attacker.name == 'b':
            dirs = ['NE', 'NW', 'SE', 'SW']

        elif attacker.name == 'Q' or attacker.name == 'q':
            dirs = ['N', 'E', 'W', 'S', 'NE', 'NW', 'SE', 'SW']

        for dir in dirs:
            ray = self.RAYS[dir][attacker.square] 
            if (ray & blocker) != 0:
                return ray & ~self.RAYS[dir][king_square]
        
    def SetMoveFilters(self):
        # set capture and push masks, these are for non-king pieces

        if self.number_of_attackers == 1:
            self.capture_mask = self.board.attackers

            # setup push mask....
            attacker = self.board.GetPiecesOnBitboard(self.board.attackers)[0]

            # if piece is a slider
            if attacker.name in ['Q', 'R', 'B', 'q', 'r', 'b']:
                self.push_mask = self.GetPushMask(self.ally_king.square, attacker)
            else:
                self.push_mask = np.uint64(0)
        
        elif self.number_of_attackers == 0:
            self.capture_mask = (2**64) - 1
            self.push_mask = (2**64) - 1

        else:
            self.capture_mask = np.uint64(0)
            self.push_mask = np.uint64(0)

    def SetPinnedMasks(self):
        """
        all pieces except for kings can be pinned

        for each possible direction from ally king, look at rays from enemy sliders in opposite direction, find intersection
        """
        # initialise
        for piece in self.board.pieces:
            piece.pinned_mask = (2**64) - 1

        if self.board.active_piece == 'w':
            enemy_sliders = self.board.GetPiecesOnBitboard(self.board.black_bishops | self.board.black_queen | self.board.black_rooks)
            enemy_pieces = self.board.all_blacks

            non_diagonal_pins = self.board.white_rooks | self.board.white_pawns | self.board.white_queen
            diagonal_pins = self.board.white_bishops | self.board.white_pawns | self.board.white_queen

        else:
            enemy_sliders = self.board.GetPiecesOnBitboard(self.board.white_bishops | self.board.white_queen | self.board.white_rooks)
            enemy_pieces = self.board.all_whites

            non_diagonal_pins = self.board.black_rooks | self.board.black_pawns | self.board.black_queen
            diagonal_pins = self.board.black_bishops | self.board.black_pawns | self.board.black_queen

        # non-diagonal
        for dir in ['N', 'E', 'W', 'S']:
            for piece in enemy_sliders:
                possible_mask = self.RAYS[self.opposite_dir[dir]][piece.square] & self.RAYS[dir][self.ally_king.square]
                
                if piece.name in ['R', 'r', 'Q', 'q'] and possible_mask & enemy_pieces == 0 and possible_mask & non_diagonal_pins in (2**np.arange(64)):
                    pinned_piece = self.board.GetPiecesOnBitboard(possible_mask & non_diagonal_pins)[0]

                    pinned_piece.pinned_mask = possible_mask | self.board.SquareToBB(piece.square) # add enemy slider to pinned mask

        # diagonal
        for dir in ['NE', 'SE', 'NW', 'SW']:
            for piece in enemy_sliders:
                possible_mask = self.RAYS[self.opposite_dir[dir]][piece.square] & self.RAYS[dir][self.ally_king.square]

                if piece.name in ['Q', 'q', 'B', 'b'] and possible_mask & enemy_pieces == 0 and possible_mask & diagonal_pins in (2**np.arange(64)):
                    pinned_piece = self.board.GetPiecesOnBitboard(possible_mask & diagonal_pins)[0]

                    pinned_piece.pinned_mask = possible_mask | self.board.SquareToBB(piece.square) # add enemy slider to pinned mask


    def GetAllyKing(self):
        return list(filter(lambda piece : self.IsAllyPiece(piece) and (piece.name == 'K' or piece.name == 'k'), self.board.pieces))[0]

    def GetEnemyKing(self):
        return list(filter(lambda piece : self.IsEnemyPiece(piece) and (piece.name == 'K' or piece.name == 'k'), self.board.pieces))[0]
    
    def AddCastlingMoves(self):
        """
        perform all necessary checks, if castling move possible, add it to list of possible moves for ally king
        """
        
        if self.ally_king.colour == 'w' and 'K' in self.board.castling_rights:
            # white king kingside castling
            rook, danger = self.get_castling_masks('CK', 'R', 'd')
            non_movement = self.board.GetPieceOnSquare(63).has_moved == False and self.ally_king.has_moved == False
            ray = danger & ~self.board.white_king

            if (rook & self.board.white_rooks) == rook and (danger & self.board.king_danger_squares) == 0 and (ray & self.board.occupied) == 0 and non_movement:
                # kingside castling possible
                self.possible_moves.append((self.ally_king, self.ally_king.square, self.ally_king.square + 2, 'CK'))

        if self.ally_king.colour == 'w' and 'Q' in self.board.castling_rights:
            # white king queenside castling
            rook, danger = self.get_castling_masks('CQ', 'R', 'd')
            non_movement = self.board.GetPieceOnSquare(56).has_moved == False and self.ally_king.has_moved == False
            ray = danger & ~self.board.white_king

            if (rook & self.board.white_rooks) == rook and (danger & self.board.king_danger_squares) == 0 and (ray & self.board.occupied) == 0 and non_movement:
                # kingside castling possible
                self.possible_moves.append((self.ally_king, self.ally_king.square, self.ally_king.square - 3, 'CQ'))

        if self.ally_king.colour == 'b' and 'k' in self.board.castling_rights:
            # white king queenside castling
            rook, danger = self.get_castling_masks('Ck', 'r', 'd')
            non_movement = self.board.GetPieceOnSquare(7).has_moved == False and self.ally_king.has_moved == False
            ray = danger & ~self.board.black_king

            if (rook & self.board.black_rooks) == rook and (danger & self.board.king_danger_squares) == 0 and (ray & self.board.occupied) == 0 and non_movement:
                # kingside castling possible
                self.possible_moves.append((self.ally_king, self.ally_king.square, self.ally_king.square + 2, 'Ck'))

        if self.ally_king.colour == 'b' and 'q' in self.board.castling_rights:
            # white king queenside castling
            rook, danger = self.get_castling_masks('Cq', 'r', 'd')
            non_movement = self.board.GetPieceOnSquare(0).has_moved == False and self.ally_king.has_moved == False
            ray = danger & ~self.board.black_king

            if (rook & self.board.black_rooks) == rook and (danger & self.board.king_danger_squares) == 0 and (ray & self.board.occupied) == 0 and non_movement:
                # kingside castling possible
                self.possible_moves.append((self.ally_king, self.ally_king.square, self.ally_king.square - 3, 'Cq'))

    def GenerateAllPossibleMoves(self):
        # reset attacked squares bitboard, and possible moves list
        self.board.attacked_squares = np.uint64(0)
        self.king_pseudo_legal_bitboard = np.uint64(0)

        self.possible_moves = []

        self.ally_king = self.GetAllyKing()
        self.enemy_king = self.GetEnemyKing()

        self.GetAttackers()
        self.SetMoveFilters() 
        self.SetPinnedMasks() 

        # THIS MUST STAY HERE ****************************
                                                        
        self.board.king_danger_squares = np.uint64(0)  

        #*************************************************

        # pawn moves, pawns code does all possible moves for all pawns on board in one go, so doesn't go into for loop
        self.PossibleWhitePawnMoves()
        self.PossibleBlackPawnMoves()

        new_possible_moves = []

        # only pawns have moves set
        for move in self.possible_moves:
            for piece in self.board.pieces:
                if piece.pinned_mask != (2**64) - 1:
                    allowed_squares = self.board.BBToSquares(piece.pinned_mask)

                    if (move[1] == piece.square and move[2] in allowed_squares) or (move[1] != piece.square):
                        new_possible_moves.append(move)
                    
                else:
                    new_possible_moves.append(move)

        self.possible_moves = new_possible_moves
            
        for piece in self.board.pieces:
            if piece.name != 'P' and piece.name != 'p':
                self.GetPossibleMoves(piece)

           
        self.FilterKingMoves()

        if self.board.castling_rights != '' and self.board.attackers == 0:
            self.AddCastlingMoves()


if __name__ == "main":
    moveGen = GenerateMoves()


        