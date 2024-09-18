from stockfish import Stockfish
import argparse
import io
import chess.pgn
stockfish = Stockfish(path = "C:\\stockfish\\stockfish-windows-x86-64-avx2.exe")

stockfish.update_engine_parameters({
    "Hash": 8192,
    "Threads": 10
    })

def file_to_str(filename):
    with open(filename, 'r') as file:
        data = file.read().replace('\n', ' ')
        startpos = data.find("1. ")
        toreturn = data[startpos:]
    file.close()
    return toreturn

def update_board(game_str):
    game = chess.pgn.read_game(io.StringIO(game_str))
    board = game.board()
    uci_moves = []
    for move in game.mainline_moves():
        uci_moves.append(str(board.uci(move)))
    return uci_moves

def calculate_accuracy(uci_move_arr, side):
    stockfish.set_position([])
    running_penalty = 0
    moves_played = 0

    start_index = 0 if side == 'w' else 1
    step = 2
    
    for i in range(start_index, len(uci_move_arr), step):
        stockfish.make_moves_from_current_position([uci_move_arr[i]])
        player_move = uci_move_arr[i]

        top_moves = stockfish.get_top_moves(3)
        best_centipawn = top_moves[0]['Centipawn']

        player_centipawn = 350
        for move_info in top_moves:
            if move_info['Move'] == player_move:
                player_centipawn = move_info['Centipawn']
                break

        running_penalty += player_centipawn - best_centipawn
        moves_played += 1

        if i + 1 < len(uci_move_arr):
            stockfish.make_moves_from_current_position([uci_move_arr[i + 1]])

    scaling_factor = 15
    accuracy = min(99.7, max(0, 100 - (running_penalty/ (moves_played * scaling_factor))))
                   
    print(f"Final position:\n{stockfish.get_board_visual()}Final accuracy: {accuracy}%")
    return accuracy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("side")
    args = parser.parse_args()

    if args.side != 'w' and args.side != 'b':
        print("Please designate which side you'd like to compute the accuracy for -- 'w' or white or 'b' for black")
        raise Exception("Incorrect side specification")

    game_str = file_to_str(args.filename)
    uci_move_arr = update_board(game_str)
    calculate_accuracy(uci_move_arr, args.side)

if __name__ == "__main__":
    main()