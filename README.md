# A web API for the sunfish chess engine


## Endpoint: https://sunfish-api.herokuapp.com/

## Routes:

- GET /fen

Provide the state of the chessboard using Forsyth–Edwards Notation (FEN) via the fen field and get chess engine's move.

Example:
``` text
https://sunfish-api.herokuapp.com/fen?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20b%20KQkq%20-%200%201
```

- GET /pgn

Provide the state of the chessboard using Portable Game Notation PGN via the pgn field and get chess engine's move

Example:
``` text
https://sunfish-api.herokuapp.com/pgn?pgn=1.%20e4%20e5%202.%20Nf3%20Nc6%203.%20Bb5%20a6%20{This%20opening%20is%20called%20the%20Ruy%20Lopez.}%204.%20Ba4%20Nf6%205.%20O-O%20Be7%206.%20Re1%20b5%207.%20Bb3%20d6%208.%20c3%20O-O%209.%20h3%20Nb8%2010.%20d4%20Nbd7%2011.%20c4%20c6%2012.%20cxb5%20axb5%2013.%20Nc3%20Bb7%2014.%20Bg5%20b4%2015.%20Nb1%20h6%2016.%20Bh4%20c5%2017.%20dxe5%20Nxe4%2018.%20Bxe7%20Qxe7%2019.%20exd6%20Qf6%2020.%20Nbd2%20Nxd6%2021.%20Nc4%20Nxc4%2022.%20Bxc4%20Nb6%2023.%20Ne5%20Rae8%2024.%20Bxf7+%20Rxf7%2025.%20Nxf7%20Rxe1+%2026.%20Qxe1%20Kxf7%2027.%20Qe3%20Qg5%2028.%20Qxg5%20hxg5%2029.%20b3%20Ke6%2030.%20a3%20Kd6%2031.%20axb4%20cxb4%2032.%20Ra5%20Nd5%2033.%20f3%20Bc8%2034.%20Kf2%20Bf5%2035.%20Ra7%20g6%2036.%20Ra6+%20Kc5%2037.%20Ke1%20Nf4%2038.%20g3%20Nxh3%2039.%20Kd2%20Kb5%2040.%20Rd6%20Kc5%2041.%20Ra6%20Nf2%2042.%20g4%20Bd3%2043.%20Re6%201/2-1/2
```


Made with lots of ⏱️, 📚 and ☕ by [InputBlackBoxOutput](https://github.com/InputBlackBoxOutput)
