# Board
```
	0		1		2
	|		|		|
	|		|		|
	|		|		|
```

You start the game with three staves (sticks) arranged vertically.
Two players join the game, one is TOP and one is BOTTOM. These names correspond with 'their side'
```
    <---   TOP   --->
	0		1		2
	|		|		|
	|		|		|
	|		|		|
	<---  BOTTOM --->
```

Each player has an openly-viewable hand of 3 cards.
A card is a triple of whole numbers. Each number is called the `points` at index X
to avoid confusion, these indices map to colors `[red, green, blue]` as `[0,1,2]` respectively. 
Thus, a card is a complete mapping from the domain of these 3 colors to whole numbers.
```rust
//eg: This card has 1 red, 5 green, 0 blue
(1,5,0)
```

Players go in turns.
For each turn, the turn's player may do any of the things <1>, <2>, <3>, <4>

<1> 'place' one card from their hand into any slot X if:
	* The stave is not full
	* There are no slots closer to 'their side' available on that stave

staves have no color if they have no cards. As soon as they acquire their first card, they take on the color from that card. The color is chosen among the values for which that card's points are maximal. Eg: `(1,4,4)` allows the player to choose between GREEN and BLUE. Most cards, in practice thus allow no choice. Eg: `(1,2,0)` always results in GREEN.

Cards always still belong to their original owner. This can be distinguished in any way desired, but it is suggested by either slanting the cards in different ways, placing one set OVER and one set UNDER the staves, or by placing to the LEFT and RIGHT of the staves. Eg:
```
       0           1           2
  (4,3,0)          |           |
       |           |           |
       |          (0,0,5) (1,1,1)
       |           |           |
       |          (4,5,5)     (1,2,4)
```


In most cases, this boils down to "the color of the largest number on the card"

<2> Move a card they own one space forward (away from 'their side') on the stave if:
	* There is no other card occupying that slot
	* it is not the end of the stave

<3> 'slide' a card 'C' from stave X, horizontally to stave Y if:
	* X and Y are adjacent staves (staves 0 and 1, 1 and 2 are adjacent pairs)
	* stave Y is colored
	* C.points[X.color] > C.points[Y.color]
	* C was not _placed_ this round.

A card may slide into the index of a slot already occupied by another card (regardless of who owns the other card). These cards 'fight'; afterward, the winner occupies the contested slot and the loser is removed from the game.
The winner of a fight is determined according to:

```rust
fn attacker_wins(attacker:Card, defender:Card, attacking_from:Stave) -> bool {
	let c = attacking_from.color;
	attacker.points[c] >= defender.points[c]
}
```

A player may perform <2> and <3> as many times as they are able during a round, but may only perform <1> at most once per round.

<4> End the game if:
	* every stave has 3/3 slots occupied

When the game _ends_, the winner of the game is the player who has won the most _staves_. The winner of a stave is determined as follows:

```rust
fn stave_winner(stave:Stave, turn:Player) -> Player {
	let mut top_pts = 0;
	let mut bottom_pts = 0;
	for card in stave.slots.iter() {
		match card.owner {
			Player::Top     => top_pts += card.points[stave.color],
			Player::Bottom  => bottom_pts += card.points[stave.color],
		}
	}
	if top_pts > bottom_pts { return Some(Player::Top) }
	if top_pts < bottom_pts { return Some(Player::Bottom) }
	turn // draw awards victory to the player whose turn it is
}
```

From the rules given above, we observe the following interesting consequences:
* If two adjacent staves have the same color, they cannot slide cards between them
* furthermore, the stave on the outside cannot slide any cards in or out


# GRAVEYARD
 The color chosen is according to the following function:
```rust

fn color(card: Card, stave: Stave) -> Color {
	if let Some(c) = card.single_max() {
		c
	} else if let Some(c) = card.single_min() {
		c
	} else {
		stave.index as Color
	}
}
```