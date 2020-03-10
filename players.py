import random
import settings as set

class Player(object):

    def __init__(self, rootSystem, window):
        self.rootSystem = rootSystem
        self.window = window

    def takeTurn(self):
        pass

class HumanPlayer(Player):
    pass

class RandomPlayer(Player):
    def takeTurn(self):
        moves = self.rootSystem.legalMoves()
        if len(moves)==0:
            self.rootSystem.passTurn()
            return
        move = random.choice(moves)
        self.rootSystem.addToTip(move[0],move[1])

class GreedyPlayer(Player):
    def __init__(self, rootSystem, window):
        super().__init__(rootSystem, window)

    def takeTurn(self):
        moves = self.rootSystem.legalMoves()

        target = None
        tdist = 99999
        #horrifyingly inefficient
        for b in self.rootSystem.nutrients:
            for t in self.rootSystem.tips.keys():
                if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                if dist < tdist and self.rootSystem.tips[t]:
                    tdist = dist
                    target = b

        newmoves = []
        if target:
            for m in moves:
                if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist:
                    newmoves.append(m)

        margin = 0
        while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
            margin += 1
            if target:
                for m in moves:
                    if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
                        newmoves.append(m)

        if len(newmoves)==0:
            self.rootSystem.passTurn()
            return

        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1])

class GreedyForker(Player):
    def __init__(self, rootSystem, window):
        super().__init__(rootSystem, window)

    def takeTurn(self):
        moves = self.rootSystem.legalMoves()

        target = None
        oldtarget = None
        origin = None
        tdist = 99999
        olddist = 99999
        oldorigin = None
        fork = True
        #find the closest and second closest nutrients
        for b in self.rootSystem.nutrients:
            for t in self.rootSystem.tips.keys():
                if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                if dist <= tdist and self.rootSystem.tips[t]:
                    tdist = dist
                    if b != target:
                        olddist = tdist
                        oldtarget = target
                        oldorigin = origin
                    target = b
                    origin = t

        newmoves = []
        if target:
            for m in moves:
                if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist:
                    newmoves.append(m)
            #if there is a second closest
            if oldtarget:
                newdist = abs(target[0]-oldtarget[0])+abs(target[1]-oldtarget[1])+abs(target[2]-oldtarget[2])
                #if the second closest nutrient is best reached from a tip other than origin, don't fork
                if oldorigin != origin:
                    fork = False
                #if it's easier to reach the second closest nutrient from the target than from the tip that will approach the target, do not fork
                if fork and (newdist-olddist < set.FORK_COST/set.ROOT_COST):
                    fork = False
            else:
                #if there is only 1 nutrient known, do not fork
                fork = False

        #accept sideways or backwards moves when moving toward the target is not possible
        margin = 0
        while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
            margin += 1
            if target:
                for m in moves:
                    if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
                        newmoves.append(m)

        if len(newmoves)==0:
            self.rootSystem.passTurn()
            return

        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1], fork)
