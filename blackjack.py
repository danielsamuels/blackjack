# coding=utf8
import click
import itertools
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
    players = {}
    dealer = []
    active_player = 0

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, 'num_{}'.format(key), kwargs[key])

        # Generate our decks.
        for index in range(self.num_decks):
            self.generated_deck.extend(DECK)

        assert len(self.generated_deck) == 52 * self.num_decks

        # Shuffle the deck.
        shuffle(self.generated_deck)

    def sum_cards(self, cards, dealer=False):
        total = 0

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
        return [len(aces), non_aces + 11 + len(aces) - 1]


    # Draws a card and adds it to the hand in place.
    def draw_card(self, *args):
        if len(args) > 1:
            raise Exception('Too many arguments..')

        drawn_card = self.generated_deck.pop(0)

        if len(args) == 0:
            self.players[self.active_player].append(drawn_card)
        else:
            if args[0] == 'dealer':
                self.dealer.append(drawn_card)
            else:
                self.players[args[0]].append(drawn_card)

        # Put the card at the back of the deck.
        self.generated_deck.append(drawn_card)

    def blackjack(self, hand):
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
        self.players = {}
        self.dealer = []

        assert len(self.generated_deck) == 52 * self.num_decks

        print 'Place your bets please..'
        print

        # Deal out a card to each player and the dealer.
        for player in range(self.num_players):
            self.active_player = player

            self.players[player] = []
            self.draw_card()

        self.draw_card('dealer')

        # Deal a second card to the players and the dealer.
        for player in range(self.num_players):
            self.active_player = player
            self.draw_card()

            # Was there a Blackjack for this player?
            if self.blackjack(self.players[player]):
                print 'BLACKJACK!'

        self.draw_card('dealer')

        self.active_player = 0

        while 1:

            while self.active_player < len(self.players):
                self.render_graphics()

                if self.blackjack(self.players[self.active_player]) or self.blackjack(self.dealer):
                    action = 's'
                elif max(self.sum_cards(self.players[self.active_player])) == 21:
                    action = 's'
                elif max(self.sum_cards(self.players[self.active_player])) > 21:
                    action = 's'
                else:
                    action = click.prompt("Player {}, what would you like to to?".format(
                        self.active_player
                    ), default='h')

                if action == 'h':  # Hit
                    # Player hits.
                    self.draw_card()
                elif action == 'd':  # Double
                    # Double the bet for this user, draw one card, then stand.
                    pass
                elif action == 's':  # Stand
                    self.active_player += 1

            # At this point, we would make sure that all players have either
            # stood, doubled, gone bust or got blackjack. Play out the dealer.

            # If there's only one player in the game and that player has
            # gone bust, the dealer only needs to reveal their cards.
            if len(self.players) == 1 and max(self.sum_cards(self.players[0])) > 21:
                self.render_graphics(show_all=True)
            else:
                self.run_dealer_turn()
                self.render_graphics(show_all=True)

            # Work out who has won and who has lost.
            for player in range(self.num_players):
                player_score = max(self.sum_cards(self.players[player]))
                dealer_score = max(self.sum_cards(self.dealer))

                if self.blackjack(self.dealer) and not self.blackjack(self.players[player]):
                    print '[Player {}] Dealer has blackjack. Dealer wins.'.format(player)
                elif self.blackjack(self.players[player]) and not self.blackjack(self.dealer):
                    print '[Player {}] Player has blackjack. Player wins.'.format(player)
                elif player_score > 21:
                    print '[Player {}] Player went bust. Dealer wins.'.format(player)
                elif dealer_score > 21:
                    print '[Player {}] Dealer went bust. Player wins.'.format(player)
                elif player_score > dealer_score:
                    print '[Player {}] Player has a higher score. Player wins.'.format(player)
                elif dealer_score > player_score:
                    print '[Player {}] Dealer has a higher score. Dealer wins.'.format(player)
                elif dealer_score == player_score:
                    print '[Player {}] Push.'.format(player)

            print
            break

        if click.confirm('Play again?', default=True, abort=True):
            self.play()

    def render_graphics(self, show_all=False):
        os.system("clear")

        if self.blackjack(self.dealer):
            print 'DEALER HAND {}'.format(
                repr(self.sum_cards(self.dealer))
            ).center(13 + (len(self.dealer) - 1) * 6)

            self.card_graphics(self.dealer)
        else:
            if show_all:
                print 'DEALER HAND {}{}'.format(
                    repr(self.sum_cards(self.dealer)),
                    ' - BUST' if max(self.sum_cards(self.dealer)) > 21 else
                    ' - BLACKJACK' if self.blackjack(self.dealer) else ''
                ).center(13 + (len(self.dealer) - 1) * 6)

                self.card_graphics(self.dealer)
            else:
                print 'DEALER HAND {}'.format(
                    repr(self.sum_cards(self.dealer, dealer=True))
                ).center(13 + (len(self.dealer) - 1) * 6)

                self.card_graphics(self.dealer, dealer=True)

        for player in self.players:
            print 'PLAYER {} HAND {}{}'.format(
                player,
                repr(self.sum_cards(self.players[player])),
                ' - BUST' if max(self.sum_cards(self.players[player])) > 21 else
                ' - BLACKJACK' if self.blackjack(self.players[player]) else ''
            ).center(13 + (len(self.players[player]) - 1) * 6)

            self.card_graphics(self.players[player])

    def card_graphics(self, hand, dealer=False):
        # +---- +-----------+
        # | A   | 10        |
        # | ♠   | ♠         |
        # |     |           |
        # |     |           |
        # |     |           |
        # |     |         ♠ |
        # |     |        10 |
        # +---- +-----------+

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

        for line in lines:
            print ''.join(line)

        print

@click.command()
@click.option('--decks', default=6, help='Number of decks', type=click.IntRange(1, 6, clamp=True))
@click.option('--players', default=1, help='Number of players', type=click.IntRange(1, None, clamp=True))
def main(**kwargs):
    game = Blackjack(**kwargs)
    game.play()


if __name__ == '__main__':
    main()
