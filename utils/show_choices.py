import numpy as np
import time
import sys,os
import curses
import threading

data = 'some value'


def draw_menu(stdscr):
    global data
    # Turn cursor off
    curses.curs_set(False)

    # Start colors in curses
    curses.start_color()

    # Initialization
    height, width = stdscr.getmaxyx()

    # Declaration of strings
    title = "Help me please"[:width-1]
    subtitle = data[:width-1]

    # Centering calculations
    start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
    start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)

    # Rendering title
    stdscr.addstr(1, start_x_title, title)
    stdscr.addstr(3, start_x_subtitle, subtitle)

    # Refresh the screen
    stdscr.refresh()
    time.sleep(2)


def main():
    global data
    for i in xrange(2):
        curses.wrapper(draw_menu)
        # Do some stuff to update values shown in the menu
        data = 'updated value {}'.format(i)
        time.sleep(3)


class Printer(object):
    def __init__(self, heads, wait=1.0, fill_char='#', empty_char='-'):
        # '%5s' % 'aa'
        self.head_len = len(max(heads, key=len))
        self.heads = ['%{}s :'.format(self.head_len) % h for h in heads]
        self.head_len += 2
        self.wait = wait
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.title = 'Q values for each action'
        self.bars_offset = 0
        # msj = ''
        # for k in self.heads:
        #     msj += k + self.fill_char * 100 + '\n'
        #
        # self.total_len = len(self.heads[0] + self.fill_char * 100 + '\n') * len(self.heads)
        # assert len(msj) == len(self.heads[0] + self.fill_char * 100 + '\n') * len(self.heads)
        #
        # print "\n"
        # self.last_msj = ''

        # print ' ' * len(str(self.last_msj)) + '\r',
        # print '{}\r'.format(msj),
        # self.last_msj = msj
        # self.k = 0
        # self.cursor_x = 0
        # self.cursor_y = 0
        #
        self.values = None

        # sys.stdout.write('\n' + msj)
        # sys.stdout.flush()

    def draw_menu(self, stdscr):
        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)



        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if self.k == curses.KEY_DOWN:
            self.cursor_y = self.cursor_y + 1
        elif self.k == curses.KEY_UP:
            self.cursor_y = self.cursor_y - 1
        elif self.k == curses.KEY_RIGHT:
            self.cursor_x = self.cursor_x + 1
        elif self.k == curses.KEY_LEFT:
            self.cursor_x = self.cursor_x - 1

        self.cursor_x = max(0, self.cursor_x)
        self.cursor_x = min(width - 1, self.cursor_x)

        self.cursor_y = max(0, self.cursor_y)
        self.cursor_y = min(height - 1, self.cursor_y)

        # Declaration of strings
        title = "Curses example"[:width - 1]
        subtitle = "Written by Clay McLeod"[:width - 1]
        keystr = "Last key pressed: {}".format(self.k)[:width - 1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(self.cursor_x, self.cursor_y)
        if self.k == 0:
            keystr = "No key press detected..."[:width - 1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        stdscr.move(self.cursor_y, self.cursor_x)

        # Refresh the screen
        stdscr.refresh()

        self.k = stdscr.getch()

    def draw_empty_bar(self, stdscr):
        # time.sleep(10)
        curses.curs_set(False)
        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)

        stdscr.attron(curses.A_BOLD)
        height, width = stdscr.getmaxyx()

        self.bars_offset = 10# int((width // 2) - ((len(heads[0]) + 100) // 2) - (len(heads[0]) + 100) % 2)
        # Rendering empty bars
        for i, head in enumerate(self.heads):
            stdscr.addstr(i + 1, self.bars_offset, head, curses.color_pair(1))
            padded, empty = self.get_individual_bar(0)
            stdscr.addstr(i + 1, self.bars_offset + len(head), padded, curses.color_pair(2))
            stdscr.addstr(i + 1, self.bars_offset + len(head) + len(padded), empty, curses.color_pair(3))

        self.bars_offset = 10 + self.head_len
        # # Render status bar
        # stdscr.attron(curses.color_pair(3))
        # stdscr.addstr(height - 1, 0, statusbarstr)
        # stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        # stdscr.attroff(curses.color_pair(3))
        #
        # # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)


        start_x_title = int((width // 2) - (len(self.title) // 2) - len(self.title) % 2)
        # # Rendering title
        stdscr.addstr(0, start_x_title, self.title)
        stdscr.refresh()
        self.values = np.zeros(len(self.heads))
        threading.Thread(target=self.draw_filled_bar, args=(stdscr, ))



        # # Turning off attributes for title
        # stdscr.attroff(curses.color_pair(2))
        # stdscr.attroff(curses.A_BOLD)
        #
        # # Print rest of text
        # stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        # stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        # stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        # stdscr.move(self.cursor_y, self.cursor_x)
        #
        # # Refresh the screen
        # stdscr.refresh()

        # self.k = stdscr.getch()

    def draw_filled_bar(self, stdscr=None):
        while True:
            time.sleep(0.5)
            curses.curs_set(False)
            # Clear and refresh the screen for a blank canvas
            # stdscr.clear()
            # stdscr.refresh()

            # Start colors in curses
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)

            # stdscr.attron(curses.A_BOLD)
            # height, width = stdscr.getmaxyx()
            i_max = np.argmax(self.values)
            # Rendering empty bars
            for i, x in enumerate(self.values):
                color_number = 4 if i == i_max else 2
                # stdscr.addstr(i + 1, self.bars_offset, x, curses.color_pair(1))
                padded, empty = self.get_individual_bar(x)
                stdscr.addstr(i + 1, self.bars_offset, padded, curses.color_pair(color_number))
                stdscr.addstr(i + 1, self.bars_offset + len(padded), empty, curses.color_pair(3))

            # # Render status bar
            # stdscr.attron(curses.color_pair(3))
            # stdscr.addstr(height - 1, 0, statusbarstr)
            # stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            # stdscr.attroff(curses.color_pair(3))
            #
            # # Turning on attributes for title
            # stdscr.attron(curses.color_pair(2))
            # stdscr.attron(curses.A_BOLD)

            # start_x_title = int((width // 2) - (len(self.title) // 2) - len(self.title) % 2)
            # # Rendering title
            # stdscr.addstr(0, start_x_title, self.title)

            # # Turning off attributes for title
            # stdscr.attroff(curses.color_pair(2))
            # stdscr.attroff(curses.A_BOLD)
            #
            # # Print rest of text
            # stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
            # stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
            # stdscr.addstr(start_y + 5, start_x_keystr, keystr)
            # stdscr.move(self.cursor_y, self.cursor_x)
            #
            # # Refresh the screen
            # stdscr.refresh()

            # self.k = stdscr.getch()

    def updete_bar(self, stdscr):
        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if self.k == curses.KEY_DOWN:
            self.cursor_y = self.cursor_y + 1
        elif self.k == curses.KEY_UP:
            self.cursor_y = self.cursor_y - 1
        elif self.k == curses.KEY_RIGHT:
            self.cursor_x = self.cursor_x + 1
        elif self.k == curses.KEY_LEFT:
            self.cursor_x = self.cursor_x - 1

        self.cursor_x = max(0, self.cursor_x)
        self.cursor_x = min(width - 1, self.cursor_x)

        self.cursor_y = max(0, self.cursor_y)
        self.cursor_y = min(height - 1, self.cursor_y)

        # Declaration of strings
        title = "Curses example"[:width - 1]
        subtitle = "Written by Clay McLeod"[:width - 1]
        keystr = "Last key pressed: {}".format(self.k)[:width - 1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(self.cursor_x, self.cursor_y)
        if self.k == 0:
            keystr = "No key press detected..."[:width - 1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        stdscr.move(self.cursor_y, self.cursor_x)

        # Refresh the screen
        stdscr.refresh()
        self.k = stdscr.getch()

    def get_individual_bar(self, x=0.0):
        x = int(x*100)
        return self.fill_char * x, self.empty_char * (100 - x)

    @staticmethod
    def softmax(x, tau=0.1):
        """Compute softmax values for each sets of scores in x."""
        x = x/tau
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    def update(self, x):
        x = self.softmax(x) * 100
        sys.stdout.write("\b" * self.total_len)
        msj = ''
        for i, k in enumerate(self.heads):
            msj += k + self.fill_char * int(x[i]) + ' ' * (100 - int(x[i])) + '\n'
        # sys.stdout.write(msj)
        # sys.stdout.flush()
        print ' ' * len(str(self.last_msj)) + '\r',
        print '{}\r'.format(msj),
        self.last_msj = msj
        assert len(msj) == len(self.heads[0] + self.fill_char * 100 + '\n') * len(self.heads)
        time.sleep(self.wait)

    def set_next_values(self, values):
        self.values = self.softmax(np.array(values), tau=1)


def graph_q(vector):
    max_value = max(vector)
    MAX_BAR = 50
    for i in xrange(len(vector)):
        line = '[ {} ] '.format(i)
        for j in xrange(int(MAX_BAR * (vector[i] / max_value))):
            line += '//'
        print(line)
    time.sleep(1)

    os.system('clear')

if __name__ == '__main__':
    main()
    exit()
    heads = ['left', 'right', 'up', 'Noop', 'leftup', 'rigthup', 'enter']
    ejemplos = [
        [-1.8276, 1.83387768,  1.87256837,  -1.877, 1.8768,  1.872837,  -0.87256837],
        [-1.81340921,  1.77184975,  1.73510218,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-1.81340921, 1.77184975, 1.76807368,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-1.2, 1.8, 1,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-1.81340921, 1.77184975, 1.76807368,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-1.2, 1.8, 1,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-1, -2, -2,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-2, -1, -2,  1.87256837, 1.83387768,  1.87256837,  -1.87256837],
        [-2,-2,-1,  1.87256837, 1.83387768,  1.87256837,  -1.87256837]
    ]
    p = Printer(heads, wait=3)

    curses.wrapper(p.draw_empty_bar)

    for _ in xrange(10):
        for e in ejemplos:
            # p.values = p.softmax(np.array(e), tau=1)
            p.set_next_values(e)
            curses.wrapper(p.draw_filled_bar)
            time.sleep(2)
#
#

# for i in xrange(100):
#     for e in ejemplos:
#         graph_q(e)


