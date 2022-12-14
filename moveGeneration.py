import numpy as np

class GenerateMoves:
    def __init__(self, board_object):
        self.possible_moves = [] # stores moves for all pieces expect kings

        self.king_pseudo_legal_bitboard = 0

        self.board = board_object

        """
        Kings, pawns* and knights move in very predictable ways. These lookup tables are pre-calculated with each square and possible squares piece can land on.
        Finding actual moves is a matter of making 
        """
        self.KING_TABLE = {}
        self.KNIGHT_TABLE = {}
        self.RAYS = {}
        
        for sq in range(0, 64):
            # each square key stores bitboard of attack set
            self.KING_TABLE[sq] = 0
            self.KNIGHT_TABLE[sq] = 0

    def PossibleWhitePawnMoves(self):
        rank_8 = self.board.RANKS(8)
        rank_4 = self.board.RANKS(4)
        rank_5 = self.board.RANKS(5)

        # right captures
        r_captures = (self.board.white_pawns << np.uint64(7)) & ~rank_8 & ~self.board.A_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= r_captures

        dest_squares = self.board.BBToSquares(r_captures & self.board.all_blacks)

        for sq in dest_squares:
            self.possible_moves.append(('P', sq + 7, sq, '_'))

        # left_captures
        l_captures = (self.board.white_pawns << np.uint64(9)) & ~rank_8 & ~self.board.H_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= l_captures

        dest_squares = self.board.BBToSquares(l_captures & self.board.all_blacks)

        for sq in dest_squares:
            self.possible_moves.append(('P', sq + 9, sq, '_'))

        # forward by 1
        forward_1 = (self.board.white_pawns << np.uint(8)) & self.board.empty & ~rank_8

        dest_squares = self.board.BBToSquares(forward_1)

        for sq in dest_squares:
            self.possible_moves.append(('P', sq + 8, sq, '_'))

        # forward by 2
        forward_2 = (self.board.white_pawns << np.uint64(16)) & self.board.empty & (self.board.empty << np.uint64(8)) & ~rank_8 & rank_4

        dest_squares = self.board.BBToSquares(forward_2)

        for sq in dest_squares:
            self.possible_moves.append(('P', sq + 16, sq, '_'))

        # promotion by right captures
        promo_r_captures = (self.board.white_pawns << np.uint64(7)) & rank_8 & ~self.board.A_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= promo_r_captures

        dest_squares = self.board.BBToSquares(promo_r_captures & self.board.all_blacks)

        for sq in dest_squares:
            for promotes_to in ['Q', 'N', 'R', 'B']:
                self.possible_moves.append(('P', sq + 7, sq, promotes_to))

        # promotion by left captures
        promo_l_captures = (self.board.white_pawns << np.uint64(9)) & rank_8 & ~self.board.H_FILE

        if self.board.active_piece == 'b':
            self.board.king_danger_squares |= promo_l_captures

        dest_squares = self.board.BBToSquares(promo_l_captures & self.board.all_blacks)

        for sq in dest_squares:
            for promotes_to in ['Q', 'N', 'R', 'B']:
                self.possible_moves.append(('P', sq + 9, sq, promotes_to))

        # promotion by forward 1
        promo_forward_1 = (self.board.white_pawns << np.uint(8)) & self.board.empty & rank_8

        dest_squares = self.board.BBToSquares(promo_forward_1)

        for sq in dest_squares:
            for promotes_to in ['Q', 'N', 'R', 'B']:
                self.possible_moves.append(('P', sq + 8, sq, promotes_to))

        # en-passant
        if len(self.board.move_history) >= 1:
            last_move = self.board.move_history[-1]

            piece_type, initial_sq, final_sq, move_type = last_move

            if piece_type == 'p' and abs(initial_sq-final_sq) == 2*8:
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

                    dest_squares = self.board.BBToSquares(ep_right)

                    for sq in dest_squares:
                        self.possible_moves.append(('P', sq + 7, sq, 'EP'))

                # en-passant left
                if (self.board.white_pawns << np.uint64(1)) & self.board.black_pawns & self.board.FILES[ep_file] & ~self.board.H_FILE & rank_5 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_left = (self.board.white_pawns << np.uint64(9))  & ~self.board.H_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'b':
                        self.board.king_danger_squares |= ep_left

                    dest_squares = self.board.BBToSquares(ep_left)

                    for sq in dest_squares:
                        self.possible_moves.append(('P', sq + 9, sq, 'EP'))

    def PossibleBlackPawnMoves(self):
        rank_1 = self.board.RANKS(1)
        rank_5 = self.board.RANKS(5)
        rank_4 = self.board.RANKS(4)

        # right captures
        r_captures = (self.board.black_pawns >> np.uint64(9)) & ~rank_1 & ~self.board.A_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= r_captures

        dest_squares = self.board.BBToSquares(r_captures & self.board.all_whites)

        for sq in dest_squares:
            self.possible_moves.append(('p', sq - 9, sq, '_'))

        # left_captures
        l_captures = (self.board.black_pawns >> np.uint64(7)) & ~rank_1 & ~self.board.H_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= l_captures
    
        dest_squares = self.board.BBToSquares(l_captures & self.board.all_whites)

        for sq in dest_squares:
            self.possible_moves.append(('p', sq - 7, sq, '_'))

        # forward by 1
        forward_1 = (self.board.black_pawns >> np.uint(8)) & self.board.empty & ~rank_1

        dest_squares = self.board.BBToSquares(forward_1)

        for sq in dest_squares:
            self.possible_moves.append(('p', sq - 8, sq, '_'))

        # forward by 2
        forward_2 = (self.board.black_pawns >> np.uint64(16)) & self.board.empty & (
                    self.board.empty >> np.uint64(8)) & ~rank_1 & rank_5

        dest_squares = self.board.BBToSquares(forward_2)

        for sq in dest_squares:
            self.possible_moves.append(('p', sq - 16, sq, '_'))

        # promotion by right captures
        promo_r_captures = (self.board.black_pawns >> np.uint64(9)) & rank_1 & ~self.board.A_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= promo_r_captures

        dest_squares = self.board.BBToSquares(promo_r_captures & self.board.all_whites)

        for sq in dest_squares:
            for promotes_to in ['q', 'n', 'r', 'b']:
                self.possible_moves.append(('p', sq - 9, sq, promotes_to))

        # promotion by left captures
        promo_l_captures = (self.board.black_pawns >> np.uint64(7)) & rank_1 & ~self.board.H_FILE

        if self.board.active_piece == 'w':
            self.board.king_danger_squares |= promo_l_captures

        dest_squares = self.board.BBToSquares(promo_l_captures & self.board.all_whites)

        for sq in dest_squares:
            for promotes_to in ['q', 'n', 'r', 'b']:
                self.possible_moves.append(('p', sq - 7, sq, promotes_to))

        # promotion by forward 1
        promo_forward_1 = (self.board.black_pawns >> np.uint(8)) & self.board.empty & rank_1

        dest_squares = self.board.BBToSquares(promo_forward_1)

        for sq in dest_squares:
            for promotes_to in ['q', 'n', 'r', 'b']:
                self.possible_moves.append(('p', sq - 8, sq, promotes_to))

        # en-passant
        if len(self.board.move_history) >= 1:
            last_move = self.board.move_history[-1]

            piece_type, initial_sq, final_sq, move_type = last_move

            if piece_type == 'P' and abs(initial_sq - final_sq) == 2 * 8:
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
                
                    dest_squares = self.board.BBToSquares(ep_right)

                    for sq in dest_squares:
                        self.possible_moves.append(('p', sq - 9, sq, 'EP'))

                # en-passant left
                if (self.board.black_pawns << np.uint64(1)) & self.board.white_pawns & self.board.FILES[
                    ep_file] & ~self.board.H_FILE & rank_4 != np.uint64(0):
                    # if there's a black pawn next to white pawn that isn't on the A file as this is right captures
                    # and is on the file on the en-passant pawn(last move)
                    # both pawns must be on rank 5 (this implies black pawn must've moved 2 down)

                    ep_left = (self.board.black_pawns >> np.uint64(7)) & ~self.board.H_FILE & self.board.FILES[ep_file]

                    if self.board.active_piece == 'w':
                        self.board.king_danger_squares |= ep_left

                    dest_squares = self.board.BBToSquares(ep_left)

                    for sq in dest_squares:
                        self.possible_moves.append(('p', sq - 7, sq, 'EP'))
 
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
    def BitscanForward(number):
        # return number of trailing zeroes

        if number==0:
            trail_zeros = 1
        else:
            a = (2**np.arange(64) & number)
            trail_zeros = (a==0).argmin()

        return trail_zeros

    @staticmethod
    def BitscanReverse(number):
        # return number of leading zeroes
        a = (2**np.arange(64) & number)
        
        return 64-a.argmax()-1

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
                
        else:
            n = np.uint64(1) << np.uint64(self.BitscanForward(masked_blockers))

            r = ray & ~self.RAYS['NE'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['NE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['NE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        # NW        
        ray = self.RAYS['NW'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = np.uint64(1) << np.uint64(self.BitscanForward(masked_blockers))

            r = ray & ~self.RAYS['NW'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['NW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type  == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['NW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #SE
        ray = self.RAYS['SE'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = 2**64 >> np.uint64(self.BitscanReverse(masked_blockers) + 1)

            r = ray & ~self.RAYS['SE'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['SE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_sqaures|= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['SE'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #SW
        ray = self.RAYS['SW'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'B' and self.board.active_piece == 'b') or (piece_type == 'b' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = 2**64 >> np.uint64(self.BitscanReverse(masked_blockers) + 1)

            r = ray & ~self.RAYS['SW'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'B' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['SW'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'b' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
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
        else:
            n = np.uint64(1) << np.uint64(self.BitscanForward(masked_blockers))

            r = ray & ~self.RAYS['N'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['N'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['N'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        # E        
        ray = self.RAYS['E'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = 2**64 >> np.uint64(self.BitscanReverse(masked_blockers) + 1)

            r = ray & ~self.RAYS['E'][self.board.BBToSquares(n)[0]]
            
            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['E'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'B':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['E'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #W
        ray = self.RAYS['W'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray

            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = np.uint64(1) << np.uint64(self.BitscanForward(masked_blockers))

            r = ray & ~self.RAYS['W'][self.board.BBToSquares(n)[0]]

            result |= r

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['W'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = np.uint64(1) << np.uint64(self.BitscanForward(msbs_without_king))
                r_prime = ray & ~self.RAYS['W'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        #S
        ray = self.RAYS['S'][square]
        masked_blockers = ray & blockers

        if masked_blockers == 0:
            result |= ray
            
            if (piece_type == 'R' and self.board.active_piece == 'b') or (piece_type == 'r' and self.board.active_piece == 'w'):
                self.board.king_danger_squares |= ray
        else:
            n = 2**64 >> np.uint64(self.BitscanReverse(masked_blockers) + 1)

            r = ray & ~self.RAYS['S'][self.board.BBToSquares(n)[0]]

            result |= r 

            if piece_type == 'R' and self.board.active_piece == 'b':
                msbs_without_king = masked_blockers & ~self.board.black_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['S'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime
                
            elif piece_type == 'r' and self.board.active_piece == 'w':
                msbs_without_king = masked_blockers & ~self.board.white_king
                n_prime = 2**64 >> np.uint64(self.BitscanReverse(msbs_without_king) + 1)
                r_prime = ray & ~self.RAYS['S'][self.board.BBToSquares(n_prime)[0]]

                self.board.king_danger_squares |= r_prime

        return result


    def GetPossibleMoves(self, piece_type, initial_sq):
        """
        For a given piece type and square, the function appends to the list of all possible moves, all moves for given piece at given square
        Attacked squares bitboard is also calculated
        """ 
        if piece_type  == 'N':
            attack_set = self.KNIGHT_TABLE[initial_sq] & (self.board.all_blacks | self.board.empty)

            for dest_sq in self.board.BBToSquares(attack_set):
                self.possible_moves.append((piece_type, initial_sq, dest_sq, '_'))

        elif piece_type == 'n':
            attack_set = self.KNIGHT_TABLE[initial_sq] & (self.board.all_whites | self.board.empty)

            for dest_sq in self.board.BBToSquares(attack_set):
                self.possible_moves.append((piece_type, initial_sq, dest_sq, '_'))

        elif piece_type == 'K':
            attack_set = self.KING_TABLE[initial_sq] & (self.board.all_blacks | self.board.empty)

            self.king_pseudo_legal_bitboard = attack_set
            
            """
            for dest_sq in self.board.BBToSquares(attack_set):
                self.possible_moves.append((piece_type, initial_sq, dest_sq, '_'))
            """

        elif piece_type == 'k':
            attack_set = self.KING_TABLE[initial_sq] & (self.board.all_whites | self.board.empty)

            self.king_pseudo_legal_bitboard = attack_set
            
            """
            for dest_sq in self.board.BBToSquares(attack_set):
                self.possible_moves.append((piece_type, initial_sq, dest_sq, '_'))
            """
        
        elif piece_type == 'B':
            result = self.PossibleBishopMoves(piece_type, initial_sq)

            result &= (self.board.all_blacks | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('B', initial_sq, dest_sq, '_'))

        elif piece_type == 'b':
            result = self.PossibleBishopMoves(piece_type, initial_sq)

            result &= (self.board.all_whites | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('b', initial_sq, dest_sq, '_'))
            
        elif piece_type == 'R':
            result = self.PossibleRookMoves(piece_type, initial_sq)

            result &= (self.board.all_blacks | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('R', initial_sq, dest_sq, '_'))

        elif piece_type == 'r':
            result = self.PossibleRookMoves(piece_type, initial_sq)

            result &= (self.board.all_whites | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('r', initial_sq, dest_sq, '_'))
            
        elif piece_type == 'Q':
            result = self.PossibleBishopMoves('B', initial_sq) | self.PossibleRookMoves('R', initial_sq)

            result &= (self.board.all_blacks | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('Q', initial_sq, dest_sq, '_'))

        elif piece_type == 'q':
            result = self.PossibleBishopMoves('b', initial_sq) | self.PossibleRookMoves('r', initial_sq)

            result &= (self.board.all_whites | self.board.empty)

            for dest_sq in self.board.BBToSquares(result):
                self.possible_moves.append(('q', initial_sq, dest_sq, '_'))
    
    def FilterLegalMoves(self, king_type, initial_square):
        filtered = self.king_pseudo_legal_bitboard & ~self.board.king_danger_squares

        for dest_sq in self.board.BBToSquares(filtered):
            self.possible_moves.append((king_type, initial_square, dest_sq, '_'))

    
    def GenerateAllPossibleMoves(self):
        # reset attacked squares bitboard, and possible moves list
        self.board.attacked_squares = np.uint64(0)
        self.board.king_danger_squares = np.uint64(0)
        self.possible_moves = []

        # pawn moves, pawns code does all possible moves for all pawns on board in one go, so doesn't go into for loop
        self.PossibleWhitePawnMoves()
        self.PossibleBlackPawnMoves()

        for piece_type, initial_sq in self.board.pieces:
            """
            gets all possible moves for given piece at square.
            Gets pseudo-legal moves for kings. 
            Gets king danger squares for active king
            """
            self.GetPossibleMoves(piece_type, initial_sq)

            # filter legal moves
            if piece_type == 'K' or piece_type == 'k':
                self.FilterLegalMoves(piece_type, initial_sq)
        
if __name__ == "main":
    moveGen = GenerateMoves()

        