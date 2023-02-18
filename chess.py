import pygame
from classicalBitboard import Board
from moveGeneration import GenerateMoves
import numpy as np

WIDTH = 650
HEIGHT = 650

BOARD_DIMENSION = 8

SQUARE_SIZE = 70
IMAGE_SIZE = 70

BOARD_WIDTH = SQUARE_SIZE*BOARD_DIMENSION
BOARD_HEIGHT = SQUARE_SIZE*BOARD_DIMENSION

TOP_X = (WIDTH-BOARD_WIDTH)//2
TOP_Y = (HEIGHT-BOARD_HEIGHT)//2

WHITE = (255,51,51) # odd squares colour
BLACK = (0,0,22) # rendering text
BOARD_GREY = (255, 255, 153)#(170, 70, 70) # # even squares colour
GREY = (255, 255, 153) # (150, 100, 100)  # background colour
ORANGE = (255, 128, 0) # initial drag piece square
RED = (255, 251, 51) # nothing
DARK_GREEN = (87, 200, 77) # possible squares
LIGHT_GREEN = (171, 224, 152) # possible squares

f = 'freesansbold.ttf'

SPRITES = {'K_w':pygame.image.load('./pieces/K_w.png'),
           'B_w':pygame.image.load('./pieces/B_w.png'),
           'N_w':pygame.image.load('./pieces/N_w.png'),
           'R_w':pygame.image.load('./pieces/R_w.png'),
           'Q_w':pygame.image.load('./pieces/Q_w.png'),
           'P_w':pygame.image.load('./pieces/P_w.png'),
           'K_b':pygame.image.load('./pieces/K_b.png'),
           'B_b':pygame.image.load('./pieces/B_b.png'),
           'N_b':pygame.image.load('./pieces/N_b.png'),
           'R_b':pygame.image.load('./pieces/R_b.png'),
           'Q_b':pygame.image.load('./pieces/Q_b.png'),
           'P_b':pygame.image.load('./pieces/P_b.png')
           }

class Chess:
    def __init__(self):
        self.board = Board()
        self.board.ParseFen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.board.FenToBitboards()
        self.board.SetUpBitboards()
        self.board.InitialiseBoard()

        self.moveGen = GenerateMoves(self.board)
        self.moveGen.PopulateAttackTables()
        self.moveGen.PopulateRayTable()

        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.run = True
        self.dragging = False
        self.promoting = False
        self.drag_piece = None  # (piece_type, square)
        self.clock = pygame.time.Clock()

        self.console_based_run = True

        self.possible_drag_piece_moves = []
        self.move = None

    def RenderPiece(self, piece_type, square):
        x, y = TOP_X + (IMAGE_SIZE * (square%8)), TOP_Y + (IMAGE_SIZE * (square//8))

        if piece_type.isupper():
            image = SPRITES[piece_type + '_w']
        else:
            image = SPRITES[piece_type.upper() + '_b']

        image = pygame.transform.scale(image, (IMAGE_SIZE, IMAGE_SIZE))
        image.get_rect(center=(x, y))
        self.win.blit(image, (x, y))

    def RenderBoard(self):
        pygame.font.init()

        font = pygame.font.Font(f, 15)

        self.win.fill(GREY)

        for rank in range(BOARD_DIMENSION):

            self.win.blit(font.render(f"{BOARD_DIMENSION-rank}", True, BLACK), (TOP_X - 15, TOP_Y+(rank*SQUARE_SIZE+SQUARE_SIZE // 2)))

            for file in range(BOARD_DIMENSION):
                if (rank + file) % 2 == 0:
                    pygame.draw.rect(self.win, WHITE, (
                    TOP_X + (file * SQUARE_SIZE), TOP_Y + (rank * SQUARE_SIZE), SQUARE_SIZE, SQUARE_SIZE), 0)
                else:
                    pygame.draw.rect(self.win, BOARD_GREY, (
                        TOP_X + (file * SQUARE_SIZE), TOP_Y + (rank * SQUARE_SIZE), SQUARE_SIZE, SQUARE_SIZE), 0)

                if rank == BOARD_DIMENSION-1:

                    self.win.blit(font.render(f"{chr(97+file)}", True, BLACK),
                                  (TOP_X + (file*SQUARE_SIZE)+SQUARE_SIZE//2, TOP_Y + BOARD_HEIGHT + 15))

        for index in range(64):
            piece_type, square = self.board.console_board[index], index
            if piece_type != '.':
                self.RenderPiece(piece_type, square)

        if self.dragging:
            drag_piece_type, drag_piece_square = self.drag_piece
            pygame.draw.rect(self.win, ORANGE, (
            (drag_piece_square%8) * SQUARE_SIZE + TOP_X, (drag_piece_square//8) * SQUARE_SIZE + TOP_Y, SQUARE_SIZE,
            SQUARE_SIZE), 0)


            for move in self.possible_drag_piece_moves:
                poss_sq = move[2]
                x, y = poss_sq%8, poss_sq//8
                if (x+y)%2 == 0:
                    pygame.draw.rect(self.win, LIGHT_GREEN, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)
                else:
                    pygame.draw.rect(self.win, DARK_GREEN,
                                     (x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE),
                                     0)

                for index in range(64):
                    piece_type, square = self.board.console_board[index], index
                    if piece_type != '.':
                        if square == poss_sq:
                            self.RenderPiece(piece_type, square)

            x, y = pygame.Vector2(pygame.mouse.get_pos())

            if drag_piece_type.isupper():
                image = SPRITES[drag_piece_type + '_w']
            else:
                image = SPRITES[drag_piece_type.upper() + '_b']

            x, y = x-(image.get_width()//2), y-(image.get_height()//2)
            image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            self.win.blit(image, (x, y))

        for n in range(64):
            number = font.render(f'{n}', True, BLACK)

            x = n%8
            y = n//8

            self.win.blit(number, (x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y))

    def DrawWindow(self):
        pygame.font.init()
        pygame.display.set_caption("Chess")
        self.RenderBoard()

        pygame.display.update()

    def IsAllyPiece(self, piece_type):
        return (self.board.active_piece == 'w' and piece_type.isupper()) or (self.board.active_piece == 'b' and piece_type.islower())

    def GetPieceUnderMouse(self):
        x, y = pygame.Vector2(pygame.mouse.get_pos())

        x, y = (x-TOP_X)//SQUARE_SIZE, (y-TOP_Y)//SQUARE_SIZE

        if (0 <= x <= 7) and (0 <= y <= 7):
            square = 8*y + x

            for index in range(64):
                piece_type = self.board.console_board[index]

                if piece_type != '.':
                    if index == int(square):
                        return piece_type, int(square)

            if self.dragging:
                return int(square)

        else:
            return None

    def MakeMove(self, move):
        self.board.MakeMove(move)
        # add ply, add moves, save game state, save move in move history

        self.board.ply += 1
        self.board.moves = self.board.ply // 2

        self.SwitchActivePiece()

    def SwitchActivePiece(self):
        if self.board.active_piece == "w":
            self.board.active_piece = "b"
        else:
            self.board.active_piece = "w"

    @staticmethod
    def AlgebraicToNumber(square):
        file, rank = square

        file_index = ord(file) - 97
        rank_index = abs(int(rank) - 8) 

        return 8*rank_index + file_index

    def ConsoleBasedBoard(self):
        self.board.PrintBoard()

        print("Move types: '_'(normal move), 'EP'(en-passant), replace string with 'Q,N,R,B,q,n,r,b' for promotion moves")
        print("____________________________________________\nType \'Q\' to quit")
        move = input("Enter the move you\'d like to make (piece_type, from, to, move_type): ")

        while not move:
            print("Move types: '_'(normal move), 'EP'(en-passant), replace string with 'Q,N,R,B,q,n,r,b' for promotion moves")
            print('____________________________________________\nType \'Q\' to quit')
            move = input('Enter the move you\'d like to make (piece_type, from, to, move_type): ')
        
        if move == 'Q':
            self.console_based_run = False 

        elif len(move) > 0:
            move = move.split(',')

            piece_type = move[0]
            initial_sq = self.AlgebraicToNumber(move[1])
            dest_sq = self.AlgebraicToNumber(move[2])
            move_type = move[3]

            self.moveGen.GenerateAllPossibleMoves()

            self.board.possible_moves = list(filter(lambda move : move[1] == initial_sq, self.moveGen.possible_moves))

            the_move = list(filter(lambda move: move[0] == piece_type and self.IsAllyPiece(piece_type) and move[1] == initial_sq and 
            move[2] == dest_sq and move[3] == move_type, self.moveGen.possible_moves))
 
            while len(the_move) == 0 and move != 'Q':
                # is the entered move valid?
                print('The move you entered is not valid')

                move = input('Enter the move you\'d like to make (piece_type, from, to, move_type): ')

                if move != 'Q':
                    move = move.split(',')

                    piece_type = move[0]
                    initial_sq = self.AlgebraicToNumber(move[1])
                    dest_sq = self.AlgebraicToNumber(move[2])
                    move_type = move[3]

                    self.moveGen.GenerateAllPossibleMoves()

                    # self.possible_drag_piece_moves = list(filter(lambda move : move[1] == initial_sq, self.moveGen.possible_moves))
        
                    the_move = list(filter(lambda move: move[0] == piece_type and self.IsAllyPiece(piece_type) and move[1] == initial_sq and 
                    move[2] == dest_sq and move[3] == move_type, self.moveGen.possible_moves))
            
            if move == 'Q':
                self.console_based_run = False
            else:
                self.MakeMove(the_move[0])


    def VisualBoard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Final state>>>>>>>>>>>>>>>>>>>>>>>')
                self.board.PrintBoard()

                self.run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.GetPieceUnderMouse() is not None:
                    if not self.dragging:
                        self.moveGen.GenerateAllPossibleMoves()
                        self.drag_piece = self.GetPieceUnderMouse()

                        drag_piece_type, drag_piece_square = self.drag_piece

                        """print('push mask')
                        self.board.PrintBitboard(self.moveGen.push_mask)
                        print('capture mask')
                        self.board.PrintBitboard(self.moveGen.capture_mask)"""

                        """
                        which of the possible moves are possible for the piece being dragged?
                        """
                        self.possible_drag_piece_moves = list(filter(lambda move : move[1] == drag_piece_square, self.moveGen.possible_moves))
                        
                    if self.IsAllyPiece(self.drag_piece[0]):
                        self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP:
                under_mouse = self.GetPieceUnderMouse()

                if under_mouse is not None and self.dragging:
                    # try to find move that corresponds to this final square
                    if isinstance(under_mouse, int):
                        self.move = list(filter(lambda move : move[2] == under_mouse, self.possible_drag_piece_moves))
                    else:
                        """under the mouse is an opponent piece we can capture, check whether final square of this move 
                        matches initial square of opponent piece under mouse"""
                        self.move = list(filter(lambda move: move[2] == under_mouse[1], self.possible_drag_piece_moves))

                    if len(self.move) == 0:
                        # not a valid move for drag piece
                        self.dragging = False
                    else:
                        if self.move[0][3] not in ['_', 'EP']:
                            # pawn promotion
                            self.promoting = True

                        elif self.move[0][3] == '_' or self.move[0][3] == 'EP':
                            # make move, it will be in list form, so index 0
                            self.MakeMove(self.move[0])
                            self.dragging = False

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
                    self.dragging = False

                self.dragging = False

        self.clock.tick(30)
        self.DrawWindow()
    


if __name__ == '__main__':
    chess = Chess()

    choice = input('Would you like to play (C)onsole based, or on the (V)isual board: ').strip()

    if choice == 'V':
        while chess.run:
            chess.VisualBoard()
    else:
        pygame.quit()

        while chess.console_based_run:
            chess.ConsoleBasedBoard()
