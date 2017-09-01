import curses
import time
import copy
import random

random.seed(0)

debug = False
HEIGHT = 20
WIDTH = 10
BEGIN_X = 0
BEGIN_Y = 0
START_X = 3
START_Y = -2

block_l = [[1, 1, 1, 1]]
block_o = [[1, 1],
           [1, 1]]
block_t = [[0, 1, 0],
           [1, 1, 1]]
block_s = [[0, 1, 1],
           [1, 1, 0]]
block_z = [[1, 1, 0],
           [0, 1, 1]]
block_J = [[1, 0, 0],
           [1, 1, 1]]
block_L = [[0, 0, 1],
           [1, 1, 1]]
blocks = [block_l, block_o, block_t, block_s,
          block_z, block_J, block_L]


def get_init_pos():
    return START_Y, START_X


def get_block_sizes(next_block):
    block_height = len(next_block)
    block_width = len(next_block[0])
    return block_height, block_width


def rotate(block, command):
    new_block = []
    height = len(block)
    width = len(block[0])
    if command == "n":
        for w in range(width):
            row = []
            for h in range(height):
                row.insert(0, block[h][w])
            new_block.append(row)
    elif command == "m":
        pass
    return new_block


def show_field(win, field):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if field[y][x] == 0:
                text = " "
            else:
                text = "O"
            win.addstr(y+1, x+1, text)


def put_block(field, next_block, pos_y, pos_x):
    block_height, block_width = get_block_sizes(next_block)
    for y in range(block_height):
        for x in range(block_width):
            if next_block[y][x] == 1:
                if pos_y + y >= 0:
                    field[pos_y + y][pos_x + x] = 1


def get_next_block():
    block_num = random.randint(0, len(blocks)-1)
    return blocks[block_num]


def check_landing(next_block, field, pos_y, pos_x):
    block_height, block_width = get_block_sizes(next_block)
    if pos_y + block_height - 1 == HEIGHT:
        return True

    for y in range(block_height):
        for x in range(block_width):
            if pos_y + y < 0:
                continue
            if next_block[y][x] == 1:
                if field[pos_y + y][pos_x + x] == 1:
                    return True
    return False


def if_filled_delete_line(field):
    for row, line in enumerate(field):
        if sum(line) == WIDTH:
            field.pop(row)
            field.insert(0, [0] * WIDTH)


def check_game_over(next_block, field, pos_y, pos_x):
    block_height, block_width = get_block_sizes(next_block)
    for y in range(block_height):
        for x in range(block_width):
            if next_block[y][x] == 1:
                if START_X <= pos_x + block_width -1 and \
                        pos_x <= START_X + 3 and pos_y + y < 0:
                    return True
    return False


def fall_block(field, pos_x, block_width):
    for y in range(HEIGHT):
        for x in range(block_width):
            if field[y][pos_x + x] == 1:
                return y
    return HEIGHT


def check_wall(field, pos_y, pos_x, next_block):
    block_height, block_width = get_block_sizes(next_block)
    for y in range(block_height):
        if field[pos_y + y][pos_x] == 1:
            return True
        if field[pos_y + y][pos_x + block_width - 1] == 1:
            return True
    return False


class Timer:
    def __init__(self, threshold=1):
        self.start = time.time()
        self.threshold = threshold

    def check(self):
        now = time.time()
        if now - self.start > self.threshold:
            self.start = now
            return True
        else:
            return False

class Field:
    def __init__(self):
        self.field = [[0] * WIDTH for _ in range(HEIGHT)]

    def check_wall(self, pos_y, pos_x, next_block):
        block_height, block_width = get_block_sizes(next_block)
        for y in range(block_height):
            if self.field[pos_y + y][pos_x] == 1:
                return True
            if self.field[pos_y + y][pos_x + block_width - 1] == 1:
                return True
        return False

    def fall_block(self, pos_x, block_width):
        for y in range(HEIGHT):
            for x in range(block_width):
                if self.field[y][pos_x + x] == 1:
                    return y
        return HEIGHT


def main():
    # main()
    field = Field()

    # window  initialize
    curses.initscr()
    win = curses.newwin(HEIGHT+2, WIDTH+2, BEGIN_Y, BEGIN_X)

    # cursor disvisable
    curses.curs_set(0)

    # non blocking getch
    win.nodelay(1)

    # default position
    pos_y, pos_x = get_init_pos()
    next_block = get_next_block()

    timer = Timer(1)

    while True:
        if timer.check():
            pos_y += 1

        win.border()
        ch = win.getch()

        block_height, block_width = get_block_sizes(next_block)

        # rotation
        if ch == ord('n'):
            if pos_x + block_width < WIDTH:
                next_block = rotate(next_block, command='n')
            if pos_x + block_width == WIDTH:
                if block_height > block_width:
                    pos_x -= block_height - block_width
                next_block = rotate(next_block, command='n')
                block_height, block_width = get_block_sizes(next_block)

        if ch == ord('q'):
            break
        elif ch == ord('h') and pos_x > 0:
            if not check_wall(field.field, pos_y, pos_x-1, next_block):
                pos_x -= 1
        elif ch == ord('j'):
            pos_y += 1
        elif ch == ord('k'):
            pos_y = fall_block(field.field, pos_x, block_width) - block_height + 1
        elif ch == ord('l') and pos_x + block_width < WIDTH:
            if not check_wall(field.field, pos_y, pos_x+1, next_block):
                pos_x += 1

        if check_landing(next_block, field.field, pos_y, pos_x):
            pos_y -= 1
            if check_game_over(next_block, field.field, pos_y, pos_x):
                break

            put_block(field.field, next_block, pos_y, pos_x)
            next_block = get_next_block()
            pos_y, pos_x = get_init_pos()

        if_filled_delete_line(field.field)

        field_copy = copy.deepcopy(field.field)
        put_block(field_copy, next_block, pos_y, pos_x)
        show_field(win, field_copy)

        if debug:
            win.addstr(1, 1, "x:%d y:%d" % (pos_x, pos_y))
            win.addstr(2, 1, "h:%d w:%d" % get_block_sizes(next_block))
        win.refresh()

    curses.endwin()

    if debug:
        import pprint
        with open("log.txt", "w") as f:
            f.write("{}\n{}\n{}\n{}".format(
                pprint.pformat(next_block),
                pprint.pformat(field.field),
                pos_y, pos_x))


if __name__ == "__main__":
    main()
