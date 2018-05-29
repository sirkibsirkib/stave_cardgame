import random
from typing import Dict, Tuple, List, Set
import time
import sys

## TYPE ALIASES
Card = (bool, int)
Pos = Tuple[int, int]
Color = int

class CardDatabase:
	card_tups = {
		0: (3,2,1),
		1: (1,2,1),
		2: (0,4,1),
		3: (2,2,3),
		4: (3,3,0),
		5: (1,2,3),
		6: (4,1,3),
		7: (5,0,1),
		8: (2,0,2),
		9: (2,3,4),
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
		self.player_bool = player_bool
		self.hand = [self.draw() for _ in range(init_hand_size)]

	def draw_into_hand(self):
		if len(self.deck_sequence) > 0:
			self.hand.push(self.deck_sequence.pop())
			return True
		return False

	def draw(self) -> int:
		return 

	def remove_from_hand(self, hand_index:int):
		card = self.hand[hand_index]
		del self.hand[hand_index]
		return card

	def deck_cards_remaining(self) -> int:
		return len(self.deck_sequence)

	def remove_matching_card_from_hand(self, card:Card):
		for i, c in enumerate(self.hand):
			self.remove_from_hand(i)
			return
		raise ValueError


class Board:
	def __init__(self):
		# grid[x][y]
		# grid[stave_id][slot_id]
		self.grid = [[None for _ in range(3)] for _ in range(3)]
		self.stave_cols = [None for _ in range(3)]
		self.place_used = False

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

	def first_empty_slot(self, owner:bool, stave_id:int) -> int:
		increment = Board.map_owner_to_forward_diff(owner)
		slot_order = [0,1,2] if increment==1 else [2,1,0]
		for slot_id in slot_order:
			pos = (stave_id, slot_id)
			if self.get_card(pos) is None:
				return slot_id
		return None

	def action_place(self, card:Card, stave_id:int, just_testing=False):
		assert(card is not None)
		slot_id = self.first_empty_slot(card[0], stave_id)
		assert(slot_id is not None)
		assert(not self.place_used)
		if just_testing: return True
		self.insert_card(card, pos=(stave_id, slot_id))
		self.place_used = True
		
	def new_turn_begin(self):
		self.place_used = False

	def insert_card(self, card:Card, pos:Pos):
		assert(card is not None)
		if self.stave_is_empty(pos[0]):
			self.stave_cols[pos[0]] = Board.card_color(card)
		self.grid[pos[0]][pos[1]] = card

	def background_str(self, stave_id:int) -> str:
		col = self.stave_cols[stave_id]
		return "      {}        ".format('#' if col is None else {0:'r', 1:'g', 2:'b'}[col])

	@staticmethod
	def map_owner_to_forward_diff(owner:bool) -> int:
		return -1 if owner else 1

	def action_slide(self, src:Pos, dest:Pos, just_testing=False):
		attacker = self.get_card(src)
		assert(attacker is not None)
		assert(abs(src[0]-dest[0]) == 1) # one stave apart
		assert(src[1]==dest[1]) # in line horizontally
		src_col, dest_col = self.stave_cols[src[0]], self.stave_cols[dest[0]]
		assert(src_col is not None)
		assert(dest_col is not None)
		assert(CardDatabase.col_value(attacker, src_col) > CardDatabase.col_value(attacker, dest_col))
		if just_testing: return True
		defender = self.get_card(dest)
		if defender is None or CardDatabase.col_value(defender, src_col) <= CardDatabase.col_value(attacker, src_col):
			# move successful
			self.insert_card(attacker, dest)
		self.remove_card(src)


	def action_forward(self, src:Pos, just_testing=False):
		card = self.get_card(src)
		assert (card is not None)
		dest = (src[0], src[1] + Board.map_owner_to_forward_diff(card[0]))
		assert (0 <= dest[1] < 3)
		assert (self.get_card(dest) is None)
		if just_testing: return True
		self.insert_card(card, dest)
		self.remove_card(src)

	def display(self):
		print()
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

	def yield_positions(self):
		try:
			for stave_id in range(3):
				for slot_id in range(3):
					yield (stave_id, slot_id)
		except GeneratorExit: return

	def yield_actors(self, player_cards:PlayerCards):
		try:
			for card in player_cards.hand:
				for stave_id in range(3):
					try: self.action_place(card, stave_id, just_testing=True); yield Actor(0, (card, stave_id))
					except AssertionError as e: pass

			for src in self.yield_positions():
				card = self.get_card(src)
				if card is not None and card[0] == player_cards.player_bool:
					try: self.action_forward(src, just_testing=True); yield Actor(1, (src,))
					except AssertionError as e: pass
					for i in range(3):
						if abs(i-src[0]) == 1:
							dest = (i, src[1])
							try: self.action_slide(src, dest, just_testing=True); yield Actor(2, (src, dest), player_cards=player_cards)
							except AssertionError as e: pass
		except GeneratorExit as e:
			return

actor_code_map = {
	0: "place  ",
	1: "forward",
	2: "slide  ",
}
class Actor:
	def __init__(self, code:int, args, player_cards=None):
		"""A class that represents an executable action"""
		self.code = code
		self.args = args
		if player_cards is not None:
			self.player_cards = player_cards

	def __repr__(self):
		return "code:{} ({}), args={}".format(self.code, actor_code_map[self.code], self.args)

	def execute(self, board:Board):
		if self.code == 0:
			board.action_place(*self.args)
			player_cards.remove_matching_card_from_hand(card)
		elif self.code == 1:
			board.action_forward(*self.args)
		else:
			board.action_slide(*self.args)


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

	player_turn = True
	while True:

		while True:
			actor_list = list(board.yield_actors(
				player_cards if player_turn else opponent_cards
			))
			if len(actor_list) == 0 or random.randint(0,3)==0:
				break
			actor = random.choice(actor_list)
			actor.execute(board)
			board.display()
			display_player_cards(player_cards)
			display_player_cards(opponent_cards)
			print('chose ', actor)
			time.sleep(0.5)


		board.display()
		display_player_cards(player_cards)
		display_player_cards(opponent_cards)
		print("END TURN")
		player_turn = not player_turn
		board.new_turn_begin()
		time.sleep(2.0)
#### TEST
p = {1,2,3,4,5,6}
o = {4,5,6,7,8}
play(p, o, 5)