# Stavegame: 'Classic'
## Setup

Two players (referred to as `A` and `B`) sit accross from another, and arrange (3) gray staves into parallel lines. Each stave support 3 _slots_ for cards along their length. 

For brevity in the text to follow, staves are indexed `0, 1, 2`, and the three
slots within each stave also. This results in a 2-Dimensional grid with coordinates
(0,0) to (2,2). Note that staves (0,1) and (1,2) are adjacent, while (0,2) are not.
```
        <--B's side-->

      stave0  stave1  stave2
slot0   |       |       |
slot1   |       |       |
slot2   |       |       |

        <--A's side-->
```
`A` shuffles the `A` deck and places it face-down on their side of the board, taking
three cards off the top and spreading them face-up. These three cards constitute their starting hand.
`B` does likewise with the `B` deck.

## Cards
A game card has an owner from `{A, B}`, as well as three numeric values indicated on the card.
They are here simply denoted by numerals in a triple (eg: `(1,2,0)`). These values
correspond to colors `red, green, blue` respectively. None of these values change during play.  

## Turns
The game begins with player `A`'s turn.
At the start of their turn:
1. `A` draws a card from their deck and places it face-up into their hand.
  requires all:
	  1. `A`'s deck is not empty.
	  1. It is not the very first turn of the game. 
1. They may choose to [END] if the _end condition_ is satisfied. (the following subsection details actions and their conditions).

After this, they may perform any number of the following
_actions_ as long as the relevant _conditions_ are satisfied:
* [PLACE]
* [FORWARD]
* [SLIDE]

After any (potentially empty) sequence of actions, `A` may decide to end their turn.
The turn ends also if no more moves are currently possible.

At the end of their turn, it becomes `B`'s turn, for whom the
turn progresses symmetrically.

## Actions
The following actions are described in the context of `A`'s turn. They apply symmetrically with respect to `A` and `B` during `B`'s turn.

### [PLACE]
`A` places a card from their hand into any slot `S` on the board.
requires any:
1. `S` is not occupied and is the nearest empty slot to `A` on the stave.
1. `S` is already occupied.

For the 2st case, if the stave is currently grey, `A` chooses the color for the stave, amongst all values of colors for which the card has a _maximal_ value out of all possibilities.

For the 2nd case, the new card will occupy an existing slot. This triggers _combat_ between the new card (as the attacker) and the existing card (as the defender). `A` chooses the color for combat, amongst all values of colors for which the _attacker_ card has a _minimal_ value out of all possibilities.
eg: For a card `(1,3,1)` `A` may choose either 1-value (`red` or `blue`).

### [Forward]
`A` moves one of their cards `X` on the board _forward_ one slot,
where 'forward' is defined as 'toward the opponent player'.
requires all:
1. The card was not [PLACE]d this turn.
1. The destination is on the same stave.
1. The destination is not already occupied by a card.

In the following example, let cards `{P,R,S}` belong to `A`. This turn, `A` cannot
move `P` as the forward slot is impeded by `Q`. `R` can move forward to position `(1,0)`.
`S` cannot move forward as there is no slot in the forward direction on `stave2`.
```
        <--B's side-->
      stave0  stave1  stave2
slot0   |       |       S
slot1   Q       R       |
slot2   P       |       |
        <--A's side-->
```

### [Slide]
`A` moves one of their cards `X` on the board to the same slot on an adjacent stave (ie horizontally).
requires all:
1. The card was not [PLACE]d this turn.
1. The destination stave is not gray.
1. require any:
      1. The source and destination staves are of the same color.
      1. The color-value of `X` for the stave it is moving _from_ is _strictly larger_
      than its color-value for the stave is it moving _to_.

If `X` slides into an occupied slot, then this triggers combat between `X` (as attacker)
and the existing card (as defender) with the color for combat matching the color
of the stave `X` is sliding _from_.

Additionally, if a slide would leave a stave empty, the stave is colored _grey_.

In the following example, let cards `P,Q` belong to `A`. Card `P` cannot slide to stave1,
as its color value would not strictly decrease (blue=2, red=2). Nor can `P` slide to stave2, as
this stave is not adjacent to its current stave, stave0.
Card `Q` may slide to stave0 (strict decrease from red=1 to blue=0) or to stave2 (red-to-red slide).
Note that if `Q` slides left to stave0, it cannot slide back again.
```
    stave0(blue)    stave1(red)    stave2(red) 
         |               |              |
        P:(2,1,2)        |              |
         |              Q:(1,2,0)       |

```

### [END]
`A` ends the game, deciding the victor.
requires any:
1. The previous 2 consecutive turns saw no _actions_.
1. All 9 total board slots are occupied.

At the moment the game ends, the victor is computed.
A player's _contribution_ is defined as the color-value of card `X` for the stave's color, for all cards `X` that are on the stave, and belong to the player.
A player is said to _win a stave_ if their _contribution_ is strictly greater than the _contribution_ of the opposing player for the same stave.
The victor is the player who has won the most staves. (equivalent staves results in a tie).

## Combat
Two cards (an attacker and a defender) _enter combat_ with some defined color `C` when they occupy the same slot on the board.
The attacker wins the combat if their value for `C` is at least as much as the defender's value for `C`. Otherwise, the defender wins combat.

The winner of combat remains in the slot, and the loser is removed from the game.











<!-- 




## Board


You start the game with three staves (sticks) arranged vertically.
Two players join the game, one is TOP and one is BOTTOM. These names correspond with 'their side'
```
    <---   TOP   ---
    0        1        2
    |        |        |
    |        |        |
    |        |        |
    <---  BOTTOM ---
```
## Cards
Each player has an openly-viewable hand of 3 cards.
A card is a triple of whole numbers. Each number is called the `points` at index X
to avoid confusion, these indices map to colors `[red, green, blue]` as `[0,1,2]` respectively. 
Thus, a card is a complete mapping from the domain of these 3 colors to whole numbers.
```rust
(1,5,0) //eg: This card has 1 red, 5 green, 0 blue
```

## Play
Players go in turns. At the start of each turn except the very first, players draw a card.
For each turn, the turn's player may perform one of the following actions: PLACE, MOVE, SLIDE, END

### Action: Place
Players can 'place' one card from their hand into any slot X if:
* The stave is not full
* There are no slots closer to 'their side' available on that stave
* The player has not performed 'place' yet this round

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

### Action: Move
Move a card they own one space forward (away from 'their side') on the stave if:
* There is no other card occupying that slot
* it is not the end of the stave


### Action: Slide
Slide a card 'C' from stave X, horizontally to stave Y if:
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
In a nutshell: The attacker and defender cards face-off. The survivor is the card with more points matching the color _of the stave the attacker is attacking from_. The tie breaks in favour of the attacker.


### Action: End
End the game if:
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
In a nutshell: The win goes to the player who has the greater sum of points in all cards on that stave _matching the stave's color_. Ties are broken in favour of the player whose round it is.

# Observations

From the rules given above, we observe the following interesting consequences:
* If two adjacent staves have the same color, they cannot slide cards between them. Furthermore, the stave on the outside cannot slide any cards in or out.
* Any card can slide at most twice, as each time the points of the color matching the stave strictly decrease and there are 3 point-fields on a card.
* Cards have no way of moving backward, and can only move forward if no other cards impede them.
* Players do not need to place a card per turn. They can instead choose to accumulate cards to have more options later.
* C

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
```  -->