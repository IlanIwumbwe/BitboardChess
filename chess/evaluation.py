

class Evaluation:
    def __init__(self):
        # piece values
        self.PIECE_VALUES = {'p': 100, 'P':100, 'N':300, 'n':300, 'b':300, 'B':300, 'r':500, 'R':500, 'q':900, 'Q':900}

        self.board = None
    
    def CountMaterial(self, side):
        if side == "w":
            pieces = ['P', 'N', 'B', 'R', 'Q']
        else:
            pieces = ['p', 'n', 'b', 'r', 'q']

        material = 0

        for piece in pieces:
            material += self.board.CountPieces(piece) * self.PIECE_VALUES[piece]

        return material
    
    def Evaluate(self):
        white_material = self.CountMaterial("w")
        black_material = self.CountMaterial("b")

        self.perspective = 1 if self.board.active_piece == "w" else -1

        return (white_material - black_material) * self.perspective
    
    


    