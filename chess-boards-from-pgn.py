import chess.pgn
from glob import glob
import numpy as np
from sys import stdout
from pandas import DataFrame

file = glob("pgn/*.pgn")[0]
pgn = open(file)

def alter_result(_result: str) -> int:
	if _result == "1-0": return +1
	elif _result == "1/2-1/2": return 0
	elif _result == "0-1": return -1
	raise ValueError()

def board_as_matrix(_board: chess.Board):
	empty_space = ord('.')
	matrix = [[ord(y) - empty_space for y in x.split(" ")] for x in str(_board).split("\n")]
	return np.asarray(matrix)

data_frame = DataFrame()

counter = 0
while True:
	pgn_game = chess.pgn.read_game(pgn)
	if pgn_game is None or counter > 1000:
		break

	counter += 1

	result = alter_result(pgn_game.headers["Result"])

	board = pgn_game.board()

	boards = []
	for move in pgn_game.main_line():
		board.push(move)
		boards.append(board_as_matrix(board))

	game_data_frame = DataFrame(data=np.array(boards).reshape((len(boards), 64,)),
	                            columns=["p"+str(x+1) for x in range(64)])
	game_data_frame["result"] = result

	data_frame = data_frame.append(game_data_frame, ignore_index=True)

import random
import string
s = "".join([random.choice(string.ascii_letters) for _ in range(10)])
data_frame.to_csv("csv/grand_master_pgn_{}.csv".format(s.lower()), index=False)