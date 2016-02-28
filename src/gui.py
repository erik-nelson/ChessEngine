#!/usr/bin/env python
from PIL import Image, ImageDraw
import StringIO
from math import floor
import chess, chess.uci
import time
import threading
import pygtk
import gtk
import subprocess

class ChessGUI:

    def __init__(self, board, player_turn):
        # Set up the GUI window.
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Chess")
        self.window.connect("destroy", self.destroy)

        # Set up button press callback.
        self.window.connect("button_press_event", self.press)
        self.window.connect("button_release_event", self.release)
        self.window.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.show_all()
        self.board_widget = gtk.Image()
        self.window.add(self.board_widget)

        # Initialize local variables.
        self.selected_square = None
        self.board = board
        self.ai_turn = not player_turn
        self.player_finished = time.time()
        self.ai_move_time_msec = 1000
        self.engine = chess.uci.popen_engine("../engine/stockfish")
        self.engine.uci()

    # Start GUI.
    def run(self):
        # Fixed frequency timer checking whether it's the AI's move.
        gtk.timeout_add(10, self.moveAI)

        # Start the main GTK thread.
        gtk.main()

    # Called on ctrl+C or window close.
    def destroy(self, widget, data=None):
        gtk.main_quit()
        return False

    # Handle left mouse button press.
    def press(self, widget, event):
        if event.button == 1:
            square = self.imageCoordsToSquareIndex(event.x, event.y)
            if self.board.piece_at(square) is not None:
                self.selected_square = square
        return True

    # Handle left mouse button release.
    def release(self, widget, event):
        if event.button == 1:
            if self.selected_square is not None:
                drop_square = self.imageCoordsToSquareIndex(event.x, event.y)

                # Build a move from the source square to the drop square.
                move = chess.Move(self.selected_square, drop_square)
                if self.board.is_legal(move):
                    self.board.push_uci(move.uci())
                    self.drawBoard()
                    print "Player's Move :  " + move.uci()

                    # If the game is finished, go to the game over screen.
                    if self.board.is_game_over():
                        self.gameOver()

                    # Set a flag notifying that it is the AI's turn.
                    self.ai_turn = True
                    self.player_finished = time.time()

            self.selected_square = None
        return True

    # Game over menu.
    def gameOver(self):
        print "Game over!"
        self.engine.quit()

    # Move the AI using the UCI Stockfish engine
    def moveAI(self):
        # Let the chess engine make a move.
        dt = time.time() - self.player_finished
        if self.ai_turn and dt > 0.5:
            self.engine.position(self.board)
            ai_move = self.engine.go(movetime = self.ai_move_time_msec)
            self.board.push_uci(ai_move.bestmove.uci())
            self.drawBoard()
            print "AI's move     :  " + ai_move.bestmove.uci()

            # If the game is finished, go to the game over screen.
            if self.board.is_game_over():
                self.gameOver()

            self.ai_turn = False

        return True

    # Convert a PIL image into a GTK pixel buffer.
    def imageToPixbuf(self, image):
        f = StringIO.StringIO()
        image.save(f, "png")
        contents = f.getvalue()
        f.close()
        loader = gtk.gdk.PixbufLoader("png")
        loader.write(contents, len(contents))
        gtk_image = loader.get_pixbuf()
        loader.close()
        return gtk_image

    # Convert from square index to image coordinates.
    def squareIndexToImageCoords(self, i):
        rank_ind = chess.rank_index(i)
        file_ind = chess.file_index(i)

        row = 448 - (rank_ind * 512 / 8)
        col = file_ind * 512 / 8
        return (col, row)

    # Convert from image coordinates to square index.
    def imageCoordsToSquareIndex(self, x, y):
        rank_ind = int((512 - y) / 64)
        file_ind = int(x / 64)
        return chess.square(file_ind, rank_ind)


    # Given a board configuration, load images of the board and pieces, and draw
    # in the GUI.
    def drawBoard(self):
        img_dir = '../img/'

        # Load the chess board image.
        board_image = Image.open(img_dir + 'board.png')

        # Function to paste piece images onto the board.
        def addToBoardImage(board_image, piece_image, squares):
            for square in range(len(squares)):
                offset = self.squareIndexToImageCoords(squares[square])
                board_image.paste(piece_image, offset, mask=piece_image)

        # Light pawns
        lp = list(self.board.pieces(1, chess.WHITE))
        lp_image = Image.open(img_dir + 'lightp.png')
        addToBoardImage(board_image, lp_image, lp)

        # Light knights
        ln = list(self.board.pieces(2, chess.WHITE))
        ln_image = Image.open(img_dir + 'lightn.png')
        addToBoardImage(board_image, ln_image, ln)

        # Light bishops
        lb = list(self.board.pieces(3, chess.WHITE))
        lb_image = Image.open(img_dir + 'lightb.png')
        addToBoardImage(board_image, lb_image, lb)

        # Light rooks
        lr = list(self.board.pieces(4, chess.WHITE))
        lr_image = Image.open(img_dir + 'lightr.png')
        addToBoardImage(board_image, lr_image, lr)

        # Light queen
        lq = list(self.board.pieces(5, chess.WHITE))
        lq_image = Image.open(img_dir + 'lightq.png')
        addToBoardImage(board_image, lq_image, lq)

        # Light king
        lk = list(self.board.pieces(6, chess.WHITE))
        lk_image = Image.open(img_dir + 'lightk.png')
        addToBoardImage(board_image, lk_image, lk)

        # Dark pawns
        dp = list(self.board.pieces(1, chess.BLACK))
        dp_image = Image.open(img_dir + 'darkp.png')
        addToBoardImage(board_image, dp_image, dp)

        # Dark knights
        dn = list(self.board.pieces(2, chess.BLACK))
        dn_image = Image.open(img_dir + 'darkn.png')
        addToBoardImage(board_image, dn_image, dn)

        # Dark bishops
        db = list(self.board.pieces(3, chess.BLACK))
        db_image = Image.open(img_dir + 'darkb.png')
        addToBoardImage(board_image, db_image, db)

        # Dark rooks
        dr = list(self.board.pieces(4, chess.BLACK))
        dr_image = Image.open(img_dir + 'darkr.png')
        addToBoardImage(board_image, dr_image, dr)

        # Dark queen
        dq = list(self.board.pieces(5, chess.BLACK))
        dq_image = Image.open(img_dir + 'darkq.png')
        addToBoardImage(board_image, dq_image, dq)

        # Dark king
        dk = list(self.board.pieces(6, chess.BLACK))
        dk_image = Image.open(img_dir + 'darkk.png')
        addToBoardImage(board_image, dk_image, dk)

        # Draw the board and pieces.
        self.window.remove(self.board_widget)
        self.board_widget = gtk.Image()
        self.board_widget.set_from_pixbuf(self.imageToPixbuf(board_image))
        self.board_widget.show()
        self.window.add(self.board_widget)
