from deck import Deck
from player import Player
import random, collections, math, itertools
from collections import Counter
import parallel_holdem_calc
import holdem_calc
import qlearning
from deuces import Card, Evaluator
import numpy as np
import sys
import copy

FLOP = 3
TURN = 1
RIVER = 1
TURNS = 4
TOTAL_POSSIBLE_CARDS = 7

class HoldemSimulator:
    def __init__(self, numPlayers, startAmount, numComputers):
        self.games = 0
        self.wins = 0
        self.folds = 0
        self.actions = 0
        self.numPlayers = numPlayers
        self.numComputers = numComputers
        self.startAmount = startAmount
        self.deck = Deck()
        self.players = []
        self.river = []
        self.pot = 0
        self.curRaise = 0
        self.roundOver = False
        self.firstRound = True
        self.winner = None
        self.qlearn = qlearning.QLearningAlgorithm(["Raise", "Fold", "Check"], 0.9, feature_extractor, self, 0.3)

        self.players.append(Player(startAmount,0,True))
        self.players.append(Player(startAmount,1,False))

    def straight(self, hand):
        total = hand + self.river
        if len(total) < 5: return False
        sTotal = [(card[1],card[0]) for card in total]
        sTotal.sort()
        best = 0
        flush = False
        for i in range(len(sTotal)-4):
            cHand = [sTotal[i]]
            current = sTotal[i]
            count = 0
            while True:
                count += 1
                if i + count < len(sTotal): break
                if sTotal[i+count][0] < current[0]+1: 
                    continue
                elif sTotal[i+count][0] == current[0]+1: 
                    cHand.append(sTotal[i+count])
                    current = sTotal[i+count]
                else: break
                if len(cHand) == 5: 
                    cFlush = len(filter(lambda x: x[1] == current[1], cHand)) == 5
                    if (flush and cFlush and current[0] > best) or (not flush and current[0] > best) or (not flush and cFlush):
                        flush = cFlush
                        best = current[0]
        if best > 0: return (best, flush)
        return (0,False)

    def nKind(self, hand, N, flush):
        allCards = self.river + hand
        index = 1
        if flush: index = 0
        values = [int(i[index]) for i in allCards]
        count = Counter(values)
        for key in count:
            if count[key] == N: return (True, key)
        return (False, None)

    def fullHouse(self, hand, twoPair):
        allCards = self.river + hand
        values = [int(i[1]) for i in allCards]
        count = Counter(values)
        trip = 3
        if twoPair: trip = 2
        best3 = 0
        best2 = 0
        for key3 in count:
            if count[key3] == trip and key3 > best3:
                best3 = key3
                best2 = 0
                for key2 in count:
                    if count[key2] >= 2 and key2 != key3 and key2 > best2:
                        best2 = key2
        if best3 > 0 and best2 > 0:
            if not twoPair: return (True,key3)
            return (True,best3,best2)
        return (False, None)

    def highCard(self, hand):
        maxCard = 0
        for card in hand:
            if card[1] == 1: return 1
            elif card[1] > maxCard: maxCard = card[1]
        return maxCard

    def computerTakeAction(self, player):
        nextAction = self.qlearn.getAction(player)
        if self.curRaise + 250 > player.chips and nextAction == "Raise": 
            nextAction = "Check"
        if not self.firstRound and player.prevState is not None: # incorporate feedback
            self.qlearn.incorporateFeedback(player.prevState, player.prevAction, 0, player)
        else:
            self.firstRound = False
        player.prevState = copy.deepcopy(player)
        player.prevAction = nextAction
        return nextAction

    def gameOver(self):
        if self.pot > 250 : return False
        for player in self.players:
            if player.getChipCount() <= 0: 
                if not player.isComputer: self.wins += 1
                return True
        return False

    def resetRound(self):
        if self.roundOver:
            if self.winner == 0:
                # print "0"
                if self.players[0].prevState != None:
                    self.qlearn.incorporateFeedback(self.players[0].prevState, 
                        self.players[0].prevAction, self.pot, self.players[0])
                self.players[0].winRound(self.pot)
            elif self.winner == 1:
                # print "1"
                if self.players[0].prevState != None:
                    self.qlearn.incorporateFeedback(self.players[0].prevState, 
                        self.players[0].prevAction, 0, self.players[0])
                self.players[1].winRound(self.pot)
            else:
                # print ".5"
                if self.players[0].prevState != None:
                    self.qlearn.incorporateFeedback(self.players[0].prevState, 
                        self.players[0].prevAction, self.pot/2, self.players[0])
                self.players[1].winRound(self.pot/float(2))
                self.players[0].winRound(self.pot/float(2))
            self.firstRound = True
            self.players[0].prevAction = None
            self.players[0].prevState = None

        self.winner = None
        self.deck = Deck()
        self.river = []
        self.pot = 0
        self.curRaise = 0
        self.roundOver = False

        for player in self.players:
            if player.chips == 0: 
                for player2 in self.players:
                    player2.takeCards()
                return 

        for player in self.players:
            player.takeCards()
            # player.resRaise()
            if player.getChipCount() < 250:
                self.pot += player.getChipCount()
                player.bet(player.getChipCount())
            else: 
                player.bet(250)
                self.pot += 250
            player.dealCard(self.deck.getRandomCard())
            player.dealCard(self.deck.getRandomCard())

    def resetGame(self):
        self.games += 1
        self.players = []
        self.players.append(Player(self.startAmount,0,True))
        self.players.append(Player(self.startAmount,1,False))
        
    def takeAction(self, player):
        while True:
            if player.isComputer:
                action = self.computerTakeAction(player)
            else: 
                action = "Check"
            # print player.getindex(), action
            actionL = action.split(",")
            if actionL[0] == "Raise": 
                if self.curRaise + 250 <= player.getChipCount():
                    player.bet(250 + self.curRaise)
                    self.pot += self.curRaise + 250
                    self.curRaise = 250
                    player.incRaise()
                    break
            if actionL[0] == "Fold": 
                self.winner = 1
                if player.getindex() == 1: 
                    self.winner = 0
                # self.players[winner].winRound(self.pot)
                self.roundOver = True
                break
            if actionL[0] == "Check":
                toPot = self.curRaise
                if self.curRaise > player.getChipCount(): toPot = player.getChipCount()
                self.pot += toPot
                player.bet(toPot)
                self.curRaise = 0
                break
                
            print action, "Invalid Action, please try again"
       

    #sf:8, 4k:7, fh:6, f:5, s:4, 3k:3, 22k:2, 2k:1, h:0
    def decideRound(self):
        totals = []
        best = None
        for i, player in enumerate(self.players): 
            hand = player.peakCards()
            strt = None
            twoPair = None
            val = self.straight(hand)
            if val[0] > 0:
                if val[1]: 
                    totals.append((8,val[0]))
                    continue
                else: strt = (4,val[1])
            val = self.nKind(hand,4,False)
            if val[0]: 
                totals.append((7,val[1]))
                continue
            val = self.fullHouse(hand, False)
            if val[0]:  
                totals.append((6,val[1]))
                continue
            val = self.nKind(hand, 5, True)
            if val[0]:
                totals.append((5,val[1]))
                continue
            if strt != None:
                totals.append(strt)
                continue
            val = self.nKind(hand, 3, False)
            if val[0]:
                totals.append((3,val[1]))
                continue
            val = self.fullHouse(hand, True)
            if val[0]: 
                totals.append((2,val[1],val[2]))
                continue
            val = self.nKind(hand, 2, False)
            if val[0]:
                totals.append((1,val[1]))
                continue
            totals.append((0,self.highCard(hand)))

        winners = None
        bHand = None
        for i,pHand in enumerate(totals):
            if bHand == None:
                winners = [self.players[i]]
                bHand = pHand
            elif pHand[0] > bHand[0]:
                winners = [self.players[i]]
                bHand = pHand
            elif pHand[0] == bHand[0]:
                if pHand[1] > bHand[1] or (len(pHand) == 3 and pHand[2] > bHand[2]): 
                    winners = [self.players[i]]
                    bHand = pHand
                elif (pHand[1] == bHand[1] and len(pHand) ==2) or (len(pHand) == 3 and pHand[1] == bHand[1] and pHand[2] == bHand[2]):
                    winners.append(self.players[i])

        if len(winners) != 1: self.winner = .5
        else: self.winner = winners[0].getindex()
        self.roundOver = True


CARD_SUITES = {0: 's', 1: 'h', 2: 'c', 3: 'd'}
CARD_VALUES = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9:'9', 10: 'T', 11:'J', 12:'Q', 13: 'K'}
def convertCards(cards):
    newCards = []
    for card in cards:
        suite = CARD_SUITES[card[0]]
        value = CARD_VALUES[card[1]]
        newCards.append(value+suite)
    return newCards

def findProbWinning(self, player):
    board_state = None
    if len(self.river) != 0:
        board_state = convertCards(self.river)
    hand = convertCards(player.peakCards()) + " ?" + " ?"
    prob_winning = parallel_holdem_calc.calculate(board_state, False, 1, hand, False)
    return prob_winning

def convertToDeuces(cards):
    newCards = []
    for card in cards:
        suit = CARD_SUITES[card[0]]
        value = CARD_VALUES[card[1]]
        #print str(value + suit)
        newCards.append(Card.new(str(value + suit)))
    return newCards

def findDeucesProbWinning(sim, player):
    # print sim.river, player.cards, sim.roundOver, sim.winner
    board = None
    if len(sim.river) != 0:
        board = convertToDeuces(sim.river)
    else:
        return 0
    hand = convertToDeuces(player.peakCards())
    evaluator = Evaluator()
    prob_winning = evaluator.evaluate(board, hand)
    return prob_winning


#prob winning, playerRank, opponentraises, pre-flop rating, bet/holdings, turn
def feature_extractor(sim, player):
    state = np.empty([5,1])
    # probability of winning given hand
    state[0] = (findDeucesProbWinning(sim, player))
    # player rank
    opponent = 1
    if player.getindex() == 1: opponent = 0
    if sim.players[opponent].getChipCount > player.getChipCount: state[1] = 0
    else: state[1] = 1
    # opponent raises 
    state[2] = sim.players[opponent].getNumRaises()
    # preflop rating
    #state.append(preFlopRate(player))
    # turn number
    state[3] = len(sim.river)
    # curRaise/holdings 
    if player.getChipCount() != 0:
        ratio = sim.curRaise/float(player.getChipCount())
        if ratio > 1: ratio = 1
    else: ratio = 1
    state[4] = int(100*ratio)
    return state.astype(np.float32)

## Use github prob like this:
# parallel_holdem_calc.calculate(None, True, 1, None, ["8s", "7s", "Ad", "Ac"], False)
# where params are (Board state, "Exact param" should be false, num iters of Monte Carlo sim, Filename - should be false,
#   Hole cards (2 for each player), verbose - should be false)
# return is array of [ (prob of tie), (prob of player 1 winning), (prob of player 2 winning), ... etc]

def playTurn(sim, first, second):
    while True:
        sim.takeAction(sim.players[first]) 
        if sim.roundOver: break
        sim.takeAction(sim.players[second])
        if sim.roundOver or sim.curRaise == 0: break

def playGame(sim):
    first = 0
    second = 1
    while True:
        temp = int(first)    # switches who bets first
        first = int(second)
        second = int(temp)
        sim.resetRound()
        if sim.gameOver(): break
        # print sim.pot, "0:",sim.players[0].chips, "1:", sim.players[1].chips

        playTurn(sim, first, second)
        # print sim.pot, "0:",sim.players[0].chips, "1:", sim.players[1].chips
        if sim.roundOver: continue

        sim.river.append(sim.deck.getRandomCard())
        sim.river.append(sim.deck.getRandomCard())
        sim.river.append(sim.deck.getRandomCard())
        playTurn(sim, first, second)
        # print sim.pot, "0:",sim.players[0].chips, "1:", sim.players[1].chips
        if sim.roundOver: continue

        sim.river.append(sim.deck.getRandomCard())
        playTurn(sim, first, second)
        # print sim.pot, "0:",sim.players[0].chips, "1:", sim.players[1].chips
        if sim.roundOver: continue

        sim.river.append(sim.deck.getRandomCard())
        playTurn(sim, first, second)
        # print sim.pot, "0:",sim.players[0].chips, "1:", sim.players[1].chips
        if sim.roundOver: continue

        sim.decideRound()


def main():
    sim = HoldemSimulator(2,2000,1)
    for i in range(10000):
        playGame(sim)
        print sim.wins, sim.games
        sys.stdout.flush()
        sim.resetGame()
    sim.qlearn.printWeights()
    print sim.wins, sim.games
    print sim.folds, sim.actions
    sim.qlearn.saveWeight()

    
if __name__ == "__main__":
    main()
