# Bitboard chess engine:

- Currently implementing chess:
     To do:
  * Implement castling
  * Filter for legal chess moves (handling pins, double checks etc)
  * Write perft test
  * Start on engine itself

GUI
______________
![chess_board](https://user-images.githubusercontent.com/56346800/207369911-f78d54ef-723f-4f5f-8ea9-01ba24f0e428.png)

CONSOLE 
______________
![console_based](https://user-images.githubusercontent.com/56346800/207369968-7fed58a5-16c6-4dc1-9236-80413c274fdf.png)


Bitboards are 64 bit numbers used to represent a chess board. They involve clever bit twiddling tricks to obtain moves 
quickly. 
