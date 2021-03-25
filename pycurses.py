import curses
from time import sleep

def main(stdscr):
    # Clear screen
    stdscr.clear()

    y, x = center(1, 8)
    stdscr.addstr(y, x, "TEST APP");
    stdscr.getkey()
    s = search("Student ID")
    stdscr.addstr(s)
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

def search(what):
    height = 12
    width = 40
    y, x = center(height, width)
    win = curses.newwin(height, width, y, x)
    win.keypad(1)
    win.box()
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
        if k in ("KEY_BACKSPACE", "\b", "\x7f", "^?"):
            if searchstr != "":
                win.move(curloc[0], curloc[1]-1)
                win.addstr(" ")
                curloc[1] -= 1
                searchstr = searchstr[:len(searchstr)-1]
                newsearch = True
        elif k in ("KEY_DOWN", "^[B"):
            if selection < len(res):
                selection += 1
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

if __name__ == "__main__":
    curses.wrapper(main)
