import json
import random
import re
import subprocess
import time
from pprint import pprint

import discord

from helperScripts import fractalGenerator, jsonHandler, textHandler, tictactoe


# Basic stuff for startup:
with open(r'data\botid.txt', 'r', encoding = 'utf-8') as BOTID:
    BOTID = BOTID.read().splitlines()
with open(r'data\token.txt', 'r') as TOKEN:
    TOKEN = TOKEN.readline()
gptComm = "python src/interactive_conditional_samples_botmodified.py"
client = discord.Client()


# Setting states to default:
jsonHandler.resetBotStates()
jsonHandler.resetGBStates()
jsonHandler.resetTTTStates()


# Loading users:
users = jsonHandler.loadUsers()


# Main bot loop:
@client.event
async def on_message(message):

    # If the message author is the bot, return
    if message.author == client.user:
        return


    # Printing basic message info:
    print('\nclient.user:', client.user, ', id:', client.user.id)
    print('User:', message.author.name, 'id:', message.author.id)
    print('Message:', message.content)


    # Remove quotes:
    text = textHandler.removeQuote(message.content)


    # Logging messages into messageLog.txt:
    # Checking that the bot was not mentioned, and removing mentions and webpages:
    if not any(word in text for word in BOTID):
        textToLog = text
        removeMatch = re.findall(r"<.*>", textToLog) + re.findall(r"http.+ ", textToLog)
        for match in removeMatch:
            textToLog = textToLog.replace(match.strip(), '').strip()
        if not textToLog == '': 
            with open('data\messageLog.txt', 'a', encoding = 'utf-8') as logTxt:
                textToLog = '\n'.join(['', textToLog, ''])
                logTxt.writelines(textToLog)


    # If the bot was mentioned outside quotes, replies depending on context
    if any(word in text for word in BOTID):
        mentionString = ''.join(['<@', str(message.author.id), '>'])
        removeMatch = re.findall(r"<[@,!,&]+[0-9]+>", text) + re.findall(r"http.+ ", text)
        for match in removeMatch:
            text = text.replace(match.strip(), '').strip()
        gptInputText = text
        text = text.lower()
        print ('Content:', text)
        print ('Length:', len(text.split(' ')), 'words')


        # Loading up user data or creating new user from/to usersJson:
        users = jsonHandler.loadUsers()
        messageAuthorID = str(message.author.id)
        if messageAuthorID in users:
            users[messageAuthorID]['interactions'] += 1
            pprint(users[messageAuthorID])
        else:
            newUser = {messageAuthorID : {'name' : message.author.name, \
                                        'interactions' : 1, \
                                        'splashMessage' : "We haven't talked much..."}}
            users.update(newUser)
        jsonHandler.updateJson(r'data\users\users.json', users)


        # Reading states from botStates.json and setting up state flags:
        botStates = jsonHandler.loadJson(r'data\botStates.json')
        print('Previous botStates:')
        pprint(botStates)
        # Checking if the dictionary values were true, and if so, the state flags are set, else reset
        gbEnabled = botStates['gbEnabled'].lower() == 'true'
        tttEnabled = botStates['tttEnabled'].lower() == 'true'
        somethingEnabled = botStates['somethingEnabled'].lower() == 'true'
        alreadyLogged = botStates['alreadyLogged'].lower() == 'true'


        # Show user profile:
        match = ['profile']
        if any(word in text for word in match) and not somethingEnabled:
            somethingEnabled = True
            response = []
            try:
                response.append(str(users[messageAuthorID]['splashMessage']))
            except:
                pass
            try:
                response.append(' '.join([str(users[messageAuthorID]['tttWins']), ':trophy: in Tic-Tac-Toe']))
            except:
                pass
            response.append(' '.join([str(users[messageAuthorID]['interactions']), 'interactions']))    
            response = '\n'.join(response)
            profileEmbed = discord.Embed(title = ''.join([message.author.name, "'s Profile"]), \
                                        description = response, color = random.randint(0, 16777215))
            await message.channel.send(embed = profileEmbed)

            return
        


        # Respond to greetings with greetings
        match = ['ahoy', 'bonjour', 'you there', 'coming online', 'online now', 'now online']
        greetMatch = [not len(re.findall(r"\bh[u,e,a,o]+[ll]+[o,a,!]", text)) == 0, \
                      not len(re.findall(r"\bh[o]+[l]+[a,o]", text)) == 0, \
                      not len(re.findall(r"\bh[o,e,i]+[y,i]", text)) == 0, \
                      not len(re.findall(r"\ba[l]+[i]+[a,o]", text)) == 0]
        if (any(greetMatch) or \
           any(word in text for word in match) and not somethingEnabled) and \
           len(text.split(sep = ' ')) < 4:

            response = '\n'.join(textHandler.getRandTextLines(r'data\greetings.txt'))
            print(response)
            response = ' '.join([mentionString, response])
            await message.channel.send(response)
            return



        # Gives random love messages from love.txt
        match = ['❤️', '💓', '💖']
        if any(trigger in message.content for trigger in match) and not somethingEnabled:
            reactEmoji = ['❤️', '💓', '💖']
            option = random.randint(0, 1)

            if option == 0:
                response = '\n'.join(textHandler.getRandTextLines(r'data\love.txt'))
                print(response)
                loveEmbed = discord.Embed(description = response, color = 0xff69b4)
                await message.channel.send(embed = loveEmbed)

            if option == 1:
                random.seed(a = None)
                await message.add_reaction(random.choice(reactEmoji))
                print('Reacted.')
            
            return



        # Generates a fractal image on demand:
        match = ['drawing', 'picture', \
                 'pattern', 'fractal', 'draw']
        if any(word in text for word in match):
            async with message.channel.typing():
                choice = random.randint(1,5)
                print ('Fractal choice:', choice)
                if choice in [1, 2, 3, 4]:
                    fractalGenerator.generateJulia()
                    fractalEmbed = discord.Embed(title = '**Fractal: Julia**', \
                                                 color = random.randint(0, 16777215))
                    fractalImg = discord.File(r'data\fractals\julia.png', \
                                                    filename = 'julia.png')
                    fractalEmbed.set_image(url = r'attachment://julia.png')
                    await message.channel.send(file = fractalImg, embed = fractalEmbed)
                    print('Image sent.')

                    return

                elif choice in [5]:
                    fractalGenerator.generateMandelbrot()
                    fractalEmbed = discord.Embed(title = '**Fractal: Mandelbrot**', \
                                                 color = random.randint(0, 16777215))
                    fractalImg = discord.File(r'data\fractals\mandelbrot.png', \
                                                    filename = 'mandelbrot.png')
                    fractalEmbed.set_image(url = r'attachment://mandelbrot.png')
                    await message.channel.send(file = fractalImg, embed = fractalEmbed)
                    print('Image sent.')

                    return

            return



        # Play Tic-Tac-Toe with another player:
        match = ['tic tac toe', 'tictactoe', 'tic-tac-toe']
        if any(word in text for word in match):
            tttText = textHandler.removeQuote(message.content)
            tttText = ' '.join(tttText.split()[1:]).lower()
            if tttEnabled:
                response = "There's already a match of Tic-Tac-Toe going on."
                print(response)
                response = ' '.join([mentionString, response])
                await message.channel.send(response)

                return
            # If no player was tagged, return
            index, index2 = tttText.find('<'), tttText.find('>')
            if index == -1 or index2 == -1:
                response = 'Mention the person you want to play with.'
                print('No player was mentioned.')
                response = ' '.join([mentionString, response])
                await message.channel.send(response)

                return
            # If the bot was tagged, return
            if any(word in tttText for word in BOTID):
                response = "Hey... Don't mention me, I don't know how to play!"
                print('Bot was tagged.')
                response = ' '.join([mentionString, response])
                await message.channel.send(response)

                return

            # Updating states and state variables:
            botStates['tttEnabled'] = 'True'
            tttEnabled = True
            botStates['somethingEnabled'] = 'True'
            somethingEnabled = True
            tttPlayer1 = messageAuthorID
            tttPlayer2 = 0

            tttStates = jsonHandler.loadJson(r'data\tictactoe\tttStates.json')
            tttStates['player1']['id'] = messageAuthorID

            # Getting second player id:
            for tttPlayer2 in tttText.split():
                if tttPlayer2.startswith('<'):
                    if any(ch.isdigit() for ch in tttPlayer2):
                        tttPlayer2 = tttPlayer2.replace('<', '').replace('>', '')
                        tttPlayer2 = tttPlayer2.replace('!', '').replace('@', '')
                        break
            tttStates['player2']['id'] = tttPlayer2

            # Choosing a symbol for the players at random:
            tttChoice = random.randint(0,1)
            if tttChoice == 0:
                tttStates['player1']['symbol'] = ':x:'
                tttStates['player2']['symbol'] = ':o:'
            else:
                tttStates['player1']['symbol'] = ':o:'
                tttStates['player2']['symbol'] = ':x:'
            tttChoice = random.randint(0,1)
            if tttChoice == 0:
                tttStates['chance'] = ':o:'
            else:
                tttStates['chance'] = ':x:'
            jsonHandler.updateJson(r'data\botStates.json', botStates)
            jsonHandler.updateJson(r'data\tictactoe\tttStates.json', tttStates)

            # Hyping up the match:
            tttHype = textHandler.getRandTextLines(r'data\tictactoe\tictactoe.txt')
            mentionStringP2 = ''.join(['<@', str(tttPlayer2), '>'])

            # If playing with self:
            if tttPlayer1 == tttPlayer2:
                response = 'Ah, you wanna play with yourself? Sure!'
            else:
                response = ' '.join([tttHype[0], mentionString, tttStates['player1']['symbol'], tttHype[1], \
                            ''.join([mentionStringP2, tttStates['player2']['symbol'], tttHype[2]])])

            tttEmbed1 = discord.Embed(title = '**Tic-Tac-Toe**', description = response, color = 0xff0000)

            tttStates = jsonHandler.loadJson(r'data\tictactoe\tttStates.json')
            print('Previous tttStates:')
            pprint([value for key, value in tttStates.items() if key not in ['board']]) 
            tttBoard = tictactoe.getBoard(tttStates)
            print('Board reset to:')
            pprint(tttBoard)

            tttBoard = tictactoe.getRandomBoard()

            tttText = tictactoe.returnBoardAsText(tttBoard)
            tttText.append('\n'.join(['', *textHandler.getTextLines(r'data\tictactoe\instructions.txt', 0)[0]]))
            tttText = '\n'.join([*tttText])

            tttEmbed1.add_field(name = '**How to play**', value = tttText, inline = False)

            await message.channel.send(embed = tttEmbed1)


            tttBoard = tictactoe.getBoard(tttStates)

            tttText = tictactoe.returnBoardAsText(tttBoard)
            tttText = '\n'.join([*tttText])

            if tttStates['player1']['symbol'] == tttStates['chance']:
                response = ''.join([mentionString, "'s"])
            else:
                response = ''.join([mentionStringP2, "'s"])
            response = ''.join(['*', response, '*'])
            response = ' '.join(['__\n', response, '*turn*', tttStates['chance']])
            response = '\n'.join([tttText, response])

            tttEmbed2 = discord.Embed(title = '**Tic-Tac-Toe**', description = response, color = 0xff0000)

            await message.channel.send(embed = tttEmbed2)
            
            return

        # Everything that requires tttEnabled flag are below:
        tttInvalid = True
        if tttEnabled:
            tttStates = jsonHandler.loadJson(r'data\tictactoe\tttStates.json')

            # To exit Tic-Tac-Toe:
            match = ['exit', 'quit', 'end']
            if any(word in text for word in match):
                jsonHandler.resetBotStates()
                jsonHandler.resetTTTStates()

                print('Exiting Tic-Tac-Toe...')

                gbEmbed = discord.Embed(title = '**Quitting the game...**', \
                                        description = 'Really? Did you just quit a game of Tic-Tac-Toe? :man_facepalming:', \
                                        color = 0xff0000)
                await message.channel.send(embed = gbEmbed)     
                tttInvalid = False

                return           
            
            match = ['a1', 'a2', 'a3', \
                     'b1', 'b2', 'b3', \
                     'c1', 'c2', 'c3']
            if any(word in text for word in match):
                # Finding the input string:
                text = re.findall("[a-c][1-3]", text)[0]
                tttInput = []
                for ch in text:
                    tttInput.append(ch)
                print('Tic-Tac-Toe Input:', tttInput)                   

                # TicTacToe states:
                tttStates = jsonHandler.loadJson(r'data\tictactoe\tttStates.json')
                print('Previous tttStates:')
                pprint([value for key, value in tttStates.items() if key not in ['board']]) 

                if not(messageAuthorID == tttStates['player1']['id']) and tttStates['chance'] == tttStates['player1']['symbol'] \
                    or not(messageAuthorID == tttStates['player2']['id']) and tttStates['chance'] == tttStates['player2']['symbol']:
                    tttValid = False
                    response = "Not your turn right now..."
                    tttText = ' '.join([mentionString, response])
                    tttEmbed = discord.Embed(title = '**Tic-Tac-Toe**', description = tttText, color = 0xff0000)
                    await message.channel.send(embed = tttEmbed)

                    return

                # Checking if move was valid:
                tttValid = False
                if messageAuthorID == tttStates['player1']['id'] and tttStates['chance'] == tttStates['player1']['symbol']:
                    if tttStates['board'][tttInput[0]][tttInput[1]] == ':black_large_square:':
                        tttValid = True
                        tttStates['board'][tttInput[0]][tttInput[1]] = tttStates['player1']['symbol']
                        tttStates['chance'] = tttStates['player2']['symbol']
                    else:
                        tttValid = False
                elif messageAuthorID == tttStates['player2']['id'] and tttStates['chance'] == tttStates['player2']['symbol']:
                    if tttStates['board'][tttInput[0]][tttInput[1]] == ':black_large_square:':
                        tttValid = True
                        tttStates['board'][tttInput[0]][tttInput[1]] = tttStates['player2']['symbol']
                        tttStates['chance'] = tttStates['player1']['symbol']
                    else:
                        tttValid = False
                jsonHandler.updateJson(r'data\tictactoe\tttStates.json', tttStates)
                
                tttBoard = tictactoe.getBoard(tttStates)
                
                print('Current Board:')
                pprint(tttBoard)

                # Checking for win conditions:
                tttWin = []
                for rowCol in range(0,3):
                    rowWin = all(entry == tttBoard[rowCol][0] for entry in tttBoard[rowCol]) and not \
                          any(entry == ':black_large_square:' for entry in tttBoard[rowCol])
                    tttWin.append(rowWin)
                    colWin = all(entry == tttBoard[0][rowCol] for entry in [row[rowCol] for row in tttBoard]) and not \
                          any(entry == ':black_large_square:' for entry in [row[rowCol] for row in tttBoard])
                    tttWin.append(colWin)
                leftDiagonal = [tttBoard[0][0], tttBoard[1][1], tttBoard[2][2]]
                leftDiagonalWin = all(entry == leftDiagonal[0] for entry in leftDiagonal) and not \
                          any(entry == ':black_large_square:' for entry in leftDiagonal)
                tttWin.append(leftDiagonalWin)
                rightDiagonal = [tttBoard[0][2], tttBoard[1][1], tttBoard[2][0]]
                rightDiagonalWin = all(entry == rightDiagonal[0] for entry in rightDiagonal) and not \
                          any(entry == ':black_large_square:' for entry in rightDiagonal)
                tttWin.append(rightDiagonalWin)

                # Responding based on validity of move:
                if tttValid:
                    tttText = tictactoe.returnBoardAsText(tttBoard)

                    tttText = '\n'.join([*tttText]) 
                else:
                    response = "That looks like an invalid move. Try another?"
                    tttText = ' '.join([mentionString, response])

                tttEmbed = discord.Embed(title = '**Tic-Tac-Toe**', description = tttText, color = 0xff0000)

                # Checking for draw conditions:
                tttDraw = []
                match = ':black_large_square:'
                for rowCol in range(0,3):   
                    # If entry is not empty, tttDraw is true
                    rowDraw = not any(entry == match for entry in tttBoard[rowCol])
                    tttDraw.append(rowDraw)

                # Win message
                if any(tttWin):
                    response = ' '.join([mentionString, tttStates['chance'], "wins!"])
                    tttEmbed.add_field(name = '**We have a winner!**', value = response, inline = False)
                    if not tttStates['player1']['id'] == tttStates['player2']['id']:
                        if 'tttWins' in users[messageAuthorID]:
                            users[messageAuthorID]['tttWins'] += 1
                        else:
                            users[messageAuthorID]['tttWins'] = 1
                    jsonHandler.updateJson(r'data\users\users.json', users)
                    print(response)
                    jsonHandler.resetTTTStates()
                    jsonHandler.resetBotStates()
                
                elif all(tttDraw):
                    # If all entries are filled, draw
                    response = "The match was drawn."
                    tttEmbed.add_field(name = '**Draw**', value = response, inline = False)
                    print(response)
                    jsonHandler.resetTTTStates()
                    jsonHandler.resetBotStates()
                    
                else:
                    mentionString = ''.join(['<@', tttStates['player1']['id'], '>'])
                    mentionStringP2 = ''.join(['<@', tttStates['player2']['id'], '>'])
                    if tttStates['player1']['symbol'] == tttStates['chance']:
                        response = ''.join([mentionString, "'s"])
                    else:
                        response = ''.join([mentionStringP2, "'s"])
                    response = ''.join(['*', response, '*'])
                    response = ' '.join([response, '*turn*', tttStates['chance']])
                    tttEmbed.add_field(name = '__', value = response, inline = False)
                    print(response)

                await message.channel.send(embed = tttEmbed)
                tttInvalid = False
                
                return

            tttInvalid = True


        if tttEnabled and tttInvalid:
            response = "That looks like an invalid move. Try another?"
            tttText = ' '.join([mentionString, response])
            tttEmbed = discord.Embed(title = '**Tic-Tac-Toe**', description = tttText, color = 0xff0000)
            await message.channel.send(embed = tttEmbed)

            return


        # Roll die:        
        match = ['roll a die', 'roll dice', 'roll a dice', 'dice roll', 'roll die', 'throw dice', 'throw die', 'throw a die']
        if any(word in text for word in match) and not somethingEnabled:
            somethingEnabled = True
            diceResult = random.randint(1, 6)
            response = '\n'.join(['I threw a die and got', ''.join(['**> ', str(diceResult), '**'])])
            print(response)
            diceEmbed = discord.Embed(title = 'Roll a Die', description = response, color = 0xfffafa)
            await message.channel.send(embed = diceEmbed)

            return


        # Coin toss:
        match = ['toss a coin', 'head or tails', 'coin toss', 'toss coin', 'tails or head']
        if any(word in text for word in match) and not somethingEnabled:
            somethingEnabled = True
            diceResult = random.randint(0,1)
            if diceResult == 0:
                diceResult = 'Head'
            else:
                diceResult = 'Tail'
            response = '\n'.join(['I tossed a coin and got a', ''.join(['**> ', diceResult, '**'])])
            print(response)
            diceEmbed = discord.Embed(title = 'Toss a Coin', description = response, color = 0xb87333)
            await message.channel.send(embed = diceEmbed)

            return



        # Enables Goosebumps
        match = ['read gb', 'gb read', 'read goosebumps']
        if any(word in text for word in match):
            botStates = jsonHandler.loadJson(r'data\botStates.json')

            # If already enabled, returns error message:
            if gbEnabled:
                response = "You're already playing Goosebumps :eyes:"
                print(response)
                response = ' '.join([mentionString, response])
                await message.channel.send(response)

                return

            # Modifying json to update botStates:
            botStates['gbEnabled'] = 'True'
            botStates['somethingEnabled'] = 'True'
            jsonHandler.updateJson(r'data\botStates.json', botStates)
            print('Play Goosebumps')

            page = textHandler.getTextLines(r'data\goosebumps\instructions.txt', 0)[0]
            gbEmbed = discord.Embed(title = '**Play Goosebumps**', 
                                    description = '\n'.join(page),
                                    color = 0x00ff00)
            
            with open(r'data\goosebumps\gbStates.json') as prevState:
                prevState = json.load(prevState)
                totalBooks = int(prevState['totalBooks'])

            for book in range(1, totalBooks + 1, 1):
                page = textHandler.getTextLines(textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0][1], 0)[0]
                serialNumber = ''.join(['**', str(book), '.', '**'])
                gbEmbed.add_field(name = ' '.join([serialNumber, textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0][0]]), 
                                value = '\n'.join(page), 
                                inline = False)

            await message.channel.send(embed = gbEmbed)
            
            return


        # Everything that requires gbEnabled flag are below
        # Anything that needs to run even with the gbEnable flag need to be above this block
        if gbEnabled:  
            # Reading gbStates from json file:
            gbStates = jsonHandler.loadJson(r'data\goosebumps\gbStates.json')
            
            print('\nPrevious gbStates:', gbStates)
            # Checking if the dictionary values were true, and if so, the state flags are set, else reset
            # and storing numerical state values to variables
            book = gbStates['book']
            bookEnd = gbStates['bookEnd'].lower() == 'true'
            options = gbStates['options']
            pageNumber = gbStates['pageNumber']
            totalBooks = int(gbStates['totalBooks'])


            # To exit Goosebumps:
            match = ['exit gb', 'gb exit', 'exit goosebumps', 'goosebumps exit', 'chicken', 'exit']
            if any(word in text for word in match):
                # Updating botStates:
                jsonHandler.resetBotStates()

                # Updating gbStates:
                jsonHandler.resetGBStates()

                print('Exiting Goosebumps...')

                gbEmbed = discord.Embed(title = 'Exiting Goosebumps...', \
                                        description = 'Hah! Chickening out, eh? :chicken:', \
                                        color = 0x00ff00)
                await message.channel.send(embed = gbEmbed)

                return


            # Chooses the book, updates states, and displays the first page:
            match = ['gb book', 'choose book', 'book', 'choose']
            if any(word in text for word in match) and book == 0:
                try:
                    book = [int(i) for i in text.split() if i.isdigit()][0]
                except:
                    response = "That was weird, considering you asked for a book. Try again?"
                    print(response)
                    response = ' '.join([mentionString, response])
                    await message.channel.send(response)

                    return

                if not book > 0 or not book <= totalBooks:
                    if not book > 0:
                        response = "That was a weird number, considering you asked for a book. Try again?"
                    else:
                        response = "I don't have that many books... Maybe some day I will. Give <@!442271366159400971> some love :sparkling_heart:"
                    print(response)
                    response = ' '.join([mentionString, response])
                    await message.channel.send(response)

                    return

                # Getting the first page of the specified book and firing it off as an embed:
                page, options = textHandler.getTextLines(textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0][1], 1)[:2]
                # Updating states in gbStates.json:
                gbStates['book'] = book
                gbStates['bookEnd'] = 'False'
                gbStates['pageNumber'] = 1   
                gbStates['options'] = options            
                jsonHandler.updateJson(r'data\goosebumps\gbStates.json', gbStates)

                print('Chose book:', book)
                print('Page contents:', '\n'.join(page))
                print('Options:', options)

                bookName = textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0]
                gbEmbed = discord.Embed(title = bookName[0], description = '\n'.join(page), color = 0x00ff00)

                await message.channel.send(embed = gbEmbed)

                return


            # Choosing options:
            match = ['choose option', 'option', 'go with', 'choice', 'choose']
            skipOption = ['next', 'continue']
            chosenOption = 0
            if any(word in text for word in match + skipOption) and not book == 0:
                firstOption = False
                try:
                    chosenOption = [int(i) for i in text.split() if i.isdigit()][0]
                except:
                    # If there was only one option, continue with 'next' instead of option number:
                    if any(word in text for word in skipOption) and len(options) == 1:
                        firstOption = True

                try:
                    if firstOption:
                        pageNumber = int(options[0])
                    else:
                        if chosenOption == 0:
                            raise Exception
                        pageNumber = int(options[chosenOption-1])
                    
                except:
                    response = "Um... I don't think that was an option. Try again?"
                    print(response)
                    response = ' '.join([mentionString, response])

                    await message.channel.send(response)

                    return

                # Retrieving the specified pageNumber from the specified book:
                page, options, embedStuff = textHandler.getTextLines(textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0][1], pageNumber)
                
                gbStates['pageNumber'] = pageNumber   
                gbStates['options'] = options
                bookEnd = options[0] == '-1'
                if bookEnd:
                    gbStates['bookEnd'] = 'True'
                jsonHandler.updateJson(r'data\goosebumps\gbStates.json', gbStates)

                print('Page contents:', '\n'.join(page))
                print('Options:', options)

                if len(embedStuff) == 0:
                    bookName = textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0]
                    gbEmbed = discord.Embed(title = bookName[0], description = '\n'.join(page), color = 0x00ff00)

                    await message.channel.send(embed = gbEmbed)

                else:
                    bookName = textHandler.getTextLines(r'data\goosebumps\booknames.txt', book)[0]
                    gbEmbed = discord.Embed(title = bookName[0], description = '\n'.join(page), color = 0x00ff00)
                    embedImg = discord.File(embedStuff[0], filename = 'embed.png')
                    gbEmbed.set_image(url = r'attachment://embed.png')

                    await message.channel.send(file = embedImg, embed = gbEmbed)

                if bookEnd:
                    gbEmbed = discord.Embed(title = 'The End', description = 'You made it to the end! :eyes:', color = 0x00ff00)
                    # Updating botStates:
                    botStates['gbEnabled'] = 'False'
                    botStates['somethingEnabled'] = 'False'
                    jsonHandler.updateJson(r'data\botStates.json', botStates)

                    # Updating gbStates:
                    gbStates['book'] = 0
                    gbStates['bookEnd'] = 'False'
                    gbStates['pageNumber'] = 0
                    gbStates['options'] = 0
                    jsonHandler.updateJson(r'data\goosebumps\gbStates.json', gbStates)

                    await message.channel.send(embed = gbEmbed)

                return


            # This is the spinner for 'The Attack of the Beastly Babysitter':
            match = ['spin spinner', 'spinner']
            if any(word in text for word in match) and book == 1:
                spinnerResult = {}
                angle = random.randint(0, 359)
                if angle >= 0 and angle < 90:
                    spinnerResult['allNothing'] = 'All'
                    spinnerResult['yesNo'] = 'Yes'
                else:
                    spinnerResult['allNothing'] = 'Nothing'
                    spinnerResult['yesNo'] = 'Now'

                if angle >= 90 and angle < 270:
                    spinnerResult['funGames'] = 'Fun'
                else:
                    spinnerResult['funGames'] = 'Games'           

                if angle >= 90 and angle < 210:
                    spinnerResult['redGreenYellow'] = 'Red'
                elif angle >= 210 and angle < 330:
                    spinnerResult['redGreenYellow'] = 'Yellow'
                else:
                    spinnerResult['redGreenYellow'] = 'Green'

                response = '\n'.join(['I spun the spinner for you:', \
                                        ' '.join(['**>**', spinnerResult['allNothing']]), \
                                        ' '.join(['**>**', spinnerResult['redGreenYellow']]), \
                                        ' '.join(['**>**', spinnerResult['yesNo']]), \
                                        ' '.join(['**>**', spinnerResult['funGames']])])
                
                gbEmbed = discord.Embed(color = 0x00ff00)
                spinnerImg = discord.File(r'data\goosebumps\attackofthebeastlybabysitter\spinner.png', \
                                            filename = 'spinner.png')
                gbEmbed.set_image(url = r'attachment://spinner.png')
                gbEmbed.add_field(name = '**Spinner**', 
                                value = response, 
                                inline = False)
                
                await message.channel.send(file = spinnerImg, embed = gbEmbed)

                return


            # If no responses match
            else:
                response = "You're playing Goosebumps right now. Check your message, or to do something else, chicken out. :chicken:"
                print(response)
                response = ' '.join([mentionString, response])
                await message.channel.send(response)
                
            return



        # Log the output of the GPT2 text generator:
        match = ['logoutput']
        if any(trigger in text for trigger in match) and not somethingEnabled:
            # The message is deleted.
            await message.delete()

            # If already logged, return
            if alreadyLogged:
                print('Already logged.')

                return

            with open(r'input.txt', 'r', encoding = 'utf-8') as inputPrompt:
                inputPrompt = inputPrompt.read().splitlines()
            with open(r'data\gptLogs\outputLogs.txt', 'a', encoding = 'utf-8') as outputLogs:
                responses = open('output.txt', encoding = 'utf-8', errors = 'ignore').read().splitlines()

                holder = []
                for response in responses:
                    holder.append(response.replace('<|endoftext|>', '').strip())
                responses = holder

                responses = '\n'.join(['', 'Prompt:', *inputPrompt, '', 'Output:', *responses, '@'])
                outputLogs.writelines(responses)    

            botStates['alreadyLogged'] = 'True'
            jsonHandler.updateJson(r'data/botStates.json', botStates)

            print('Logged.')

            return



        if not somethingEnabled and not gptInputText == '':
            # This entire block is for GPT2 text generation:
            async with message.channel.typing():
                if len(gptInputText.split()) >= 4:
                    print('Input to GPT:\n', gptInputText)
                    with open('input.txt', 'w', encoding = 'utf-8') as gptInput:
                        gptInput.writelines(gptInputText)

                    botStates['alreadyLogged'] = 'False'
                    jsonHandler.updateJson(r'data/botStates.json', botStates)

                    # Starting up the GPT2 script:
                    subprocess.check_output(gptComm, shell = True, stderr = subprocess.STDOUT)

                    with open(r'output.txt', encoding = 'utf-8', errors = 'ignore') as responses:
                        responses = responses.read().splitlines()
                        responses = [string for string in responses if string]

                    holder = []
                    for response in responses:
                        holder.append(response.replace('<|endoftext|>', ''))
                    responses = holder

                    print('GPT response:')
                    for response in responses:
                        print(response)

                    responseLength = 0
                    for response in responses:
                        response = ' '.join([mentionString, response])
                        async with message.channel.typing():
                            time.sleep(10)
                            response = (response[:1999]) if len(response) > 1998 else (response)
                            await message.channel.send(response)
                        responseLength += len(response)
                        if responseLength > 1000:
                            break

                # GPT2 response ends here

                # Sends an error message for longer text, if text was too short:
                else:
                    async with message.channel.typing():
                        response = textHandler.getRandTextLines(r'data\longertext.txt')
                        print(*response)
                        response = ' '.join([mentionString, *response])
                        await message.channel.send(response)
                    
                return
                
        return

print('\nNotABot is ready!')
client.run(TOKEN)
