 # def newDeal(self):
    #     self.pot = 0
    #     self.curRaise = 0
    #     self.turn = 0
    #     self.dealCards()
    #     for i in range(TURNS):
    #         self.newRound()
    #         self.roundResults()
    #         self.turn += 1

    # def dealCards(self):
    #     for player in self.players:
    #         if player.getChipCount <= 0: continue
    #         player.dealCard(self.deck.getRandomCard())
    #         player.dealCard(self.deck.getRandomCard())

    # def newRound(self):
    #     for index, player in enumerate(self.players):
    #         if player.cards == []: continue # Previous Fold
    #         self.takeAction(player)

    # def roundResults(self):
    #     if self.turn == 0:
    #         for i in range(FLOP):
    #             self.river.append(self.deck.getRandomCard())
    #     elif self.turn <= 2: self.river.append(self.deck.getRandomCard())
    #     else: self.decideGame()
    #     print " "
    #     print "River Cards: ", self.river


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

