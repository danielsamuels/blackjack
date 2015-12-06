# blackjack
Multi-player, multi-hand, multi-deck command-line blackjack game featuring standard blackjack casino rules.

![](https://i.imgur.com/XLdhxvY.png)

### Features:

* Dealer hits on 16 and soft-17s, stands on 17.
* Player can double on 9, 10, 11.
* Player can split infinitely on matching card values.
* Player can have multiple hands each with a different bet.

## Installation

```
git clone https://github.com/danielsamuels/blackjack.git
cd blackjack/
pip install -r requirements.txt
```

## Usage

To start a game with the default 6 decks and 1 player:

```
python blackjack.py
```

## Options

```
Usage: blackjack.py [OPTIONS]

Options:
  --decks INTEGER RANGE    Number of decks
  --players INTEGER RANGE  Number of players
  --help                   Show this message and exit.
```
