# coding=utf8
import click
import itertools
from random import shuffle

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

    decks = 6
    players = 1
    generated_deck = []

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def sum_cards(self, cards):
        total = 0

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
        return [non_aces + 11 + len(aces) - 1]


    def draw_card(self, hand):
        drawn_card = self.generated_deck.pop(0)
        hand.append(drawn_card)

        print u'DRAWN: {} of {} {}'.format(
            drawn_card[1],
            drawn_card[0],
            repr(self.sum_cards(hand))
        )

        return hand


    def run_dealer_turn(self, cards):
        # Dealer hits on <17 and soft 17.
        hand_value = self.sum_cards(cards)

        if len(hand_value) == 1 and hand_value[0] < 17:
            # Draw card.
            cards = self.draw_card(cards)

        elif len(hand_value) == 2:
            if hand_value[1] < 17:
                # Draw card.
                cards = self.draw_card(cards)

        hand_value = self.sum_cards(cards)

        if len(hand_value) == 1 and hand_value[0] < 17:
            hand_value = self.run_dealer_turn(cards)
        elif len(hand_value) > 1:
            if hand_value[1] >= 17:
                return [hand_value[1]]

        return hand_value

    def play(self):
        # Generate our decks.
        for index in range(self.decks):
            self.generated_deck.extend(DECK)

        assert len(self.generated_deck) == 52 * self.decks

        # Shuffle the deck.
        shuffle(self.generated_deck)

        print 'Place your bets please..'
        print

        # Deal out a card to each player and the dealer.
        player_cards = {}
        dealer_cards = []

        for player in range(self.players):
            player_cards[player] = [
                self.generated_deck.pop(0)
            ]

        dealer_cards = [
            self.generated_deck.pop(0)
        ]

        # Deal a second card to the players and the dealer.
        for player in range(self.players):
            player_cards[player].append(self.generated_deck.pop(0))

            print u'Player {} has {} {}'.format(
                player,
                ', '.join(u'{} of {}'.format(card[1], card[0]) for card in player_cards[player]),
                repr(self.sum_cards(player_cards[player]))
            )

            # Was there a Blackjack for this player?
            if 21 in self.sum_cards(player_cards[player]):
                print 'BLACKJACK!'

        dealer_cards.append(self.generated_deck.pop(0))


        if 21 in self.sum_cards(dealer_cards):
            print u'Dealer has {} of {} and {} of {} {}'.format(
                dealer_cards[0][1],
                dealer_cards[0][0],
                dealer_cards[1][1],
                dealer_cards[1][0],
                repr(self.sum_cards(dealer_cards))
            )
            print 'DEALER BLACKJACK!'
        else:
            print u'Dealer has {} of {} and ???'.format(
                dealer_cards[0][1],
                dealer_cards[0][0],
            )

        print
        while 1:
            action = click.prompt("What would you like to to?", default='h')

            if action == 'h':
                # Player hits.
                player_cards[0].append(self.generated_deck.pop(0))

                print u'Player {} has {} {}'.format(
                    0,
                    ', '.join(u'{} of {}'.format(card[1], card[0]) for card in player_cards[0]),
                    repr(self.sum_cards(player_cards[0]))
                )

                if max(self.sum_cards(player_cards[0])) > 21:
                    print 'BUST!'
                    break
            elif action == 's':
                # At this point, we would make sure that all players have either
                # stood, doubled, gone bust or got blackjack. Play out the dealer.
                print
                print u'Dealer has {} of {} and {} of {} {}'.format(
                    dealer_cards[0][1],
                    dealer_cards[0][0],
                    dealer_cards[1][1],
                    dealer_cards[1][0],
                    repr(self.sum_cards(dealer_cards))
                )

                self.run_dealer_turn(dealer_cards)

                player = max(self.sum_cards(player_cards[0]))
                dealer = max(self.sum_cards(dealer_cards))

                print
                print 'Player: {}. Dealer: {}.'.format(player, dealer)

                if player > 21:
                    print 'Player went bust. Dealer wins.'
                elif dealer > 21:
                    print 'Dealer went bust. Player wins.'
                elif player > dealer:
                    print 'Player has a higher score.'
                elif dealer > player:
                    print 'Dealer has a higher score.'
                elif dealer == player:
                    print 'Push.'

                print
                break

        click.confirm('Hit Enter to start a new game.', abort=True)


@click.command()
@click.option('--decks', default=6, help='Number of decks')
@click.option('--players', default=1, help='Number of players')
def main(**kwargs):
    game = Blackjack(**kwargs)
    game.play()


if __name__ == '__main__':
    main()
