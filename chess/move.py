
class Move:
    def __init__(self, piece, initial, dest, type, captured_piece=None):
        self.piece = piece
        self.initial = initial
        self.dest = dest
        self.type = type
        self.captured_piece = captured_piece
        self.is_promotion_move = False
