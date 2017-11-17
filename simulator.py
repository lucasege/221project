from deck import Deck
from player import Player

class HoldemSimulator:
	def __init__(self, numPlayers, startAmount):
		self.startAmount = startAmount
		self.numPlayers = numPlayers
		self.deck = Deck()
		self.players = []
		self.river = []
		for i in range(self.numPlayers): self.players.append(Player(i,startAmount))

	def newRound(self):
		self.deck = Deck()
		for player in self.players:
			player.takeCards()
			if player.getChipCount > 0:
				player.dealCard(self.deck.getRandomCard())
				player.dealCard(self.deck.getRandomCard())

	# def getWinningHand(self, hands):
		

def main():
	game = HoldemSimulator(4, 1000)
	maxIterations = 1000
	for i in range(maxIterations)
		game.newRound()

	for player in game.players:
		print player.cards


if __name__ == "__main__":
	main()