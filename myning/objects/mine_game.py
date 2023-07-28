from blessed import Terminal

term = Terminal()


class MineGame:
    def __init__(self, width: int):
        self.width = width
        self.cursor = 0
        self.direction = 1

    def move_cursor(self):
        if self.cursor == self.width - 1:
            self.direction = -1
        elif self.cursor == 0:
            self.direction = 1
        self.cursor += self.direction

    @property
    def score(self):
        middle = self.width / 2
        off_target = middle - self.cursor
        multiplier = 100 / self.width
        return 100 - abs(off_target * multiplier) * 2

    @property
    def bar_str(self):
        size = int(self.width / 5)
        red = f"{term.red}{'█' * size}{term.normal}"
        yellow = f"{term.yellow}{'█' * size}{term.normal}"
        green = f"{term.green}{'█' * size}{term.normal}"
        return f"{red}{yellow}{green}{yellow}{red}"

    @property
    def arrow_str(self):
        return f"{' ' * self.cursor}^{' ' * (self.width - self.cursor - 1)}"

    def __str__(self):
        return f"{self.bar_str}\n{self.arrow_str}"
