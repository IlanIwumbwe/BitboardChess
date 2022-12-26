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
![Screenshot from 2022-12-26 22-04-54](https://user-images.githubusercontent.com/56346800/209585725-da41ed24-0293-4eea-be5f-296608778c5d.png)

Bitboards are 64 bit numbers used to represent a chess board. They involve clever bit twiddling tricks to obtain moves 
quickly. 
