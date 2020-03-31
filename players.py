import random

class Player(object):

    def __init__(self, rootSystem, window, settings):
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
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)

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
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)

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
                if fork and (newdist-olddist < self.rootSystem.world.set.FORK_COST/self.rootSystem.world.set.ROOT_COST):
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

class ExploreExploitPlayer(Player):
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)
        self.genestrand = settings["genes"]
        self.gene_length = settings["gene_length"]
        self.traits = []
        self.readGenes()
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[j] == '1':
                    count += 1
            self.traits.append(count)
        
        # read gene strand for this particular player and determine probabilities
    def determineLikelihood(self):
        # runs the probabilities based on allele counts in genes
        probExplore = random.randint(0, self.traits[0])
        probExploit = random.randint(0, self.traits[1])
        
        if probExplore > probExploit:
            return 0
        else:
            return 1
        
        # choose a turn to make
    def takeTurn(self):
        #determine if in explore or exploit mode
        moveToMake = self.determineLikelihood()
        if moveToMake == 0:
            self._exploitMove()
        else:
            self._exploreMove()
        #call the correct play turn based on the information from the string
        
# lazy repurposing of greedy to search outwards for furthest nutrient
    def _exploreMove(self):
        
        moves = self.rootSystem.legalMoves()                  
         
        target = None
        oldtarget = None
        origin = None
        tdist = 0
        olddist = 0
        oldorigin = None
        fork = True
         
        for b in self.rootSystem.world.nutrients:
                for t in self.rootSystem.tips.keys():
                    dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                    if dist >= tdist and self.rootSystem.tips[t]:
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
                if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) > tdist:
                    newmoves.append(m)
            
            if oldtarget:
                newdist = abs(target[0]-oldtarget[0])+abs(target[1]-oldtarget[1])+abs(target[2]-oldtarget[2])

                if oldorigin != origin:
                    fork = False

                if fork and (newdist-olddist < self.rootSystem.world.set.FORK_COST/self.rootSystem.world.set.ROOT_COST):
                    fork = False
            else:

                fork = False
 
         #accept sideways or backwards moves when moving toward the target is not possible
        margin = 0
        while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
            margin += 1
            if target:
                for m in moves:
                    if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
                        newmoves.append(m)
 
 
        if len(newmoves)==0: return
             
        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1], fork)


# use of greedy algorithm to exploit nearby blocks if called on
    def _exploitMove(self):
        
        moves = self.rootSystem.legalMoves()                  
         
        target = None
        oldtarget = None
        origin = None
        tdist = 99999
        olddist = 99999
        oldorigin = None
        fork = True
         #find the closest and second closest nutrients
        for b in self.rootSystem.world.nutrients:
                for t in self.rootSystem.tips.keys():
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
                if fork and (newdist-olddist < self.rootSystem.world.set.FORK_COST/self.rootSystem.world.set.ROOT_COST):
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
 
 
        if len(newmoves)==0: return
             
        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1], fork)
