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
		10: (1,1,5),
		11: (4,4,0),
		12: (3,2,4),
		13: (0,1,3),
		14: (3,2,4),
		15: (0,2,3),
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

	def clone(self):
		x = PlayerCards.__new__(PlayerCards)
		x.deck_sequence = list(self.deck_sequence)
		x.player_bool = self.player_bool
		x.hand = list(self.hand)
		return x

	def draw_into_hand(self):
		if len(self.deck_sequence) > 0:
			self.hand.append(self.deck_sequence.pop())
			return True
		return False

	def draw(self) -> Card:
		return self.deck_sequence.pop()

	def remove_from_hand(self, hand_index:int):
		card = self.hand[hand_index]
		del self.hand[hand_index]
		return card

	def no_hand_no_deck(self) -> bool:
		return len(self.deck) + len(self.hand) == 0

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
		self.game_over = False
		self.grid = [[None for _ in range(3)] for _ in range(3)]
		self.stave_cols = [None for _ in range(3)]
		self.place_used = False

	def clone(self):
		x = Board.__new__(Board)
		x.grid = [list(self.grid[i]) for i in range(3)]
		x.stave_cols = list(self.stave_cols)
		x.place_used = self.place_used
		x.game_over = self.game_over
		return x

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
		return "        {}        ".format('#' if col is None else {0:'r', 1:'g', 2:'b'}[col])

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



	def action_end(self, just_testing=False):
		for x in range(3):
			for y in range(3):
				assert(self.grid[x][y] is not None)
		if just_testing: return True
		self.game_over = True

	def victory(self):
		res = [0,0,0]
		for stave_id in range(3):
			t,f = 0,0
			for slot_id in range(3):
				card = self.get_card((stave_id, slot_id))
				if card is not None:
					val = CardDatabase.col_value(card, self.stave_cols[stave_id])
					if card[0]: 
						t += val
					else:
						f += val
			res[stave_id] = (t,f, "==" if t==f else ("p " if t>f else "o "))
		return res

	def victor(self):
		assert self.game_over
		v = self.victory()
		b = 0
		for (p,o,_) in self.victory():
			if   p > o: b += 1
			elif p < o: b -= 1
		if b > 0: return True
		if b < 0: return False 
		return None


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
			try: self.action_end(just_testing=True); yield Actor(3,None)
			except AssertionError as e: pass
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
							try: self.action_slide(src, dest, just_testing=True); yield Actor(2, (src, dest))
							except AssertionError as e: pass
		except GeneratorExit as e:
			return

actor_code_map = {
	0: "place  ",
	1: "forward",
	2: "slide  ",
	3: "end    ",
}
class Actor:
	def __init__(self, code:int, args):
		"""A class that represents an executable action"""
		self.code = code
		self.args = args

	def __repr__(self):
		return "code:{} ({}), args={}".format(self.code, actor_code_map[self.code], self.args)

	def execute(self, board:Board, player_cards:PlayerCards):
		if self.code == 0:
			board.action_place(*self.args)
			player_cards.remove_matching_card_from_hand(self.args[0])
		elif self.code == 1:
			board.action_forward(*self.args)
		elif self.code == 2:
			board.action_slide(*self.args)
		else:
			board.action_end()



def display_card(card:Card):
	return ("{}: #{} ({},{},{})".format(
		"p" if card[0] else "o",
		card[1],
		CardDatabase.r(card),
		CardDatabase.g(card),
		CardDatabase.b(card),
	)).ljust(17)


def display_player_cards(player_cards:PlayerCards):
	x = player_cards.deck_cards_remaining()
	print("["* x + " {} ]".format(x) if x > 0 else "<deck empty>")
	for card in player_cards.hand:
		print(display_card(card))
	print()

def heuristic(board:Board, player_cards:PlayerCards, opponent_cards:PlayerCards):
	h = 0 # pos for True player, neg for False opponent

	# straight-up win points
	for x in board.victory(): 
		h += x[0] - x[1] + (3 if x[2] else -3)
	if board.game_over:
		return h * 100

	# more options = better	
	for actor in board.yield_actors(player_cards):
		h += 0.1
	for actor in board.yield_actors(opponent_cards):
		h -= 0.1
	return h

def starting_h(turn:bool):
	return -999999 if turn else 999999

calls = 0
def minimax(board:Board, turn:bool, depth_to_go:int, player_cards:PlayerCards, opponent_cards:PlayerCards, best_h_above) -> Tuple[float,Actor]:
	global calls
	calls += 1
	if depth_to_go == 0 or board.game_over:
		# no more depth. time to estimate
		return heuristic(board, player_cards, opponent_cards), None

	# ending turn is the default choice (None) to beat
	turn_end_board = board.clone()
	turn_end_board.new_turn_begin()
	best_h, best_actor = starting_h(turn), None

	if turn: # player turn
		for actor in board.yield_actors(player_cards):
			branch_board = board.clone()
			branch_p_cards = player_cards.clone()
			actor.execute(branch_board, branch_p_cards)
			h,a = minimax(branch_board, turn, depth_to_go-1, branch_p_cards, opponent_cards, None)
			if h > best_h: # maximizing
				best_actor = actor
				best_h = h
				if best_h_above is not None:
					if best_h >= best_h_above:
						return best_h * 0.9, best_actor
	else: # opponent turn
		for actor in board.yield_actors(opponent_cards):
			branch_board = board.clone()
			branch_o_cards = opponent_cards.clone()
			actor.execute(branch_board, branch_o_cards)
			h,a = minimax(branch_board, turn, depth_to_go-1, player_cards, branch_o_cards, None)
			if h < best_h: # minimizing
				best_actor = actor
				best_h = h
				if best_h_above is not None:
					if best_h <= best_h_above:
						return best_h * 0.9, best_actor
	# print(" "*(12-depth_to_go) + (">p" if turn else ">o"))

	h,a = minimax(turn_end_board, not turn, depth_to_go-1, player_cards, opponent_cards, best_h)
	if (h > best_h if turn else h < best_h):
		best_actor = None # end turn
		best_h = h

	return best_h * 0.9, best_actor





def play(player_deck:Set[int], opponent_deck:Set[int], seed:int):
	random.seed(seed)
	player_cards = PlayerCards(player_deck, True, init_hand_size=1)
	opponent_cards = PlayerCards(opponent_deck, False, init_hand_size=2)
	board = Board()
	player_turn = True

	# TODO the only winning move is not to play
	
	# 
	# return

	while not board.game_over:
		# one loop per turn
		cards = player_cards if player_turn else opponent_cards
		cards.draw_into_hand()
		while not board.game_over:
			global calls
			calls = 0
			h,a = minimax(board, player_turn, 5, player_cards, opponent_cards, None)
			print(h, a)
			print('calls', calls)
			time.sleep(0.1)
			if a is None:
				break
			a.execute(board, cards)
			board.display()
			display_player_cards(player_cards)
			display_player_cards(opponent_cards)
			print(board.victory())


		board.display()
		display_player_cards(player_cards)
		display_player_cards(opponent_cards)
		print(board.victory())
		print("=============== END TURN =======================")
		player_turn = not player_turn
		board.new_turn_begin()
		time.sleep(0.5)
	print("GAME OVER!")
	v = board.victor()
	if v is None: print("DRAW!")
	if v: print("PLAYER is the WINNER")
	else: print("OPPONENT is the WINNER") 
	
#### TEST
p = {1,2,3,4,5,6,7,8,9}
o = {4,5,6,7,8,9,10,11,12,13,14}
play(p, o, 1)