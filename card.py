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
    
    # def getValue(self):
    #     # if self.value == "A": ??
    #     #     return 
    #     if self.value in ["A", "J", "Q", "K"]:
    #         return 10
    #     return int(self.value)