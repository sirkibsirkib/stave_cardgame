import random
import os
import sys
from helper import *


# x = "{}hi{}".format(bcolors.WARNING, bcolors.ENDC)
# for c in x:
#   print(c, c in string.printable)
# sys.exit(0)


WIDTH = 80
HEIGHT = 16


def printed_width(some_string):
    count = 0
    enabled = True
    for char in some_string:
        if char == '\033':
            enabled = False
        else:
            if enabled: count += 1
            elif char == 'm': enabled = True
    return count


col2ind = {'r': 0, 'g': 1, 'b': 2}
ind2col = ['r', 'g', 'b']
ind2ansi = [bcolors.RED, bcolors.GREEN, bcolors.BLUE]

class Stave:
    def __init__(self, color=None):
        self.color = color
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
        if self.population() == 0:
            self.color = None
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
        if self.population() == 0:
            self.color = None

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

    def tidy(self):
        def maybe_swap(lower, higher):
            if self.slots[lower] is not None and self.slots[higher] is not None:
                if self.slots[lower].owner and not self.slots[higher].owner:
                    temp = self.slots[lower]
                    self.slots[lower] = self.slots[higher]
                    self.slots[higher] = temp
                    return True
            return False
        def maybe_compact(lower, higher):
            if self.slots[lower] is None and self.slots[higher] is not None and not self.slots[higher].owner:
                self.slots[lower] = self.slots[higher]
                self.slots[higher] = None
                return True
            elif self.slots[higher] is None and self.slots[lower] is not None and self.slots[lower].owner:
                self.slots[higher] = self.slots[lower]
                self.slots[lower] = None
                return True
            return False

        change = True
        while maybe_swap(0,1) or maybe_swap(1,2) or maybe_compact(0,1) or maybe_compact(1,2):
            pass

    def draw(self, screen:Screen, x, y, index:int, turn_0:bool):
        screen.put(x-1, y, '#')
        screen.put_str(x, y, str(index))

        for y_offset in range(1,8):
            screen.put(x, y+y_offset, (bcolors.WARNING if self.color is None else ind2ansi[self.color])+"|"+bcolors.ENDC)
        for i, card in enumerate(self.slots):
            if card is None: continue
            dx = x-1 if card.owner else x-5
            dy = y+2+(2*i)
            card.draw(screen, dx, dy)
            left = index > 0 and staves[index-1].valid_slide_from(card, self.color)
            right = index < 2 and staves[index+1].valid_slide_from(card, self.color)
            if left: screen.put(dx-1, dy, "<")
            if right: screen.put(dx+7, dy, ">")
            if card.owner == turn_0 and (left or right):
                    action = ShiftAction(index, i)
                    handle = handles.register(action)
                    screen.put(dx+9, dy, handle)

        tots = self.totals()
        screen.put_str(x, 8, "{}/{}".format(tots[0], tots[1]))
        screen.put_str(x, 9, "==" if tots[0] == tots[1] else 
            "<<" if tots[0] > tots[1] else ">>"
            )


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
        src_stave.tidy()
        dest_stave.tidy()


class PlaceAction:
    def __init__(self, hand_a:bool, hand_slot:int):
        self.hand_a = hand_a
        self.hand_slot = hand_slot

    def execute(self, args:str):
        global move_available
        print("EXECUTING PlaceAction")
        dest = int(args)
        stave = staves[dest]
        if stave.population() == 3:
            raise ValueError
        hand = hand_a if self.hand_a else hand_b
        stave.add_card(hand.pop(self.hand_slot))
        move_available = False

class Handles:
    def __init__(self):
        self.mappings = dict()
        self.next = 0

    def clear(self):
        self.next = 0
        self.mappings.clear()

    def execute(self, player_input:str):
        k = player_input[0]
        try:
            self.mappings[k].execute(player_input[1:])
        except KeyError as e:
            raise ValueError


    def register(self, action) -> str:
        handle = chr(ord('a') + self.next)
        self.next += 1
        self.mappings[handle] = action
        return handle

    def num_handles(self) -> int:
        return self.next


random.seed(0)
HAND_SIZE = 4
hand_a = [Card(True) for _ in range(HAND_SIZE-1)]
hand_b = [Card(False) for _ in range(HAND_SIZE-1)]
staves = [Stave(),Stave(),Stave()]
screen = Screen()
turn_0 = True
handles = Handles()
move_available = True

def print_hand(is_hand_a:bool, x:int, my_turn:bool):
    global move_available
    hand = hand_a if is_hand_a else hand_b
    for i, card in enumerate(hand):
        y = 10+i
        somewhere_to_go = False
        if my_turn and move_available:
            for j in range(3):
                if staves[j].population() < 3:
                    somewhere_to_go = True
                    screen.put(x+9+j, y, str(j))
            if somewhere_to_go:
                action = PlaceAction(is_hand_a, i)
                handle = handles.register(action)
                screen.put(x+8, y, handle)
        card.draw(screen, x, y)
    if my_turn:
        screen.put_str(x, 15, "^^^^^^^")


os_screen_clear = lambda: os.system('cls')
while True:
    handles.clear()
    os_screen_clear()
    screen.set_clear_screen()
    print_hand(True, 31, turn_0)
    print_hand(False, 5, not turn_0)

    for i, stave in enumerate(staves):
        x = i*20 + 5
        y = 0
        stave.draw(screen, x, y, i, turn_0)
    screen.show()
    p_input = "" if handles.num_handles() == 0 else input().strip()
    if len(p_input) == 0:
        turn_0 = not turn_0
        if turn_0:
            while len(hand_a) < HAND_SIZE:
                hand_a.append(Card(True))
        else:
            while len(hand_b) < HAND_SIZE:
                hand_b.append(Card(False))
        move_available = True
    else:
        print("EXECUTING")
        try:
            handles.execute(p_input)
        except ValueError as e:
            print("VALUE ERROR", e)

