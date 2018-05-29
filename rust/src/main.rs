
#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
struct Position(u8, u8);

#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
struct CardId(u32);


#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
enum Col {
	Red, Green, Blue,
}

macro_rules! tup_echo {
	($e:expr, $q:($arg:expr),*) => {
        (
        	$e,
        	99,
            $($arg,)*
        )
    };
	($($arg:expr),*) => {
        (
            $($arg,)*
        )
    };
}

macro_rules! lex_iter {
	($e:expr, $f:expr, $g:expr) => {{
		$e.flat_map(
			move |x|
			$f.flat_map(
				move |y|
				$g.map(
					move |z|
					(x, y, z)
				)
			)
		)
	}};
	($e:expr, $f:expr) => {{
		$e.flat_map(
			move |x|
			$f.map(
				move |y|
				(x, y)
			)
		)
	}};
	($e:expr) => {{
		$e
	}};
	() => { iter::empty() };
}




use std::time::Instant;
fn main() {
	let t = tup_echo!(5,6,true);
	println!("{:?}", t);
	for pos in Board::iter_positions() {
		println!("{:?}", pos);
	}
}

struct Board {
	cards: Grid33,
	stave_cols: [Option<Col>; 3],
}

impl Board {
	pub fn new() -> Self {
		Self {
			cards: Grid33::new(),
			stave_cols: [None, None, None],
		}
	}
	pub fn iter_positions() -> impl Iterator<Item=Position> {
		lex_iter!(0..3, 0..3)
		.map(|(x,y)| Position(x,y))
	}
}

use std::iter;
struct Grid33 {
	v: Vec<Option<CardId>>,
}
impl Grid33 {
	fn new() -> Self {
		Self {
			v: iter::repeat(None).take(9).collect()
		}
	}
	fn pos_to_index(pos:Position) -> usize {
		(pos.0 * 3 + pos.1) as usize
	}
}

use std::ops::Range;
fn lexicographic_range<O,I,X,Y>(outer: O, inner: I) -> impl Iterator<Item=(X, Y)>
where
	O: Iterator<Item=X>,
	I: Iterator<Item=Y> + Clone,
	X: Clone,
	Y: Clone,
{
	outer.flat_map(
		move |x|
		inner.clone().map(
			move |y|
			(x.clone(), y.clone())
		)
	)
}


// fn lexicographic_range3<O,I,Q,X,Y,Z>(outer: O, inner: I, center: Q) -> impl Iterator<Item=(X, Y, Z)>
// where
// 	O: Iterator<Item=X> + Clone,
// 	I: Iterator<Item=Y> + Clone,
// 	Q: Iterator<Item=Z> + Clone,
// 	X: Clone,
// 	Y: Clone,
// 	Z: Clone,
// {
// 	outer.flat_map(
// 		move |x|
// 		inner.clone().flat_map(
// 			move |y|
// 			center.clone().map(
// 				move |z|
// 				(x.clone(), y.clone(), z.clone())
// 			)
// 		)
// 	)
// }

use std::ops::{Index,IndexMut};
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