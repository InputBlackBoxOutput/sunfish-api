import flask
from flask import request, jsonify
from flask_cors import CORS
from sunfish import sunfish

import os
import re
import time

app = flask.Flask(__name__)
app.secret_key = os.urandom(24)
app.config["DEBUG"] = True
cors = CORS(app)

# The API uses Forsyth–Edwards Notation (FEN) to specify the position of pieces on the chessboard
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
        return (True, " FEN doesn`t match follow this example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ")

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
    # Get FEN from the query string
    if 'fen' in request.args:
        fen = str(request.args['fen'])
    else:
        return jsonify({"error": "No 'fen' field provided.",
                        "remedy": "Please specify the state of the chessboard using Forsyth–Edwards Notation (FEN)."})

    # Validate the FEN
    has_error, reason = validate_fen(fen)
    if has_error:
        return jsonify({"error": "Incorrect Forsyth–Edwards Notation (FEN) for the board state",
                        "reason": reason})

    fen = fen.split()

    # Return an error if active colour is white
    if fen[1] == 'w':
        return jsonify({"error": "The white player is supposed to make a move. The computer is playing with the black pieces!"})

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


if __name__ == '__main__':
    app.run()
