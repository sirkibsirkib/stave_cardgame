
class bcolors:
    WARNING = '\033[93m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    ENDC = '\033[0m'


class Card:
    def __init__(self, owner:bool):
        pts = random.randint(3,9)
        self.owner = owner
        self.pts = [0,0,0]
        for _ in range(pts):
            self.pts[random.randint(0,2)] += 1

    def draw(self, screen, x, y):
        screen.put_str(x, y,
            "({}{}{}`{}{}{}`{}{}{})"
            .format(
                bcolors.RED, self.pts[0], bcolors.ENDC,
                bcolors.GREEN, self.pts[1], bcolors.ENDC,
                bcolors.BLUE, self.pts[2], bcolors.ENDC,
            )
        )

    def inds_less_than(self, value):
        results = []
        for i in range(3):
            if self.pts[i] < value:
                results.append(i)
        return results


class Screen:
    def __init__(self):
        self.set_clear_screen()

    def put(self, x, y, char):
        self.pixels[y][x] = char



    def put_str(self, x, y, given):
        for i in range(printed_width(given)):
            self.put(x+i, y, '')
        self.put(x, y, given)

    def set_clear_screen(self):
        self.pixels = [
            [' ' for _ in range(WIDTH)]
            for _ in range(HEIGHT)
        ]

    def show(self):
        for row in self.pixels:
            print("".join(row))