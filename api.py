from blackjack import Blackjack


class APIBlackjack(Blackjack):
    def __init__(self, **kwargs):
        super(APIBlackjack, self).__init__(interactive=False, **kwargs)

    def setup(self):
        # Reset everything.
        self.players = []
        self.dealer = []
        self.bets = []

        assert len(self.generated_deck) == 52 * self.num_decks

        for player in range(self.num_players):
            self.active_player = player

            player_hands = 1

            self.players.append([[]] * player_hands)
            self.bets.append([[]] * player_hands)

            for index, hand in enumerate(self.players[player]):
                self.bets[player][index] = self.player_balance[player] * 0.1  # Default to 10% of their balance.
                self.player_balance[player] -= self.bets[player][index]

        # Deal out a card to each player and the dealer.
        for player in range(self.num_players):
            self.active_player = player

            for index, hand in enumerate(self.players[player]):
                self.active_hand = index
                self.draw_card()

        self.draw_card('dealer')

        # Deal a second card to the players and the dealer.
        for player in range(self.num_players):
            self.active_player = player

            for index, hand in enumerate(self.players[player]):
                self.active_hand = index
                self.draw_card()

        self.draw_card('dealer')

        return

    def options_available(self, player, hand):
        self.active_player = player
        self.active_hand = hand

        if (self.blackjack() or self.blackjack(self.dealer) or  # If either the player or dealer has Blackjack
            max(self.sum_cards()) > 21):  # If the player has gone bust (in the real world you wouldn't "stand")
            return ['s']

        options = ['h', 's']

        if len(self.hand()) == 2 and max(self.sum_cards()) in [9, 10, 11]:
            options.append('d')

        # if len(self.hand()) == 2 and self.card_value(self.hand()[0][1]) == self.card_value(self.hand()[1][1]):
        #     options.append('p')

        return options

    def perform_action(self, player, hand, action):
        self.active_player = player
        self.active_hand = hand

        if action == 'h':  # Hit
            # Player hits.
            self.draw_card()
        elif action == 'd':  # Double
            # Double the bet for this user, draw one card, then stand.
            self.player_balance[self.active_player] -= self.bets[self.active_player][self.active_hand]
            self.bets[self.active_player][self.active_hand] *= 2
            self.draw_card()
        elif action == 'p':  # Split
            # Take the current hand and split it into two.
            hand = self.hand()
            self.players[self.active_player][self.active_hand] = [hand[0]]
            self.draw_card()

            self.players[self.active_player].insert(self.active_hand + 1, [hand[1]])
            self.bets[self.active_player].insert(self.active_hand + 1, self.bets[self.active_player][self.active_hand])
            self.player_balance[self.active_player] -= self.bets[self.active_player][self.active_hand]

            self.active_hand += 1
            self.draw_card()
            self.active_hand -= 1
        elif action == 's':  # Stand
            pass

    def finish_round(self):
        # At this point, we would make sure that all players have either
        # stood, doubled, gone bust or got blackjack. Play out the dealer.

        # If there's only one player in the game and that player has
        # gone bust, the dealer only needs to reveal their cards.
        if len(self.players) == 1 and len(self.players[0]) == 1 and max(self.sum_cards(self.players[0][0])) > 21:
            pass
        else:
            self.run_dealer_turn()

    def get_status(self, player, hand):
        # Work out who has won and who has lost.
        dealer_score = max(self.sum_cards(self.dealer))

        self.active_player = player
        self.active_hand = hand

        player_score = max(self.sum_cards())

        player_won = None

        if self.blackjack(self.dealer) and not self.blackjack():
            player_won = False
        elif self.blackjack() and not self.blackjack(self.dealer):
            player_won = True
            self.player_balance[player] += self.bets[player][hand] * 2.5
        elif player_score > 21:
            player_won = False
        elif dealer_score > 21:
            player_won = True
            self.player_balance[player] += self.bets[player][hand] * 2
        elif player_score > dealer_score:
            player_won = True
            self.player_balance[player] += self.bets[player][hand] * 2
        elif dealer_score > player_score:
            player_won = False
        elif dealer_score == player_score:
            self.player_balance[player] += self.bets[player][hand]

        return player_won
