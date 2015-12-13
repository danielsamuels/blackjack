# coding=utf8
import click
from random import shuffle
import os

from blackjack import Blackjack


class GUIBlackjack(Blackjack):

    def __init__(self, decks=6, players=1, **kwargs):
        super(GUIBlackjack, self).__init__(decks, players, interactive=True, **kwargs)

    def play(self):
        # Reset everything.
        self.players = []
        self.dealer = []
        self.bets = []
        self.console_width = int(os.popen('stty size', 'r').read().split()[1])

        os.system("clear")

        assert len(self.generated_deck) == 52 * self.num_decks

        for player in range(self.num_players):
            self.active_player = player

            player_hands = click.prompt(
                '{}, how many hands would you like to play?'.format(self.name()),
                default=1,
                type=click.IntRange(1, None, clamp=True)
            )

            self.players.append([[]] * player_hands)
            self.bets.append([[]] * player_hands)

            if self.player_balance[player] < 5:
                print "{}, you don't have enough money to bet. Please deposit more money.".format(self.name())

                self.player_balance[self.active_player] += click.prompt(
                    'How much would you like to deposit?',
                    default=1000,
                    type=click.IntRange(100, None, clamp=True)
                )

            for index, hand in enumerate(self.players[player]):
                self.bets[player][index] = click.prompt(
                    '{}, you have a balance of {}. How much would you like to bet on hand {}?'.format(
                        self.name(),
                        self.player_balance[player],
                        index
                    ),
                    default=int(self.player_balance[player] / 5 * 5 * 0.1),  # Default to 10% of their balance.
                    type=click.IntRange(5, self.player_balance[player], clamp=True)
                )

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

        self.active_player = 0
        self.active_hand = 0

        while self.active_player < len(self.players):
            while self.active_hand < len(self.players[self.active_player]):
                self.render_graphics()

                if self.blackjack() or self.blackjack(self.dealer):
                    action = 's'
                elif max(self.sum_cards()) == 21:
                    action = 's'
                elif max(self.sum_cards()) > 21:
                    action = 's'
                else:
                    action = None

                    while not action:
                        print 'Options: [h]it, [s]tand{}{}'.format(
                            ', [d]ouble' if len(self.hand()) == 2 and max(self.sum_cards()) in [9, 10, 11] else '',
                            ', s[p]lit' if len(self.hand()) == 2 and self.card_value(self.hand()[0][1]) == self.card_value(self.hand()[1][1]) else ''
                        )
                        action = click.prompt("{}, what would you like to to?".format(
                            self.name()
                        ), default='h')

                        if action == 'h' and max(self.sum_cards()) >= 17:
                            if not click.confirm('{}, you have {}, are you sure you want to hit?'.format(
                                self.name(),
                                max(self.sum_cards())
                            )):
                                action = None
                        elif action == 'd':
                            # Can this player actually double?
                            if len(self.hand()) != 2:
                                action = None

                            if max(self.sum_cards()) not in [9, 10, 11]:
                                action = None
                        elif action == 'p':
                            if len(self.hand()) != 2:
                                action = None

                            if self.card_value(self.hand()[0][1]) != self.card_value(self.hand()[1][1]):
                                action = None

                if action == 'h':  # Hit
                    # Player hits.
                    self.draw_card()
                elif action == 'd':  # Double
                    # Double the bet for this user, draw one card, then stand.
                    self.player_balance[self.active_player] -= self.bets[self.active_player][self.active_hand]
                    self.bets[self.active_player][self.active_hand] *= 2
                    self.draw_card()

                    if self.active_hand == len(self.players[self.active_player]) - 1:
                        self.active_hand = 0
                        self.active_player += 1
                        break
                    else:
                        self.active_hand += 1
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
                    if self.active_hand == len(self.players[self.active_player]) - 1:
                        self.active_hand = 0
                        self.active_player += 1
                        break
                    else:
                        self.active_hand += 1

        # At this point, we would make sure that all players have either
        # stood, doubled, gone bust or got blackjack. Play out the dealer.

        # If there's only one player in the game and that player has
        # gone bust, the dealer only needs to reveal their cards.
        if len(self.players) == 1 and len(self.players[0]) == 1 and max(self.sum_cards(self.players[0][0])) > 21:
            self.render_graphics(show_all=True)
        else:
            self.run_dealer_turn()
            self.render_graphics(show_all=True)

        # Work out who has won and who has lost.
        dealer_score = max(self.sum_cards(self.dealer))

        for player in range(self.num_players):
            self.active_player = player

            for hand, _ in enumerate(self.players[player]):
                self.active_hand = hand

                player_score = max(self.sum_cards())

                if self.blackjack(self.dealer) and not self.blackjack():
                    print '[{}, Hand {}] Dealer has blackjack. Dealer wins.'.format(self.name(), hand)
                elif self.blackjack() and not self.blackjack(self.dealer):
                    print '[{}, Hand {}] Player has blackjack. Player wins.'.format(self.name(), hand)
                    self.player_balance[player] += self.bets[player][hand] * 2.5
                elif player_score > 21:
                    print '[{}, Hand {}] Player went bust. Dealer wins.'.format(self.name(), hand)
                elif dealer_score > 21:
                    print '[{}, Hand {}] Dealer went bust. Player wins.'.format(self.name(), hand)
                    self.player_balance[player] += self.bets[player][hand] * 2
                elif player_score > dealer_score:
                    print '[{}, Hand {}] Player has a higher score. Player wins.'.format(self.name(), hand)
                    self.player_balance[player] += self.bets[player][hand] * 2
                elif dealer_score > player_score:
                    print '[{}, Hand {}] Dealer has a higher score. Dealer wins.'.format(self.name(), hand)
                elif dealer_score == player_score:
                    print '[{}, Hand {}] Push.'.format(self.name(), hand)
                    self.player_balance[player] += self.bets[player][hand]

        print

        if click.confirm('Play again?', default=True, abort=True):
            self.play()

    def render_graphics(self, show_all=False):
        os.system("clear")
        graphics = []

        if self.blackjack(self.dealer):
            graphics.append(['DEALER HAND {}'.format(
                repr(self.sum_cards(self.dealer))
            ).center(13 + (len(self.dealer) - 1) * 6)])

            graphics.extend(self.card_graphics(self.dealer, include_bets=True))
        else:
            if show_all:
                graphics.append(['DEALER HAND {}{}'.format(
                    repr(self.sum_cards(self.dealer)),
                    ' - BUST' if max(self.sum_cards(self.dealer)) > 21 else
                    ' - BLACKJACK' if self.blackjack(self.dealer) else ''
                ).center(13 + (len(self.dealer) - 1) * 6)])

                graphics.extend(self.card_graphics(self.dealer))
            else:
                graphics.append(['DEALER HAND {}'.format(
                    repr(self.sum_cards(self.dealer, dealer=True))
                ).center(13 + (len(self.dealer) - 1) * 6)])

                graphics.extend(self.card_graphics(self.dealer, dealer=True))

        for player, hands in enumerate(self.players):
            for hand, _ in enumerate(hands):
                current_hand = self.hand(player, hand)
                sum_cards = self.sum_cards(current_hand)

                graphics.append([''])
                graphics.append(['{}{}'.format(
                    '{} HAND {} - {}{}'.format(
                        self.player_names[player].upper(),
                        hand,
                        repr(self.sum_cards(self.hand(player, hand))),
                        ' - BUST' if max(sum_cards) > 21 else
                        ' - BLACKJACK' if self.blackjack(current_hand) else '',
                    ).center(13 + (len(current_hand) - 1) * 6),
                    ' <<<' if self.active_player == player and self.active_hand == hand else ''
                )])

                graphics.extend(self.card_graphics(current_hand))

        # We need to add the players current balances and bets at the top right.
        # We'll generate the box and then add it to each line programatically.

        bet_box = []
        for player in range(self.num_players):
            bet_box.append(self.player_names[player])
            bet_box.append('Balance: {}'.format(self.player_balance[player]))
            bet_box.append('Current bet: {}'.format(sum(self.bets[player])))

            if player < self.num_players - 1:
                bet_box.append('')

        max_line_length = max(len(line) for line in bet_box)

        bet_box.insert(0, '+{}+'.format('-' * (max_line_length + 2)))
        bet_box.append('+{}+'.format('-' * (max_line_length + 2)))

        for index, line in enumerate(bet_box):
            if index != 0 and index != len(bet_box) - 1:
                bet_box[index] = '| {} |'.format(line.ljust(max_line_length))

        for index, contents in enumerate(bet_box):
            # Append each bet box line to the end of the graphics lines.
            # Add some spacing.
            current_line_length = sum(len(item) for item in graphics[index])

            spacing_required = self.console_width - current_line_length - len(contents)

            graphics[index].append(' ' * spacing_required)
            graphics[index].append(contents)

        for line in graphics:
            print ''.join(line)

        print

    def card_graphics(self, hand=None, dealer=False, include_bets=False):
        # +---- +-----------+
        # | A   | 10        |
        # | ♠   | ♠         |
        # |     |           |
        # |     |           |
        # |     |           |
        # |     |         ♠ |
        # |     |        10 |
        # +---- +-----------+

        if not hand:
            hand = self.hand()

        lines = [[], [], [], [], [], [], [], [], []]

        for index, card in enumerate(hand):
            if index == len(hand) - 1:
                if dealer and len(hand) == 2:
                    # Hide this card.
                    card = ('?', '?')

                # Full card
                lines[0].append('+-----------+')
                lines[1].append('| {}        |'.format(str(card[1]).ljust(2)))
                lines[2].append(u'| {}         |'.format(card[0]))
                lines[3].append('|           |')
                lines[4].append('|           |')
                lines[5].append('|           |')
                lines[6].append(u'|         {} |'.format(card[0]))
                lines[7].append('|        {} |'.format(str(card[1]).rjust(2)))
                lines[8].append('+-----------+')
            else:
                # Partial card
                lines[0].append('+---- ')
                lines[1].append('| {}  '.format(str(card[1]).ljust(2)))
                lines[2].append(u'| {}   '.format(card[0]))
                lines[3].append('|     ')
                lines[4].append('|     ')
                lines[5].append('|     ')
                lines[6].append('|     ')
                lines[7].append('|     ')
                lines[8].append('+---- ')

        return lines
