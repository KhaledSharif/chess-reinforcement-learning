from copy import copy
from pprint import pprint
from typing import Tuple, List
import numpy as np
import chess
from random import choice


def print_move(m: chess.Move) -> str:
	return "{} -> {}".format(m.from_square, m.to_square)

def check_state(_board: chess.Board):
	states = {
		"checkmate": _board.is_checkmate(),
		"stalemate": _board.is_stalemate(),
		"insufficient material": _board.is_insufficient_material(),
		"the seventyfive-move rule": _board.is_seventyfive_moves(),
		"fivefold repetition": _board.is_fivefold_repetition(),
		"variant win": _board.is_variant_win(),
		"variant loss": _board.is_variant_loss(),
		"variant draw": _board.is_variant_draw(),
		"variant end": _board.is_variant_end(),
	}

	for i, j in states.items():
		if j is True:
			return i

	return None

def get_piece_count(_board: chess.Board) -> Tuple[int, int]:
	board_as_string = str(_board).replace(".", "")
	board_as_string = "".join(board_as_string.split())
	white_pieces = sum([1 if x.isupper() else 0 for x in board_as_string])
	black_pieces = sum([1 if x.islower() else 0 for x in board_as_string])
	return white_pieces, black_pieces

def alter_result(result: str) -> int:
	if result == "1-0": return +1
	elif result == "1/2-1/2": return 0
	elif result == "0-1": return -1
	return None

def board_as_matrix(board: chess.Board):
	empty_space = ord('.')
	matrix = [[ord(y)-empty_space for y in x.split(" ")] for x in str(board).split("\n")]
	return np.asarray(matrix)

def get_piece_count_after_move(_board: chess.Board, _move: chess.Move):
	_board_copy = copy(_board)
	_board_copy.push(_move)
	return _board_copy

def get_all_piece_counts(_board: chess.Board):
	return [
		{
			"move_as_uci": x.uci(),
			"board_after_move": get_piece_count_after_move(_board, x),
		}
		for x in _board.legal_moves
	]

class Player:
	def __init__(self):
		pass

	def choose_move(self, current_board: chess.Board, list_of_moves: List[chess.Move]):
		return choice(list_of_moves)

from pandas import DataFrame
grand_master = DataFrame()

for iteration in range(10000):
	board = chess.Board()
	white, black = Player(), Player()

	boards = []

	for t in range(1000):
		moves = [b for b in board.legal_moves]
		if len(moves) == 0:
			# print("The {} player cannot perform any moves!".format("white" if board.turn else "black"))
			result = alter_result(board.result())
			print("Result: {}".format(result))
			break

		turn = ("white" if board.turn else "black").upper()

		if turn == "WHITE":
			move = white.choose_move(board, list(board.legal_moves))
		elif turn == "BLACK":
			move = black.choose_move(board, list(board.legal_moves))

		# print("Performing {} move:".format(print_move(move)))
		# print("Turn is {}.".format(turn))

		g = board.is_game_over(claim_draw=False)
		if g is True:
			g = check_state(board)

		# print("Game is {}.".format("on-going" if g is False else "ended due to {}".format(g)))
		if g is not False:
			result = alter_result(board.result())
			print("Result: {}".format(result))
			break

		board.push(move)

		bam = board_as_matrix(board).reshape((64,))
		# assert np.equal(bam.reshape((8, 8,)), board_as_matrix(board)).all()

		boards.append(bam)

		# print(board)
		# print("\n")

	df = DataFrame(data=np.array(boards), columns=["p" + str(x) for x in range(64)])
	df['result'] = result

	grand_master = grand_master.append(df, ignore_index=True)

import random
import string
s = "".join([random.choice(string.ascii_letters) for _ in range(10)])
grand_master.to_csv("csv/grand_master_random_{}.csv".format(s.lower()), index=False)



