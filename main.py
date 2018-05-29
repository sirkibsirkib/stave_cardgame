import random
from typing import Dict, Tuple, List, Set
import sys

## TYPE ALIASES
Card = (bool, int)
Pos = Tuple[int, int]
Color = int

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
	def col_value(card:Card, color:Color) -> int:
		assert(0 <= color < 3)
		return CardDatabase.card_tups[card[1]][color]

	@staticmethod
	def r(card:Card) -> int: return CardDatabase.col_value(card, 0)

	@staticmethod
	def g(card:Card) -> int: return CardDatabase.col_value(card, 1)

	@staticmethod
	def b(card:Card) -> int: return CardDatabase.col_value(card, 2)


class PlayerCards:
	def __init__(self, deck:set, player_bool:bool, init_hand_size:int):
		self.deck_sequence = list(map(lambda c: (player_bool, c), deck))
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
		self.stave_cols = [None for _ in range(3)]

	def get_card(self, pos:Pos) -> Card:
		return self.grid[pos[0]][pos[1]]

	def remove_card(self, pos:Pos) -> Card:
		card = self.grid[pos[0]][pos[1]]
		self.grid[pos[0]][pos[1]] = None
		if self.stave_is_empty(pos[0]):
			self.stave_cols[pos[0]] = None
		return card

	def stave_is_empty(self, stave_id:int) -> bool:
		return all(x is None for x in self.grid[stave_id])\

	@staticmethod
	def card_color(card:Card) -> Color:
		cols = [CardDatabase.r(card), CardDatabase.g(card), CardDatabase.b(card)]
		return cols.index(max(cols))

	def action_place(self, player_cards:PlayerCards, hand_index:int, pos:Pos):
		card = player_cards.remove_from_hand(hand_index)
		self.insert_card(card, pos)
		

	def insert_card(self, card:Card, pos:Pos):
		assert(card is not None)
		if self.stave_is_empty(pos[0]):
			self.stave_cols[pos[0]] = Board.card_color(card)
		self.grid[pos[0]][pos[1]] = card

	def background_str(self, stave_id:int) -> str:
		col = self.stave_cols[stave_id]
		return "      {}        ".format('#' if col is None else {0:'r', 1:'g', 2:'b'}[col])


	def action_slide(self, src:Pos, dest:Pos):
		attacker = self.get_card(src)
		assert(attacker is not None)
		assert(abs(src[0]-dest[0]) == 1) # one stave apart
		assert(src[1]==dest[1]) # in line horizontally
		src_col, dest_col = self.stave_cols[src[0]], self.stave_cols[dest[0]]
		assert(src_col is not None)
		assert(dest_col is not None)
		assert(CardDatabase.col_value(attacker, src_col) > CardDatabase.col_value(attacker, dest_col))
		defender = self.get_card(dest)
		if defender is None or CardDatabase.col_value(defender, src_col) <= CardDatabase.col_value(attacker, src_col):
			# move successful
			self.insert_card(attacker, dest)
		self.remove_card(src)

	def display(self):

		for stave_id in range(3):
			sys.stdout.write(self.background_str(stave_id))
		print()
		for slot_id in range(3):
			for stave_id in range(3):
				pos = (stave_id, slot_id)
				card = self.get_card(pos)
				if card is None:
					sys.stdout.write(self.background_str(stave_id))
				else:
					sys.stdout.write(display_card(card))

			print()
			for stave_id in range(3):
				sys.stdout.write(self.background_str(stave_id))
			print()


def display_card(card:Card):
	return "{}: #{} ({},{},{})  ".format(
		"p" if card[0] else "o",
		card[1],
		CardDatabase.r(card),
		CardDatabase.g(card),
		CardDatabase.b(card),
	)


def display_player_cards(player_cards:PlayerCards):
	x = player_cards.deck_cards_remaining()
	print("["* x + " {} ]".format(x))
	for card in player_cards.hand:
		print(display_card(card))
	print()


def play(player_deck:Set[int], opponent_deck:Set[int], seed:int):
	random.seed(seed)
	player_cards = PlayerCards(player_deck, True, init_hand_size=3)
	opponent_cards = PlayerCards(opponent_deck, False, init_hand_size=3)
	board = Board()

	board.action_place(player_cards, 0, (0,0))
	board.action_place(player_cards, 0, (1,0))
	board.action_place(opponent_cards, 0, (2,1))
	board.display()
	display_player_cards(player_cards)
	display_player_cards(opponent_cards)
	board.action_slide((0,0), (1,0))
	board.display()
	display_player_cards(player_cards)
	display_player_cards(opponent_cards)


#### TEST
p = {1,2,3,4,5,6}
o = {4,5,6,7,8}
play(p, o, 5)