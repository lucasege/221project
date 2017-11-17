from card import Card

class Player:
	def __init__(self, startingAmount, index):
		self.chips = startingAmount
		self.index = index
		self.cards = []

	def __repr__(self):
		return str(self.index) + ", " + str(self.chips)

	def __str__(self):
		return str(self.index) + ", " + str(self.chips)

	def peakCards(self): return self.cards

	def getChipCount(self): return self.suit

	def getindex(self): return self.index

	def dealCard(self, card): self.cards.append(card)

	def takeCards(self): self.cards = []

	def bet(self, amount): 
		if amount <= self.chips: self.chips -= amount

	def winRound(self, totalWinnings): self.chips += totalWinnings

