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

# Which piece are we? This will likely be 1 or 2.
# This is passed in with the runner scipt.
MY_PIECE = 1
if len(sys.argv) < 2:
    print("No arguments passed. Defaulting to piece 1: red.")
else:
    MY_PIECE = int(sys.argv[1])

# Size of each square on the screen (in pixels)
SQUARE_SIZE = 100
CIRCLE_RADIUS = (SQUARE_SIZE // 2) - 5

# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

# Server settings
SERVER_IP = "104.238.145.167"
PORT = 12345
CODEC = "ascii"

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

def draw_top_row():
    pygame.draw.rect(screen, BLACK, (0, 0, screen_width, SQUARE_SIZE))

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
            sys.exit()

        # If the user clicked the mouse or button, return true.
        if event.type == pygame.MOUSEBUTTONDOWN:
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
    

# Get the next 2048 bytes (overkill) from a socket
def get_next_data(sock):
    data = sock.recv(2048).decode(CODEC)
    # print("Received data: \"{}\"".format(data))
    return data

# Send data to the server
def send_data(data):
    server_sock.send(data.encode(CODEC))

# Query the server for the opponent's move. If the other player hasn't moved
# yet, then wait a second and try again.
def get_move(turn_num):
    print("Waiting for opponent to move ", end='')
    response = ''
    while True:
        send_data("waiting {}".format(turn_num))
        response = get_next_data(server_sock)
        if response == "wait":
            time.sleep(1)
            print('.', end='')
        elif len(response) == 1:
            break
    print("\nOpponent played on col {}!".format(response))
    return(int(response))

def play_game():

    # Game variables!
    # The board. A numpy matrix.
    board = create_board()
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

    draw_board(board)
    pygame.display.update()

    # Start the server connection if needed.
    if not socket_connected:
        init_networking(SERVER_IP, PORT)
    
    while not game_over:

        # Draw the board as it currently is.
        draw_board(board)

        # send the server our piece
        send_data("p={}".format(MY_PIECE))

        # Check if other player has connected
        if get_next_data(server_sock) == "wait" and not game_started:
            # Other player hasn't connected. Let's wait.
            print("Waiting for other player to connect ", end='')
            while True:
                time.sleep(1)
                print('.', end='')
                send_data("waited")
                if get_next_data(server_sock) == "start":
                    print("\nOpponent found!")
                    game_started = True
                    break

        # If we get here, the other player has connected.
        print("Starting game!")

        if 2 - (turn % 2) == MY_PIECE:
            # It's player 1's turn! Start moving the piece over the top of the
            # board.
            
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

                # Determine the piece's position and draw it.
                circle_pos = ((piece_col * SQUARE_SIZE) + (SQUARE_SIZE // 2), SQUARE_SIZE // 2)
                pygame.draw.circle(screen, MY_COLOR, circle_pos, CIRCLE_RADIUS)
                pygame.display.update()

                # Wait some time.
                pygame.time.wait(position_change_delay)
                # Check for important events
                if important_event_happened():

                    # Looks like the user clicked the mouse or the big red
                    # button! See if we can execute that move.
                    if is_valid_location(board, piece_col):
                        
                        # Valid move! Send the turn to the server.
                        while True:
                            send_data("turn {}:{}".format(turn, piece_col))
                            if get_next_data(server_sock) == "affirm":
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
                            label = text_font.render("Player {} wins!".format(MY_PIECE), 1, MY_COLOR)
                            # display the label.
                            screen.blit(label, (40, 10))
                            pygame.display.update()
                            game_over = True

                            # Tell the server to reset.
                            send_data("reset")

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
            pygame.display.update()

            # Check if the other player has just won.
            if winning_move(board, OPP_PIECE):
                # They did! gg!
                label = text_font.render("Player {} wins!".format(OPP_PIECE), 1, OPP_COLOR)
                # Display the label.
                screen.blit(label, (40, 10))
                pygame.display.update()
                game_over = True

            # Increment the turn counter.
            turn += 1

    # Looks like the game just ended!
    # Let's wait a few seconds to let this sink in.
    pygame.time.wait(5000)
    

# initialize pygame
pygame.init()
# Determine screen width and height. The height gets an extra square added
# for the space that holds the text and the piece to be dropped.
screen_width = COLUMN_COUNT * SQUARE_SIZE
screen_height = (ROW_COUNT + 1) * SQUARE_SIZE
screen_size = (screen_width, screen_height)

screen = pygame.display.set_mode(screen_size)

text_font = pygame.font.SysFont("monospace", 75)

# Start up networking! This doesn't actually connect to anything yet (that is
# done where the user can see). The two arguments here are really just
# boilerplate to us. We don't need to change them.
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_connected = False

while True:

    # Clear any events from the queue. This prevents people from placing chips
    # in-between games.
    pygame.event.clear()

    # start the game! Lessss gooo!
    play_game()

server_sock.close()
