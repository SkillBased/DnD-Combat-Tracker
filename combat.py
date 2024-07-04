from random import randint

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

class Combat:
    def __init__(self) -> None:
        self.creatures = []
        self.roundCounter = 0
        self.turnCounter = 0
    
    def addCreature(self, creature):
        self.creatures.append(creature)
        self.creatures[-1].prepare()
    
    def newRound(self):
        self.roundCounter += 1
        self.creatures = sorted([creature.getAdvanced() for creature in self.creatures])
    
    def newTurn(self):
        if self.turnCounter == 0:
            self.newRound()
        snapshot = (self.roundCounter, self.turnCounter + 1, self.creatures[self.turnCounter])
        self.turnCounter = (self.turnCounter + 1) % len(self.creatures)
        return snapshot
    
