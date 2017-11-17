from card import Card

class Deck:

    def __init__(self):
        self.cards = [ \
            [Card(0, "A"), Card(0, "2"), Card(0, "3"), Card(0, "4"), Card(0, "5"), Card(0, "6"), Card(0, "7"), Card(0, "8"), Card(0, "9"), Card(0, "10"), Card(0, "J"), Card(0, "Q"), Card(0, "K")], \
            [Card(1, "A"), Card(1, "2"), Card(1, "3"), Card(1, "4"), Card(1, "5"), Card(1, "6"), Card(1, "7"), Card(1, "8"), Card(1, "9"), Card(1, "10"), Card(1, "J"), Card(1, "Q"), Card(1, "K")], \
            [Card(2, "A"), Card(2, "2"), Card(2, "3"), Card(2, "4"), Card(2, "5"), Card(2, "6"), Card(2, "7"), Card(2, "8"), Card(2, "9"), Card(2, "10"), Card(2, "J"), Card(2, "Q"), Card(2, "K")], \
            [Card(3, "A"), Card(3, "2"), Card(3, "3"), Card(3, "4"), Card(3, "5"), Card(3, "6"), Card(3, "7"), Card(3, "8"), Card(3, "9"), Card(3, "10"), Card(3, "J"), Card(3, "Q"), Card(3, "K")], \
        ]