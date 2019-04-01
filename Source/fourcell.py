# -*- coding: utf-8 -*-

from enum import Enum
import random
from time import sleep

# gui made with asciimatics
from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen

"""
fourcell
simple terminal freecell game

The open card in each pile are mapped to
a s d f j k l ;
The 4 free cells are mapped to
q w e r
and the foundations are mapped to
u i o p

Move a card by pressing its key and then pressing
the key of its destination.
"""

tablekeybinds = {
    'a':0,
    's':1,
    'd':2,
    'f':3,
    'j':4,
    'k':5,
    'l':6,
    ';':7
    }

freecellskeybinds = {
    'q':0,
    'w':1,
    'e':2,
    'r':3
    }

foundationskeybinds = {
    'u':0,
    'i':1,
    'o':2,
    'p':3
    }

class Suit(Enum):
    SPADES = '♠'
    HEARTS = '♥'
    CLUBS = '♣'
    DIAMONDS = '♦'
    
class Card:

    def __init__(self, _value, _suit):
        self.suit = _suit
        self.value = _value
        if self.suit == Suit.SPADES or self.suit == Suit.CLUBS:
            self.color = Screen.COLOUR_WHITE
        else:
            self.color = Screen.COLOUR_RED

    def __str__(self):
        text = None
        if self.value == 1:
            text = 'A'
        elif self.value == 11:
            text = 'J'
        elif self.value == 12:
            text = 'Q'
        elif self.value == 13:
            text = 'K'
        else:
            text = str(self.value)
        return text + self.suit.value

class IllegalMove(Exception):
    pass

class FreeCellGame:

    def __init__(self):
        random.seed()
        self.table = [] # array of Stacks on the table
        for i in range(0,8):
            self.table.append([])
        self.freecells = [] # 4 1-card stacks
        for i in range(0,4):
            self.freecells.append([])
        self.foundations = [] # array of foundation stacks
        for i in range(0,4):
            self.foundations.append([])
        self.deal()

    #initialize the table by dealing out cards
    def deal(self):
        # construct deck
        deck = []
        for suit in [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]:
            for i in range(1,14):
                deck.append(Card(i,suit))

        # shuffle, then start dealing onto table
        random.shuffle(deck)
        currentColumn = 0
        while len(deck) > 0:
            self.table[currentColumn].append(deck.pop())
            currentColumn = (currentColumn + 1) % 8

    def attemptMove(self, move):
        sourceCard = None
        sourceStack = None
        sourceInd = None
        destInd = None
        try:
            if move[0] in tablekeybinds.keys():
                sourceInd = tablekeybinds[move[0]]
                if len(self.table[sourceInd]) < 1:
                    raise IllegalMove
                else:
                    sourceCard = self.table[sourceInd][-1]
                    sourceStack = self.table[sourceInd]
                    
            elif move[0] in freecellskeybinds.keys():
                    sourceInd = freecellskeybinds[move[0]]
                    if len(self.freecells[sourceInd]) < 1:
                        raise IllegalMove
                    else:
                        sourceCard = self.freecells[sourceInd][-1]
                        sourceStack = self.freecells[sourceInd]
            else:
                raise IllegalMove
            
            if move[1] in tablekeybinds.keys():
                destInd = tablekeybinds[move[1]]
                # is this column empty?
                if len(self.table[destInd]) == 0:
                    self.table[destInd].append(sourceStack.pop())
                # only allow sourceCard to move here if whats on the top already has different color and value greater by 1
                else:
                    currentTop = self.table[destInd][-1]
                    if sourceCard.color != currentTop.color and sourceCard.value == currentTop.value - 1:
                        self.table[destInd].append(sourceStack.pop())
                    else:
                        raise IllegalMove
            
            elif move[1] in freecellskeybinds.keys():
                destInd = freecellskeybinds[move[1]]
                if len(self.freecells[destInd]) == 0:
                    self.freecells[destInd].append(sourceStack.pop())
                else:
                    raise IllegalMove
            
            elif move[1] in foundationskeybinds.keys():
                destInd = foundationskeybinds[move[1]]
                # empty foundations can be filled by aces. Nonepmtpy foundations filled y successive card of same suit
                if len(self.foundations[destInd]) == 0:
                    if sourceCard.value == 1:   
                        self.foundations[destInd].append(sourceStack.pop())
                    else:
                        raise IllegalMove
                else:
                    currentTop = self.foundations[destInd][-1]
                    if currentTop.suit == sourceCard.suit and sourceCard.value == currentTop.value + 1:
                        self.foundations[destInd].append(sourceStack.pop())
                    else:
                        raise IllegalMove
                        
        except IllegalMove:
            pass
        finally:
            move.clear() # reset




            
def playGame(screen):

    game = FreeCellGame()
    move = [] # store 2 moves
    oldMove = None # copy of last inputs to show user
    while True:
        screen.clear()
        ev = screen.get_event()
        key = None
        try:
            key = chr(ev.key_code)
            move.append(key)
        except AttributeError:
            pass # mouse event 
        except ValueError:
            pass # invalid key pressed. ignore it
        
        if len(move) != 0:
            oldMove = move.copy()
        if oldMove is not None:
            print(oldMove)
        if len(move) == 2:
            game.attemptMove(move)
        
        renderFreeCells(screen, game.freecells)
        renderFoundations(screen, game.foundations)
        renderTable(screen, game.table)
        
        screen.refresh()
        sleep(.1)


def renderTable(screen,table):
    # renders the table (not the free cells or the foundations)

    xOffset = 5
    xSpacePerCard = 4
    yOffset = 5
    ySpacePerCard = 1

    # draw partition
    screen.move(xOffset, yOffset - 1)
    screen.draw(xOffset + 8 *xSpacePerCard, yOffset - 1, thin=True)
    
    # iterate through each of the 8 stacks
    for x, cardStack in enumerate(table):
        for y, card in enumerate(cardStack):
            screen.print_at(str(card),
                            xOffset + x * xSpacePerCard, yOffset + y * ySpacePerCard,
                            card.color)

def renderFreeCells(screen, freecells):
    xOffset = 2
    yOffset = 2
    xSpacePerCard = 4
    for x, stack in enumerate(freecells): # should be 4
        toPrint = '_'
        toColor = Screen.COLOUR_BLUE
        if len(stack) > 0:
            toPrint = str(stack[-1])
            toColor = stack[-1].color
            
        screen.print_at(toPrint,
                        xOffset + x * xSpacePerCard, yOffset,
                        toColor)
            
def renderFoundations(screen, foundations):
    xSpacePerCard = 4
    xOffset = 2 + 5 * xSpacePerCard
    yOffset = 2
    for x, stack in enumerate(foundations): # should be 4
        toPrint = '_'
        toColor = Screen.COLOUR_RED
        if len(stack) > 0:
            toPrint = str(stack[-1])
            toColor = stack[-1].color
            
        screen.print_at(toPrint,
                        xOffset + x * xSpacePerCard, yOffset,
                        toColor)

        
if __name__ == '__main__':
    # use asciimatics to render the game
    Screen.wrapper(playGame)
