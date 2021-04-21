import numpy as np

ROW_COUNT = 6
COLUMN_COUNT = 7

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

# Change the orientation of the board so it looks nice when printing,
# then print the board.
def print_board(board):
    # flip the board over the 0 axis (x)
    print(np.flip(board, 0))

board = create_board()
print_board(board)
game_over = False
turn = 1

while not game_over:
    # ask player 1 for input
    if turn % 2 == 1:
        col = int(input("Player 1, make your selection (0-6)"))
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, 1)

    # ask player 2 for input
    else:
        col = int(input("Player 2, make your selection (0-6)"))
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, 2)

    turn += 1
    print_board(board)
