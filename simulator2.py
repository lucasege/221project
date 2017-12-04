from deck import Deck
from player import Player
import random, collections, math, itertools
from collections import Counter

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
        self.weights = [[range(10)],[range(11,20)],[range(21,30)]]
        for i in range((self.numPlayers - numComputers)): self.players.append(Player(startAmount, i, False))
        for j in range(numComputers): self.players.append(Player(startAmount, i+j+1, True))

    def dealCards(self):
        for player in self.players:
            if player.getChipCount <= 0: continue
            player.dealCard(self.deck.getRandomCard())
            player.dealCard(self.deck.getRandomCard())

    def bet(self, player):
        while True:
            amount = input("Amount: ")
            if amount > player.getChipCount(): continue
            self.curRaise = amount - self.pot
            self.pot += amount
            player.bet(amount)
            return

    def straight(self, hand):
        total = hand + self.river
        if len(total) < 5: return False
        sTotal = [(card[1],card[0]) for card in total].sort()
        best = 0
        bHand = []
        flush = False
        for i in range(len(total)-4):
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

    # also finds flush
    def nKind(self, hand, N, flush):
        allCards = self.river + hand
        index = 1
        if flush: index = 0
        values = [int(i[index]) for i in allCards]
        count = Counter(values)
        for key in count:
            if count[key] == N: return (True, key)
        return (False, None)

    def fullHouse(self, hand):
        allCards = self.river + hand
        values = [int(i[1]) for i in allCards]
        count = Counter(values)
        triple = None
        for key in count:
            if count[key] == 3:
                triple = key
        for key in count:
            if count[key] == 2 and key != triple:
                return (True,triple)
        return (False, None)

    def getHandValues(self, hand):
        hand = list(hand)
        values = [card[1] for card in hand]
        values.sort(reverse = True)
        return values

    def highCard(self, hand):
        return max(hand)

    #checks = [str.royalFlush, str.stFlush, str.fourKind, str.fullHouse, str.flush, str.straight, str.threeKind, str.pairs, str.highCard]
    def computeHandValue(self, player, possibleHands):
        handValue = 0
        checks = [self.highCard]
        #print len(possibleHands)
        for hand in possibleHands:
            for permutations in itertools.permutations(hand, 5):
                for check in checks:
                    values = self.getHandValues(hand)
                    value = check(values)
                    handValue += value
                    if value: break
                if value: break
        return handValue


    ## Go through possibleHands to sum duplicates!
    def computerTakeAction(self, player):
        possibleHands = []
        deck = Deck()

        for card in player.peakCards():
            deck.cards.remove(card)
        for card in self.river:
            deck.cards.remove(card)
        deck = deck.cards
        for hand in itertools.combinations(iter(deck), TOTAL_POSSIBLE_CARDS - len(player.peakCards()) - len(self.river)):
            possibleHands.append(hand)
        for i, hand in enumerate(possibleHands):
            possibleHands[i] = hand + tuple(player.peakCards())
        handValue = self.computeHandValue(player, possibleHands)
        avgHand = float(handValue)/float(len(possibleHands))
        print avgHand
        if avgHand > 13: return "Bet"
        else: return "Fold"

    def takeAction(self, player):
        while True:
            print "Player ", player.getindex(), " cards are ", player.peakCards()
            if player.isComputer: action = self.computerTakeAction(player)
            else: action = raw_input("Take Action (Bet, Fold, Check): ")
            if action == "Bet": return self.bet(player)
            if action == "Fold": return player.takeCards()
            if action == "Check" and self.curRaise == 0: return
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

    #sf:7, 4k:6, fh:5, f:4, s:3, 3k:2, 2k:1, h:0
    def endGame(self):
        totals = []
        best = None
        for i, player in enumerate(self.players()): 
            hand = player.peakCards()
            straight = None
            val = straight(self, hand)
            if val[0] > 0:
                if val[1]: 
                    totals.append((7,val[0]))
                    continue
                else: straight = (3,val[1])
            val = nKind(self, hand,4,False)
            if val[0]: 
                totals.append((6,val[1]))
                continue
            val = fullHouse(self,hand)
            if val[0]: 
                totals.append((5,val[1]))
                continue
            val = nKind(self, hand, 5, True)
            if val[0]:
                totals.append((4,val[1]))
                continue
            if straight != None:
                totals.append((3,val[0]))
                continue
            val = nKind(self, hand, 3, False)
            if val[0]:
                totals.append((2,val[1]))
                continue
            val = nKind(self, hand, 2, False)
            if val[0]:
                totals.append((1,val[1]))
                continue
            totals.append((0,highCard(self,hand)))

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
                if pHand[1] > bHand[1]: 
                    winners = [self.players[i]]
                    bHand = pHand
                elif pHand[1] == bHand[1]:
                    winners.append(self.players[i])

        for player in winners:
            player.winRound(self.pot/float(len(winners)))
            print "Player ", player, " won ", self.pot/float(len(winners))

    def roundResults(self):
        if self.turn == 0:
            for i in range(FLOP):
                self.river.append(self.deck.getRandomCard())
        elif self.turn <= 2: self.river.append(self.deck.getRandomCard())
        else: self.endGame()
        print " "
        print "River Cards: ", self.river

def gameExplanation():
    print "EXPLAIN RULES OF GAME, (SUITE: 0 = SPADES, 1 = HEARTS, 2 = CLUBS, 3 = DIAMONDS, CARD) ETC...."

def main():
    gameExplanation()
    #numPlayers = input("Number of players: ")
    #startAmount = input("Start Amount: ")
    #numComputer = input("How many of players will be computers? : ")
    game = HoldemSimulator(2, 1000, 1)
    for i in range(5):
        game.newDeal()
        game.deck = Deck() # Reshuffle Deck
main()
