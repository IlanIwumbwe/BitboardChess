
class Move:
    def __init__(self, piece, initial, dest, type, captured_piece=None):
        self.piece = piece
        self.initial = initial
        self.dest = dest
        self.type = type
        self.captured_piece = captured_piece
        self.is_promotion_move = False


"""
Move representation

can use 16 bits to store a move:

5:0 -> dest square
11:6 -> initial square

15:12 -> flags for move kind and promoted piece 



"""