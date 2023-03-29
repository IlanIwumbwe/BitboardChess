import pygame

WIDTH = 700
HEIGHT = 700

BOARD_DIMENSION = 8

SQUARE_SIZE = 70
IMAGE_SIZE = 70

BOARD_WIDTH = SQUARE_SIZE*BOARD_DIMENSION
BOARD_HEIGHT = SQUARE_SIZE*BOARD_DIMENSION

TOP_X = (WIDTH-BOARD_WIDTH)//2
TOP_Y = (HEIGHT-BOARD_HEIGHT)//2

ODD_SQUARES = (40,54,60)#(221,240,228)#(255,51,51) # odd squares colour
TEXT_COLOUR = (0,0,22) # rendering text
EVEN_SQUARES =(221,240,228) #(40,54,60)# (255, 255, 153)#(170, 70, 70) # # even squares colour
BG = (221,240,228)#(40,54,60) #(255, 255, 153) # (150, 100, 100)  # background colour
DRAG_HIGHLIGHT = (255, 128, 0) # initial drag piece square
MATE_HIGHLIGHT = (255, 251, 51) # nothing
POSSIBLE_EVENS = (87, 200, 77) # possible squares
POSSIBLE_ODDS = (171, 224, 152) # possible squares

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


class Render:
    def __init__(self):
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.game_state = None
        self.clock = pygame.time.Clock()

    def UpdateRenderer(self, game_state):
        self.game_state = game_state

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

        self.win.fill(BG)

        for rank in range(BOARD_DIMENSION):

            self.win.blit(font.render(f"{BOARD_DIMENSION-rank}", True, TEXT_COLOUR), (TOP_X - 15, TOP_Y+(rank*SQUARE_SIZE+SQUARE_SIZE // 2)))

            for file in range(BOARD_DIMENSION):
                if (rank + file) % 2 == 0:
                    pygame.draw.rect(self.win, EVEN_SQUARES, (
                    TOP_X + (file * SQUARE_SIZE), TOP_Y + (rank * SQUARE_SIZE), SQUARE_SIZE, SQUARE_SIZE), 0)
                else:
                    pygame.draw.rect(self.win, ODD_SQUARES, (
                        TOP_X + (file * SQUARE_SIZE), TOP_Y + (rank * SQUARE_SIZE), SQUARE_SIZE, SQUARE_SIZE), 0)

                if rank == BOARD_DIMENSION-1:

                    self.win.blit(font.render(f"{chr(97+file)}", True, TEXT_COLOUR),
                                  (TOP_X + (file*SQUARE_SIZE)+SQUARE_SIZE//2, TOP_Y + BOARD_HEIGHT + 15))

        if self.game_state.is_checkmate:
            self.win.blit(font.render("Checkmate", True, TEXT_COLOUR), (TOP_X , TOP_Y//2))

            if self.game_state.board.active_piece == 'w':
                self.win.blit(font.render("Black wins", True, TEXT_COLOUR), (TOP_X + 100 , TOP_Y//2))
            else:
                self.win.blit(font.render("White wins", True, (255, 255, 255)), (TOP_X + 100 , TOP_Y//2))

            x, y = self.game_state.moveGen.ally_king.square % 8, self.game_state.moveGen.ally_king.square // 8

            pygame.draw.rect(self.win, MATE_HIGHLIGHT, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)

        elif self.game_state.is_stalemate:
            self.win.blit(font.render("Stalemate", True, TEXT_COLOUR), (TOP_X , TOP_Y//2))

            enemy_king = self.game_state.moveGen.GetEnemyKing()

            x, y = self.game_state.moveGen.ally_king.square % 8, self.game_state.moveGen.ally_king.square // 8

            pygame.draw.rect(self.win, MATE_HIGHLIGHT, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)
            pygame.draw.rect(self.win, MATE_HIGHLIGHT, ( enemy_king.square % 8 * SQUARE_SIZE + TOP_X, enemy_king.square // 8 * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)

        for index in range(64):
            piece_type, square = self.game_state.board.console_board[index], index
            if piece_type != '.':
                self.RenderPiece(piece_type, square)

        if self.game_state.dragging:
            drag_piece_type, drag_piece_square = self.game_state.drag_piece
            pygame.draw.rect(self.win, DRAG_HIGHLIGHT, (
            (drag_piece_square%8) * SQUARE_SIZE + TOP_X, (drag_piece_square//8) * SQUARE_SIZE + TOP_Y, SQUARE_SIZE,
            SQUARE_SIZE), 0)

            for move in self.game_state.drag_piece_moves:
                poss_sq = move.dest
                x, y = poss_sq%8, poss_sq//8

                if (x+y)%2 == 0:
                    pygame.draw.rect(self.win, POSSIBLE_EVENS, ( x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE), 0)
                else:
                    pygame.draw.rect(self.win, POSSIBLE_ODDS,
                                     (x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y, SQUARE_SIZE, SQUARE_SIZE),
                                     0)

                for index in range(64):
                    piece_type, square = self.game_state.board.console_board[index], index
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

        """for n in range(64):
            number = font.render(f'{n}', True, BLACK)

            x = n%8
            y = n//8

            self.win.blit(number, (x * SQUARE_SIZE + TOP_X, y * SQUARE_SIZE + TOP_Y))"""

    def DrawWindow(self):
        pygame.font.init()
        pygame.display.set_caption("Chess")
        self.RenderBoard()

        pygame.display.update()
