from tkinter import Tk, Canvas
from os import path, makedirs, listdir, remove
from copy import deepcopy
from random import randint

SAVEDIR = "./DnD-Init-Tracker-Resources/"

BGCOLOR = "#1e1e1e"
HLCOLOR = "#3e3e3e"
SELECTCOLOR = "#9e8e00"

PLAYERCOLOR = "#1e4e1e"
ENEMYCOLOR = "#4e1e1e"
NPCCOLOR = "#1e1e4e"
STARCOLOR = "#6e6e1e"

FACTIONMAP = {
    "player": PLAYERCOLOR,
    "enemy": ENEMYCOLOR,
    "NPC": NPCCOLOR,
    "undef": HLCOLOR
}

def roll(n: int):
    return randint(1, n)

class Creature:
    def __init__(self, name, hp, ac, speed, faction, starred) -> None:
        self.name = name
        self.HitPoints = hp
        self.ArmorClass = ac
        self.InititativeBonus = speed
        self.InititativeValue = 0
        self.faction = faction
        self.starred = starred

    def prepare(self):
        self.InititativeValue = roll(20)
    
    def advance(self):
        self.InititativeValue += self.InititativeBonus
    
    def getAdvanced(self):
        self.advance()
        return self
    
    def damage(self, damage):
        self.HitPoints -= damage
    
    def __lt__(self, other):
        if self.InititativeValue != other.InititativeValue:  # might as well reverse it as a built-in
            return self.InititativeValue > other.InititativeValue
        if self.faction != other.faction:  # heroes go first
            if self.faction == "player":
                return True
            if other.faction == "player":
                return False
            if self.faction == "NPC":
                return True
            if other.faction == "NPC":
                return False
            return self.faction == "unset"
        if self.InititativeBonus != other.InititativeBonus:  # fatster goes first
           return self.InititativeBonus > other.InititativeBonus
        return self.name < other.name  # last resort

root = Tk()
root.title("D'n'D Combat Assistant | Ver 0.1.0")
root.geometry("1600x900")
root.update()

WUNIT, HUNIT = root.winfo_width() / 20, root.winfo_height() / 20
TRANSPOSE = HUNIT / WUNIT

MAINFONT = "Consolas 16"
DIALFONT = "Consolas 14"
SUBFONT = "Consolas 12"

SYMBOLMAP = {
    "space": " ",
    "plus": "+",
    "minus": "-"
}

canvas = Canvas(width=root.winfo_width(), height=root.winfo_height(), bg="#1e1e1e")
canvas.pack(fill="both", expand=True)

class WidgetBase:
    def __init__(self, x0, y0, width, height) -> None:
        self.rawEdges = (x0, y0, x0 + width, y0 + height)
        self.edges = (x0, y0, x0 + width, y0 + height)
        self.update()
        self.defaultFill = ""
        self.defaultOutline = "white"
        self.box = None
    
    def update(self):
        x0, y0, x1, y1 = self.rawEdges
        self.edges = (x0 * WUNIT, y0 * HUNIT, x1 * WUNIT, y1 * HUNIT)

    def draw(self):
        self.erase()
        self.box = canvas.create_rectangle(self.edges, fill=self.defaultFill, outline=self.defaultOutline)
    
    def erase(self):
        if self.box is not None:
            canvas.delete(self.box)
            self.box = None
    
    def cursorIn(self, x, y):
        x0, y0, x1, y1 = self.edges
        return (x0 < x and x < x1 and y0 < y and y < y1)
    
    def focusIn(self):
        canvas.itemconfig(self.box, fill=HLCOLOR)

    def focusOut(self):
        canvas.itemconfig(self.box, fill=self.defaultFill)
    
    def select(self):
        canvas.itemconfig(self.box, outline=SELECTCOLOR)

    def deselect(self):
        canvas.itemconfig(self.box, outline=self.defaultOutline)
    
    def get(self):
        return None

    def set(self):
        pass

    def input(self, keysim, char):
        pass

class LineWidget(WidgetBase):
    def __init__(self, x0, y0, x1, y1) -> None:
        super().__init__(x0, y0, x1 - x0, y1 - y0)
    
    def draw(self):
        self.erase()
        self.box = canvas.create_line(self.edges, fill=self.defaultOutline)
      
    def cursorIn(self, x, y):
        return False
    
    def focusIn(self):
        pass

    def focusOut(self):
        pass
    
    def select(self):
        pass

    def deselect(self):
        pass
    
class BorderedLabel(WidgetBase):
    def __init__(self, x0, y0, width, height, label, outlined=True) -> None:
        super().__init__(x0, y0, width, height)
        self.text = label
        self.textImage = None
        self.outlined = outlined
    
    def draw(self):
        self.erase()
        self.box = canvas.create_rectangle(self.edges, fill=self.defaultFill, outline = self.defaultOutline if self.outlined else "")
        x0, y0, x1, y1 = self.edges
        width, height = x1 - x0, y1 - y0
        self.textImage = canvas.create_text(x0 + width / 2, y0 + height / 2, anchor="center", text=self.text, fill="white", font=MAINFONT)
    
    def erase(self):
        super().erase()
        if self.textImage is not None:
            canvas.delete(self.textImage)
            self.textImage = None
    
    def focusIn(self):
        pass

    def focusOut(self):
        pass
    
    def select(self):
        pass

    def deselect(self):
        pass
    
    def set(self, value):
        self.text = value
        self.draw()

class ToggleableLabel(WidgetBase):
    def __init__(self, x0, y0, width, height, label, color, script=None) -> None:
        super().__init__(x0, y0, width, height)
        self.text = label
        self.textImage = None
        self.onColor = color
        self.currentFill = self.defaultFill
        self.on = False
        self.script = script
    
    def draw(self):
        self.erase()
        self.box = canvas.create_rectangle(self.edges, fill=self.currentFill, outline=self.defaultOutline)
        x0, y0, x1, y1 = self.edges
        width, height = x1 - x0, y1 - y0
        self.textImage = canvas.create_text(x0 + width / 2, y0 + height / 2, anchor="center", text=self.text, fill="white", font=MAINFONT)

    def erase(self):
        super().erase()
        if self.textImage is not None:
            canvas.delete(self.textImage)
            self.textImage = None

    def focusOut(self):
        canvas.itemconfig(self.box, fill=self.currentFill)

    def select(self):
        self.on = self.on ^ True
        self.currentFill = self.onColor if self.on else self.defaultFill
        if self.script is not None:
            self.script()

    def deselect(self):
        pass

    def get(self):
        return self.on

    def set(self, value):
        self.on = value
        self.currentFill = self.onColor if self.on else self.defaultFill
        self.draw()

class Button(WidgetBase):
    def __init__(self, x0, y0, width, height, label, script) -> None:
        super().__init__(x0, y0, width, height)
        self.text = label
        self.textImage = None
        self.script = script

    def draw(self):
        super().draw()
        x0, y0, x1, y1 = self.edges
        width, height = x1 - x0, y1 - y0
        self.textImage = canvas.create_text(x0 + width / 2, y0 + height / 2, anchor="center", text=self.text, fill="white", font=MAINFONT)

    def erase(self):
        super().erase()
        if self.textImage is not None:
            canvas.delete(self.textImage)
            self.textImage = None

    def select(self):
        self.script()

    def deselect(self):
        pass

class TextField(WidgetBase):
    def __init__(self, x0, y0, width, height) -> None:
        super().__init__(x0, y0, width, height)
        self.text = ""
        self.textImage = None

    def draw(self):
        super().draw()
        x0, y0, x1, y1 = self.edges
        width, height = x1 - x0, y1 - y0
        self.textImage = canvas.create_text(x0 + width / 2, y0 + height / 2, anchor="center", text=self.text, fill="white", font=MAINFONT)

    def erase(self):
        super().erase()
        if self.textImage is not None:
            canvas.delete(self.textImage)
            self.textImage = None

    def input(self, keysim, char):
        if len(char) == 1 and ord(char) > 20:
            self.text = self.text + char
        elif keysim == "BackSpace" and len(self.text):
            self.text = self.text[:-1]
        elif keysim == "Delete" and len(self.text):
            self.text = ""
        elif SYMBOLMAP.get(keysim) is not None:
            self.text += SYMBOLMAP[keysim]
        if self.textImage is not None:
            canvas.itemconfig(self.textImage, text=self.text)

    def get(self):
        return self.text

    def set(self, value):
        self.text = value
        self.draw()

class NamedTextLine(WidgetBase):
    def __init__(self, x0, y0, width, name, textmode="sw", subtextmode="nw", script=None) -> None:
        self.defaultFill = ""
        self.defaultOutline = "white"
        self.rawEdges = (x0, y0 -  0.5, x0 + width, y0)
        self.edges = (x0, y0 -  0.5, x0 + width, y0)
        self.text = ""
        self.textmode = textmode
        self.undertext = name
        self.undertextmode = subtextmode
        self.box = None
        self.underline = None
        self.textImage = None
        self.underTextImage = None
        self.script = script
    
    def draw(self):
        self.erase()
        x0, y0, x1, y1 = self.edges
        width, height = x1 - x0, y1 - y0
        self.box = canvas.create_rectangle(self.edges, fill="", outline="")
        self.underline = canvas.create_line(x0, y1, x0 + width, y1, fill="white")
        self.textImage = canvas.create_text(x0 + (2 if self.textmode == "sw" else (width / 2)), y1, anchor=self.textmode, text=self.text, fill="white", font=DIALFONT)
        self.underTextImage = canvas.create_text(x0 + (2 if self.undertextmode == "nw" else (width / 2)), y1, anchor=self.undertextmode, text=self.undertext, fill="white", font=SUBFONT)

    def erase(self):
        if self.box is not None:
            canvas.delete(self.box)
            self.box = None
        if self.underline is not None:
            canvas.delete(self.underline)
            self.underline = None
        if self.textImage is not None:
            canvas.delete(self.textImage)
            self.textImage = None
        if self.underTextImage is not None:
            canvas.delete(self.underTextImage)
            self.underTextImage = None
    
    def select(self):
        canvas.itemconfig(self.underline, fill=SELECTCOLOR)

    def deselect(self):
        canvas.itemconfig(self.underline, fill=self.defaultOutline)

    def input(self, keysim, char):
        if len(char) == 1 and ord(char) > 20:
            self.text = self.text + char
        elif keysim == "BackSpace" and len(self.text):
            self.text = self.text[:-1]
        elif keysim == "Delete" and len(self.text):
            self.text = ""
        elif SYMBOLMAP.get(keysim) is not None:
            self.text += SYMBOLMAP[keysim]
        if self.textImage is not None:
            canvas.itemconfig(self.textImage, text=self.text)
        if self.script is not None:
            self.script()

    def get(self):
        return self.text

    def set(self, value):
        self.text = value
        self.draw()

class ColorBox(WidgetBase):
    def __init__(self, x0, y0, width, height, colors=["", "white"]) -> None:
        super().__init__(x0, y0, width, height)
        self.colors = colors
        self.current = 0
        self.checkBox = canvas.create_rectangle(x0 + 5, y0 + 5, x0 + width - 4, y0 + height - 4, fill=self.colors[self.current], outline="")
    
    def select(self):
        self.current = (self.current + 1) % len(self.colors)
        canvas.itemconfig(self.checkBox, fill=self.colors[self.current])

    def get(self):
        return self.colors[self.current]

    def set(self, value):
        self.current = value
        self.draw()

widgets = []
ghosts = []
focusedWidget = None
selectedWidget = None

class Master():
    def __init__(self) -> None:
        self.editor = None
        self.collection = None
        self.battle = None
        self.settings = None
        self.logs = None
    
    def addCollectionCreature(self, creature):
        if self.collection is not None and creature is not None:
            self.collection.addCreature(creature)
    
    def setEtitorToCreatue(self, creature):
        if self.editor is not None and creature is not None:
            self.editor.setValues(creature)
    
    def forwardCreatureToBattle(self, creature):
        if self.battle is not None and creature is not None:
            self.battle.addCreature(deepcopy(creature))

appMaster = Master()

class WidgetManagerBase:
    def __init__(self) -> None:
        self.widgets = {}
    
    def addWidget(self, widget, tag):
        global widgets
        self.widgets[tag] = widget
        widgets.append(widget)
    
    def getWidgetData(self, tag):
        widget = self.widgets.get(tag)
        if widget is not None:
            return widget.get()

def exclusiveLabelSelector(manager, labels, current):
    if not manager.getWidgetData(current):
        return
    for label in labels:
        if label == current:
            continue
        if manager.getWidgetData(label):
            manager.widgets[label].set(False)

def exclusiveFilterSelector(manager, labels, current):
    exclusiveLabelSelector(manager, labels, current)
    manager.fullUpdate()

class EditorManager(WidgetManagerBase):
    def __init__(self) -> None:
        super().__init__()

        editorHead = BorderedLabel( 0.0,  0.0,  6.0,  1.0, "Editor")
        self.addWidget(editorHead, "head")

        favoriteMarker = ToggleableLabel( 0.5, 1.2,  0.75 * TRANSPOSE,  0.75, "*", STARCOLOR)
        self.addWidget(favoriteMarker, "favorite")
        nameField = NamedTextLine( 0.7 + 0.75 * TRANSPOSE,  1.7,  5.5 - (0.7 + 0.75 * TRANSPOSE), "name")
        self.addWidget(nameField, "name")

        factionPlayer = ToggleableLabel( 0.500,  2.2,  1.666,  0.5, "Player", PLAYERCOLOR, lambda : exclusiveLabelSelector(self, ["isPlayer", "isEnemy", "isNPC"], "isPlayer"))
        self.addWidget(factionPlayer, "isPlayer")
        factionEnemy = ToggleableLabel( 2.166,  2.2,  1.666,  0.5, "Enemy", ENEMYCOLOR, lambda : exclusiveLabelSelector(self, ["isPlayer", "isEnemy", "isNPC"], "isEnemy"))
        self.addWidget(factionEnemy, "isEnemy")
        factionNPC = ToggleableLabel( 3.832,  2.2,  1.666,  0.5, "NPC", NPCCOLOR, lambda : exclusiveLabelSelector(self, ["isPlayer", "isEnemy", "isNPC"], "isNPC"))
        self.addWidget(factionNPC, "isNPC")

        hpField = NamedTextLine( 0.866,  3.4,  1.0, "hit points" , textmode="s")
        self.addWidget(hpField, "hp")
        acField = NamedTextLine( 2.4,  3.4,  1.0, "armor class", textmode="s")
        self.addWidget(acField, "ac")
        initField = NamedTextLine( 4.165,  3.4,  1.0, "initiative" , textmode="s")
        self.addWidget(initField, "initiative")

        saveButton = Button( 0.0,  4.0,  3.0,  1.0, "Save to Collection", lambda : appMaster.addCollectionCreature(self.makeCreature()))
        self.addWidget(saveButton, "save")
        toBattleButon = Button( 3.0,  4.0,  3.0,  1.0, "Add to Battle >>>", lambda : appMaster.forwardCreatureToBattle(self.makeCreature()))
        self.addWidget(toBattleButon, "toBattle")
    
    def makeCreature(self):
        name = self.getWidgetData("name")
        faction = "player" if self.getWidgetData("isPlayer") else ("enemy" if self.getWidgetData("isEnemy") else ("NPC" if self.getWidgetData("isNPC") else "undef"))
        hp = self.getWidgetData("hp")
        ac = self.getWidgetData("ac")
        init = self.getWidgetData("initiative")
        starred = int(self.getWidgetData("favorite"))
        if name == "" or hp == "" or ac == "" or init == "":
            print("some data missing")
            return None
        if (not hp.isdigit()) or (not ac.isdigit()):
            print("hp or ac is nan")
            return None
        if (init[0] == "-" and (not init[1].isdigit())) or (init[0] != "-" and (not init.isdigit())):
            print("init is nan")
            return None
        creature = Creature(name, int(hp), int(ac), int(init), faction, starred)
        self.setValues()
        return creature

    def setValues(self, creature=None):
        if creature is None:
            self.widgets["name"].set("")
            self.widgets["hp"].set("")
            self.widgets["ac"].set("")
            self.widgets["initiative"].set("")

            self.widgets["favorite"].set(0)
            self.widgets["isPlayer"].set(0)
            self.widgets["isEnemy"].set(0)
            self.widgets["isNPC"].set(0)
        else:
            self.widgets["name"].set(creature.name)
            self.widgets["hp"].set(str(creature.HitPoints))
            self.widgets["ac"].set(str(creature.ArmorClass))
            self.widgets["initiative"].set(str(creature.InititativeBonus))

            self.widgets["favorite"].set(1 if creature.starred else 0)
            self.widgets["isPlayer"].set(1 if creature.faction == "player" else 0)
            self.widgets["isEnemy"].set(1 if creature.faction == "enemy" else 0)
            self.widgets["isNPC"].set(1 if creature.faction == "NPC" else 0)

class CollectionManager(WidgetManagerBase):
    def __init__(self) -> None:
        super().__init__()

        self.creatureCollection = {}
        self.collectionStringWidgets = []

        self.creatureList = []
        self.creatureListShift = 0
        self.creatureLimit = 11

        self.textFilter = ""
        self.factionFilter = ""
        self.starredOnly = False

        self.scrollBounds = (0, 7, 6, 19)

        collectionHead = BorderedLabel( 0.0,  5.0,  6.0,  1.0, "Collection")
        self.addWidget(collectionHead, "head")

        searchBar = NamedTextLine(0.25,  6.6,  5.5, "search", script = lambda : self.fullUpdate())
        self.addWidget(searchBar, "search")

        filterPlayer = ToggleableLabel( 0.0, 19.0,  1.5,  1.0, "Players", PLAYERCOLOR, lambda : exclusiveFilterSelector(self, ["filterPlayer", "filterEnemy", "filterNPC"], "filterPlayer"))
        self.addWidget(filterPlayer, "filterPlayer")
        filterEnemy = ToggleableLabel( 1.5, 19.0,  1.5,  1.0, "Enemies", ENEMYCOLOR, lambda : exclusiveFilterSelector(self, ["filterPlayer", "filterEnemy", "filterNPC"], "filterEnemy"))
        self.addWidget(filterEnemy, "filterEnemy")
        filterNPC = ToggleableLabel( 3.0, 19.0,  1.5,  1.0, "NPCs", NPCCOLOR, lambda : exclusiveFilterSelector(self, ["filterPlayer", "filterEnemy", "filterNPC"], "filterNPC"))
        self.addWidget(filterNPC, "filterNPC")
        filterStarred = ToggleableLabel( 4.5, 19.0,  1.5,  1.0, "Starred", STARCOLOR, lambda : self.fullUpdate())
        self.addWidget(filterStarred, "filterStarred")

        self.attemptLoad()
    
    def attemptLoad(self):
        if not path.exists(SAVEDIR):
            makedirs(SAVEDIR)
        for name in listdir(SAVEDIR[:-1]):
            with open(SAVEDIR + name, "r") as file:
                try:
                    hp = int(file.readline().strip())
                    ac = int(file.readline().strip())
                    init = int(file.readline().strip())
                    faction = file.readline().strip()
                    starred = int(file.readline().strip())
                    creature = Creature(name, int(hp), int(ac), int(init), faction, starred)
                    self.addCreature(creature, save=False)
                except Exception:
                    continue
    
    def addCollectionItemWidgets(self, name="", starred=False):
        hBase = 7
        hShift = len(self.collectionStringWidgets)
        starredMark = ToggleableLabel( 0.25,  (hBase + hShift + 0.5),  0.75 * TRANSPOSE,  0.75, "*", STARCOLOR, lambda : self.updateCreatureStar(self.getNameByRow(hShift)))
        if starred:
            starredMark.set(True)
        starredMark.draw()
        widgets.append(starredMark)
        nameField = Button( 0.35 + 0.75 * TRANSPOSE,  (hBase + hShift + 0.5),  4.55 - (0.35 + 0.75 * TRANSPOSE),  0.75, name, lambda : appMaster.setEtitorToCreatue(self.creatureCollection[self.getNameByRow(hShift)]))
        nameField.draw()
        widgets.append(nameField)
        discardButton = Button( 4.65,  (hBase + hShift + 0.5),  0.5,  0.75, "X", lambda : self.deleteCreature(self.getNameByRow(hShift)))
        discardButton.draw()
        widgets.append(discardButton)
        toCombatButton = Button( 5.25,  (hBase + hShift + 0.5),  0.5,  0.75, ">>>", lambda : appMaster.forwardCreatureToBattle(self.creatureCollection[self.getNameByRow(hShift)]))
        toCombatButton.draw()
        widgets.append(toCombatButton)
        self.collectionStringWidgets.append({
            "isStarred": starredMark,
            "name": nameField,
            "discard": discardButton,
            "toCombat": toCombatButton
        })
    
    def getNameByRow(self, row):
        if row >= min(11, len(self.creatureList)):
            return None
        name = self.collectionStringWidgets[row]["name"].text
        return name

    def eraseList(self):
        for string in self.collectionStringWidgets:
            for widget in string.values():
                widget.erase()
                widgets.pop(widgets.index(widget))
        self.collectionStringWidgets = []
    
    def updateFilters(self):
        self.textFilter = self.getWidgetData("search")
        self.factionFilter = ""

        if self.getWidgetData("filterPlayer"):
            self.factionFilter = "player"
        elif self.getWidgetData("filterEnemy"):
            self.factionFilter = "enemy"
        elif self.getWidgetData("filterNPC"):
            self.factionFilter = "NPC"

        if self.getWidgetData("filterStarred"):
            self.starredOnly = True
        else:
            self.starredOnly = False

    def makeCreatureList(self):
        self.creatureList = []
        for name in self.creatureCollection.keys():
            if self.textFilter not in name:
                continue
            creature = self.creatureCollection[name]
            if self.factionFilter != "" and self.factionFilter != creature.faction:
                continue
            if self.starredOnly and (not creature.starred):
                continue
            self.creatureList.append(name)
        self.creatureList.sort()
    
    def shiftList(self, shift):
        canditate = self.creatureListShift + shift
        print(canditate)
        if canditate < 0:
            print("negative")
            return
        if canditate + self.creatureLimit > len(self.creatureList):
            print("too much")
            return
        print(f"{canditate} - shift OK")
        self.creatureListShift = canditate
        self.fullUpdate()
    
    def drawList(self):
        for idx in range(self.creatureListShift, min(self.creatureListShift + self.creatureLimit, len(self.creatureList))):
            creatureName = self.creatureList[idx]
            self.addCollectionItemWidgets(creatureName, self.creatureCollection[creatureName].starred)
    
    def fullUpdate(self):
        self.updateFilters()
        self.eraseList()
        self.makeCreatureList()
        if self.creatureListShift + self.creatureLimit > len(self.creatureList):
            self.creatureListShift = len(self.creatureList) - self.creatureLimit
        if self.creatureListShift < 0:
            self.creatureListShift = 0
        self.drawList()
    
    def addCreature(self, creature : Creature, save=True):
        self.creatureCollection[creature.name] = creature
        if save:
            self.saveCreature(creature)
        self.fullUpdate()
    
    def deleteCreature(self, creatureName):
        if self.creatureCollection.get(creatureName) is None:
            return
        del self.creatureCollection[creatureName]
        remove(SAVEDIR + creatureName)
        self.fullUpdate()
    
    def updateCreatureStar(self, creatureName):
        creature = deepcopy(self.creatureCollection[creatureName])
        creature.starred = creature.starred ^ 1
        self.creatureCollection[creatureName] = creature
        self.saveCreature(creature)
    
    def saveCreature(self, creature):
        if not path.exists(SAVEDIR):
            makedirs(SAVEDIR)
        with open(SAVEDIR + creature.name, "w+") as file:
            file.write(str(creature.HitPoints) + "\n")
            file.write(str(creature.ArmorClass) + "\n")
            file.write(str(creature.InititativeBonus) + "\n")
            file.write(str(creature.faction) + "\n")
            file.write(str(creature.starred) + "\n")

class BattleManager(WidgetManagerBase):
    def __init__(self) -> None:
        super().__init__()

        self.creatures = []
        self.roundCounter = 0
        self.turnCounter = 0

        self.battleStringWidgets = []

        battleHead = BorderedLabel( 6.0,  0.0,  8.0,  1.0, "Battlefield")
        self.addWidget(battleHead, "head")

        nextTurn = Button( 6.0, 19.0,  4.0,  1.0, "> Next Turn >", lambda : self.newTurn())
        self.addWidget(nextTurn, "nextTurn")
        nextRound = Button(10.0, 19.0,  4.0,  1.0, ">>> Next Round >>>", lambda : self.newRound())
        self.addWidget(nextRound, "nextRound")

    def newRound(self):
        if not len(self.creatures):
            return
        self.roundCounter += 1
        self.creatures = sorted([creature.getAdvanced() for creature in self.creatures])
        self.fullUpdate()
    
    def newTurn(self):
        if not len(self.creatures):
            return
        if self.turnCounter >= len(self.creatures) - 1 or self.roundCounter == 0:
            self.newRound()
            self.turnCounter = 0
        else:
            self.turnCounter += 1
        self.fullUpdate()

    def addBattleItemWidgets(self, creature):
        hBase = 2
        hShift = len(self.battleStringWidgets)

        LocalEPS = 0.01
        background = BorderedLabel( 6.0 + LocalEPS,  hBase + hShift + 0.0,  8.0 - LocalEPS, 1.0, "", outlined=False)
        if hShift == self.turnCounter and self.roundCounter:
            background.defaultFill = FACTIONMAP[creature.faction]
        background.draw()
        widgets.append(background)
        ghosts.append(background)

        initValue = BorderedLabel(  6.25,  hBase + hShift + 0.125,  0.75 * TRANSPOSE,  0.75, str(creature.InititativeValue))
        initValue.draw()
        widgets.append(initValue)
        initBonus = BorderedLabel(  6.35 + 0.75 * TRANSPOSE,  hBase + hShift + 0.125,  0.75 * TRANSPOSE,  0.75, str(creature.InititativeBonus))
        initBonus.draw()
        widgets.append(initBonus)

        name = BorderedLabel(  6.45 + 1.5 * TRANSPOSE,  hBase + hShift + 0.125,  4.55 - (0.45 + 1.5 * TRANSPOSE),  0.75, creature.name)
        name.draw()
        widgets.append(name)
        armorClass = BorderedLabel( 10.65,  hBase + hShift + 0.125,  0.5,  0.75, str(creature.ArmorClass))
        armorClass.draw()
        widgets.append(armorClass)
        hitPoints = BorderedLabel( 11.25,  hBase + hShift + 0.125,  0.5,  0.75, str(creature.HitPoints))
        hitPoints.draw()
        widgets.append(hitPoints)
        damageButton = Button( 11.85,  hBase + hShift + 0.125,  0.25,  0.75, "-", lambda : self.modifyHealth(hShift, -1))
        damageButton.draw()
        widgets.append(damageButton)
        healButton = Button( 12.60,  hBase + hShift + 0.125,  0.25,  0.75, "+", lambda : self.modifyHealth(hShift, 1))
        healButton.draw()
        widgets.append(healButton)
        damageTextField = TextField( 12.10,  hBase + hShift + 0.125,  0.5,  0.75)
        damageTextField.draw()
        widgets.append(damageTextField)
        killButton = Button( 12.95,  hBase + hShift + 0.125,  0.8,  0.75, "kill", lambda : self.removeCreature(hShift))
        killButton.draw()
        widgets.append(killButton)

        self.battleStringWidgets.append({
            "background": background,
            "initValue": initValue,
            "initBonus": initBonus,
            "name": name,
            "armorClass": armorClass,
            "hitPoints": hitPoints,
            "damageButton": damageButton,
            "healButton": healButton,
            "damageTextField": damageTextField,
            "killButton": killButton
        })
    
    def removeCreature(self, row):
        self.creatures.pop(row)
        if self.turnCounter > row:
            self.turnCounter -= 1
        if not len(self.creatures):
            self.roundCounter = 0
            self.turnCounter = 0
        self.fullUpdate()
    
    def modifyHealth(self, row, delta):
        value = int(self.battleStringWidgets[row]["damageTextField"].text)
        self.creatures[row].HitPoints += delta * value
        self.fullUpdate()

    def eraseList(self):
        for string in self.battleStringWidgets:
            for widget in string.values():
                widget.erase()
                widgets.pop(widgets.index(widget))
        self.battleStringWidgets = []
    
    '''
    def shiftList(self, shift):
        canditate = self.creatureListShift + shift
        print(canditate)
        if canditate < 0:
            print("negative")
            return
        if canditate + self.creatureLimit > len(self.creatureList):
            print("too much")
            return
        print(f"{canditate} - shift OK")
        self.creatureListShift = canditate
        self.fullUpdate()
    '''

    def drawList(self):
        for creature in self.creatures:
            self.addBattleItemWidgets(creature)
    
    def fullUpdate(self):
        self.eraseList()
        self.drawList()
    
    def addCreature(self, creature):
        self.creatures.append(creature)
        self.creatures[-1].prepare()
        self.creatures.sort()
        self.fullUpdate()

def cursorMove(event):
    global focusedWidget
    x, y = event.x, event.y
    if focusedWidget is not None and focusedWidget.cursorIn(x, y):
        return
    elif focusedWidget is not None:
        focusedWidget.focusOut()
        focusedWidget = None
    for widget in widgets:
        if widget.cursorIn(x, y) and widget not in ghosts:
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
        selectedWidget.input(event.keysym, event.char)

def mouseWithin(x, y, units):
    x0, y0, x1, y1 = units
    x0s, y0s, x1s, y1s = x0 * WUNIT, y0 * HUNIT, x1 * WUNIT, y1 * HUNIT
    if x <= x0s or x >= x1s or y <= y0s or y >= y1s:
        return False
    return True

def mouseScroll(event):
    x, y = event.x, event.y
    shift = int(-1 * event.delta / abs(event.delta))
    if mouseWithin(x, y, appMaster.collection.scrollBounds):
        appMaster.collection.shiftList(shift)

def configure(event):
    global WUNIT, HUNIT, widgets
    WUNIT, HUNIT = event.width / 20, event.height / 20
    for widget in widgets:
        widget.update()
        widget.draw()
    root.update()
    
def dud():
    print("Action Perofrmed")

def makeLayout():
    global widgets

    appMaster.editor = EditorManager()
    appMaster.collection = CollectionManager()
    appMaster.battle = BattleManager()

    widgets.append(LineWidget( 6.0,  0.0,  6.0, 20.0))  # colletion | battle separator
    widgets.append(LineWidget(14.0,  0.0, 14.0, 20.0))  # battle | settings separator

    for widget in widgets:
        widget.draw()

makeLayout()

canvas.bind("<Motion>", cursorMove)
canvas.bind("<Button-1>", LMBPress)
canvas.bind("<KeyPress>", keyPress)
canvas.bind("<MouseWheel>", mouseScroll)
canvas.bind("<Configure>", configure)
canvas.bind("<Escape>", lambda event: root.destroy())
canvas.focus_set()

root.mainloop()