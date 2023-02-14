
"""
piece class that contains information about the piece type, square, pinned mask (changes based on whether or not it is pinned)
name, colour, pinned mask,  
"""

class Piece:
    def __init__(self, name) -> None:
        self.name = name
        self.colour = self.name.split('_')[1]
        self.pinned_mask : int = 0


