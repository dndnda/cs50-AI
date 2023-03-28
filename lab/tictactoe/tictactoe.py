"""
Tic Tac Toe Player
"""

import math


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCounter = 0
    oCounter = 0
    em = 0
    for i in range(0, len(board)):
        for j in range(0, len(board[0])):
            if board[i][j] == X:
                xCounter += 1
            elif board[i][j] == O:
                oCounter += 1

    if xCounter > oCounter:
        return O
    else:
        return X



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    rt = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                rt.add((i, j))
    return rt

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action

    if board[i][j] is not EMPTY:
        raise Exception
    
    player_ = player(board)

    from copy import deepcopy
    copy_board = deepcopy(board)
    copy_board[i][j] = player_
    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # speculate the row
    for items in board:
        if items[0] == items[1] and items[1] == items[2]:
            return items[0]
        
    #speculate the col
    for i in range(0, 3):
        if board[0][i] == board[1][i] and board[1][i] == board[2][i]:
            return board[0][i]
        
    # speculate the 对角线
    if board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[1][1]
    
    # else is tie
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or (not any(EMPTY in sublist for sublist in board) and winner(board) is None):
        return True
    else:
        return False
    #return True if winner(board) is not None or (not any(EMPTY in sublist for sublist in board) and winner(board) is None) else False # noqa E501


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    player_ = player(board)
    
    if player_ == X:
        value, move = max_value(board)
        return move
    else:
        value, move = min_value(board)
        return move

    

def max_value(board):
    if terminal(board):
        return utility(board), None
    
    v = float('-inf')
    move = None
    for action in actions(board):
        #v = max(v, min_value(result(board, action)))
        aux, act = min_value(result(board, action))
        if aux > v:
            v = aux
            move = action
            if v == 1:
                return v, move
    
    return v, move 

def min_value(board):
    
    if terminal(board):
        return utility(board), None
    
    v = float('inf')
    move = None
    for action in actions(board):
        #v = min(v, max_value(result(board, action)))
        aux, act = max_value(result(board, action))
        if aux < v:
            v = aux 
            move = action
            if v == -1:
                return v, move
    
    return v, move