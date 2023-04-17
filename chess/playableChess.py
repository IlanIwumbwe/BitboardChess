import pygame
import sys
from move import Move
from chessLogic import ChessLogic
from render import Render, TOP_X, TOP_Y, SQUARE_SIZE
from engine import Engine

class PlayableChess:
    def __init__(self, starting_fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", play="T"):
        self.logic = ChessLogic(starting_fen)
        self.render = Render()
        self.render.UpdateRenderer(self.logic)
        self.promoting = False
        
        self.move = None

        self.visual_run = True
        self.console_run = False

        self.play = play

        if self.play == "A":
            self.engine = Engine()
            self.engine.chess = self.logic

    def GetPieceUnderMouse(self):
        x, y = pygame.Vector2(pygame.mouse.get_pos())

        x, y = (x-TOP_X)//SQUARE_SIZE, (y-TOP_Y)//SQUARE_SIZE

        if (0 <= x <= 7) and (0 <= y <= 7):
            square = 8*y + x

            piece = list(filter(lambda piece : piece.square == square, self.logic.board.pieces))

            if self.logic.dragging and len(piece) == 0:
                return int(square)
            elif len(piece) != 0:
                return piece[0]
            
        else:
            return None

    def MakeMove(self, move):
        # makes move and updates renderer
        self.logic.MakeMove(move)
        self.render.UpdateRenderer(self.logic)

    def UnmakeMove(self):
        # unmakes most recent move and updates renderer
        self.logic.UnmakeMove()
        self.render.UpdateRenderer(self.logic)

    @staticmethod
    def AlgebraicToNumber(square):
        file, rank = square

        file_index = ord(file) - 97
        rank_index = abs(int(rank) - 8) 

        return 8*rank_index + file_index

    def ConsoleBasedBoard(self, size="S"):
       
        print(f"Turn: {self.logic.board.active_piece}")

        if (self.logic.board.attackers != 0):
            print("King in check")

        self.logic.board.PrintBoard(size)

        if self.logic.board.active_piece == "b" and len(self.logic.moveGen.possible_moves) != 0 and self.play == "A":

            try:
                move = self.engine.BestMove()

                print(f"{move.piece.name} {self.logic.NumbertoAlgebraic(move.initial)} {self.logic.NumbertoAlgebraic(move.dest)} {move.type}")
                self.MakeMove(move)
            except:
                print("Final state before crash")
                self.logic.board.PrintBoard()

        else:
            move = input("Move (piece_type, from, to, move_type): ")

            while not move:
                print("Move types:\n - '_'(normal move)\n - 'EP'(en-passant)\n - 'Q,N,R,B,q,n,r,b' for promotion moves\n - 'CQ, CK, cq, ck for white and black castling respectively\n")
                print('Type \'Q\' to quit')
                move = input("Move (piece_type, from, to, move_type): ")
            
            if move == 'Q':
                self.console_based_run = False 
            
            elif move == 'U':
                self.UnmakeMove()

            elif len(move) > 0:
                move = move.split(' ')

                piece_type = move[0]
                initial_sq = self.AlgebraicToNumber(move[1])
                dest_sq = self.AlgebraicToNumber(move[2])
                move_type = move[3]

                the_move = list(filter(lambda move: move.piece.name == piece_type and self.logic.IsAllyPiece(piece_type) and move.initial == initial_sq and 
                move.dest == dest_sq and move.type == move_type, self.logic.moveGen.possible_moves))

                while len(the_move) == 0 and move != 'Q':
                    # is the entered move valid?
                    print('The move you entered is not valid')

                    move = input('Enter the move you\'d like to make (piece_type, from, to, move_type): ')

                    if move != 'Q':
                        move = move.split(' ')

                        piece_type = move[0]
                        initial_sq = self.AlgebraicToNumber(move[1])
                        dest_sq = self.AlgebraicToNumber(move[2])
                        move_type = move[3]

                        the_move = list(filter(lambda move: move.piece.name == piece_type and self.logic.IsAllyPiece(piece_type) and move.initial == initial_sq and 
                        move.dest == dest_sq and move.type == move_type, self.logic.moveGen.possible_moves))
                
                if move == 'Q':
                    self.console_based_run = False
                else:
                    print(' '.join(move))
                    self.MakeMove(the_move[0])

    def VisualBoard(self):
        if self.logic.board.active_piece == "b" and len(self.logic.moveGen.possible_moves) != 0 and self.play == "A":
            try:
                move = self.engine.BestMove()

                print(f"{move.piece.name} {self.logic.NumbertoAlgebraic(move.initial)} {self.logic.NumbertoAlgebraic(move.dest)} {move.type}")
                self.MakeMove(move)

            except:
                print("Final state before crash")
                self.logic.board.PrintBoard()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.logic.board.PrintBoard()

                    self.run = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.UnmakeMove()    

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.GetPieceUnderMouse() is not None:
                        if not self.logic.dragging:
                            
                            self.logic.drag_piece = self.GetPieceUnderMouse()
        
                            """
                            which of the possible moves are possible for the piece being dragged?
                            """
                            self.logic.drag_piece_moves = list(filter(lambda move : (move & 0xfc0) >> 6 == self.logic.drag_piece.square, self.logic.moveGen.possible_moves))

                
                        if self.logic.IsAllyPiece(self.logic.drag_piece.name):
                            self.logic.dragging = True

                if event.type == pygame.MOUSEBUTTONUP:
                    under_mouse = self.GetPieceUnderMouse()

                    if under_mouse is not None and self.logic.dragging:
                        # try to find move that corresponds to this final square
                        if isinstance(under_mouse, int):
                            self.move = list(filter(lambda move : move & 0x3f == under_mouse, self.logic.drag_piece_moves))
                        else:
                            """under the mouse is an opponent piece we can capture, check whether final square of this move 
                            matches initial square of opponent piece under mouse"""
                            self.move = list(filter(lambda move: move & 0x3f == under_mouse.square, self.logic.drag_piece_moves))

                        if len(self.move) == 0:
                            # not a valid move for drag piece
                            self.logic.dragging = False
                        else:
                            if self.move[0] & 0x8000 != 0:
                                # pawn promotion
                                self.promoting = True

                            else:
                                # make move, it will be in list form, so index 0
                                self.MakeMove(self.move[0])
                                self.logic.dragging = False
                                

                if event.type == pygame.KEYDOWN and self.promoting:
                    # convention -> q, n, r, b
                    if event.key == pygame.K_q:
                        # promote to queen
                        self.MakeMove(self.move[0])
                        
                    elif event.key == pygame.K_n:
                        # promote to knight
                        self.MakeMove(self.move[1])
                        
                    elif event.key == pygame.K_r:
                        # promote to rook
                        self.MakeMove(self.move[2])
                        
                    elif event.key == pygame.K_b:
                        # promote to bishop
                        self.MakeMove(self.move[3])
                        
                    else:
                        self.logic.dragging = False

                    self.logic.dragging = False

            self.render.clock.tick(30)
            self.render.DrawWindow()


if __name__ == '__main__':
    starting_fen = input("Fen: ")

    choice = input('Would you like to play (C)onsole based, or on the (V)isual board: ').strip().upper()
    play = input("(T)esting or (A)I: ").strip().upper()

    if not starting_fen:
        chess = PlayableChess(play=play)
    else:
        chess = PlayableChess(starting_fen, play)

    if choice == 'V':
        while chess.visual_run:
            chess.VisualBoard()

    else:
        pygame.quit()
        chess.console_based_run = True

        size = input("(L)arge or (S)mall board: ").strip().upper()

        while size != "S" and size != "L":
            size = input("(L)arge or (S)mall board: ").strip().upper()

        while chess.console_based_run:
            chess.ConsoleBasedBoard(size)
