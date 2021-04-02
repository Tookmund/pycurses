import curses
from time import sleep

def defaultwinwidth():
    return curses.COLS // 2

def main(stdscr):
    # Clear screen
    stdscr.clear()

    y, x = center(4, 8)
    stdscr.addstr(y, x, "TEST APP");
    stdscr.addstr(y+1, x, "(a) Add");
    stdscr.addstr(y+2, x, "(r) Remove");
    stdscr.addstr(y+3, x, "(s) Search");
    stdscr.getkey()

    s = search("Student ID")
    stdscr.clear()
    stdscr.addstr(s)
    stdscr.refresh()
    stdscr.getkey()

    r = form("TEST", "A", "B", "C")
    stdscr.clear()
    stdscr.addstr(str(r))
    stdscr.refresh()
    r = form("Short Long", "Very Long Text Sample")
    stdscr.clear()
    stdscr.addstr(str(r))
    stdscr.refresh()
    stdscr.getkey()

def autocomplete(s):
    #sleep(1)
    TEST = ["alpha", "beta", "gamma"]
    ret = []
    for t in TEST:
        if t.find(s) >= 0:
            ret.append(t)
    return ret

def center(height, width):
    return ((curses.LINES - height) // 2, (curses.COLS - width) // 2)

def is_backspace(key):
    # Many terminal configs are broken, outputting delete instead
    return key in ("KEY_BACKSPACE", "\b", "\x7f", "^?")

def makewin(height, width=None, title=None):
    # Account for the borders
    height += 2
    if width is None:
        width = defaultwinwidth()
    y, x = center(height, width)
    win = curses.newwin(height, width, y, x)
    win.keypad(True)
    win.box()
    if title is not None:
        win.addstr(0, (width - len(title)) // 2, title)
    return win

def search(what):
    width = defaultwinwidth()
    win = makewin(12, width)
    win.addstr(1, 1, what+": ")
    searchstr = ""
    k = ""
    curloc = [0,0]
    selection = -1
    newsearch = False

    while k != "\n":
        k = win.getkey()
        curloc[0], curloc[1]  = win.getyx()
        win.move(curloc[0], curloc[1])
        if k == "\n":
            break
        if is_backspace(k):
            if searchstr != "":
                win.move(curloc[0], curloc[1]-1)
                win.addstr(" ")
                curloc[1] -= 1
                searchstr = searchstr[:len(searchstr)-1]
                newsearch = True
        elif k in ("KEY_DOWN", "^[B"):
            if selection < len(res):
                selection += 1
            else:
                selection = -1
        elif k in ("KEY_UP", "^[A"):
            if selection > -1:
                selection -= 1
        elif len(k) == 1:
            if curloc[1] < width-1:
                win.addstr(k)
                newsearch = True
                searchstr += k
                curloc[1] += 1
        win.clrtobot()
        win.box()
        if newsearch:
            newsearch = False
            if searchstr == "":
                res = []
            else:
                res = autocomplete(searchstr)
        for i in range(len(res)):
            y = curloc[0]+1+i
            x = 1
            win.addstr(y, x, res[i])
            if i == selection:
                win.chgat(y, x, len(res[i]), curses.A_REVERSE)
        win.move(curloc[0], curloc[1])
        win.refresh()
    if selection != -1:
        return res[selection]
    return searchstr

def form(*args):
    title = args[0]
    args = args[1:]
    res = [None] * len(args)
    width = defaultwinwidth()
    win = makewin(len(args), width, title)
    for i in range(len(args)):
        win.addstr(i+1, 1, args[i]+": ")
    win.refresh()
    curses.echo()
    for i in range(len(args)):
        qwidth = len(args[i])+3
        win.move(i+1, qwidth)
        res[i] = win.getstr(width-qwidth-1)
    curses.noecho()
    return res

if __name__ == "__main__":
    curses.wrapper(main)
