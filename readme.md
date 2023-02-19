# Bitboard chess engine:

![chess_img2](https://user-images.githubusercontent.com/56346800/219978489-f2e89eeb-1feb-47b2-a8f3-099c19d712ba.jpg)

Currently implementing chess: [DONE? - need perft test]
  - Implement castling [DONE]
  - Filter for legal chess moves (handling pins, double checks etc)[DONE]
  - Write perft test 
  - Start on engine itself

GUI
______________
![Screenshot from 2023-02-19 22-20-45](https://user-images.githubusercontent.com/56346800/219978609-54e750e1-35fc-484f-9a16-31a74ad3d315.png)

CONSOLE 
______________
![Screenshot from 2022-12-26 22-04-54](https://user-images.githubusercontent.com/56346800/209585725-da41ed24-0293-4eea-be5f-296608778c5d.png)

Bitboards are 64 bit numbers used to represent a chess board. They involve clever bit twiddling tricks to obtain moves 
quickly.

I start by parsing a FEN string to initialise the board, then I make my first bitboards for each piece type from that. Whenever a move is made, the bitboards change. 
