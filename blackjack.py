# coding=utf8
import click
from random import shuffle
import os

VALUES = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
SUITS = [u'♠', u'♣', u'♥', u'♦']
DECK = [
    (suit, value)
    for suit in SUITS
    for value in VALUES
]

assert len(VALUES) == 13
assert len(SUITS) == 4
assert len(DECK) == 52


class Blackjack:

    generated_deck = []
    players = []
    player_balance = []
    dealer = []
    player_names = []
    active_player = 0
    active_hand = 0

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, 'num_{}'.format(key), kwargs[key])

        # Generate our decks.
        for index in range(self.num_decks):
            self.generated_deck.extend(DECK)

        assert len(self.generated_deck) == 52 * self.num_decks

        # Shuffle the deck.
        shuffle(self.generated_deck)

        for player in range(self.num_players):
            self.player_balance.append(1000)
            self.player_names.append(click.prompt('Player {}, what is your name?'.format(player)))

    def sum_cards(self, cards=None, dealer=False):
        if not cards:
            cards = self.hand()

        if dealer and len(cards) == 2:
            card = cards[0][1]

            if card in ['J', 'Q', 'K']:
                return [10]
            elif card == 'A':
                return [1, 11]
            return card

        # First deal with any non-Ace cards.
        aces = [card for card in cards if card[1] == 'A']
        non_aces = sum(
            card[1] if card[1] not in ['J', 'Q', 'K'] else 10
            for card in cards
            if card[1] != 'A'
        )

        if not aces:
            return [non_aces]

        # Based on the number of Aces we have, how many can be 1 OR 11?
        if len(aces) == 1:
            if non_aces > 10:
                return [non_aces + 1]
            elif non_aces == 10:
                return [21]
            elif non_aces < 10:
                return [non_aces + 1, non_aces + 11]

        # We have more than one Ace, but we can only ever have one Ace worth 11, but
        # can we even have that given our other cards? We also know that we have at
        # least 2 aces, so we need to be able to spare 12 without going bust.

        if non_aces + 11 + len(aces) - 1 > 21:
            # All aces are worth 1.
            return [non_aces + len(aces)]

        # We can have one 11 and the rest as 1.
        return [non_aces + len(aces), non_aces + 11 + len(aces) - 1]

    def name(self):
        return self.player_names[self.active_player]

    def hand(self, *args):
        from copy import copy

        if args:
            return copy(self.players[args[0]][args[1]])
        return copy(self.players[self.active_player][self.active_hand])

    def card_value(self, card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return [1, 11]
        return card

    # Draws a card and adds it to the hand in place.
    def draw_card(self, *args):
        if len(args) > 1:
            raise Exception('Too many arguments..')

        drawn_card = self.generated_deck.pop(0)

        if len(args) == 0:
            hand = self.hand()
            hand.append(drawn_card)

            self.players[self.active_player][self.active_hand] = hand
        else:
            if args[0] == 'dealer':
                self.dealer.append(drawn_card)
            else:
                raise Exception("You have called `draw_card` wrongly somewhere.")

        # Put the card at the back of the deck.
        self.generated_deck.append(drawn_card)

    def blackjack(self, hand=None):
        if not hand:
            return len(self.hand()) == 2 and max(self.sum_cards()) == 21
        return len(hand) == 2 and max(self.sum_cards(hand)) == 21

    def run_dealer_turn(self):
        # Dealer hits on <17 and soft 17.
        hand_value = self.sum_cards(self.dealer)

        if len(hand_value) == 1 and hand_value[0] < 17:
            # Draw card.
            self.draw_card('dealer')

        elif len(hand_value) > 1:
            if hand_value[1] <= 17:
                # Draw card.
                self.draw_card('dealer')

        hand_value = self.sum_cards(self.dealer)

        # Do we need to draw another card?
        if len(hand_value) == 1 and hand_value[0] < 17:
            hand_value = self.run_dealer_turn()
        elif len(hand_value) > 1:
            if hand_value[1] > 17:
                return [hand_value[1]]
            else:
                hand_value = self.run_dealer_turn()

        return hand_value

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


@click.command()
@click.option('--decks', default=6, help='Number of decks', type=click.IntRange(1, 6, clamp=True))
@click.option('--players', default=1, help='Number of players', type=click.IntRange(1, None, clamp=True))
def main(**kwargs):
    game = Blackjack(**kwargs)
    game.play()


if __name__ == '__main__':
    main()
