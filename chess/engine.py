from chessLogic import ChessLogic
import time
import random
from evaluation import Evaluation
import math

class Engine:
    def __init__(self):
        self.run = True
        self.chess = None
        self.evaluate = Evaluation()
        self.search_depth = 2
        self.best_move = None
    
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
        with open("../stockfish_output.txt", "r") as s:
            st = sorted([i.replace('\n', '') for i in s.readlines()])
        
        with open("../my_output.txt", "r") as m:
            my = sorted([i.replace('\n', '') for i in m.readlines()])
        
        if len(st) == 0 or len(my) == 0:
            print("No comparison can be made")

        elif len(st) == len(my):
            for j in zip(st, my):
                if j[0] != j[1]:
                    print("*This branch has a descrepancy.\n*Moves searched under this branch aren't the same as Stockfish.\n*Stockfish, Mine")
                    print(j)

        else:
            print(set(st).difference(set(my)))
            print("*Perft hasn't searched the same number of branches as Stockfish.\n*Find bug")

    def Search(self, depth):
        if depth == 0:
            self.evaluate.board = self.chess.board
            return self.evaluate.Evaluate()
        
        if self.chess.is_checkmate:
            return -math.inf
        
        best_score = -math.inf

        for move in self.chess.moveGen.possible_moves:
            self.chess.MakeMove(move)

            evaluation = -self.Search(depth - 1)
            
            if evaluation > best_score:
                best_score = evaluation

                if depth == self.search_depth:
                    self.best_move = move

            self.chess.UnmakeMove()

        return best_score

    def RandomMove(self):
        move = random.choice(self.chess.moveGen.possible_moves)
        
        return move
    
    def BestMove(self):
        self.Search(self.search_depth)
        return self.best_move
     
if __name__ == '__main__':
    engine = Engine()
   
    while engine.run:
        option = input("\n(T)est, (C)ompare with Stockfish, (Q)uit: ").strip().upper()

        if option == "T":
            fen = input("Fen: ").strip()

            if not fen:
                engine.chess = ChessLogic()
            else:
                engine.chess = ChessLogic(fen)

            depth = int(input('Depth limit: '))    
            print(f'Testing on: {engine.chess.board.position_fen}') 

            start = time.time()
            positions = engine.Perft(depth)
            print(f'Depth: {depth} | Num of positions: {positions}')   
            end = time.time()  
            time_taken = end - start
            print(f"Time taken: {time_taken : .4f} seconds")
            print(f"Positions per second: {positions / time_taken : .4f}")

        elif option == "C":
            engine.ComparePerft()

        elif option == "Q":
            engine.run = False        

            
        
        
    