from copy import copy
import random
import string
from typing import Tuple, List
import numpy as np
import chess
import chess.uci
from random import choice

from tqdm import tqdm


def print_move (m: chess.Move) -> str:
	return "{} -> {}".format(m.from_square, m.to_square)


def check_state (_board: chess.Board):
	states = {
		"checkmate"                : _board.is_checkmate(),
		"stalemate"                : _board.is_stalemate(),
		"insufficient material"    : _board.is_insufficient_material(),
		"the seventyfive-move rule": _board.is_seventyfive_moves(),
		"fivefold repetition"      : _board.is_fivefold_repetition(),
		"variant win"              : _board.is_variant_win(),
		"variant loss"             : _board.is_variant_loss(),
		"variant draw"             : _board.is_variant_draw(),
		"variant end"              : _board.is_variant_end(),
	}

	for i, j in states.items():
		if j is True:
			return i

	return None


def get_piece_count (_board: chess.Board) -> Tuple[int, int]:
	board_as_string = str(_board).replace(".", "")
	board_as_string = "".join(board_as_string.split())
	white_pieces = sum([1 if x.isupper() else 0 for x in board_as_string])
	black_pieces = sum([1 if x.islower() else 0 for x in board_as_string])
	return white_pieces, black_pieces


def alter_result (result: str) -> int:
	if result == "1-0":
		return +1
	elif result == "1/2-1/2":
		return 0
	elif result == "0-1":
		return -1
	return None


def board_as_matrix (board: chess.Board):
	empty_space = ord('.')
	matrix = [[ord(y) - empty_space for y in x.split(" ")] for x in str(board).split("\n")]
	return np.asarray(matrix).reshape((1, 64,))


def get_piece_count_after_move (_board: chess.Board, _move: chess.Move):
	_board_copy = copy(_board)
	_board_copy.push(_move)
	return _board_copy


def get_all_piece_counts (_board: chess.Board):
	return [
		{
			"move_as_uci"     : x.uci(),
			"board_after_move": get_piece_count_after_move(_board, x),
		}
		for x in _board.legal_moves
	]


class StockfishPlayer:
	def __init__ (self, evaluation_time: float, turn: int):
		assert turn in [-1, 1]
		self.turn = turn
		self.eval_time = evaluation_time
		sf_engine_path = '/home/khaled/repositories/Stockfish/src/stockfish'
		self.handler = chess.uci.InfoHandler()
		self.engine = chess.uci.popen_engine(sf_engine_path)
		self.engine.info_handlers.append(self.handler)

	def choose_move (self, current_board: chess.Board) -> Tuple[chess.Move, float]:
		self.engine.position(current_board)
		evaluation = self.engine.go(movetime=self.eval_time)
		try:
			evaluation_value = self.handler.info["score"][1].cp / 100.0 * self.turn
		except:
			evaluation_value = None
		return evaluation[0], evaluation_value


class RandomPlayer:
	def __init__ (self):
		pass

	def choose_move (self, current_board: chess.Board) -> Tuple[chess.Move, float]:
		return choice(list(current_board.legal_moves)), None


from pandas import DataFrame

grand_master = DataFrame()


board = chess.Board()
white, black = StockfishPlayer(5 * 1000, turn=1), StockfishPlayer(5 * 1000, turn=-1)

boards = []

for t in range(1000):
	moves = [b for b in board.legal_moves]
	if len(moves) == 0:
		result = alter_result(board.result())
		print("Result: {}".format(result))
		break

	turn = ("white" if board.turn else "black").upper()

	if turn == "WHITE":
		print("White's turn")
		move, evaluation = white.choose_move(board)
	elif turn == "BLACK":
		print("Black's turn")
		move, evaluation = black.choose_move(board)
	
	print(move, evaluation)

	g = board.is_game_over(claim_draw=False)
	if g is True:
		g = check_state(board)

	if g is not False:
		result = alter_result(board.result())
		print("Result: {}".format(result))
		break

	board.push(move)
	print(board)
	print("\n")

	boards.append(board_as_matrix(board))

