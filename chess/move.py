
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
- 0-5 (dest sq)
- 6-11(origin sq)
- 12-13(promotion piece type)
- 14-15(special move)

special moves:
* en-passant
* castling
* promotion
"""