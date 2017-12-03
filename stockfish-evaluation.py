import chess.pgn
import chess.uci

pgnfilename = "./pgn/adams_kasparov_2005.pgn"

with open(pgnfilename) as f:
	game = chess.pgn.read_game(f)

game = game.end()
board = game.board()

print(board)

handler = chess.uci.InfoHandler()
sf_engine_path = '/home/khaled/repositories/Stockfish/src/stockfish'
engine = chess.uci.popen_engine(sf_engine_path)
engine.info_handlers.append(handler)

engine.position(board)

evaltime = 10 * 1000  # so 5 seconds
evaluation = engine.go(movetime=evaltime)

# print best move, evaluation and mainline:
print('best move: ', board.san(evaluation[0]))
print('evaluation value: ', handler.info["score"][1].cp / 100.0)
print('Corresponding line: ', board.variation_san(handler.info["pv"][1]))
