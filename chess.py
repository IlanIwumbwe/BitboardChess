import pygame
from classicalBitboard import Board
from moveGeneration import GenerateMoves
import numpy as np
import sys
from piece import Piece

WIDTH = 700
HEIGHT = 700

BOARD_DIMENSION = 8

SQUARE_SIZE = 70
IMAGE_SIZE = 70

BOARD_WIDTH = SQUARE_SIZE*BOARD_DIMENSION
BOARD_HEIGHT = SQUARE_SIZE*BOARD_DIMENSION

TOP_X = (WIDTH-BOARD_WIDTH)//2
TOP_Y = (HEIGHT-BOARD_HEIGHT)//2

WHITE = (221,240,228)#(255,51,51) # odd squares colour
BLACK = (0,0,22) # rendering text
BOARD_GREY = (40,54,60)# (255, 255, 153)#(170, 70, 70) # # even squares colour
GREY = (40,54,60) #(255, 255, 153) # (150, 100, 100)  # background colour
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
        self.ParseFen('r3k1r1/1b2bp1p/3qp3/1pnp4/3B4/4Q1P1/3NPPBP/R4RK1 w - - 0 0')
        self.board.FenToBitboards()
        self.board.SetUpBitboards()
        self.board.InitialiseBoard()

        self.moveGen = GenerateMoves(self.board)
        self.moveGen.PopulateAttackTables()
        self.moveGen.PopulateRayTable()

        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.run = True
        self.is_checkmate = False
        self.is_stalemate = False
        self.dragging = False
        self.promoting = False
        self.drag_piece = None  
        self.generate_moves = True
        self.clock = pygame.time.Clock()

        self.console_based_run = True

        self.move = None

        self.previous_possible_moves = []
        self.drag_piece_possible_moves = []

        # populate initial set of possible moves
        self.moveGen.GenerateAllPossibleMoves()

    def ParseFen(self, full_fen):
        self.board.position_fen, self.board.active_piece, self.board.castling_rights, self.board.en_passant, self.board.ply, self.board.moves = full_fen.split(' ')

        if self.board.en_passant != '-':
            x = ord(self.board.en_passant[0])-97
            y = 8 - int(self.board.en_passant[1])

            if y == 2:
                # last move by black pawn 2 down
                black_pawn = Piece('p', x + 8)
                self.board.move_history.append((black_pawn, black_pawn.square, black_pawn.square + 16, 'EP'))

            elif y == 5:
                # last move by white pawn 2 up
                white_pawn = Piece('P', x + 48)
                self.board.move_history.append((white_pawn, white_pawn.square, white_pawn.square - 16, 'EP'))

        self.board.ply = int(self.board.ply)
        self.board.moves = int(self.board.moves)

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

        if self.is_checkmate:
            self.win.blit(font.render("Checkmate", True, BLACK), (TOP_X , TOP_Y//2))

            if self.board.active_piece == 'w':
                self.win.blit(font.render("Black wins", True, BLACK), (TOP_X + 100 , TOP_Y//2))
            else:
                self.win.blit(font.render("White wins", True, (255, 255, 255)), (TOP_X + 100 , TOP_Y//2))

            x, y = self.moveGen.ally_king.square % 8, self.moveGen.ally_king.square // 8

            pygame.draw.rect(self.win, RED, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)

        elif self.is_stalemate:
            self.win.blit(font.render("Stalemate", True, BLACK), (TOP_X , TOP_Y//2))

            enemy_king = self.moveGen.GetEnemyKing()

            x, y = self.moveGen.ally_king.square % 8, self.moveGen.ally_king.square // 8

            pygame.draw.rect(self.win, RED, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)
            pygame.draw.rect(self.win, RED, ( enemy_king.square % 8 * SQUARE_SIZE + TOP_X, enemy_king.square // 8 * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)

        for index in range(64):
            piece_type, square = self.board.console_board[index], index
            if piece_type != '.':
                self.RenderPiece(piece_type, square)

        if self.dragging:
            drag_piece_type, drag_piece_square = self.drag_piece
            pygame.draw.rect(self.win, ORANGE, (
            (drag_piece_square%8) * SQUARE_SIZE + TOP_X, (drag_piece_square//8) * SQUARE_SIZE + TOP_Y, SQUARE_SIZE,
            SQUARE_SIZE), 0)

            for move in self.drag_piece_possible_moves:
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

    def IsCheckmate(self):
        king_can_move = len(list(filter(lambda move : move[0] == self.moveGen.ally_king, self.moveGen.possible_moves))) != 0

        return (king_can_move == False and self.board.attackers != 0)

    def IsStalemate(self):
        return len(self.moveGen.possible_moves) == 0 and self.board.attackers == 0

    def VisualBoard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('>>>>>>>>>>>>>>>>>>>>>>>')
                self.board.PrintBoard()

                self.run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.UnmakeMove()    

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.GetPieceUnderMouse() is not None:
                    if not self.dragging:
                        
                        self.drag_piece = self.GetPieceUnderMouse()
                        drag_piece_type, drag_piece_square = self.drag_piece

                        """
                        which of the possible moves are possible for the piece being dragged?
                        """
                        self.drag_piece_possible_moves = list(filter(lambda move : move[1] == drag_piece_square, self.moveGen.possible_moves))

                    if self.IsAllyPiece(self.drag_piece[0]):
                        self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP:
                under_mouse = self.GetPieceUnderMouse()

                if under_mouse is not None and self.dragging:
                    # try to find move that corresponds to this final square
                    if isinstance(under_mouse, int):
                        self.move = list(filter(lambda move : move[2] == under_mouse, self.drag_piece_possible_moves))
                    else:
                        """under the mouse is an opponent piece we can capture, check whether final square of this move 
                        matches initial square of opponent piece under mouse"""
                        self.move = list(filter(lambda move: move[2] == under_mouse[1], self.drag_piece_possible_moves))

                    if len(self.move) == 0:
                        # not a valid move for drag piece
                        self.dragging = False
                    else:
                        if self.move[0][3] not in ['_', 'EP', 'CK', 'CQ', 'Ck', 'Cq']:
                            # pawn promotion
                            self.promoting = True

                        else:
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

        if self.IsCheckmate():
            self.dragging = False
            self.is_checkmate = True

        if self.IsStalemate():
            self.dragging = False
            self.is_stalemate = True

        self.clock.tick(30)
        self.DrawWindow()


    def SwitchActivePiece(self):
        if self.board.active_piece == "w":
            self.board.active_piece = "b"
        else:
            self.board.active_piece = "w"

    def MakeMove(self, move):
        """
        move structure -> piece_name, initial_sq, final_sq, move_type

        P, 52, 36, _  (normal move)
        P, 13, 5, Q (promotion move to white queen)
        P, 18, 11, EP (pawn capture by en-passant)
        K, 60, 62, CK (white king kingside castle)
        K, 60, 57, CQ (white king queenside castle)

        move[3] will change from _ to piece object of captured piece if 
        captures happens
        """
        piece, initial_sq, final_sq, move_type = move
        
        self.board.move_history.append(move)

        # remove piece from initial square
        drag_piece_bitboard = self.board.GetBitboard(piece.name)
        drag_piece_bitboard &= ~self.board.SquareToBB(initial_sq)
        self.board.SetBitboard(piece.name, drag_piece_bitboard)

        if self.board.IsSquareOccupied(final_sq) == True:
            # remove captured piece from final square
            captured_piece = self.board.GetPieceOnSquare(final_sq)
            captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
            captured_piece_bitboard &= ~self.board.SquareToBB(final_sq)
            self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

            self.board.pieces.remove(captured_piece)

            # add captured piece to move tuple
            self.board.move_history[-1] = self.board.move_history[-1][:3] + (captured_piece,)

        else:
            if move_type == 'EP' and piece.name in ['P', 'p']:
                # en-passant capture

                captured_piece = None
        
                if piece.name == 'P':
                    # white pawn performs EP capture, black pawn is below final square
                    captured_piece = self.board.GetPieceOnSquare(final_sq + 8)

                elif piece.name == 'p':
                    # black pawn performs EP capture, white pawn is above final square
                    captured_piece = self.board.GetPieceOnSquare(final_sq - 8)
                
                # remove captured piece from square
                captured_piece_bitboard = self.board.GetBitboard(captured_piece.name)
                captured_piece_bitboard &= ~self.board.SquareToBB(captured_piece.square)
                self.board.SetBitboard(captured_piece.name, captured_piece_bitboard)

                self.board.pieces.remove(captured_piece)

                self.board.move_history[-1] = self.board.move_history[-1][:3] + (captured_piece,)

        if move_type != '_' and move_type != 'EP' and 'C' not in move_type:
            # promotion, set bitboard of move type parameter, which is the piece we want to promote to
            promotion_piece_bitboard = self.board.GetBitboard(move_type)
            promotion_piece_bitboard |= self.board.SquareToBB(final_sq)
            self.board.SetBitboard(move_type, promotion_piece_bitboard)

            # change piece's name and square, increased times moved
            piece.name = move_type
            piece.square = final_sq
            piece.times_moved += 1
            piece.promoted = True
        
        else:
            # move piece to final square in its bitboard
            drag_piece_bitboard = self.board.GetBitboard(piece.name)
            drag_piece_bitboard |= self.board.SquareToBB(final_sq)
            self.board.SetBitboard(piece.name, drag_piece_bitboard)

            # change piece's square, set has moved to true
            piece.square = final_sq
            piece.times_moved += 1

            # perform rook movement for castling move
            if move_type == 'CK':
                rook = self.board.GetPieceOnSquare(63)
                new_rook_position = initial_sq + 1

                self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('K', '')             

            elif move_type == 'CQ':
                rook = self.board.GetPieceOnSquare(56)
                new_rook_position = initial_sq - 2

                self.board.white_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.white_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('Q', '')

            elif move_type == 'Ck':
                rook = self.board.GetPieceOnSquare(7)
                new_rook_position = initial_sq + 1

                self.board.black_rooks &= ~self.ooard.SquareToBB(rook.square)
                self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('k', '')

            elif move_type == 'Cq':
                rook = self.board.GetPieceOnSquare(0)
                new_rook_position = initial_sq - 2

                self.board.black_rooks &= ~self.board.SquareToBB(rook.square)
                self.board.black_rooks |= self.board.SquareToBB(new_rook_position)

                rook.square = new_rook_position
                rook.times_moved += 1

                self.board.castling_rights = self.board.castling_rights.replace('q', '')
                            
        self.board.ply += 1
        self.board.moves = self.board.ply // 2

        # after move is made, bitboards have changed, so update all bitboard variables. 
        # update ascii board, this is used for rendering
        self.board.SetUpBitboards()
        self.board.UpdateBoard()

        self.SwitchActivePiece()

        self.previous_possible_moves.append(self.moveGen.possible_moves)
        self.moveGen.GenerateAllPossibleMoves()   

    def UnmakeMove(self):
        """
        revert move at top of move history list
        
        - subtract ply and moves
        - if castling move, add castling type to castling rights 
        """
        if len(self.board.move_history) >= 1:
            piece, initial_sq, final_sq, move_type = self.board.move_history.pop()

            if isinstance(move_type, Piece):
                # move drag piece to initial square, remove from final square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard &= ~self.board.SquareToBB(final_sq)

                if piece.promoted:
                    piece.name = 'P' if piece.name.isupper() else 'p'
                    piece.square = initial_sq
                    piece.times_moved -= 1
                    piece.promoted = False

                    # piece name now correct, can get correct bitboard
                    drag_piece_bitboard = self.board.GetBitboard(piece.name)
                    drag_piece_bitboard |= self.board.SquareToBB(initial_sq)
                else:
                    drag_piece_bitboard |= self.board.SquareToBB(initial_sq)

                self.board.SetBitboard(piece.name, drag_piece_bitboard)

                # captures move happened, so restore captured piece
                captured_piece_bitboard = self.board.GetBitboard(move_type.name)
                captured_piece_bitboard |= self.board.SquareToBB(move_type.square)
                self.board.SetBitboard(move_type.name, captured_piece_bitboard)

                self.board.pieces.append(move_type)

                piece.square = initial_sq
                piece.times_moved -= 1

            elif move_type != '_' and move_type != 'EP' and 'C' not in move_type:
                # must be promotion move

                # remove promoted piece from final square
                prom_piece_bitboard = self.board.GetBitboard(piece.name)
                prom_piece_bitboard &= ~self.board.SquareToBB(final_sq)
                self.board.SetBitboard(piece.name, prom_piece_bitboard)

                piece.name = 'P' if piece.name.isupper() else 'p'
                piece.square = initial_sq
                piece.times_moved -= 1

                # piece name now correct, can get correct bitboard
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard |= self.board.SquareToBB(initial_sq)
                self.board.SetBitboard(piece.name, drag_piece_bitboard)

            else:
                # must be normal move, movement with no captures, or castling

                # move drag piece back to initial square
                drag_piece_bitboard = self.board.GetBitboard(piece.name)
                drag_piece_bitboard |= self.board.SquareToBB(initial_sq)

                # remove drag piece from final square
                drag_piece_bitboard &= ~self.board.SquareToBB(final_sq)

                self.board.SetBitboard(piece.name, drag_piece_bitboard)

                piece.square = initial_sq
                piece.times_moved -= 1

                # if castling move, move rook back to where it has to be, and revert castlng rights

                if move_type == 'CK':
                    new_rook_position = initial_sq + 1
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.white_rooks |= self.board.SquareToBB(63)

                    rook.square = 63
                    rook.times_moved -= 1

                    self.board.castling_rights += 'K'            

                elif move_type == 'CQ':
                    new_rook_position = initial_sq - 2
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.white_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.white_rooks |= self.board.SquareToBB(56)

                    rook.square = 56
                    rook.times_moved -= 1

                    self.board.castling_rights += 'Q'       

                elif move_type == 'Ck':
                    new_rook_position = initial_sq + 1
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.black_rooks |= self.board.SquareToBB(7)

                    rook.square = 7
                    rook.times_moved -= 1

                    self.board.castling_rights += 'k'    

                elif move_type == 'Cq':
                    new_rook_position = initial_sq - 2
                    rook = self.board.GetPieceOnSquare(new_rook_position)
                
                    self.board.black_rooks &= ~self.board.SquareToBB(new_rook_position)
                    self.board.black_rooks |= self.board.SquareToBB(0)

                    rook.square = 0
                    rook.times_moved -= 1

                    self.board.castling_rights += 'q'    
                
            self.board.ply -= 1
            self.board.moves -= 1 # ?
            self.SwitchActivePiece()

            self.moveGen.ally_king = self.moveGen.GetAllyKing()
            self.moveGen.GetAttackers()

            self.is_checkmate = False
            self.is_stalemate = False
        
            self.board.SetUpBitboards()
            self.board.UpdateBoard()

            self.moveGen.possible_moves = self.previous_possible_moves.pop()
    


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
