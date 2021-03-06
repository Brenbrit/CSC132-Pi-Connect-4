#  _____ _    _____                            _     _  _
# |  __ (_)  / ____|                          | |   | || |
# | |__) |  | |     ___  _ __  _ __   ___  ___| |_  | || |_
# |  ___/ | | |    / _ \| '_ \| '_ \ / _ \/ __| __| |__   _|
# | |   | | | |___| (_) | | | | | | |  __/ (__| |_     | |
# |_|   |_|  \_____\___/|_| |_|_| |_|\___|\___|\__|    |_|

# written by The Muffin Men for CSC 132
# Presented on May 11, 2021
# Big thank you to Keith Galli for his tutorial on writing the UI with Pygame.
# His series was used heavily in the beginning of the project to write the
# base game and UI. His work is provided under the MIT license, which means
# it is free to use The full source code of his can be found at
# https://github.com/KeithGalli/Connect4-Python.

import numpy as np
import pygame
import socket
import sys
import time

# Board settings
ROW_COUNT = 6
COLUMN_COUNT = 7

# Piece settings. Best not to change.
PLAYER_1_PIECE = 1
PLAYER_2_PIECE = 2

# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

# Spacing of GUI features
SQUARE_SIZE = 68
CIRCLE_RADIUS = (SQUARE_SIZE // 2) - 4
LABEL_POS = (40, 10)
TEXT_SIZE = 48
TEXT_FONT = "monospace"

# The pins connected to the button and LED
BUTTON_PIN = 24
LED_PIN = 23
# How many milliseconds to wait in-between GPIO checks.
GPIO_CHECK_DELAY = 10

# Server settings
SERVER_IP = "104.238.145.167"
PORT = 12345
CODEC = "ascii"

# How long to wait for various notifications (ms)
START_TEXT_TIME = 1000

# Argument processing. If none are passed, default to red piece and testing
# mode.
MY_PIECE = 1
KIOSK_MODE = False
if len(sys.argv) == 1:
    print("No arguments passed.")
    print("Defaulting to piece 1: red.")
    print("Defaulting to testing mode.")
    print("Script is properly run: \"python3 connect-4.py <piece> <kiosk>\"")
elif len(sys.argv) == 2:
    MY_PIECE = int(sys.argv[1])
    print("Defaulting to testing mode.")
else:
    MY_PIECE = int(sys.argv[1])
    if sys.argv[2].lower() == "kiosk":
        print("Running in kiosk mode.")
        KIOSK_MODE = True
        import RPi.GPIO as GPIO
    else:
        print("Running in testing mode.")

# Some derivative variables
# 3 - MY_PIECE only works if the pieces are 1 and 2.
OPP_PIECE = 3 - MY_PIECE
# Our color.
if MY_PIECE == 1:
    MY_COLOR = RED
    OPP_COLOR = YELLOW
else:
    MY_COLOR = YELLOW
    OPP_COLOR = RED


# Function which creates an empty "board" - a 6x7 numpy matrix.
def create_board():
    # Make a numpy matrix with 6 rows and 7 columns. Each item is 0 - no chip.
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

# Function which changes the value of a given board at a given row and column
# to a given value.
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Function to determine if a chip can be dropped in the given column.
def is_valid_location(board, col):
    # The top row has an index of ROW_COUNT - 1. If the top row at a given
    # column has a value of 0, then the chip can be dropped there.
    return board[ROW_COUNT - 1][col] == 0

# The below function is run when a user selects a column to drop a chip into.
# It returns the lowest row available. In real life, gravity does this.
def get_next_open_row(board, col):
    for row in range(ROW_COUNT):
        if board[row][col] == 0:
            return row

# A function which takes in a board and a piece. Returns True if piece has won
# the game, or False if piece has not won the game.
def winning_move(board, piece):
    # Check horizontal locations for wins. Since we are only checking for
    # horizontal wins, we don't need or want to start checking from the
    # spaces in the rightmost 3 columns of the board since we will overstep
    # the bounds of the board in doing so.
    for c in range(COLUMN_COUNT - 3):
        # For hozontal wins, we must check all the rows.
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertical locations for wins. This is very similar to the horizontal
    # check above.
    for c in range(COLUMN_COUNT):
        # We don't want or need to check all the rows.
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positively sloped diagonals for wins. This only needs to be done for
    # row 0 to ROW_COUNT-3, and column 0 to COLUMN_COUNT - 3. Anything more
    # would result in us trying to access a variable outside the range of the
    # board.
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check negatively sloped diagonals for wins. Similar to the above loop,
    # but we only need to check from row 3 to ROW_COUNT, and column 0 to
    # COLUMN_COUNT - 3.
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# Change the orientation of the board so it looks nice when printing,
# then print the board.
def print_board(board):
    # flip the board over the 0 axis (x)
    print(np.flip(board, 0))

# Fill the top row of the screen (where text is placed) with a
# BLACK rectangle.
def draw_top_row():
    pygame.draw.rect(screen, BLACK, (0, 0, screen_width, SQUARE_SIZE))

# Close down Pygame and then exit the program.
def exit_all():
    pygame.display.quit()
    pygame.quit()
    sys.exit()

# The function which translates the numpy matrix into a pretty picture for
# us to look at!
def draw_board(board):
    # We need to flip the board to make x=0,y=0 the bottom-right.
    board = np.flip(board, 0)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            # Pygame's draw.rect() func needs a rectangle as its third argument.
            # Rectangles have an X value, a Y value, an X size, and a Y size.
            # There is also a 4th available parameter, but we don't need to
            # use it - it is for the outline of the rectangle, which we don't
            # want.
            rect = (c*SQUARE_SIZE, (r+1)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, BLUE, rect)

            # Pygame's circles need a position and a radius.
            circle_position = ((c*SQUARE_SIZE) + (SQUARE_SIZE // 2), ((r+1)*SQUARE_SIZE) + (SQUARE_SIZE // 2))
            # We default to a black circle - no piece. If there is actually a
            # piece at board[r][c] though, change that color.
            circle_color = BLACK
            if board[r][c] == PLAYER_1_PIECE:
                circle_color = RED
            elif board[r][c] == PLAYER_2_PIECE:
                circle_color = YELLOW

            pygame.draw.circle(screen, circle_color, circle_position, CIRCLE_RADIUS)

    # This needs to be called to actually change what is shown on the screen.
    pygame.display.update()

# Check for important events (like the mouse button being clicked, the GPIO
# button being pressed, or the QUIT signal). This is run after the chip changes
# position over the top of the board.
def important_event_happened():
    for event in pygame.event.get():

        # If the user has quit the game, terminate immediately.
        if event.type == pygame.QUIT:
            exit_all()

        # Also exit if the user pressed Q.
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                exit_all()
            if event.key == pygame.K_SPACE:
                return True

        # If the user clicked the mouse or button, return true.
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return True

    # We didn't find anything worth writing home about. Return False.
    return False

# This function creates the initial connection to the server.
def init_networking(server_ip, port):
    try:
        # Bind to the host and port
        server_sock.connect((server_ip, port))
    except Exception as e:
        print("Failed to connect to server. Exception:")
        print(e)
        return None
    print("Connected to server, response: ", end='')
    print(get_next_data(server_sock))

    global socket_connected
    socket_connected = True

# Set up all the GPIO stuff. Lots of things that don't need changing here.
def setupGPIO():
    # Set pin mode
    GPIO.setmode(GPIO.BCM)

    # Set up our one input pin.
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    # Set up our one LED pin.
    GPIO.setup(LED_PIN, GPIO.OUT)

# Is the GPIO button being pressed right now?
def read_button():
    return GPIO.input(BUTTON_PIN)

# Get the next 2048 bytes (overkill) from a socket
def get_next_data(sock):
    data = sock.recv(2048).decode(CODEC)
    # print("Received data: \"{}\"".format(data))
    return data

# Send data to the server
def send_data(data):
    # print("Sent data: \"{}\"".format(data))
    server_sock.send(data.encode(CODEC))

# Query the server for the opponent's move. If the other player hasn't moved
# yet, then wait a second and try again.
def get_move(turn_num):
    print("Waiting for opponent to move ", end='')
    seconds_waited = 0
    response = ''
    while True:
        send_data("waiting {}".format(turn_num))
        response = get_next_data(server_sock)
        if response == "wait":
            waiting_move_text(seconds_waited)
            time.sleep(1)
            seconds_waited += 1
            print('.', end='')
        elif len(response) == 1:
            break
    print("\nOpponent played on col {}!".format(response))
    return(int(response))

# Generic function to show text on the top of the screen. Intended to be
# called by functions other than play_game().
def show_text(text, color):
    # Remove anything that was on the screen before
    draw_top_row()
    # Create the label and display it
    label = text_font.render(text, 1, color)
    # Display the label
    screen.blit(label, LABEL_POS)
    pygame.display.update()

# Function which shows some text at the top of the screen to indicate that the
# other player has not yet connected.
def no_opponent_text(seconds_waited):
    show_text(" Matching " + "." * (seconds_waited % 4), MY_COLOR)

# Function which makes the Opponent playing... text
def waiting_move_text(seconds_waited):
    show_text(" Waiting " + "." * (seconds_waited % 4), MY_COLOR)

# Show text at the top of the screen to indicate that the game is starting.
# The one argument indicates the amount of time to wait with this text at the top.
def show_game_start_text():
    # Show the text.
    show_text("Starting game!", MY_COLOR)

    # Wait for duration seconds
    pygame.time.wait(START_TEXT_TIME)

    # Remove the starting text
    draw_top_row()
    pygame.display.update()

# Show text at the beginning of the game before the server connection
# is established.
def show_startup_screen():
    show_text("Press to play!", MY_COLOR)
    while True:
        if KIOSK_MODE:
            GPIO.output(LED_PIN, GPIO.HIGH)
        if wait_for_event(500):
            break
        if KIOSK_MODE:
            GPIO.output(LED_PIN, GPIO.LOW)
        if wait_for_event(500):
            break
    if KIOSK_MODE:
        GPIO.output(LED_PIN, GPIO.LOW)

# Wait a maximum time for some interesting event (mouse click, button press).
def wait_for_event(millis_to_wait):
    if KIOSK_MODE:
        start_millis = time.time() * 1000
        while time.time() * 1000 < (start_millis + millis_to_wait):
            if read_button():
                return True
            else:
                pygame.time.wait(GPIO_CHECK_DELAY)
    else:
        pygame.time.wait(millis_to_wait)
    return important_event_happened()


def play_game():

    # Game variables!

    # the game board
    global board
    # The game's state. The game is not over by default, and the game has not
    # started by default.
    game_over = False
    game_started = False
    # Which turn is it? This increments each time someone places a piece down.
    turn = 1
    # which spot over the board is the piece hovering? Changes many times
    # per turn.
    piece_col = 0
    # Is the piece moving right or left? 1 for right, -1 for left.
    piece_direction = 1

    # Show the board on the screen.
    draw_board(board)
    # Wait for a button press before starting.
    show_startup_screen()
    # The board. A numpy matrix.
    board = create_board()
    pygame.display.update()

    # Start the server connection if needed.
    if not socket_connected:
        init_networking(SERVER_IP, PORT)

    while not game_over:

        # Draw the board as it currently is.
        draw_board(board)

        # Clear the Pygame events.
        pygame.event.clear()

        if not game_started:
            # send the server our piece
            send_data("p={}".format(MY_PIECE))
            print("Sent piece to server.")

            # Check if other player has connected
            response = get_next_data(server_sock)
            if response == "wait":
                # Other player hasn't connected. Let's wait.
                print("Waiting for other player to connect.", end='')
                seconds_waited = 0
                while True:
                    time.sleep(1)
                    seconds_waited += 1
                    send_data("waited")
                    if get_next_data(server_sock) == "start":
                        print("\nOpponent found! Starting game.")
                        game_started = True
                        show_game_start_text()
                        break
                    no_opponent_text(seconds_waited)

            # If the initial response is "start", then the other player has
            # already connected.
            elif response == "start":
                print("Opponent found! Starting game.")
                game_started = True
                show_game_start_text()

        # If we get to turn 43, then the game is a tie. Tell the user this,
        # and then break.
        if turn == 43:
            show_text("    Tie!", MY_COLOR)
            game_over = True
            break

        # If we get here, the other player has connected.

        if 2 - (turn % 2) == MY_PIECE:
            # It's player 1's turn! Start moving the piece over the top of the
            # board.

            # Clear any events from the queue. This is done so that we don't
            # count clicks made while the other player was playing.
            pygame.event.clear()

            # How long should we wait before changing the position of the piece? (ms)
            # This time starts off at 500ms, then goes down by 25ms for each
            # turn until it reaches 100ms. It then stays there fore the rest
            # of the game.
            if turn <= 17:
                position_change_delay = 500 - (25 * (turn - 1))
            else:
                position_change_delay = 100

            is_our_turn = True
            while is_our_turn:

                # Remove the previous piece's circle on the screen.
                draw_top_row()

                # Turn on the LED if we're in kiosk mode.
                if KIOSK_MODE:
                    GPIO.output(LED_PIN, GPIO.HIGH)

                # Determine the piece's position and draw it.
                circle_pos = ((piece_col * SQUARE_SIZE) + (SQUARE_SIZE // 2), SQUARE_SIZE // 2)
                pygame.draw.circle(screen, MY_COLOR, circle_pos, CIRCLE_RADIUS)
                pygame.display.update()

                # If, in the last position_change_delay millis, the mouse was
                # clicked or the GPIO was pressed, try to place the piece.
                if wait_for_event(position_change_delay):

                    # Looks like the user clicked the mouse or the big red
                    # button! See if we can execute that move.
                    if is_valid_location(board, piece_col):

                        # Valid move! Send the turn to the server.
                        while True:
                            send_data("turn {}:{}".format(turn, piece_col))
                            if get_next_data(server_sock) == "affirm":
                                print("Turn {}:{} received by server.".format(turn, piece_col))
                                if KIOSK_MODE:
                                    GPIO.output(LED_PIN, GPIO.LOW)
                                break


                        # Place the piece.
                        row = get_next_open_row(board, piece_col)
                        drop_piece(board, row, piece_col, MY_PIECE)
                        # Draw the top row to get rid of the piece that was
                        # just there.
                        draw_top_row()
                        draw_board(board)
                        pygame.display.update()
                        is_our_turn = False
                        turn += 1

                        # Check to see if the game is over.
                        if winning_move(board, MY_PIECE):
                            # It is!
                            # Make the label which will be displayed.
                            show_text("Player {} wins!".format(MY_PIECE), MY_COLOR)
                            game_over = True


                # If we get here, nothing interesting happened since we started
                # wait()ing. Move the piece to the next column.
                else:
                    if piece_col == 6 and piece_direction == 1:
                        # We reached the right side of the board.
                        # Move to col 5 and change direction.
                        piece_direction = -1
                        piece_col = 5
                    elif piece_col == 0 and piece_direction == -1:
                        # We reached the left side of the board.
                        # Move to col 1 and change direction.
                        piece_direction = 1
                        piece_col = 1
                    else:
                        piece_col += piece_direction

        else:
            # Looks like it's not our turn. Get (read: wait for) the opponent's
            # move, then do the normal operations on it. Assuming the other
            # player isn't cheating in some way, this will be a guaranteed
            # good move.
            opp_move = get_move(turn)
            row = get_next_open_row(board, opp_move)
            drop_piece(board, row, opp_move, OPP_PIECE)
            draw_board(board)
            pygame.display.update()

            # Check if the other player has just won.
            if winning_move(board, OPP_PIECE):
                # They did! gg!
                show_text("Player {} wins!".format(OPP_PIECE), OPP_COLOR)
                game_over = True
                # Tell the server that the game is over.
                while True:
                    print("Telling the server that the game is over.")
                    send_data("gameover")
                    if get_next_data(server_sock) == "affirm":
                        break

            # Increment the turn counter.
            turn += 1



    # Looks like the game just ended!
    # Let's wait a few seconds to let this sink in.
    pygame.time.wait(5000)


#
#
#   MAIN CODE!
#
#

# initialize pygame
pygame.init()

# FYI: The Raspi screens are 800x480 pixels.

# Determine screen width and height. The height gets an extra square added
# for the space that holds the text and the piece to be dropped.
screen_width = COLUMN_COUNT * SQUARE_SIZE
screen_height = (ROW_COUNT + 1) * SQUARE_SIZE
screen_size = (screen_width, screen_height)

# Depending on whether or not we're in kiosk mode, activate fullscreen.
if KIOSK_MODE:
    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(screen_size)

text_font = pygame.font.SysFont(TEXT_FONT, TEXT_SIZE)

# If we're in kiosk mode, set up GPIO.
if KIOSK_MODE:
    setupGPIO()

# Start up networking! This doesn't actually connect to anything yet (that is
# done where the user can see). The two arguments here are really just
# boilerplate to us. We don't need to change them.
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_connected = False

board = create_board()

while True:

    # Clear any events from the queue. This prevents people from placing chips
    # in-between games.
    pygame.event.clear()

    # start the game! Lessss gooo!
    play_game()

server_sock.close()
