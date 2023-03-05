import numpy as np
from piece import Piece

class Board:
    def __init__(self):
        # bitboards
        self.all_whites = 0
        self.all_blacks = 0
        self.white_bishops = 0
        self.white_rooks = 0
        self.white_bishops = 0
        self.white_rooks = 0
        self.white_king = 0
        self.white_queen = 0
        self.white_pawns = 0
        self.black_rooks = 0
        self.black_knights = 0
        self.black_bishops = 0
        self.black_king = 0
        self.black_queen = 0
        self.black_pawns = 0
        self.occupied = 0
        self.empty = 0

        self.attackers = 0 # bitboard of pieces giving check
        self.king_danger_squares = np.uint64(0)
        self.ally_king_checked = False

        self.CENTRE = np.uint64(103481868288)
        self.EXTENDED_CENTRE = np.uint64(66229406269440)
        self.A_FILE = np.uint64(9259542123273814144)
        self.H_FILE = np.uint64(72340172838076673)

        self.FILES = {1 : self.A_FILE, 2 : np.uint64(4629771061636907072), 3 : np.uint64(2314885530818453536), 4 : np.uint64(1157442765409226768),
                      5 : np.uint64(578721382704613384), 6 : np.uint64(289360691352306692), 7 : np.uint64(144680345676153346), 8 : self.H_FILE}

        self.AB_FILE = self.FILES[1] | self.FILES[2]
        self.GH_FILE = self.FILES[7] | self.FILES[8]

        self.RANKS = lambda rank_number : np.uint64(255 << (rank_number-1) * 8)
        
        # board_repr
        self.console_board = None

        #pieces
        self.pieces = []

        # from FEN
        self.position_fen = ''
        self.active_piece = ''
        self.castling_rights = ''
        self.en_passant = ''
        self.ply = ''
        self.moves = ''

        # history
        self.move_history = []

    def FenToBitboards(self):
        # bitboards setup
        bbs = {'P':['0']*64, 'N':['0']*64, 'B':['0']*64, 'R':['0']*64, 'Q':['0']*64, 'K':['0']*64, 'p':['0']*64, 'n':['0']*64, 'b':['0']*64, 'r':['0']*64, 'q':['0']*64, 'k':['0']*64}

        # On start of game, parse fen string to setup starting bitboards
        ranks = self.position_fen.split('/')

        sq = 0

        for rank in ranks:
            if rank == '8':
                sq += 8
            else:
                for file in rank:
                    if file.isdigit():
                        sq += int(file)
                    else:
                        bbs[file][sq] = '1'
                        sq += 1
                        
        for p_type, bb in bbs.items():
            binary = ''
            for line in [bb[i:i+8] for i in range(0, 64, 8)]:
                binary += ''.join(line)

            bit_board = int(binary, 2)

            bit_board = np.uint64(bit_board)

            self.SetBitboard(p_type, bit_board)

    @staticmethod
    def ArrayToBitboard(array):
        binary = ''
        for line in [array[i:i + 8] for i in range(0, 64, 8)]:
            binary += ''.join(line)

        bit_board = int(binary, 2)

        return np.uint64(bit_board)

    @staticmethod
    def PrintBitboard(bb):
        bb = np.binary_repr(bb, width=64)

        for line in [bb[i:i + 8] for i in range(0, 64, 8)]:
            print(line)

    def UpdateBoard(self):
        self.console_board = ['.'] * 64

        for piece in self.pieces:
            self.console_board[piece.square] = piece.name

    def SwitchActivePiece(self):
        if self.active_piece == "w":
            self.active_piece = "b"
        else:
            self.active_piece = "w"

    def InitialiseBoard(self):
        self.pieces = []
        # for rendering
        self.console_board = ['.'] * 64
        piece_str = {self.white_pawns: 'P', self.white_knights: 'N', self.white_bishops: 'B',
                          self.white_rooks: 'R', self.white_queen: 'Q', self.white_king: 'K', self.black_pawns: 'p',
                          self.black_knights: 'n', self.black_bishops: 'b', self.black_rooks: 'r',
                          self.black_queen: 'q', self.black_king: 'k'}


        for bb, string in piece_str.items():
            for sq in self.BBToSquares(bb):
                self.console_board[sq] = string
                self.pieces.append(Piece(string, sq))

    def PrintAllBitboards(self):
        for piece_type in ['R', 'N', 'B', 'Q', 'K', 'r', 'n', 'b', 'q', 'k', 'P', 'p']:
            print(piece_type + "_______")
            self.PrintBitboard(self.GetBitboard(piece_type))

    def PrintBoard(self):
        print('  ________')
        for r_ind, rank in enumerate([self.console_board[i:i + 8] for i in range(0, 64, 8)]):
            self.console_board += rank

            print(f'{8 - r_ind}|' + ''.join(rank) + '|')

            if r_ind == 7:
                print('  '+''.join([chr(97+i) for i in range(8)]))

    def SetBitboard(self, p_type, bb):
        if p_type == 'P':
            self.white_pawns = bb
        elif p_type == 'R':
            self.white_rooks = bb
        elif p_type == 'N':
            self.white_knights = bb
        elif p_type == 'K':
            self.white_king = bb
        elif p_type == 'Q':
            self.white_queen = bb
        elif p_type == 'B':
            self.white_bishops = bb
        elif p_type == 'p':
            self.black_pawns = bb
        elif p_type == 'r':
            self.black_rooks = bb
        elif p_type == 'n':
            self.black_knights = bb
        elif p_type == 'k':
            self.black_king = bb
        elif p_type == 'q':
            self.black_queen = bb
        elif p_type == 'b':
            self.black_bishops = bb
            
    def GetBitboard(self, p_type):
        if p_type == 'P':
            return self.white_pawns
        elif p_type == 'R':
            return self.white_rooks
        elif p_type == 'N':
            return self.white_knights
        elif p_type == 'K':
            return self.white_king 
        elif p_type == 'Q':
            return self.white_queen
        elif p_type == 'B':
            return self.white_bishops
        elif p_type == 'p':
            return self.black_pawns
        elif p_type == 'r':
            return self.black_rooks
        elif p_type == 'n':
            return self.black_knights
        elif p_type == 'k':
            return self.black_king 
        elif p_type == 'q':
            return self.black_queen 
        elif p_type == 'b':
            return self.black_bishops

    def ParseFen(self, full_fen):
        self.position_fen, self.active_piece, self.castling_rights, self.en_passant, self.ply, self.moves = full_fen.split(' ')

        if self.en_passant != '-':
            x = ord(self.en_passant[0])-97
            y = 8 - int(self.en_passant[1])

            if y == 2:
                # last move by black pawn 2 down
                black_pawn = Piece('p', x + 8)
                self.move_history.append((black_pawn, black_pawn.square, black_pawn.square + 16, 'EP'))

            elif y == 5:
                # last move by white pawn 2 up
                white_pawn = Piece('P', x + 48)
                self.move_history.append((white_pawn, white_pawn.square, white_pawn.square - 16, 'EP'))

        self.ply = int(self.ply)
        self.moves = int(self.moves)

    def SetUpBitboards(self):
        # do not consider kings to prevent illegal captures
        self.all_whites = self.white_pawns | self.white_rooks | self.white_bishops | self.white_queen | self.white_knights
        self.all_blacks = self.black_pawns | self.black_rooks | self.black_bishops | self.black_queen | self.black_knights

        # occupied means there's any piece on the square therefore kings considered
        self.occupied = self.all_blacks | self.all_whites | self.black_king | self.white_king
        # empty is inverse of occupied
        self.empty = ~ self.occupied

    def BBToSquares(self, bb):

        bb = np.binary_repr(bb, width=64)
        squares = []

        for rank_ind, line in enumerate([bb[i:i + 8] for i in range(0, 64, 8)]):
            for file_ind, c in enumerate(line):
                if c == '1':
                    squares.append(8*rank_ind + file_ind)

        return squares

    def GetPiecesOnBitboard(self, bb):
        return [piece for sq in self.BBToSquares(bb) for piece in self.pieces if piece.square == sq]

    def GetPieceOnSquare(self, square):
        if self.IsSquareOccupied(square):
            return list(filter(lambda piece : piece.square == square, self.pieces))[0]

    def SquareToBB(self, square):
        binary = ['0']*64
        bb = ''

        try:
            binary[square] = '1'
        except TypeError:
            x = ord(square[0])-97
            y = 8 - int(square[1])

            binary[8*y+x] = '1'

        for rank in [binary[i:i+8] for i in range(0, 64, 8)]:
            bb += ''.join(rank)

        bit_board = int(bb, 2)

        bit_board = np.uint64(bit_board)

        return bit_board


    def IsSquareOccupied(self, square):
        square_mask = self.SquareToBB(square)

        if square_mask & self.occupied == np.uint64(0):
            return False
        else:
            return True

    def GetAllBitboards(self):
        return [self.all_whites,
        self.all_blacks,
        self.white_pawns,
        self.white_knights,
        self.white_bishops,
        self.white_rooks,
        self.white_king,
        self.white_queen,
        self.black_rooks,
        self.black_knights,
        self.black_bishops,
        self.black_king,
        self.black_queen,
        self.black_pawns,
        self.empty]

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
        piece, initial_sq, final_sq, move_type = move
        
        self.move_history.append(move)

        # remove piece from initial square
        drag_piece_bitboard = self.GetBitboard(piece.name)
        drag_piece_bitboard &= ~self.SquareToBB(initial_sq)
        self.SetBitboard(piece.name, drag_piece_bitboard)

        if self.IsSquareOccupied(final_sq) == True:
            # remove captured piece from final square
            captured_piece = self.GetPieceOnSquare(final_sq)
            captured_piece_bitboard = self.GetBitboard(captured_piece.name)
            captured_piece_bitboard &= ~self.SquareToBB(final_sq)
            self.SetBitboard(captured_piece.name, captured_piece_bitboard)

            self.pieces.remove(captured_piece)

            # add captured piece to move tuple
            self.move_history[-1] = self.move_history[-1] + (captured_piece,)

        else:
            if move_type == 'EP' and piece.name in ['P', 'p']:
                # en-passant capture

                captured_piece = None
        
                if piece.name == 'P':
                    # white pawn performs EP capture, black pawn is below final square
                    captured_piece = self.GetPieceOnSquare(final_sq + 8)

                elif piece.name == 'p':
                    # black pawn performs EP capture, white pawn is above final square
                    captured_piece = self.GetPieceOnSquare(final_sq - 8)
                
                # remove captured piece from square
                captured_piece_bitboard = self.GetBitboard(captured_piece.name)
                captured_piece_bitboard &= ~self.SquareToBB(captured_piece.square)
                self.SetBitboard(captured_piece.name, captured_piece_bitboard)

                self.pieces.remove(captured_piece)

                self.move_history[-1] = self.move_history[-1][:3] + (captured_piece,)

        if move_type != '_' and move_type != 'EP' and 'C' not in move_type:
            # promotion, set bitboard of move type parameter, which is the piece we want to promote to
            promotion_piece_bitboard = self.GetBitboard(move_type)
            promotion_piece_bitboard |= self.SquareToBB(final_sq)
            self.SetBitboard(move_type, promotion_piece_bitboard)

            # change piece's name and square, set has moved to true
            piece.name = move_type
            piece.square = final_sq
            piece.times_moved += 1
        
        else:
            # move piece to final square in its bitboard
            drag_piece_bitboard = self.GetBitboard(piece.name)
            drag_piece_bitboard |= self.SquareToBB(final_sq)
            self.SetBitboard(piece.name, drag_piece_bitboard)

            # change piece's square, set has moved to true
            piece.square = final_sq
            piece.times_moved += 1

            # perform rook movement for castling move
            if move_type == 'CK':
                rook = self.GetPieceOnSquare(63)
                new_rook_position = initial_sq + 1

                self.white_rooks &= ~self.SquareToBB(rook.square)
                self.white_rooks |= self.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.time_moved += 1

                self.castling_rights = self.castling_rights.replace('K', '')             

            elif move_type == 'CQ':
                rook = self.GetPieceOnSquare(56)
                new_rook_position = initial_sq - 2

                self.white_rooks &= ~self.SquareToBB(rook.square)
                self.white_rooks |= self.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.castling_rights = self.castling_rights.replace('Q', '')

            elif move_type == 'Ck':
                rook = self.GetPieceOnSquare(7)
                new_rook_position = initial_sq + 1

                self.black_rooks &= ~self.SquareToBB(rook.square)
                self.black_rooks |= self.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.castling_rights = self.castling_rights.replace('k', '')

            elif move_type == 'Cq':
                rook = self.GetPieceOnSquare(0)
                new_rook_position = initial_sq - 2

                self.black_rooks &= ~self.SquareToBB(rook.square)
                self.black_rooks |= self.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.castling_rights = self.castling_rights.replace('q', '')
                            
        self.ply += 1
        self.moves = self.ply // 2

        # after move is made, bitboards have changed, so update all bitboard variables. 
        # update ascii board, this is used for rendering
        self.SetUpBitboards()
        self.UpdateBoard()

    def UnmakeMove(self):
        """
        revert move at top of move history list
        
        - subtract ply and moves
        - if castling move, add castling type to castling rights 
        """
        if len(self.move_history) >= 1:
            piece, initial_sq, final_sq, move_type = self.move_history.pop()

            if isinstance(move_type, Piece):
                # move drag piece to initial square, remove from final square
                drag_piece_bitboard = self.GetBitboard(piece.name)
                drag_piece_bitboard |= self.SquareToBB(initial_sq)
                drag_piece_bitboard &= ~self.SquareToBB(final_sq)
                self.SetBitboard(piece.name, drag_piece_bitboard)

                # captures move happened, so restore captured piece
                captured_piece_bitboard = self.GetBitboard(move_type.name)
                captured_piece_bitboard |= self.SquareToBB(move_type.square)
                self.SetBitboard(move_type.name, captured_piece_bitboard)

                self.pieces.append(move_type)

                piece.square = initial_sq
                piece.times_moved -= 1

            elif move_type != '_' and move_type != 'EP' and 'C' not in move_type:
                # must be promotion move

                # remove promoted piece from final square
                prom_piece_bitboard = self.GetBitboard(piece.name)
                prom_piece_bitboard &= ~self.SquareToBB(final_sq)
                self.SetBitboard(piece.name, prom_piece_bitboard)

                piece.name = 'P' if piece.name.isupper() else 'p'
                piece.square = initial_sq
                piece.times_moved -= 1

                print(piece.name, piece.square)

                # piece name now correct, can get correct bitboard
                drag_piece_bitboard = self.GetBitboard(piece.name)
                drag_piece_bitboard |= self.SquareToBB(initial_sq)
                self.SetBitboard(piece.name, drag_piece_bitboard)

            else:
                # must be normal move, movement with no captures, or castling

                # move drag piece back to initial square
                drag_piece_bitboard = self.GetBitboard(piece.name)
                drag_piece_bitboard |= self.SquareToBB(initial_sq)

                # remove drag piece from final square
                drag_piece_bitboard &= ~self.SquareToBB(final_sq)

                self.SetBitboard(piece.name, drag_piece_bitboard)

                piece.square = initial_sq
                piece.times_moved -= 1

                # if castling move, move rook back to where it has to be, and revert castlng rights

                if move_type == 'CK':
                    new_rook_position = initial_sq + 1
                    rook = self.GetPieceOnSquare(new_rook_position)
                
                    self.white_rooks &= ~self.SquareToBB(new_rook_position)
                    self.white_rooks |= self.SquareToBB(63)

                    rook.square = 63
                    rook.times_moved -= 1

                    self.castling_rights += 'K'            

                elif move_type == 'CQ':
                    new_rook_position = initial_sq - 2
                    rook = self.GetPieceOnSquare(new_rook_position)
                
                    self.white_rooks &= ~self.SquareToBB(new_rook_position)
                    self.white_rooks |= self.SquareToBB(56)

                    rook.square = 56
                    rook.times_moved -= 1

                    self.castling_rights += 'Q'       

                elif move_type == 'Ck':
                    new_rook_position = initial_sq + 1
                    rook = self.GetPieceOnSquare(new_rook_position)
                
                    self.black_rooks &= ~self.SquareToBB(new_rook_position)
                    self.black_rooks |= self.SquareToBB(7)

                    rook.square = 7
                    rook.times_moved -= 1

                    self.castling_rights += 'k'    

                elif move_type == 'Cq':
                    new_rook_position = initial_sq - 2
                    rook = self.GetPieceOnSquare(new_rook_position)
                
                    self.black_rooks &= ~self.SquareToBB(new_rook_position)
                    self.black_rooks |= self.SquareToBB(0)

                    rook.square = 0
                    rook.times_moved -= 1

                    self.castling_rights += 'q'    
                
            self.ply -= 1
            self.moves -= 1 # ?
            self.SwitchActivePiece()
        
            self.SetUpBitboards()
            self.UpdateBoard()

if __name__=='__main__':
    board = Board()
    """board.ParseFen('R7/8/5rk1/5p2/7P/1p3KP1/P7/8 b - - 0 0')
    board.FenToBitboards()
    board.InitialiseBoard()
    board.SetUpBitboards()

    board.PrintBoard()"""
    
    board.PrintBitboard(2**57 + 2**58 + 2**59)












    

    













