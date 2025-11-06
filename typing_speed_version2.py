import curses
import time
from curses.textpad import Textbox, rectangle
class TypingSpeedTest:

    def __init__(self):
        with open("text.txt", "r") as f:
            self.sentences = f.read()

        self.green = self.red = None

        self.wpm_pad = self.time_pad = None
        self.options_pad = self.title_pad = self.title_win = None

        self.rows, self.cols = None, None
        self.tab_char = []
        self.result_wpm = ""

    def wpm(self, start_time):
        #per min
        interval = (time.time() - start_time) / 60

        self.wpm_pad.erase() #clean the terminal
        #divided by 5 because it's average word length
        self.result_wpm = f"WPM: {((len(self.tab_char) / 5) / interval):.0f}"
        return self.result_wpm

    def stopwatch(self, start_time):
        interval = (time.time() - start_time)
        self.time_pad.addstr(0,0, f"Time: {interval:.2f}", curses.A_BOLD)
        self.time_pad.refresh(0, 0, 3, 0, 4, 20)

    def title_blink(self, stdscr):
        start_time = time.time()
        color_title = self.green

        text = "<------ Welcome in typing speed test! ------>"
        text_columns = round((self.cols - len(text))/2)
        row = round(self.rows / 2)

        win = curses.newwin(6, len(text)+6, row-2, text_columns-2)
        stdscr.refresh()

        win.addstr(2, 1, "Choose the options:")
        win.addstr(3, 1, "-> WPM in live click key 1")
        win.addstr(4, 1, "-> Typing in time click key 2")
        win.refresh()

        while True:
            # change_title
            if time.time() - start_time > 0.7:
                color_title = self.red if color_title == self.green else self.green
                start_time = time.time()  # reset time

            win.attron(color_title)
            win.addstr(1, 2, text)
            rectangle(win, 0, 0, 5, len(text) + 4)
            win.refresh()
            win.attroff(color_title)

            #get a number from keyboard
            stdscr.nodelay(True)
            try:
                key = stdscr.getkey()
            except:
                key = None

            if key == "1" or key == "2":
                stdscr.clear()
                stdscr.refresh()
                return key

    def mechanism_live(self, stdscr, option):
        stdscr.nodelay(True)
        while True:
            stdscr.addstr(1, 0, self.sentences)
            stdscr.move(1, 0)

            wrong_letter = 0
            right_letter = 0
            index = 0

            self.tab_char = []
            start_time = time.time()
            while index < len(self.sentences):
                try:
                    char_input = stdscr.get_wch()
                    if char_input in ("\n", curses.KEY_ENTER):
                        break
                    self.tab_char.append(char_input)

                    stdscr.move(1, index)
                    #BACKSPACE in text
                    if char_input in (curses.KEY_BACKSPACE, 'b', '\x7f'):
                        if index > 0:
                            index -= 1
                            stdscr.move(1, index)
                            stdscr.addch(self.sentences[index]) #orginal letter print
                            stdscr.move(1, index)
                    #color of text
                    else:
                        if char_input == self.sentences[index]:
                            stdscr.echochar(char_input, self.green)
                            right_letter += 1
                        elif char_input != self.sentences[index]:
                            stdscr.echochar(char_input, self.red)
                            wrong_letter += 1

                        index += 1

                except curses.error:
                    pass

                if option:
                    if len(self.tab_char) < len(self.sentences):
                        self.wpm_pad.addstr(self.wpm(start_time), curses.A_BOLD)
                        self.wpm_pad.refresh(0, 0, 3, 0, 4, 20)
                else:
                    if len(self.tab_char) < len(self.sentences):
                        self.stopwatch(start_time)

            stdscr.clear()
            stdscr.refresh()
            stdscr.addstr(4, 0, f"____________________", curses.A_BOLD)
            stdscr.addstr(5, 0, f"{self.wpm(start_time)}")
            stdscr.addstr(6, 0, f"Wrong letter: {wrong_letter}", self.red)
            stdscr.addstr(7, 0, f"Right letter: {right_letter}", self.green)
            stdscr.addstr(8, 0, f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾", curses.A_BOLD)
            stdscr.addstr(9, 0, f"To restart and see result, click enter")

            try:
                menu_input = stdscr.get_wch()
                if menu_input == curses.KEY_ENTER:
                    break
            except curses.error:
                pass

    def typing_speed(self, stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        self.green = curses.color_pair(1)
        self.red = curses.color_pair(2)

        self.rows, self.cols = stdscr.getmaxyx()

        self.wpm_pad = curses.newpad(1, 10)
        self.time_pad = curses.newpad(1, 30)
        self.title_pad = curses.newpad(1, 50)
        self.title_win = curses.newwin(1, 50, 10, 20)
        self.options_pad = curses.newpad(5, 50)
        choice = self.title_blink(stdscr)

        choice = ["WPM LIVE", True] if choice == "1" else ["TYPING IN TIME", False]
        stdscr.addstr(0, 0,f"You choose: {choice[0]}")
        stdscr.addstr(1, 0, f"Loading", curses.A_BOLD)
        stdscr.addstr(5, 0, f":{self.cols} {self.rows}")
        stdscr.refresh()

        #Adding dot in "Loading"
        for dot in range(7):
            stdscr.addstr(1, dot + 7, f".", curses.A_BOLD)
            time.sleep(0.7)
            stdscr.refresh()

        stdscr.clear()
        stdscr.refresh()

        self.mechanism_live(stdscr, choice[1])

if __name__ == "__main__":
    curses.wrapper(TypingSpeedTest().typing_speed)