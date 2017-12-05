from deck import Deck
from player import Player
import random, collections, math, itertools
from collections import Counter
import parallel_holdem_calc
import holdem_calc
import qlearning
from deuces import Card, Evaluator

FLOP = 3
TURN = 1
RIVER = 1
TURNS = 4
TOTAL_POSSIBLE_CARDS = 7

class HoldemSimulator:
    def __init__(self, numPlayers, startAmount, numComputers):
        self.numPlayers = numPlayers
        self.startAmount = startAmount
        self.deck = Deck()
        self.players = []
        self.river = []
        self.pot = 0
        self.curRaise = 0
        self.discardPile = []
        self.roundOver = False
        self.gameOver = False
        self.weights = [[range(10)],[range(11,20)],[range(21,30)]]
        i = 0
        for i in range((self.numPlayers - numComputers)): self.players.append(Player(startAmount, i, False))
        for j in range(numComputers): self.players.append(Player(startAmount, i+j+1, True))

    def dealCards(self):
        for player in self.players:
            if player.getChipCount <= 0: continue
            player.dealCard(self.deck.getRandomCard())
            player.dealCard(self.deck.getRandomCard())

    # def bet(self, player):
    #     while True:
    #         amount = input("Amount: ")
    #         if amount > player.getChipCount(): continue
    #         self.curRaise = amount - self.pot
    #         self.pot += amount
    #         player.bet(amount)
    #         return

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
            while True:# j in range(1,5):
                count += 1
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

    # def computerTakeAction(self, player):
        
    def takeAction(self, player):
        while True:
            print "Player ", player.getindex(), " cards are ", player.peakCards()
            # qlearn = qlearning.QLearningAlgorithm(["Raise", "Fold", "Check"], 0.9, feature_extractor, 0.2)

            if player.isComputer: action = self.computerTakeAction(player)
            else: action = raw_input("Take Action (Bet, Fold, Check): ")

            actionL = action.split(",")
            if actionL[0] == "Raise": 
                if len(actionL) == 2 and actionL[1] + self.curRaise < player.getChipCount():
                    player.bet(int(actionL[1]) + self.curRaise)
                    self.pot += self.curRaise + actionL[1]
                    self.curRaise = actionL[1]
                    player.incRaise()
                    break
            if actionL[0] == "Fold": 
                winner = 0
                if player.getindex() == 0: winner = 1
                self.players[winner].winRound(self.pot)
                self.roundOver = True
                break
            if actionL[0] == "Check":
                toPot = self.curRaise
                if curRaise > player.getChipCount(): toPot = player.getChipCount()
                self.pot =+ toPot
                player.bet(toPot)
                self.curRaise = 0
                break
                
            print "Invalid Action, please try again"

    def newDeal(self):
        self.pot = 0
        self.curRaise = 0
        self.turn = 0
        self.dealCards()
        for i in range(TURNS):
            self.newRound()
            self.roundResults()
            self.turn += 1

    def newRound(self):
        for index, player in enumerate(self.players):
            if player.cards == []: continue # Previous Fold
            self.takeAction(player)

    #sf:8, 4k:7, fh:6, f:5, s:4, 3k:3, 22k:2, 2k:1, h:0
    def decideGame(self):
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

        for player in winners:
            player.winRound(self.pot/float(len(winners)))
            print "Player ", player, " won ", self.pot/float(len(winners))

    def roundResults(self):
        if self.turn == 0:
            for i in range(FLOP):
                self.river.append(self.deck.getRandomCard())
        elif self.turn <= 2: self.river.append(self.deck.getRandomCard())
        else: self.decideGame()
        print " "
        print "River Cards: ", self.river

    # used to test simulator
    def test(self):
        self.players[0].dealCard((1,1))
        self.players[0].dealCard((3,3))
        self.players[1].dealCard((2,2))
        self.players[1].dealCard((3,7))

        self.river.append((0,3))
        self.river.append((0,1))
        self.river.append((1,2))
        self.river.append((0,9))
        self.river.append((1,9))

def gameExplanation():
    print "EXPLAIN RULES OF GAME, (SUITE: 0 = SPADES, 1 = HEARTS, 2 = CLUBS, 3 = DIAMONDS, CARD) ETC...."

def main():
    game = HoldemSimulator(2,1000,1)
    game.test()
    # game.decideGame()

    #gameExplanation()
    #numPlayers = input("Number of players: ")
    #startAmount = input("Start Amount: ")
    #numComputer = input("How many of players will be computers? : ")
    # print holdem_calc.calculate(None, False, 1, None, ["8s", "6s", "?", "?"], False)
    # print parallel_holdem_calc.calculate(None, False, 1, None, ["8s", "6s", "?", "?"], False)
    game = HoldemSimulator(2, 1000, 1)
    for i in range(5):
        game.newDeal()
        game.deck = Deck() # Reshuffle Deck
    
if __name__ == "__main__":
    main()

CARD_SUITES = {0: 's', 1: 'a', 2: 'c', 3: 'h'}
CARD_VALUES = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9:'9', 10: '10', 11:'J', 12:'Q', 13: 'K'}
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
        newCards.append(Card.new(str(value + suit)))
    return newCards


def findDeucesProbWinning(self, player):
    board = None
    if len(self.river) != 0:
        board = convertToDeuces(self.river)
    hand = convertToDeuces(player.peakCards())
    evaluator = Evaluator()
    prob_winning = evaluator.evaluate(board, hand)


# def feature_extractor(self, player):
#     features = []
#     prob_winning = findProbWinning(player)
#     features.append(prob_winning[1]) # probability of winning given hand
#     features.append(self.pot)
#     for cur_player in self.players:
#         features.append(cur_player.getChipCount())
#         features.append(cur_player.total_Bet())
#     feautures.append(self.numPlayers)
#     return features

#prob winning, playerRank, opponentraises, pre-flop rating, bet/holdings, turn
def feature_extractor(self, player):
    state = []
    # probability of winning given hand
    state.append(int(findDeucesProbWinning(player)))
    # prob_winning = findDeucesProbWinning(player)
    # state.append(int(findProbWinng(player)[1])) 
    # player rank
    opponent = 1
    if player.getindex() == 1: opponent = 0
    if self.players[opponent].getChipCount > player.getChipCount: state.append(0)
    else: state.append(1) 
    # opponent raises 
    state.append(self.players[opponent].getNumRaises())
    # preflop rating
    #state.append(preFlopRate(player))
    # turn number
    state.append(len(self.river))
    # curRaise/holdings 
    ratio = self.curRaise/float(player.getChipCount())
    if ration > 1: ratio = 1
    state.append(int(100*ratio))
    return state



## Use github prob like this:
# parallel_holdem_calc.calculate(None, True, 1, None, ["8s", "7s", "Ad", "Ac"], False)
# where params are (Board state, "Exact param" should be false, num iters of Monte Carlo sim, Filename - should be false,
#   Hole cards (2 for each player), verbose - should be false)
# return is array of [ (prob of tie), (prob of player 1 winning), (prob of player 2 winning), ... etc]
