import random

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
		print('_____')

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

	def add_card(self, card:Card, top:bool):
		if self.population == 0:
			ind = card.pts.index(max(card.pts))
			self.color = ind
		slot = self.next_slot_for(card)
		assert(slot is not None)
		self.slots[slot] = card

	def totals(self):
		top_tot = 0
		bot_tot = 0
		if self.color == None:
			return (0,0)
		for card in self.top:
			top_tot += card.pts[self.color]
		for card in self.bottom:
			bot_tot += card.pts[self.color]
		return (top_tot, bot_tot)

	def draw(self, screen:Screen, x, y, index:int, turn_0:bool):
		screen.put(x-1, y, '#')
		screen.put_str(x, y, str(index))

		for y_offset in range(1,8):
			screen.put(x, y+y_offset, "|" if self.color is None else ind2col[self.color])
		for i, card in enumerate(self.slots):
			if card is None: continue
			card.draw(screen, x-1 if card.owner else x-5, y+2+(2*i))
		tots = self.totals()
		screen.put_str(x, 8, "{}/{}".format(tots[0], tots[1]))
		screen.put_str(x, 9, "<<" if tots[0] >= tots[1] else ">>")


hand_a = [Card(True) for _ in range(5)]
hand_b = [Card(False) for _ in range(5)]
staves = [Stave(),Stave(),Stave()]
screen = Screen()
turn_0 = True
while True:
	screen.set_clear_screen()
	for i, stave in enumerate(staves):
		x = i*20 + 5
		y = 0
		stave.draw(screen, x, y, i, True)
	for i, card in enumerate(hand_a):
		x = 5
		y = 10+i
		if turn_0:
			screen.put(x-2, y, chr(i+ord('a')))
		card.draw(screen, x, y)
	for i, card in enumerate(hand_b):
		x = 20
		y = 10+i
		if not turn_0:
			screen.put(x-2, y, chr(i+ord('a')))
		card.draw(screen, x, y)
	screen.put_str(5 if turn_0 else 20, 15, "^^^^^^^")
	screen.show()
	p_input = input().strip()
	print("`{}`".format(p_input))
	# try:
	if True:
		index = ord(p_input[0]) - ord('a')
		stave = ord(p_input[1]) - ord('0')
		card = (hand_a if turn_0 else hand_b).pop(index)
		staves[stave].add_card(card, top=turn_0)
	# except Exception as e:
	# 	print("EXCEPT", e)

	turn_0 = not turn_0

