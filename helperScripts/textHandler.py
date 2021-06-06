"""Functions for handling text and text files"""


import random


def getRandTextLines(txtFile):
    """
    Gets a random set of lines from the given text file txtFile.

    Args:
        txtFile: The path of the text file to be accessed.

    Returns:
        lines: A random set of lines chosen from the file.

    """
    with open(txtFile, 'r', encoding = 'utf-8', errors = 'ignore') as txt:
        linecount = 0
        for line in txt.read().splitlines():
            if line.startswith('@'):
                linecount += 1
        choice = random.randrange(1, linecount, 1)
        txt.close()

        linecount = 0
        lines = []
        getLines = False
        txt = open(txtFile, 'r', encoding = 'utf-8', errors = 'ignore')
        for line in txt.read().splitlines():
            if linecount == choice:
                getLines = True
            if getLines:
                if line.startswith('@'):
                    break
                lines.append(line)
            if line.startswith('@'):
                linecount += 1
        
    return lines

def getTextLines(txtFile, choice):
    """
    Gets the specified page or set of lines from the given text file txtFile; 
    choice represents the page.

    Args:
        txtFile: The path of the text file to be accessed.
        choice: The page number of the required text.

    Returns:
        lines: Lines of text from passed page number.
        options: Page number options from current page; meant for Goosebumps.
        embedStuff: Any local links to images to be embedded; meant for 
            Goosebumps.

    """
    linecount = 0
    lines = []
    getLines = False
    getOptions = False
    getEmbed = False
    options = []
    embedStuff = []
    with open(txtFile, 'r', encoding = 'utf-8', errors = 'ignore') as txt:
        for line in txt.read().splitlines():
            if linecount == int(choice):
                if not len(lines):
                    getLines = True
            if getLines:
                if line.startswith('@'):
                    break
                if line.startswith('$'):
                    getLines = False
                    getOptions = False
                    getEmbed = True
                    continue
                if line.startswith('^'):
                    getLines = False
                    getOptions = True
                    getEmbed = False
                    continue
                if getLines:
                    lines.append(line)
            if getEmbed:
                if line.startswith('@'):
                    break
                if line.startswith('^'):
                    getEmbed = False
                    getLines = False
                    getOptions = True
                    continue
                if getEmbed:
                    embedStuff.append(line)
                    getEmbed = False
                    getLines = True
            if getOptions:
                if line.startswith('@'):
                    break
                options.append(line)
            if line.startswith('@'):
                linecount += 1
        
    return lines, options, embedStuff

def removeQuote(text):
    """
    Removes the quote from the passed message text.

    Args:
        text: Text from which quotes are to be removed.
    
    Returns:
        text: Text with quotes removed.
    """
    if text.startswith('> '):
        index = text.find('\n')
        if not index == -1:
            text = text[index+1:]
    
    return text


if __name__ == '__main__':
    print("This script wasn't meant to be run standalone.")
    pass