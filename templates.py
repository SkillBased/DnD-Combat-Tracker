from tkinter import Tk, Canvas

BGCOLOR = "#1e1e1e"
HLCOLOR = "#3e3e3e"
SELECTCOLOR = "#9e8e00"

ANEMOCOLOR = "#75c3aa"
CRYOCOLOR = "#9fd5e1"
DENDROCOLOR = "#a6c938"
ELECTROCOLOR = "#b08fc2"
GEOCOLOR = "#fab72e"
HYDROCOLOR = "#4b9ef1"
PYROCOLOR = "#ef7a35"
OMNICOLOR = "white"

root = Tk()
root.title("TCG outlet")

canvas = Canvas(width=1600, height=900, bg=BGCOLOR)
canvas.pack()

class WidgetBase:
    def __init__(self, x0, y0, width, height) -> None:
        self.edges = (x0, y0, x0 + width, y0 + height)
        self.box = canvas.create_rectangle(self.edges, fill="", outline="white")
    
    def cursorIn(self, x, y):
        x0, y0, x1, y1 = self.edges
        return (x0 < x and x < x1 and y0 < y and y < y1)
    
    def focusIn(self):
        canvas.itemconfig(self.box, fill=HLCOLOR)

    def focusOut(self):
        canvas.itemconfig(self.box, fill="")
    
    def select(self):
        canvas.itemconfig(self.box, outline=SELECTCOLOR)

    def deselect(self):
        canvas.itemconfig(self.box, outline="white")
    
    def input(self, char):
        pass

class TextField(WidgetBase):
    def __init__(self, x0, y0, width, height) -> None:
        super().__init__(x0, y0, width, height)
        self.text = "sample text"
        self.textImage = canvas.create_text(x0 + 10, y0 + height / 2, anchor="w", text=self.text, fill="white", font="consolas 18")
    
    def input(self, char):
        if len(char) == 1:
            self.text = self.text + char
        elif char == "BackSpace" and len(self.text):
            self.text = self.text[:-1]
        elif char == "Delete" and len(self.text):
            self.text = ""
        canvas.itemconfig(self.textImage, text=self.text)

class ColorBox(WidgetBase):
    def __init__(self, x0, y0, width, height, colors=["", "white"]) -> None:
        super().__init__(x0, y0, width, height)
        self.colors = colors
        self.current = 0
        self.checkBox = canvas.create_rectangle(x0 + 5, y0 + 5, x0 + width - 4, y0 + height - 4, fill=self.colors[self.current], outline="")
    
    def select(self):
        self.current = (self.current + 1) % len(self.colors)
        canvas.itemconfig(self.checkBox, fill=self.colors[self.current])

elementScale = ["", OMNICOLOR, ANEMOCOLOR, CRYOCOLOR, DENDROCOLOR, ELECTROCOLOR, GEOCOLOR, HYDROCOLOR, PYROCOLOR]
tf = TextField(100, 100, 300, 50)
cb = ColorBox(420, 100, 50, 50, elementScale)
widgets = [tf, cb]

focusedWidget = None
selectedWidget = None
def cursorMove(event):
    global focusedWidget
    x, y = event.x, event.y
    if focusedWidget is not None and focusedWidget.cursorIn(x, y):
        return
    elif focusedWidget is not None:
        focusedWidget.focusOut()
        focusedWidget = None
    for widget in widgets:
        if widget.cursorIn(x, y):
            focusedWidget = widget
            focusedWidget.focusIn()
            break

def LMBPress(event):
    global selectedWidget
    if selectedWidget is not None and focusedWidget != selectedWidget:
        selectedWidget.deselect()
    selectedWidget = focusedWidget
    if selectedWidget is not None:
        selectedWidget.select()

def keyPress(event):
    if selectedWidget is not None:
        selectedWidget.input(event.keysym)

canvas.bind("<Motion>", cursorMove)
canvas.bind("<Button-1>", LMBPress)
canvas.bind("<KeyPress>", keyPress)
canvas.focus_set()

root.mainloop()