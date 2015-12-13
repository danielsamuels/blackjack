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


class Blackjack(object):

    generated_deck = []
    players = []
    player_balance = []
    dealer = []
    player_names = []
    active_player = 0
    active_hand = 0

    def __init__(self, decks=6, players=1, interactive=True, **kwargs):
        """Set up the game.

        Keyword arguments
        decks -- the number of decks to play with (default 6)
        players -- the number of players in the game (default 1)
        """
        setattr(self, 'num_decks', decks)
        setattr(self, 'num_players', players)
        self.interactive = interactive

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

            if self.interactive:
                self.player_names.append(click.prompt('Player {}, what is your name?'.format(player)))
            else:
                self.player_names.append('Player {}'.format(player))

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


@click.command()
@click.option('--decks', default=6, help='Number of decks', type=click.IntRange(1, 6, clamp=True))
@click.option('--players', default=1, help='Number of players', type=click.IntRange(1, None, clamp=True))
def main(**kwargs):
    from gui import GUIBlackjack
    game = GUIBlackjack(**kwargs)
    game.play()

if __name__ == '__main__':
    main()
