#!/usr/bin/env python
import sys, chess
from gui import ChessGUI

def play(args):

    # Initialize a new chess board.
    board = chess.Board()

    # Get the player's preferred starting color.
    player_color = ''
    while player_color is not 'l' and player_color is not 'd':
        player_color = raw_input('Would you like to play as light or dark [ld]? ')


    # If the player wants to be dark, flip the board.
    if player_color is 'd':
        board = chess.Board(board.board_fen()[::-1] + ' b KQkq - 1 0')

    # Decide whether the player or AI goes first.
    player_turn = player_color == 'l'

    # Initialize a GUI run its main loop. All game logic is inside the ChessGUI
    # class.
    gui = ChessGUI(board, player_turn)
    gui.drawBoard()
    gui.run()

if __name__ == '__main__':
    play(sys.argv)
