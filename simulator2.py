from deck import Deck
from player import Player
import random, collections, math, itertools

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

    #def fourKind(self, hand):
    #def straight(self, hand):
    #def royalFlush(self, hand):
    #def flush(self, hand):
    #def triples(self, hand):

    def pairs(self, hand):
        for i in len(hand):
            for j in len(hand):
                if hand[i] == hand[j+i]:
                     return self.weights[3][hand[i]]

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
        print len(possibleHands)
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

    def endGame(self):
        totals = []
        for i, player in enumerate(self.players()):
            cards = player.peakCards()
            total[i] = cards[0][0] + cards[0][1] + cards[1][0] + cards[1][1]
        winner = self.players(totals.index(max(totals)))
        winner.winRound(self.pot)
        print "Player ", winner, " won ", self.pot

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
