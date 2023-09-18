# Chess game:

<img width="210" alt="Screenshot 2023-03-11 110641" src="https://user-images.githubusercontent.com/56346800/224480781-678ed55c-2e52-4064-9e93-d25be41df5dd.png">

Implementing chess: 
  - Implement castling [DONE]
  - Filter for legal chess moves (handling pins, double checks etc)[DONE]
  - Write perft test [DONE]
    
GRAPHICAL
_________

![Screenshot from 2023-03-28 01-34-06](https://user-images.githubusercontent.com/56346800/228096703-5dfec546-1753-419d-899d-b53f8bd192d1.png)

TERMINAL
_________

![Screenshot from 2023-03-28 01-30-07](https://user-images.githubusercontent.com/56346800/228096360-73e32778-0d40-4060-9c75-a5d9002a7d99.png)

Can perform move undo on terminal board
![Screenshot from 2023-03-28 01-30-19](https://user-images.githubusercontent.com/56346800/228096368-d1aa6049-78e0-4f76-bfd4-51a243a1a653.png)

Bitboards are 64 bit numbers used to represent a chess board. They involve clever bit twiddling tricks to obtain moves 
quickly.

I start by parsing a FEN string to initialise the board, then I make my first bitboards for each piece type from that. Whenever a move is made, the bitboards change. 

Perft test results:
___________________

Looks good. Will keep testing until I'm satisfied enough that there's 'no' bugs in move generation
