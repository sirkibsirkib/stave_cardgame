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

	fn iter_slots_forward(&self, player:Player) -> impl Iterator<Item=&usize> {
		match player {
			Player::Bottom => Self::UPWARD.iter(),
			Player::Top => Self::DOWNWARD.iter(),
		}
	}

	pub fn place_card(&mut self, card:Card, player:Player) {
		let slot = self.iter_slots_forward(player)
		.filter(|&&slot| self.slots[slot].is_none())
		.nth(0)
		.expect("No empty slots");
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