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

        self.CENTRE = np.uint64(103481868288)
        self.EXTENDED_CENTRE = np.uint64(66229406269440)
        self.A_FILE = np.uint64(9259542123273814144)
        self.H_FILE = np.uint64(72340172838076673)

        self.FILES = {1 : self.A_FILE, 2 : np.uint64(4629771061636907072), 3 : np.uint64(2314885530818453536), 4 : np.uint64(1157442765409226768),
                      5 : np.uint64(578721382704613384), 6 : np.uint64(289360691352306692), 7 : np.uint64(144680345676153346), 8 : self.H_FILE}

        self.AB_FILE = self.FILES[1] | self.FILES[2]
        self.GH_FILE = self.FILES[7] | self.FILES[8]

        self.RANKS = lambda rank_number : np.uint64(255 << (rank_number-1) * 8)

        self.all_squares = [np.uint64(2**i) for i in range(64)]
        
        # board_repr
        self.console_board = None

        self.pieces = []
        self.move_history = []

        # from FEN
        self.position_fen = ''
        self.active_piece = ''
        self.castling_rights = ''
        self.en_passant = ''
        self.ply = ''
        self.moves = ''

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

    

if __name__=='__main__':
    board = Board()
    """board.ParseFen('R7/8/5rk1/5p2/7P/1p3KP1/P7/8 b - - 0 0')
    board.FenToBitboards()
    board.InitialiseBoard()
    board.SetUpBitboards()

    board.PrintBoard()"""
    
    board.PrintBitboard(2**57 + 2**58 + 2**59)












    

    













