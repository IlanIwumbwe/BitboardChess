from chess_logic import ChessLogic
import time

class Engine:
    def __init__(self):
        self.run = True
        self.chess = None
        self.fen = ""

        self.option = input("(P)erft test, (Q)uit: ")
        
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

    def Run(self):

        while self.run:

            if self.option.upper() == "P":
                self.fen = input("Fen: ").strip()
                self.chess = ChessLogic(self.fen)

                depth = int(input('Depth limit: '))    
                print(f'Testing on: {self.chess.board.position_fen}') 

                start = time.time()
                print(f'Depth: {depth} | Num of positions: {self.Perft(depth)}')   
                end = time.time()  
                print(f"Time taken: {end - start} seconds")

            elif self.option.upper() == "C":
                self.ComparePerft()

            elif self.option.upper() == "Q":
                self.run = False
            
            self.option = input("(P)erft test, (C)ompare with Stockfish, (Q)uit: ").strip()
            
    
if __name__ == '__main__':
    engine = Engine()
    engine.Run()


    
   
    