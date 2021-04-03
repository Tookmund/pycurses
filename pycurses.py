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

def autocomptest(win):
    s = search("Autocomplete", sample_autocomplete)
    win.clear()
    win.addstr(s)
    win.refresh()
    win.getkey()

def formtest(win):
    r = form("TEST", "A", "B", "C")
    win.clear()
    win.addstr(str(r))
    win.refresh()
    win.getkey()

def sample_autocomplete(s, limit):
    #sleep(1)
    lorum = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".lower().split()
    ret = []
    for t in lorum:
        if t.find(s) >= 0:
            ret.append((t, t.upper()))
    return ret[:limit]

def menu(win, title, *entries):
    maxtitle = 0
    maxy, maxx = win.getmaxyx()
    for entry in entries:
        titlelen = len(entry[1])
        if titlelen > maxtitle:
            maxtitle = titlelen

    while True:
        curses.curs_set(0)
        win.box()
        addtitle(win, maxx, title)
        addhelptext(win, ", or press the key in parentheses")

        selection = 0
        key = ""
        while key != "\n":
            x = (maxx - maxtitle) // 2
            # (key, title, function)
            for i in range(len(entries)):
                y = i+2
                item = "({}) {}".format(entries[i][0], entries[i][1])
                win.addstr(y, x, item)
                if i == selection:
                    win.chgat(y, x, len(item), curses.A_REVERSE)
            win.refresh()

            key = win.getkey()
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
        curses.curs_set(1)
        win.clear()
        win.refresh()
        if entries[selection][2] is None:
            return
        entries[selection][2](win)

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

def addhelptext(win, additional=""):
    y, x = win.getmaxyx()
    win.addstr(y-1, 1, "↑ ↓ to select, ENTER to accept"+additional)

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

def search(what, autocomplete):
    width = defaultwinwidth()
    height = curses.LINES // 2
    limit = height-3
    win = makewin(height, width)
    addhelptext(win)
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
            selection = -1
            newsearch = False
            if searchstr == "":
                res = []
            else:
                res = autocomplete(searchstr, limit)
        for i in range(len(res)):
            y = curloc[0]+1+i
            x = 1
            item = " ".join(res[i])
            win.addstr(y, x, item)
            if i == selection:
                win.chgat(y, x, len(item), curses.A_REVERSE)
        win.move(curloc[0], curloc[1])
        win.refresh()
    if selection != -1:
        return res[selection][0]
    return searchstr

def form(title, *args):
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
