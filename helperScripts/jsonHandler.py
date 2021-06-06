"""Functions for handling jsons"""


import json


def updateJson(jsonFile, dictUpdated):
    """Updates the passed jsonFile with the passed dictionary dictUpdated."""
    with open(jsonFile, 'w', encoding = 'utf-8') as fileJson:
        json.dump(dictUpdated, fileJson, ensure_ascii = False, \
                  sort_keys = True, indent = 4)

def loadJson(jsonFile):
    """Returns passed json file as a dictionary"""
    with open(jsonFile) as state:
        jsonDict = json.load(state)
    return jsonDict

# This json keeps track of the basic things the bot does
def resetBotStates():
    """
    Resets botStates to default.
    botStates keeps track of basic bot functions.

    """
    botStates = {'gbEnabled' : 'False', \
                'tttEnabled' : 'False', \
                'somethingEnabled' : 'False', \
                'alreadyLogged' : 'True'}
    updateJson(r'data\botStates.json', botStates)

def resetTTTStates():
    """
    Resets tttStates to default.
    tttStates keeps track of Tic-Tac-Toe states
    
    """
    tttStates = {'player1' : {'id' : '0', 'symbol' : '0'}, \
            'player2' : {'id' : '0', 'symbol' : '0'}, \
            'board' : {'a' : {'1' : ':black_large_square:', '2': ':black_large_square:', '3' : ':black_large_square:'}, \
                       'b' : {'1' : ':black_large_square:', '2': ':black_large_square:', '3' : ':black_large_square:'}, \
                       'c' : {'1' : ':black_large_square:', '2': ':black_large_square:', '3' : ':black_large_square:'}}, \
                       'chance' : '0'}
    updateJson(r'data\tictactoe\tttStates.json', tttStates)

def resetGBStates():
    """
    Resets gbStates to default.
    gbStates keeps track of Goosebumps adventure states.
    
    """
    gbStates = {'book' : 0, \
                'pageNumber' : 0, \
                'options' : 0, \
                'bookEnd' : 'False', \
                'totalBooks' : 2}
    updateJson(r'data\goosebumps\gbStates.json', gbStates)

def loadUsers():
    """
    Loads users dictionary from users.json
    Initializes if not present.

    """
    try:
        users = loadJson(r'data\users\users.json')
    except:
        users = {}
        updateJson(r'data\users\users.json', users)
    
    return users


if __name__ == '__main__':
    print("This script wasn't meant to be run standalone.")
    pass