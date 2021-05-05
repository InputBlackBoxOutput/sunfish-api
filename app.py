import flask
from flask import request, jsonify
from flask_cors import CORS
from sunfish import sunfish
import chess
import chess.pgn

import os
import re
import time
import io

app = flask.Flask(__name__)
app.secret_key = os.urandom(24)
app.config["DEBUG"] = True
cors = CORS(app)

# Forsyth–Edwards Notation (FEN)
# Example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1


# Function to validate FEN entered by the user
# Originally written by Dani4kor. Modified by InputBlackBoxOutput
def validate_fen(fen):
    regexMatch = re.match(
        '\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q]{1,4})\s(-|[a-h][1-8])\s(\d+\s\d+)$', fen)

    if regexMatch:
        regexList = regexMatch.groups()
        fen = regexList[0].split("/")
        if len(fen) != 8:
            return (True, "Expected 8 rows in position part of fen: {0}".format(repr(fen)))

        for fenPart in fen:
            field_sum = 0
            previous_was_digit, previous_was_piece = False, False

            for c in fenPart:
                if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    if previous_was_digit:
                        return (True, "Two subsequent digits in position part of FEN: {0}".format(repr(fen)))
                    field_sum += int(c)
                    previous_was_digit = True
                    previous_was_piece = False
                elif c == "~":
                    if not previous_was_piece:
                        return (True, "~ not after piece in position part of FEN: {0}".format(repr(fen)))
                    previous_was_digit, previous_was_piece = False, False
                elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                    field_sum += 1
                    previous_was_digit = False
                    previous_was_piece = True
                else:
                    return (True, "Invalid character in position part of FEN: {0}".format(repr(fen)))

            if field_sum != 8:
                return (True, "Expected 8 columns per row in position part of FEN: {0}".format(repr(fen)))

    else:
        return (True, "Incorrect format. Here is an example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ")

    return(False, None)

# Function to convert piece placement in FEN to the format required by sunfish


def convert_piece_placement(piece_placement):
    out = "         \n         \n "
    count = 0
    for c in piece_placement:
        if c.isalpha():
            out += c
            count += 1
        elif c.isnumeric():
            for _ in range(int(c)):
                out += '.'
                count += 1

                # Add newline when dealing with dots
                if count == 8:
                    out += '\n '
                    count = 0

        if count == 8:
            out += '\n '
            count = 0

    out += "         \n         \n'"
    return out


@app.route('/', methods=['GET'])
def root():
    return '''
            <h3>You have accessed the sunfish-API endpoint.</h3>

            To know more about using the API, head to the link given below: <br>
            <a href="https://github.com/InputBlackBoxOutput/sunfish-API">
                https://github.com/InputBlackBoxOutput/sunfish-API
            </a>
            '''


@app.route('/fen', methods=['GET'])
def fen():
    # Get FEN from the query string
    if 'fen' in request.args:
        fen = str(request.args['fen'])
    else:
        return jsonify({"error": "No 'fen' field provided or the 'fen' field is empty",
                        "docs": "Please specify the state of the chessboard using Forsyth–Edwards Notation (FEN)."})

    # Validate the FEN
    has_error, reason = validate_fen(fen)
    if has_error:
        return jsonify({"error": "Incorrect Forsyth–Edwards Notation (FEN) for the board state",
                        "reason": reason})

    fen = fen.split()

    # Return an error if active colour is white
    if fen[1] == 'w':
        return jsonify({"error": "The white player is supposed to make a move"})

    state = convert_piece_placement(fen[0])
    hist = [sunfish.Position(state, 0, (True, True), (True, True), 0, 0)]
    searcher = sunfish.Searcher()

    start = time.time()
    for _depth, move, _ in searcher.search(hist[-1], hist):
        if time.time() - start > 2:
            m = sunfish.render(119-move[0]) + sunfish.render(119-move[1])
            return jsonify({"move": m})

    m = sunfish.render(119-move[0]) + sunfish.render(119-move[1])

    return jsonify({"move": m})


# Portable Game Notation PGN
example = '''
[Event "F/S Return Match"]
[Site "Belgrade, Serbia JUG"]
[Date "1992.11.04"]
[Round "29"]
[White "Fischer, Robert J."]
[Black "Spassky, Boris V."]
[Result "1/2-1/2"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 {This opening is called the Ruy Lopez.}
4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7
11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5
Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6
23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5
hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5
35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6
Nf2 42. g4 Bd3 43. Re6 1/2-1/2
'''


@app.route('/pgn', methods=['GET'])
def pgn():
    # Get pgn from the query string
    if 'pgn' in request.args:
        pgn = str(request.args['pgn']).split(',')
    else:
        return jsonify({"error": "No 'pgn' field provided. or the 'fen' field is empty",
                        "docs": "Please provide the flow of the game in Portable Game Notation (PGN) format "})

    pgn = io.StringIO(str(pgn))
    game = chess.pgn.read_game(pgn)

    board = game.board()
    moves = game.mainline_moves()

    # moves_uci = [x.uci() for x in moves]
    # print(str(moves_uci))

    for move in moves:
        board.push(move)

    placement = board.fen().split()[0]
    state = convert_piece_placement(placement)
    hist = [sunfish.Position(state, 0, (True, True), (True, True), 0, 0)]

    # Find a good move for the computer
    searcher = sunfish.Searcher()

    start = time.time()
    for _depth, move, _ in searcher.search(hist[-1], hist):
        if time.time() - start > 2:
            m = sunfish.render(119-move[0]) + sunfish.render(119-move[1])
            return jsonify({"move": m})

    m = sunfish.render(119-move[0]) + sunfish.render(119-move[1])
    return jsonify({"move": m})


if __name__ == '__main__':
    app.run()
