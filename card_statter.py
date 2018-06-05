
from typing import Dict, Tuple, List, Set
from functools import reduce

class Card:
	def __init__(self, r, g, b):
		self.pts =  (r,g,b)

	def total(self):
		return sum(self.pts)

	def get_pts_for(self, color:int) -> int:
		assert(0 <= color < 3)
		return self.pts[color]

	def __repr__(self):
		return "<{},{},{}>".format(*self.pts)

	def min_pt_cols:
		val = min(self.pts)
		return [col if self.pts[col] == val for col in range(3)]

	def max_pt_cols:
		val = max(self.pts)
		return [col if self.pts[col] == val for col in range(3)]



def attacker_wins(attacker:Card, defender:Card, color:int) -> int:
	assert(0 <= color < 3)
	return attacker.get_pts_for(color)\
		>= defender.get_pts_for(color)

class Deck:
	def __init__(self):
		self.cards = []

	def add_new_card(self, r, g, b):
		self.add_card(Card(r,g,b))

	def add_card(self, card:Card):
		self.cards.append(card)

	def avg_pt_totals(self) -> int:
		x = self.avg_col_totals()
		return x[0] + x[1] + x[2]

	def avg_col_totals(self) -> Tuple[int, int, int]:
		totals = [0,0,0]
		for card in self.cards:
			for col in range(3):
					totals[col] += card.get_pts_for(col)
		for col in range(3):
			totals[col] /= float(len(self.cards))	
		return totals

	def print_stats(self):
		print(
			(
				"avg col:\t{} \n" + 
				"avg tot:\t{} \n" +
				"num cards:\t{} \n"
			).format(
				self.avg_col_totals(),
				self.avg_pt_totals(),
				len(self.cards)
			)
		)

	def card_to_deck_cmp(self, card:Card):
		cv = CardValue()
		for c in self.cards:
			vs = card_cmp(c, card)
			for col in range(3):
				vscol = vs[col]
				if   vscol <  0: cv.incr_lt(col)
				elif vscol == 0: cv.incr_eq(col)
				else           : cv.incr_gr(col)
		return cv

class CardWorth:
	# version 2
	def __init_(self, card:Card):
		self.card = card
		self.balance_place_att = 0
		self.balance_place_def = 0
		self.balance_slide_att = 0
		self.balance_slide_def = 0

	def feed(self, other_card:Card):
		# balance_place_att
		for col in self.card.min_pt_cols:




class CardValue:
	# version 1
	def __init__(self):
		x = {"lt":0, "eq":0, "gr":0}
		self.data = [x.copy() for _col in range(3)]

	def incr_lt(self, color:int):
		assert(0 <= color < 3)
		self.data[color]["lt"] += 1

	def incr_eq(self, color:int):
		assert(0 <= color < 3)
		self.data[color]["eq"] += 1

	def incr_gr(self, color:int):
		assert(0 <= color < 3)
		self.data[color]["gr"] += 1

	def __repr__(self):
		return "\n".join([
				"color{}\t{}\t{}\t{}".format(
					color,
					self.data[color]["lt"],
					self.data[color]["eq"],
					self.data[color]["gr"],
				)
				for color in range(3)
			])


def card_cmp(a:Card, b:Card):
	return tuple(a.get_pts_for(i) - b.get_pts_for(i) for i in range(3))


def gen_cards_with_pts(pts:int):
	try:
		for r in range(pts+1):
			for g in range(pts-r+1):
				b = pts-r-g
				yield Card(r, g, b)
	except GeneratorExit as e:
		return

import operator as op
def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer//denom

def stars_and_boxes(balls:int, boxes:int) -> int:
	return ncr(n=boxes+balls-1, r=boxes-1)

def num_cards_for_pts(pts:int) -> int:
	return stars_and_boxes(balls=pts, boxes=3)

#################################################
deck = Deck()
for card in gen_cards_with_pts(3):
	deck.add_card(card)
deck.print_stats()
cv = deck.card_to_deck_cmp(Card(3,0,0))
print(cv)