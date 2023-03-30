from chessLogic import ChessLogic
import time
import random

class Engine:
    def __init__(self):
        self.run = True
        self.chess = None
    
    def Perft(self, depth, root = True):
        if depth == 0:
            return 1
        else:
            num_of_positions = 0

            for move in self.chess.moveGen.possible_moves:
                self.chess.MakeMove(move)
                p = self.Perft(depth - 1, False)
                if root:
                    if move.type not in ['Q', 'R', 'B', 'N', 'q', 'r', 'b', 'n']:
                        print(f"{self.chess.NumbertoAlgebraic(move.initial)}{self.chess.NumbertoAlgebraic(move.dest)}: {p}")
                    else:
                        print(f"{self.chess.NumbertoAlgebraic(move.initial)}{self.chess.NumbertoAlgebraic(move.dest)}{move.type}: {p}")

                num_of_positions += p
                self.chess.UnmakeMove()
                
            return num_of_positions
    
    @staticmethod
    def ComparePerft():
        with open("stockfish_output.txt", "r") as s:
            st = sorted([i.replace('\n', '') for i in s.readlines()])
        
        with open("my_output.txt", "r") as m:
            my = sorted([i.replace('\n', '') for i in m.readlines()])
        
        if len(st) != len(my):
            for j in zip(st, my):
                if j[0] != j[1]:
                    print("*This branch has a descrepancy.\n*Moves searched under this branch aren't the same as Stockfish.\n*Find bug")
                    print(j)
        else:
            print("*Perft hasn't searched the same number of branches as Stockfish.\n*Find bug")

    def RandomMove(self):
        move = random.choice(self.chess.moveGen.possible_moves)

        return move

 
if __name__ == '__main__':
    engine = Engine()
   
    option = input("(T)est move generation, (Q)uit: ").strip().upper()
    while engine.run:
        if option == "T":
            fen = input("Fen: ").strip()
            engine.chess = ChessLogic(fen)

            depth = int(input('Depth limit: '))    
            print(f'Testing on: {engine.chess.board.position_fen}') 

            start = time.time()
            print(f'Depth: {depth} | Num of positions: {engine.Perft(depth)}')   
            end = time.time()  
            print(f"Time taken: {end - start} seconds")

        elif option == "C":
            engine.ComparePerft()

        elif option == "Q":
            engine.run = False
        
        option = input("(T)est, (C)ompare with Stockfish, (Q)uit: ").strip().upper()

    
   
    