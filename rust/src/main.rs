
extern crate fnv;


#[macro_use] 
mod macros;

mod game;
use game::Board;

use std::time::Instant;
fn main() {
	for pos in Board::iter_positions() {
		println!("{:?}", pos);
	}
}
