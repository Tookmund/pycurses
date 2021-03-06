import curses
import sys

def menu(win, title, loop, *entries):
    """
    Creates a menu out of an existing curses window.

    win: A curses window object
    title: str, The title of the window, displayed as the first line of the menu
    loop: boolean, whether to keep going after an option is selected, or
        return the result of the selected option function instead
    entries: 3-element tuples used to create each menu item
        key: str, What key the user can press to directly select the menu item
        name: str, The name of the menu item
        function(win): The function to call when this item is selected
            If function is None, then menu will exit instead
            win: The curses window object originally passed to menu
            return: None

    +-------------------------------TITLE-------------------------------+
    |                                                                   |
    |                           (a) NAME A                              |
    |                           (b) NAME B                              |
    |                           (c) NAME C                              |
    |                                                                   |
    |                                                                   |
    |                                                                   |
    +-↑ ↓ to select, ENTER to accept, or press the key in parentheses---+
    """
    maxtitle = 0
    maxy, maxx = win.getmaxyx()
    for entry in entries:
        titlelen = len(entry[1])
        if titlelen > maxtitle:
            maxtitle = titlelen

    while True:
        win.clear()
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
        r = entries[selection][2](win)
        if not loop:
            return r

def search(title, autocomplete):
    """
    A curses search window with autocomplete functionality.

    title: str, What the user is trying to search for, used to title the window
    autocomplete(s, limit): The autocomplete function to call on user input
        s: str, The current user input
        limit: int, How many results to return
        return: list of 2 element tuples
            match: The actual matching text
            explain: Additional info the user might want about the match

    return: The final user input, either what they have selected, or the
    contents of the search box if they didn't select anything

    +------------------------------WHAT---------------------------------+
    |                                                                   |
    |-------------------------------------------------------------------|
    |AUTOCOMPLETE 1                                                     |
    |AUTOCOMPLETE 2                                                     |
    |AUTOCOMPLETE 3                                                     |
    |                                                                   |
    +-↑ ↓ to select, ENTER to accept------------------------------------+
    """
    width = max(defaultwinwidth(), len(title))
    height = curses.LINES // 2
    # One line for text entry, another for the horizontal separator
    limit = height-2
    win = makewin(height, width)
    addtitle(win, width, title)
    addhelptext(win)
    win.hline(2, 1, curses.ACS_HLINE, width)
    win.move(1, 1)
    searchstr = ""
    k = ""
    curloc = [0,0]
    selection = -1
    newsearch = True

    while k != "\n":
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
            if curloc[1] < width:
                win.addstr(k)
                newsearch = True
                searchstr += k
                curloc[1] += 1
        win.move(3,1)
        win.clrtobot()
        win.box()
        addtitle(win, width, title)
        addhelptext(win)
        if newsearch:
            selection = -1
            newsearch = False
            res = autocomplete(searchstr, limit)
        for i in range(len(res)):
            y = curloc[0]+2+i
            x = 1
            item = " ".join(res[i])
            win.addstr(y, x, item)
            if i == selection:
                win.chgat(y, x, len(item), curses.A_REVERSE)
        win.move(curloc[0], curloc[1])
        win.refresh()
        k = win.getkey()

    if selection != -1:
        return res[selection][0]
    return searchstr

def form(title, *args):
    """
    A curses window for form input

    title: str, The title of the form, displayed at the top
    *args: str, Name of each field to ask the user for
        Note that user input for each field can only be as long as one line
        One line is half of the columns available, which should be enough
        for any reasonable terminal these days

    return: List of all of the user inputs, in the same order the arguments
        were passed to form

    +---------------------------TITLE-----------------------------------+
    |A:                                                                 |
    |B:                                                                 |
    |C:                                                                 |
    |D:                                                                 |
    |                                                                   |
    +-↑ ↓ to select, ENTER to accept------------------------------------+

    """
    res = [None] * len(args)
    width = max(defaultwinwidth(), len(title))
    win = makewin(len(args), width, title)
    for i in range(len(args)):
        win.addstr(i+1, 1, args[i]+": ")
    win.refresh()
    curses.echo()
    for i in range(len(args)):
        qwidth = len(args[i])+2
        win.move(i+1, qwidth+1)
        res[i] = win.getstr(width-qwidth-1).decode("utf-8")
    curses.noecho()
    return res

def table(title, header, inputrows):
    """
    A curses window for displaying tabular information
    title: str, Window title, displayed in the top line
    header: [str], Array of lines to be displayed before the table in the window
    rows: [[any]], Array of rows, assumes all rows have the same length
    """
    rows = []
    for r in inputrows:
        rows.append([])
        for c in r:
            rows[-1].append(" "+str(c)+" ")
    if len(rows) == 0 or len(rows[0]) == 0:
        collen = [1]
    else:
        collen = [1] * len(rows[0])
    for r in rows:
        for i in range(len(r)):
            curlen = len(r[i])
            if collen[i] < curlen:
                collen[i] = curlen
    width = max(sum(collen)+len(collen), len(title), max([len(x) for x in header]))
    win = makewin(len(header)+(len(rows)*2), width, title)
    win.move(1,1)
    for i in range(len(header)):
        win.addstr(i+1, 1, header[i])

    for r in rows:
        y, x = win.getyx()
        win.move(y+1, 0)
        win.addch(curses.ACS_LTEE)
        for w in range(1, width+1):
            win.move(y+1, w)
            if win.inch() != curses.ACS_BTEE:
                win.addch(curses.ACS_HLINE)
        win.addch(y+1, width+1, curses.ACS_RTEE)
        win.move(y+2, 1)
        for i in range(len(r)):
            if i > 0:
                y, x = win.getyx()
                if r[i-1] != "  " and r[i] != "  ":
                    win.addch(curses.ACS_VLINE)
                    if win.inch(y-1, x) == curses.ACS_BTEE:
                        win.addch(y-1, x, curses.ACS_PLUS)
                    else:
                        win.addch(y-1, x, curses.ACS_TTEE)
                    win.addch(y+1, x, curses.ACS_BTEE)
                    win.move(y,x+1)
                else:
                    win.addstr(" ")
            spaces = " " * (collen[i] - len(r[i]))
            win.addstr(r[i]+spaces)
    win.refresh()
    win.getkey()

def alert(title, message):
    """
    A curses window for alerting the user

    title: str, Title of the window, displayed at the top
    message: str, Message to be displayed in the window
    +---------------------------TITLE-----------------------------------+
    | ALERT TEXT                                                        |
    |                                                                   |
    +-Press any key to continue-----------------------------------------+
    """
    message = message.split("\n")
    helptext = "Press any key to continue"
    width = max(max([len(x) for x in message]), len(helptext), len(title))
    win = makewin(len(message), width, title)
    y, x = 1, 1
    for m in message:
        win.addstr(y,x, m)
        y += 1
    win.addstr(y,1, "Press any key to continue")
    win.refresh()
    win.getkey()

# Helper functions for all the above window-making functions
# Could be useful to outside consumers, but not intended for their direct use

def defaultwinwidth():
    return curses.COLS // 2

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
    width += 2
    if width is None:
        width = max(defaultwidth(), len(title))
    y, x = center(height, width)
    try:
        win = curses.newwin(height, width, y, x)
    except:
        curses.endwin()
        print("\n\nYour Terminal is Too Small! Please get a bigger one and try again!")
        sys.exit(1)

    win.keypad(True)
    win.box()
    if title is not None:
        addtitle(win, width, title)
    return win

# Test functions demonstrating how to use this module

def main(stdscr):
    menu(stdscr, "TEST APP", True,
        ("a", "Autocomplete Test", autocomptest),
        ("f", "Form Test", formtest),
        ("t", "Table Test", tabletest),
        ("l", "Alert Test", alerttest),
        ("q", "Quit", None),
    )

def autocomptest(win):
    s = search("Autocomplete", sample_autocomplete)
    win.clear()
    win.addstr(s)
    win.refresh()
    win.getkey()

def sample_autocomplete(s, limit):
    lorum = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".lower().split()
    ret = []
    for t in lorum:
        if t.find(s) >= 0:
            ret.append((t, t.upper()))
    return ret[:limit]

def formtest(win):
    r = form("TEST", "A", "B", "C")
    win.clear()
    win.addstr(str(r))
    win.refresh()
    win.getkey()

def tabletest(win):
    table("TEST", "THIS IS MY TEST".split(), [
        ["electricity","everything","stuck","island","straw","bowl"],
        ["practice","frame","arm","managed","avoid","driving"],
        ["behavior","leather","another","fur","particularly","sale"],
        ["feel","indeed","continued","slept","forest","dance"],
        ["gather","facing","race","anyone","regular","fighting"],
        ["constantly","win","exciting","rest","positive","value"],
        ["failed","zero","summer","toward","park","spring"],
    ])

def alerttest(win):
    alert("TEST", "This is a long alert message for you to read")

# Functions for handling making windows from standard input

def stdin_menu(stdscr):
    options = []
    title = sys.argv[2].strip()
    for arg in sys.argv[3:]:
        a = arg.split(";")
        options.append((a[0], a[1], stdin_menu_select(a[0])))
    return menu(stdscr, title, False, *options)

def stdin_menu_select(option):
    def select_option(win):
        return option
    return select_option

def stdin_form(stdscr):
    title = sys.argv[2].strip()
    rl = form(title, *sys.argv[3:])
    s = ""
    for r in rl:
        s += r.decode("utf-8")+"\n"
    return s[:-1]

def stdin_table(stdscr):
    title = sys.argv[2].strip()
    header = sys.argv[3].split(";")
    rows = [x.split(";") for x in sys.argv[4:]]
    return table(title, header, rows)

def stdin_alert(stdscr):
    title = sys.argv[2].strip()
    message = sys.argv[3].strip()
    alert(title, message)

if __name__ == "__main__":
    func = None
    if len(sys.argv) == 1 or sys.argv[1] == "test":
        func = main
    else:
        if sys.argv[1] == "menu":
            func = stdin_menu
        elif sys.argv[1] == "form":
            func = stdin_form
        elif sys.argv[1] == "table":
            func = stdin_table
        elif sys.argv[1] == "alert":
            func = stdin_alert
    r = curses.wrapper(func)
    if r is not None:
        print(r)
