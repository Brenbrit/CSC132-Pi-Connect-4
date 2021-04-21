import numpy as np
import pygame
import sys

# Board settings
ROW_COUNT = 6
COLUMN_COUNT = 7

# Piece settings. Best not to change.
PLAYER_1_PIECE = 1
PLAYER_2_PIECE = 2

# Size of each square on the screen (in pixels)
SQUARE_SIZE = 100
CIRCLE_RADIUS = (SQUARE_SIZE // 2) - 5

# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)

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

def draw_board(board):
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
            pygame.draw.circle(screen, BLACK, circle_position, CIRCLE_RADIUS)

board = create_board()
print_board(board)
game_over = False
turn = 1

# initialize pygame
pygame.init()
# Determine screen width and height. The height gets an extra square added
# for the space that holds the text and the piece to be dropped.
screen_width = COLUMN_COUNT * SQUARE_SIZE
screen_height = (ROW_COUNT + 1) * SQUARE_SIZE
screen_size = (screen_width, screen_height)

screen = pygame.display.set_mode(screen_size)
draw_board(board)
pygame.display.update()

while not game_over:

    for event in pygame.event.get():

        # Two boilerplate lines. If pygame says to quit, quit.
        if event.type == pygame.QUIT:
            sys.exit()

        # Now onto the more interesting stuff. Check for mouse down.
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Event heard.")
##            # ask player 1 for input
##            if turn % 2 == 1:
##                col = int(input("Player 1, make your selection (0-6)"))
##                if is_valid_location(board, col):
##                    row = get_next_open_row(board, col)
##                    drop_piece(board, row, col, PLAYER_1_PIECE)
##
##                    if winning_move(board, PLAYER_1_PIECE):
##                        print("Player 1 wins! Congrats!")
##                        game_over = True
##
##            # ask player 2 for input
##            else:
##                col = int(input("Player 2, make your selection (0-6)"))
##                if is_valid_location(board, col):
##                    row = get_next_open_row(board, col)
##                    drop_piece(board, row, col, PLAYER_2_PIECE)
##
##                    if winning_move(board, PLAYER_2_PIECE):
##                        print("Player 2 wins! Congrats!")
##                        game_over = True
##
##            turn += 1
##            print_board(board)
