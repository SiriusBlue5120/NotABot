"""Functions for handling Tic-Tac-Toe games."""

import random
from helperScripts import jsonHandler


def getBoard(tttStates):
    """Reads the board from tttStates dict and returns it as a list."""

    tttBoard = [[tttStates['board']['a']['1'], tttStates['board']['a']['2'], tttStates['board']['a']['3']], \
                [tttStates['board']['b']['1'], tttStates['board']['b']['2'], tttStates['board']['b']['3']], \
                [tttStates['board']['c']['1'], tttStates['board']['c']['2'], tttStates['board']['c']['3']]]

    return tttBoard

def getRandomBoard():
    """Returns a board with randomized entries."""

    possEntry = [':x:', ':o:', ':black_large_square:']
    tttBoard = [[possEntry[random.randint(0,2)], possEntry[random.randint(0,2)], possEntry[random.randint(0,2)]], \
                [possEntry[random.randint(0,2)], possEntry[random.randint(0,2)], possEntry[random.randint(0,2)]], \
                [possEntry[random.randint(0,2)], possEntry[random.randint(0,2)], possEntry[random.randint(0,2)]]]

    return tttBoard

def returnBoardAsText(tttBoard):
    """Returns the passed board as lines of text in a list."""

    tttText = []
    tttText.append(' '.join([*tttBoard[0][:]]))
    tttText.append(' '.join([*tttBoard[1][:]]))
    tttText.append(' '.join([*tttBoard[2][:]]))

    return tttText


if __name__ == '__main__':
    print("This script wasn't meant to be run standalone.")
    pass