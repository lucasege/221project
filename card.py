class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def getSuit(self):
        return self.suit

    def getValue(self):
        return self.value

    def __repr__(self):
        return str(self.suit) + ", " + str(self.value)

    def __str__(self):
        return str(self.suit) + ", " + str(self.value)