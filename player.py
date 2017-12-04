class Player:
	def __init__(self, startingAmount, index, isComputer):
		self.chips = startingAmount
		self.index = index
		self.cards = []
		self.totalBets = 0
		self.isComputer = isComputer

	def __repr__(self):
		return str(self.index) + ", " + str(self.chips)

	def __str__(self):
		return str(self.index) + ", " + str(self.chips)

	def peakCards(self): return self.cards

	def getChipCount(self): return self.chips

	def getindex(self): return self.index

	def dealCard(self, card): self.cards.append(card)

	def takeCards(self): self.cards = []

	def totalBet(self): return self.totalBets

	def isComputer(self): return self.isComputer

	def bet(self, amount):
		if amount <= self.chips:
			self.chips -= amount
			self.totalBets += amount

	def winRound(self, totalWinnings): self.chips += totalWinnings
