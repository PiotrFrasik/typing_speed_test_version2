import curses
import time
from curses.textpad import Textbox, rectangle
class TypingSpeedTest:

    def __init__(self):
        with open("text.txt", "r") as f:
            self.sentences = f.read()

        self.green = self.red = None

        self.wpm_pad = self.time_pad = None
        self.options_pad = self.win_menu = self.title_win = None

        self.rows, self.cols = None, None
        self.tab_char = []
        self.result_wpm = ""
        self.text = "<------ Welcome in typing speed test! ------>"

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

    def change_color(self, start_time, color_title):
        # change_title
        if time.time() - start_time > 0.7:
            color_title = self.red if color_title == self.green else self.green
            start_time = time.time()  # reset time
        return start_time, color_title


    def under_menu(self, stdscr, choice, color_title, start_time):

        self.win_menu.attron(color_title)
        rectangle(self.win_menu, 0, 0, 5, len(self.text) + 4)
        self.win_menu.refresh()
        self.win_menu.attroff(color_title)

        choice = ["WPM LIVE", True] if choice == "1" else ["TYPING IN TIME", False]
        self.win_menu.addstr(1, 1, f"You choose: {choice[0]}")
        self.win_menu.addstr(2, 1, f"Loading", curses.A_BOLD)
        self.win_menu.refresh()
        stdscr.refresh()

        # Adding dot in "Loading"
        for dot in range(7):
            self.win_menu.addstr(2, dot + 8, f".", curses.A_BOLD)
            time.sleep(0.7)
            self.win_menu.refresh()
            stdscr.refresh()

        stdscr.clear()
        stdscr.refresh()

        return choice

    def main_menu(self, stdscr):
        start_time = time.time()
        color_title = self.green

        self.text = "<------ Welcome in typing speed test! ------>"
        text_columns = round((self.cols - len(self.text))/2)
        row = round(self.rows / 2)

        self.win_menu = curses.newwin(6, len(self.text)+6, row-2, text_columns-2)
        self.win_menu.refresh()
        stdscr.refresh()

        self.win_menu.addstr(2, 1, "Choose the options:")
        self.win_menu.addstr(3, 1, "-> WPM in live click key 1")
        self.win_menu.addstr(4, 1, "-> Typing in time click key 2")
        self.win_menu.refresh()

        while True:
            start_time, color_title = self.change_color(start_time, color_title)

            self.win_menu.attron(color_title)
            self.win_menu.addstr(1, 2, self.text)
            rectangle(self.win_menu, 0, 0, 5, len(self.text) + 4)
            self.win_menu.refresh()
            self.win_menu.attroff(color_title)

            #get a number from keyboard
            stdscr.nodelay(True)
            try:
                key = stdscr.getkey()
            except:
                key = None

            if key == "1" or key == "2":
                self.win_menu.clear()
                return self.under_menu(stdscr, key, color_title, start_time)

    def mechanism_live(self, stdscr, option):
        win_mechanism = curses.newwin(5,self.cols-2,0,1)
        win_mechanism.nodelay(True)
        win_mechanism.refresh()

        while True:
            win_mechanism.addstr(1, 0, self.sentences)
            win_mechanism.move(1, 0)

            wrong_letter = 0
            right_letter = 0
            index = 0
            y_writing = 1

            self.tab_char = []
            start_time = time.time()

            stdscr.border()
            stdscr.refresh()

            while index < len(self.sentences):
                try:
                    if index == (self.cols - 2):
                        index = 0

                    stdscr.addstr(1,10,f"{index}")

                    char_input = win_mechanism.get_wch()
                    if char_input in ("\n", curses.KEY_ENTER):
                        break
                    self.tab_char.append(char_input)

                    win_mechanism.move(y_writing, index)
                    #BACKSPACE in text
                    if char_input in (curses.KEY_BACKSPACE, '\b', '\x7f'):
                        if index > 0:
                            index -= 1
                            win_mechanism.move(y_writing, index)
                            win_mechanism.addch(self.sentences[index]) #orginal letter print
                            win_mechanism.move(y_writing, index)
                    #color of text
                    else:
                        if char_input == self.sentences[index]:
                            win_mechanism.echochar(char_input, self.green)
                            right_letter += 1
                        elif char_input != self.sentences[index]:
                            win_mechanism.echochar(char_input, self.red)
                            wrong_letter += 1

                        index += 1

                except curses.error:
                    pass

                if option:
                    if len(self.tab_char) < len(self.sentences):
                        self.wpm_pad.addstr(self.wpm(start_time), curses.A_BOLD)
                        self.wpm_pad.refresh(0, 0, 3, 1, 4, 20)
                else:
                    if len(self.tab_char) < len(self.sentences):
                        self.stopwatch(start_time)

            win_mechanism.clear()
            win_mechanism.refresh()
            stdscr.clear()
            stdscr.addstr(4, 1, f"____________________", curses.A_BOLD)
            stdscr.addstr(5, 1, f"{self.wpm(start_time)}")
            stdscr.addstr(6, 1, f"Wrong letter: {wrong_letter}", self.red)
            stdscr.addstr(7, 1, f"Right letter: {right_letter}", self.green)
            stdscr.addstr(8, 1, f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾", curses.A_BOLD)
            stdscr.addstr(9, 1, f"To restart and see result, click enter")
            stdscr.refresh()
            try:
                menu_input = win_mechanism.get_wch()
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

        if not(self.rows >= 20 and self.cols >= 100):
            raise "To small terminal, min. size: 20x100!"

        self.wpm_pad = curses.newpad(1, 10)
        self.time_pad = curses.newpad(1, 30)
        self.title_win = curses.newwin(1, 50, 10, 20)
        self.options_pad = curses.newpad(5, 50)
        choice = self.main_menu(stdscr)

        stdscr.clear()
        stdscr.refresh()

        self.mechanism_live(stdscr, choice[1])

if __name__ == "__main__":
    curses.wrapper(TypingSpeedTest().typing_speed)