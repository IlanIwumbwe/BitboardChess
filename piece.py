import numpy as np

"""
piece class that contains information about the piece type, square, pinned mask (changes based on whether or not it is pinned)
name, colour, pinned mask,  
"""

class Piece:
    def __init__(self, name, square) -> None:
        self.name = name
        self.colour = "w" if self.name.isupper() else "b"
        self.square : int  = square
        self.pinned_mask = (2**64) - 1
        self.times_moved : int = 0


