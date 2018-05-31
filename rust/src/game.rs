use fnv::FnvHashMap;
use std::{
	iter,
	ops::{
		Index,
		IndexMut,
	},
};

/////////////////////////

#[derive(Copy, Clone, Eq, PartialEq, Debug)]
pub struct PlayerName(char);

#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
pub struct Position {
	stave: u8,
	slot: u8,
}

impl Position {
	pub fn new(stave:u8, slot:u8) -> Self {
		Position { stave, slot }
	}
	pub fn side_neighbours(self) -> impl Iterator<Item=Self> {
		(0..3)
		.map(move |slot| Position::new(self.stave, slot))
		.filter(move |pos|
			(pos.slot as i8 - self.slot as i8).abs() == 1
		)
	}
	pub fn forward(self, player: &Player) -> Option<Position> {
		let increment = match player.plays_upward {
			true  => 1,
			false => -1,
		};
		if (self.slot == 0 && !player.plays_upward)
		|| (self.slot == 2 && player.plays_upward) {
			None
		} else {
			Some(Position::new(
				self.stave,
				(self.slot as i8 + increment) as u8,
			))
		}
	}
}

#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
pub struct CardId(usize);


#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
pub enum Col {
	Red, Green, Blue,
}

pub struct Card {
	r: u8,
	g: u8,
	b: u8,
}

pub struct CardDatabase {
	cards: Vec<Card>,
}

macro_rules! define_card {
	($vector:expr, $r:expr, $g:expr, $b:expr) => {{
		$vector.push(Card {
			r:$r, g:$g, b:$b, 
		});
	}}
}

impl CardDatabase {
	pub fn new(&self, cid: CardId) -> Self {
		let mut cards = vec![];
		define_card!(cards,1,2,3);
		define_card!(cards,1,1,3);
		define_card!(cards,0,2,3);
		define_card!(cards,0,3,3);
		define_card!(cards,1,2,3);
		define_card!(cards,0,2,4);
		Self {cards}
	}
	pub fn lookup(&self, cid: CardId) -> &Card {
		&self.cards[cid.0]
	}
}

pub struct Board {
	cards: Grid33,
	stave_cols: [Option<Col>; 3],
}

pub struct Player {
	hand: Vec<CardId>,
	deck: Vec<CardId>,
	name: PlayerName,
	plays_upward: bool,
}

impl Board {
	pub fn new() -> Self {
		Self {
			cards: Grid33::new(),
			stave_cols: [None, None, None],
		}
	}
	pub fn iter_gaps<'a>(&'a self) -> impl 'a + Iterator<Item=Position> {
		Self::iter_positions()
		.filter(move |&pos| self.cards[pos].is_none())
	}
	pub fn iter_cards<'a>(&'a self) -> impl 'a + Iterator<Item=(Position,CardId)> {
		Self::iter_positions()
		.filter(move |&pos| self.cards[pos].is_some())
		.map(move |pos| (pos,self.cards[pos].unwrap()))
	}
	pub fn iter_positions() -> impl Iterator<Item=Position> {
		lex_iter!(0..3, 0..3)
		.map(|(stave, slot)| Position::new(stave, slot))
	}
}

struct Grid33 {
	v: Vec<Option<CardId>>,
}
impl Grid33 {
	fn new() -> Self {
		Self { v: iter::repeat(None).take(9).collect() }
	}
	fn pos_to_index(pos:Position) -> usize {
		(pos.stave * 3 + pos.slot) as usize
	}
}

impl Index<Position> for Grid33 {
	type Output = Option<CardId>;
	fn index(&self, pos:Position) -> &Option<CardId> {
		&self.v[Self::pos_to_index(pos)]
	}
}
impl IndexMut<Position> for Grid33 {
	fn index_mut(&mut self, pos:Position) -> &mut Option<CardId> {
		&mut self.v[Self::pos_to_index(pos)]
	}
}