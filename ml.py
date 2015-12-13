"""Machine learning Blackjack bot."""
from api import APIBlackjack
import json
import random

# Create a dictionary to store the history of each combination.

"""
history = {
    'A-7J': {
        'h': [True, False, False],  # Won 1/3 games
        's': [True, False, True]  # Won 2/3 games
    }
}
"""

try:
    with open('history.json') as f:
        turn_history = json.load(f)

    print 'Loaded games from history.'
except IOError:
    turn_history = {}
    print 'Unable to load history.'

game_history = []

b = APIBlackjack()

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"

def run():
    player_choices = {}

    # Initialise the game, this sets the bets and draws the initial cards.
    b.setup()

    dealer_hand = max(b.sum_cards(b.dealer))

    # For each of the player hands, figure out what to do.
    for active_player, player in enumerate(b.players):
        player_choices[active_player] = {}

        for active_hand, _ in enumerate(player):
            player_choices[active_player][active_hand] = {}
            action = None

            while action != 's':
                hand = b.hand(active_player, active_hand)

                shorthand = ''.join(sorted([str(card[1]) for card in hand]))

                # print 'Dealer has {}. We have {}.'.format(
                #     b.sum_cards(b.dealer),
                #     b.sum_cards(hand),
                # )

                key = '{}-{}'.format(
                    b.dealer[0][1],
                    shorthand,
                )

                # What options are available to us?
                options = b.options_available(active_player, active_hand)

                # Set baseline option weights.
                weighted_options = []

                # Have we seen this situation before?
                base_weight = 0.1

                if key in turn_history:
                    for option in turn_history[key]:
                        weight = base_weight + sum(filter(None, turn_history[key][option])) / float(len(turn_history[key][option]))
                        weighted_options.append((option, weight))

                for option in options:
                    # Is this option in our weighted options list?
                    found = False

                    for woption in weighted_options:
                        if woption[0] == option:
                            found = True
                            break

                    if found == False:
                        weighted_options.append((option, base_weight))

                action = weighted_choice(weighted_options)

                player_choices[active_player][active_hand][key] = action

                # print 'We have chosen to {}'.format(action)
                b.perform_action(active_player, active_hand, action)

    b.finish_round()

    for active_player, player in enumerate(b.players):
        for active_hand, hand in enumerate(player):
            # print 'Player {} Hand {}'.format(active_player, active_hand)
            status = b.get_status(active_player, active_hand)
            game_history.append(status)

            # if status == True:
            #     print 'Won'
            # elif status == False:
            #     print 'Lost'
            # elif status == None:
            #     print 'Push'

            # Add our choices to the history.
            for choice in player_choices[active_player][active_hand]:
                action = player_choices[active_player][active_hand][choice]

                if choice not in turn_history:
                    turn_history[choice] = {}

                if action in turn_history[choice]:
                    turn_history[choice][action].append(status)
                else:
                    turn_history[choice][action] = [status]

def last_x_games(num):
    print """LAST {} GAMES
    Won: {} ({}%)
    Lost: {} ({}%)
    Push: {} ({}%)
    """.format(
        num,
        len(filter(lambda x: x == True, game_history[-num:])),
        len(filter(lambda x: x == True, game_history[-num:])) / float(len(game_history[-num:])) * 100.0,
        len(filter(lambda x: x == False, game_history[-num:])),
        len(filter(lambda x: x == False, game_history[-num:])) / float(len(game_history[-num:])) * 100.0,
        len(filter(lambda x: x == None, game_history[-num:])),
        len(filter(lambda x: x == None, game_history[-num:])) / float(len(game_history[-num:])) * 100.0,
    )

import os

try:
    while True:
        run()

        if len(game_history) % 50000 == 0:
            os.system('clear')

            # memory = 0

            # for hand in turn_history:
            #     for action in turn_history[hand]:
            #         memory += len(turn_history[hand][action])


            print """ALL TIME
    Played: {}
    Won: {} ({}%)
    Lost: {} ({}%)
    Push: {} ({}%)
            """.format(
                len(game_history),
                len(filter(lambda x: x == True, game_history)),
                len(filter(lambda x: x == True, game_history)) / float(len(game_history)) * 100.0,
                len(filter(lambda x: x == False, game_history)),
                len(filter(lambda x: x == False, game_history)) / float(len(game_history)) * 100.0,
                len(filter(lambda x: x == None, game_history)),
                len(filter(lambda x: x == None, game_history)) / float(len(game_history)) * 100.0,
            )

            last_x_games(10000)
            last_x_games(5000)
            last_x_games(1000)
            last_x_games(500)
            last_x_games(100)
            last_x_games(50)
            last_x_games(10)
except KeyboardInterrupt:
    print 'Writing out games to history.'

    with open('history.json', 'w') as f:
        json.dump(turn_history, f, indent=2)

    print 'Write complete, exiting..'
