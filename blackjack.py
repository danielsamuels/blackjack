# coding=utf8
import click
import itertools
from random import shuffle

VALUES = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
# VALUES = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 8, 9, 10, 'J', 'Q', 'K']

SUITS = [u'♠', u'♣', u'♥', u'♦']
DECK = [
    (suit, value)
    for suit in SUITS
    for value in VALUES
]

assert len(VALUES) == 13
assert len(SUITS) == 4
assert len(DECK) == 52

def sum_cards(cards):
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


def draw_card(generated_deck, hand):
    hand.append(generated_deck.pop(0))
    return hand


def run_dealer_turn(cards):
    # Dealer hits on <17 and soft 17.

    hand_value = sum_cards(cards)

    print hand_value

    if len(hand_value) == 1 and hand_value[0] < 17:
        # Draw card.
        pass
    elif len(hand_value) == 2:
        if hand_value[1] < 17:
            # Draw card.
            pass

    print hand_value


@click.command()
@click.option('--decks', default=6, help='Number of decks')
@click.option('--players', default=1, help='Number of players')
def play(decks, players):
    # Generate our decks.
    generated_deck = []
    for index in range(decks):
        generated_deck.extend(DECK)

    assert len(generated_deck) == 52 * decks

    # Shuffle the deck.
    shuffle(generated_deck)

    print 'Place your bets please..'
    print

    # Deal out a card to each player and the dealer.
    player_cards = {}
    dealer_cards = []

    for player in range(players):
        player_cards[player] = [
            generated_deck.pop(0)
        ]

    dealer_cards = [
        generated_deck.pop(0)
    ]

    # Deal a second card to the players and the dealer.
    for player in range(players):
        player_cards[player].append(generated_deck.pop(0))

        print u'Player {} has {} {}'.format(
            player,
            ', '.join(u'{} of {}'.format(card[1], card[0]) for card in player_cards[player]),
            repr(sum_cards(player_cards[player]))
        )

        # Was there a Blackjack for this player?
        if 21 in sum_cards(player_cards[player]):
            print 'BLACKJACK!'

    dealer_cards.append(generated_deck.pop(0))


    if 21 in sum_cards(dealer_cards):
        print u'Dealer has {} of {} and {} of {} {}'.format(
            dealer_cards[0][1],
            dealer_cards[0][0],
            dealer_cards[1][1],
            dealer_cards[1][0],
            repr(sum_cards(dealer_cards))
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
            player_cards[0].append(generated_deck.pop(0))

            print u'Player {} has {} {}'.format(
                0,
                ', '.join(u'{} of {}'.format(card[1], card[0]) for card in player_cards[0]),
                repr(sum_cards(player_cards[0]))
            )

            if max(sum_cards(player_cards[0])) > 21:
                print 'BUST!'
                break
        elif action == 's':
            # At this point, we would make sure that all players have either
            # stood, doubled, gone bust or got blackjack. Play out the dealer.
            run_dealer_turn(dealer_cards)

            player = max(sum_cards(player_cards[0]))
            dealer = max(sum_cards(dealer_cards))

if __name__ == '__main__':
    play()
