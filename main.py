import random
import os

class Card:
	def __init__(self, owner:bool):
		pts = random.randint(5,9)
		self.owner = owner
		self.pts = [0,0,0]
		for _ in range(pts):
			self.pts[random.randint(0,2)] += 1

	def draw(self, screen, x, y):
		screen.put_str(x, y,
			"[{},{},{}]"
			.format(self.pts[0], self.pts[1], self.pts[2])
		)

	def inds_less_than(self, value):
		results = []
		for i in range(3):
			if self.pts[i] < value:
				results.append(i)
		return results

WIDTH = 80
HEIGHT = 16
class Screen:
	def __init__(self):
		self.set_clear_screen()

	def put(self, x, y, char):
		self.pixels[y][x] = char

	def put_str(self, x, y, string):
		for i, char in enumerate(string):
			self.put(x+i, y, char)

	def set_clear_screen(self):
		self.pixels = [
			[' ' for _ in range(WIDTH)]
			for _ in range(HEIGHT)
		]

	def show(self):
		for row in self.pixels:
			print("".join(row))

col2ind = {'r': 0, 'g': 1, 'b': 2}
ind2col = {v:k for k,v in col2ind.items()}

class Stave:
	def __init__(self):
		self.color = None
		self.slots = [None, None, None]

	def next_slot_for(self, card):
		for i in ([2,1,0] if card.owner else [0,1,2]):
			if self.slots[i] is None:
				return i
		return None

	def population(self):
		return 3 - self.slots.count(None)

	def add_card(self, card:Card):
		if self.population() == 0:
			ind = card.pts.index(max(card.pts))
			print(ind)
			self.color = ind
		slot = self.next_slot_for(card)
		assert(slot is not None)
		self.slots[slot] = card

	def remove_card(self, slot_index:int):
		c = self.slots[slot_index]
		self.slots[slot_index] = None
		return c

	def remove_collapse(self, slot_index:int):
		c = self.slots[slot_index]
		self.slots[slot_index] = None
		for i in range(slot_index+1, 3):
			if not self.slots[i].owner:
				self.slots[i-1] = self.slots[i]
				self.slots[i] = None 
		for i in range(slot_index-1, -1, -1):
			if self.slots[i].owner:
				self.slots[i+1] = self.slots[i]
				self.slots[i] = None 

	def totals(self):
		t_tot = 0
		f_tot = 0
		if self.color == None:
			return (0,0)
		for i, card in enumerate(self.slots):
			if card is None: continue
			if card.owner:
				t_tot += card.pts[self.color]
			else:
				f_tot += card.pts[self.color]
		return (f_tot, t_tot)

	def valid_slide_from(self, card:Card, src_stave_color:int) -> bool:
		if self.population() != 3:
			return False
		return card.pts[src_stave_color] > card.pts[self.color]

	def card_slot_from_slide(self, card:Card):
		for i in ([2,1,0] if card.owner else [0,1,2]):
			if self.slots[i].owner != card.owner:
				return i
		return 2 if card.owner else 0

	def draw(self, screen:Screen, x, y, index:int, turn_0:bool):
		screen.put(x-1, y, '#')
		screen.put_str(x, y, str(index))

		for y_offset in range(1,8):
			screen.put(x, y+y_offset, "|" if self.color is None else str(self.color))
		for i, card in enumerate(self.slots):
			if card is None: continue
			dx = x-1 if card.owner else x-5
			dy = y+2+(2*i)
			card.draw(screen, dx, dy)
			if card.owner == turn_0:
				left = index > 0 and staves[index-1].valid_slide_from(card, self.color)
				right = index < 2 and staves[index+1].valid_slide_from(card, self.color)
				if left or right:
					action = ShiftAction(index, i)
					handle = handles.register(action)
					screen.put(dx+8, dy, handle)
					if left: screen.put(dx+9, dy, "<")
					if right: screen.put(dx+10, dy, ">")

		tots = self.totals()
		screen.put_str(x, 8, "{}/{}".format(tots[0], tots[1]))
		screen.put_str(x, 9, "<<" if tots[0] >= tots[1] else ">>")


class ShiftAction:
	def __init__(self, stave_src_index:int, card_slot:int):
		self.stave_src_index = stave_src_index
		self.card_slot = card_slot

	def execute(self, args:str):
		print("EXECUTING Shift")
		src_stave = staves[self.stave_src_index]
		src_col = src_stave.color
		card = src_stave.slots[self.card_slot]
		assert(card is not None)
		if args == "<": left = True
		elif args == ">": left = False
		else: raise ValueError
		dest_stave = staves[self.stave_src_index + (-1 if left else 1)]
		if not dest_stave.valid_slide_from(card, src_col):
			raise ValueError
		defender_card_slot = dest_stave.card_slot_from_slide(card)
		defender = dest_stave.slots[defender_card_slot]
		if defender.pts[src_col] <= card.pts[src_col]:
			#VICTORY
			dest_stave.slots[defender_card_slot] = card
		src_stave.remove_card(self.card_slot)


class PlaceAction:
	def __init__(self, hand_a:bool, hand_slot:int):
		self.hand_a = hand_a
		self.hand_slot = hand_slot

	def execute(self, args:str):
		print("EXECUTING PlaceAction")
		dest = int(args)
		stave = staves[dest]
		if stave.population() == 3:
			raise ValueError
		hand = hand_a if self.hand_a else hand_b
		stave.add_card(hand.pop(self.hand_slot))

class Handles:
	def __init__(self):
		self.mappings = dict()
		self.next = 0

	def clear(self):
		self.next = 0
		self.mappings.clear()

	def execute(self, player_input:str):
		k = player_input[0]
		self.mappings[k].execute(player_input[1:])


	def register(self, action) -> str:
		handle = chr(ord('a') + self.next)
		self.next += 1
		self.mappings[handle] = action
		return handle


hand_a = [Card(True) for _ in range(5)]
hand_b = [Card(False) for _ in range(5)]
staves = [Stave(),Stave(),Stave()]
screen = Screen()
turn_0 = True
handles = Handles()

staves[1].add_card(Card(True))
staves[1].add_card(Card(False))
staves[1].add_card(Card(False))

def print_hand(is_hand_a:bool, x:int, my_turn:bool):
	hand = hand_a if is_hand_a else hand_b
	for i, card in enumerate(hand):
		y = 10+i
		if my_turn:
			action = PlaceAction(is_hand_a, i)
			handle = handles.register(action)
			screen.put(x+8, y, handle)
			for j in range(3):
				if staves[j].population() < 3:
					screen.put(x+9+j, y, str(j))
		card.draw(screen, x, y)
	if my_turn:
		screen.put_str(x, 15, "^^^^^^^")


os_screen_clear = lambda: os.system('cls')
while True:
	handles.clear()
	os_screen_clear()
	screen.set_clear_screen()
	print_hand(True, 5, turn_0)
	print_hand(False, 31, not turn_0)
	for i, stave in enumerate(staves):
		x = i*20 + 5
		y = 0
		stave.draw(screen, x, y, i, turn_0)
	screen.show()
	p_input = input().strip()
	if len(p_input) == 0:
		"USED ENDED ROUND"
		turn_0 = not turn_0
	else:
		print("EXECUTING")
		handles.execute(p_input)

