import curses
from time import sleep

def defaultwinwidth():
    return curses.COLS // 2

def main(stdscr):
    menu(stdscr, "TEST APP",
        ("a", "Autocomplete Test", autocomptest),
        ("f", "Form Test", formtest),
		("q", "Quit", None),
    )

def autocomptest(stdscr):
    s = search("Autocomplete")
    stdscr.clear()
    stdscr.addstr(s)
    stdscr.refresh()
    stdscr.getkey()

def formtest(stdscr):
    r = form("TEST", "A", "B", "C")
    stdscr.clear()
    stdscr.addstr(str(r))
    stdscr.refresh()


def autocomplete(s):
    #sleep(1)
    TEST = ["alpha", "beta", "gamma"]
    ret = []
    for t in TEST:
        if t.find(s) >= 0:
            ret.append(t)
    return ret

def menu(stdscr, title, *entries):
    maxtitle = 0
    for entry in entries:
        titlelen = len(entry[1])
        if titlelen > maxtitle:
            maxtitle = titlelen

    while True:
        stdscr.box()
        addtitle(stdscr, curses.COLS, title)

        selection = 0
        key = ""
        while key != "\n":
            x = (curses.COLS - maxtitle) // 2
            # (key, title, function)
            for i in range(len(entries)):
                y = i+2
                item = "({}) {}".format(entries[i][0], entries[i][1])
                stdscr.addstr(y, x, item)
                if i == selection:
                    stdscr.chgat(y, x, len(item), curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getkey()
            if is_down(key):
                if selection < len(entries)-1:
                    selection += 1
                else:
                    selection = 0
            elif is_up(key):
                if selection > 0:
                    selection -= 1
                else:
                    selection = len(entries)-1
            else:
                for i in range(len(entries)):
                    if key == entries[i][0]:
                        selection = i
                        key = "\n"
                        break
        stdscr.clear()
        stdscr.refresh()
        if entries[selection][2] is None:
            return
        entries[selection][2](stdscr)

def center(height, width):
    return ((curses.LINES - height) // 2, (curses.COLS - width) // 2)

def is_backspace(key):
    # Many terminal configs are broken, outputting delete instead
    return key in ("KEY_BACKSPACE", "\b", "\x7f", "^?")

def is_up(key):
    return key in ("KEY_UP", "^[A")

def is_down(key):
    return key in ("KEY_DOWN", "^[B")

def addtitle(win, width, title):
    win.addstr(0, (width - len(title)) // 2, title)

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
        addtitle(win, width, title)
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
        elif is_down(k):
            if selection < len(res):
                selection += 1
            else:
                selection = -1
        elif is_up(k):
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
