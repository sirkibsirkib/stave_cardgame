use std::{
	self,
	slice,
};


#[derive(Copy, Clone, PartialEq, Eq)]
pub enum Player {
	Top, // starts at index 2
	Bottom, // starts at index 0
}

pub struct Stave {
	slots: [Option<Card>; 3],
	col: Option<Col>,
}
impl Stave {
	const UPWARD: [usize;3] = [0,1,2];
	const DOWNWARD: [usize;3] = [2,1,0];

	pub fn new() -> Self {
		Self {
			slots: [None, None, None],
			col: None,
		}
	}

	pub fn col(&self) -> Option<Col> {
		self.col
	}

	pub fn card_at(&self, index:usize) -> &Option<Card> {
		&self.slots[index]
	}

	pub fn population(&self) -> usize {
		self.slots.iter().filter(|x| x.is_none()).count()
	}

	pub fn iter_slots_forward(&self, player:Player) -> impl Iterator<Item=(usize, &Option<Card>)> {
		let clos = move |&x| (x, &self.slots[x]);
		match player {
			Player::Bottom => Self::UPWARD.iter().map(clos),
			Player::Top => Self::DOWNWARD.iter().map(clos),
		}
	}

	pub fn place_card(&mut self, card:Card) -> Option<usize> {
		let hold;
		if let Some((slot, _card)) = self.iter_slots_forward(card.owner())
				.filter(|(_slot,card)| card.is_none())
				.nth(0) {
			hold = slot;
		} else {
			return None;
		}
		self.slots[hold] = Some(card);
		return Some(hold)
	}
}

#[derive(Copy, Clone, PartialEq, Eq)]
pub enum Col {
	Red, Green, Blue,
}

pub struct Card {
	r: u32,
	g: u32,
	b: u32,
	owner: Player,
}

impl Card {
	pub fn new(r:u32, g:u32, b:u32, owner:Player) -> Self {
		Self {r,g,b,owner}
	}
	pub fn owner(&self) -> Player {
		self.owner
	}
	pub fn pts_for(&self, col:Col) -> u32 {
		match col {
			Col::Red => self.r,
			Col::Green => self.g,
			Col::Blue => self.b,
		}
	}
}