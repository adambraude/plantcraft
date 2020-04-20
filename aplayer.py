import random

from players import *

class APlayer(Player):
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)
        self.genestrand = settings["genes"]
        self.gene_length = settings["gene_length"]
        self.traits = []
        self.readGenes()
        self.target = None
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[j+i*self.gene_length] == '1':
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
        self._move()
        
    def _move(self):
        tipflag = False
        #recalibrate when a tip is done absorbing nutrients
        for t in self.rootSystem.tips.keys():
            if (self.rootSystem.world.world[t] in self.rootSystem.absorb[-2:-1]): tipflag = True
        if self.target:
            #did something happen to the target?
            if self.target not in self.rootSystem.nutrients:
                self.target = None
        if not self.target:
            print("choosing target")
            self._findTarget()
            self._moveTowardTarget()
        else:
            self._moveTowardTarget()
        if tipflag:
            self.target = None

    def _findTarget(self):
        self.target = None
        oldtarget = None
        #self.origin = None
        shortestDist = 999999
        longestDist = 0
        closest = None
        furthest = None
        olddist = 0
        oldorigin = None
         
        for b in self.rootSystem.nutrients:
            for t in self.rootSystem.tips.keys():
                if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                if dist <= shortestDist and self.rootSystem.tips[t]:
                    shortestDist = dist
                    closest = b
                if dist >= longestDist and self.rootSystem.tips[t]:
                    longestDist = dist
                    furthest = b
        moveToMake = self.determineLikelihood()
        if moveToMake == 1:
            print("exploring")
            self.target = furthest
        else:
            print("exploiting")
            self.target = closest

    def _moveTowardTarget(self):
        moves = self.rootSystem.legalMoves()
        target = self.target
        tdist = 99999
        for t in self.rootSystem.tips.keys():
            if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
            d = abs(t[0]-target[0])+abs(t[1]-target[1])+abs(t[2]-target[2])
            if d < tdist:
                tdist = d
        fork = False
        newmoves = []
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

        if len(newmoves)==0: return
             
        move = random.choice(newmoves)
        #print("moving from " + str(move[0]) + " to " + str(move[1]) + " in approach of target " + str(target))
        self.rootSystem.addToTip(move[0], move[1], fork)