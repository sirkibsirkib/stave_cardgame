import random
from typing import Dict, Tuple, List
import sys

## TYPE ALIASES
Card = int
Pos = Tuple[int, int]

class CardDatabase:
	card_tups = {
		0: (0,0,0),
		1: (0,0,1),
		2: (0,1,0),
		3: (0,1,1),
		4: (1,0,0),
		5: (1,0,1),
		6: (1,1,0),
		7: (1,1,1),
		8: (0,0,2),
		9: (2,2,2),
	}

	@staticmethod
	def r(card:Card) -> int:
		return CardDatabase.card_tups[card][0]

	@staticmethod
	def g(card:Card) -> int:
		return CardDatabase.card_tups[card][1]

	@staticmethod
	def b(card:Card) -> int:
		return CardDatabase.card_tups[card][2]


class PlayerCards:
	def __init__(self, deck:set, init_hand_size:int):
		self.deck_sequence = list(deck)
		random.shuffle(self.deck_sequence)
		self.hand = [self.draw() for _ in range(init_hand_size)]

	def draw(self) -> int:
		return self.deck_sequence.pop()

	def remove_from_hand(self, hand_index:int):
		card = self.hand[hand_index]
		del self.hand[hand_index]
		return card
	def deck_cards_remaining(self) -> int:
		return len(self.deck_sequence)
class Board:
	def __init__(self):
		# grid[x][y]
		# grid[stave_id][slot_id]
		self.grid = [[None for _ in range(3)] for _ in range(3)]

	def get_card(self, pos:Pos) -> Card:
		return self.grid[pos[0]][pos[1]]

	def action_place(self, player_cards:PlayerCards, hand_index:int, pos:Pos):
		card = player_cards.remove_from_hand(hand_index)
		self.grid[pos[0]][pos[1]] = card

	def display(self):
		for stave_id in range(3):
			for slot_id in range(3):
				card = self.get_card(pos=(stave_id, slot_id))
				if card is None:
					sys.stdout.write("         `")
				else:
					sys.stdout.write("({},{},{})  `".format(
						CardDatabase.r(card),
						CardDatabase.g(card),
						CardDatabase.g(card),
					))
			sys.stdout.write("\n")

def display_player_cards(player_cards:PlayerCards):
	x = player_cards.deck_cards_remaining()
	print("["* x + " {} ]".format(x))
	for card in player_cards.hand:
		print("[{}_ {}`{}`{}]".format(
			card,
			CardDatabase.r(card),
			CardDatabase.g(card),
			CardDatabase.b(card),
		))
	print()


def play(player_deck:set, opponent_deck:set, seed:int):
	random.seed(seed)
	player_cards = PlayerCards(player_deck, init_hand_size=3)
	opponent_cards = PlayerCards(opponent_deck, init_hand_size=3)
	board = Board()

	board.action_place(player_cards, 0, (0,0))
	board.display()
	display_player_cards(player_cards)
	display_player_cards(opponent_cards)


#### TEST
p = {1,2,3,4,5,6}
o = {4,5,6,7,8}
play(p, o, 5)