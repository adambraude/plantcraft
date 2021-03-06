import random

from players import *

class APlayer(Player):
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)
        self.genestrand = settings["genes"]
        self.gene_length = settings["gene_length"]
        self.traits = []
        #Needs a genestrand of length 80
        #Trait 0: probability of restricting search to closest [Trait 4] nutrients
        #Trait 1: probability of picking a random nutrient as the target
        #Trait 2: Number of turns spent pursuing a target while following Trait 0 targeting. If turns run out, retarget.
        #Trait 3: Number of turns spent pursuing a target while following Trait 1 targeting
        #Trait 4: See Trait 1
        #Trait 5: Reluctance to fork
        #Trait 6: Higher value -> cares more about how far away nutrients are
        #Trait 7: Higher value -> more interest in pursuing far away nutrients
        self.readGenes()
        self.target = None
        self.persistence = 0
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[j+i*self.gene_length] == '1':
                    count += 1
            self.traits.append(count)
        if self.traits[2] == self.gene_length: self.traits[2] = 9999
        if self.traits[3] == self.gene_length: self.traits[3] = 9999
        
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
            else:
                self.persistence -= 1
        if not self.target:
            #print("choosing target")
            self._findTarget()
            self._moveTowardTarget()
        else:
            self._moveTowardTarget()
        if tipflag or self.persistence < 0:
            self.target = None

    def _findTarget(self):
        self.target = None
        oldtarget = None
        shortestDist = 999999
        longestDist = 0
        closest = []
        olddist = 0
        oldorigin = None
        dists = []
         
        for b in self.rootSystem.nutrients:
            for t in self.rootSystem.tips.keys():
                if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                dists.append((b, dist))
        dists = sorted(dists, key=snd)
        closest = dists[:self.traits[4]]
        distWeight = self.traits[6]
        constWeight = self.traits[7]*2+1
        moveToMake = self.determineLikelihood()
        if moveToMake == 1:
            #print("exploring")
            if not dists:
                target = None
                return
            self.target = random.choices(dists, weights=[(1/(t[1]))*distWeight + 1/constWeight for t in dists], k=1)[0][0]
            self.alttarget = random.choices(dists, weights=[(1/(t[1]))*distWeight + 1/constWeight for t in dists], k=1)[0][0]
            self.persistence = self.traits[3]
        else:
            #print("exploiting")
            if not closest:
                target = None
                return
            self.target = random.choices(closest, weights=[(1/(t[1]))*distWeight + 1/constWeight for t in closest], k=1)[0][0]
            self.alttarget = random.choices(dists, weights=[(1/(t[1]))*distWeight + 1/constWeight for t in dists], k=1)[0][0]
            self.persistence = self.traits[2]


    def _moveTowardTarget(self):
        if not self.target: return
        moves = self.rootSystem.legalMoves()
        target = self.target
        tdist = 99999
        for t in self.rootSystem.tips.keys():
            if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
            d = abs(t[0]-target[0])+abs(t[1]-target[1])+abs(t[2]-target[2])
            if d < tdist:
                tdist = d
        fork = True
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
        if self.alttarget:
            newdist = abs(target[0]-self.alttarget[0])+abs(target[1]-self.alttarget[1])+abs(target[2]-self.alttarget[2])
            olddist = abs(move[0][0]-self.alttarget[0])+abs(move[0][1]-self.alttarget[1])+abs(move[0][2]-self.alttarget[2])
            for t in self.rootSystem.tips.keys():
                if olddist > abs(t[0]-self.alttarget[0])+abs(t[1]-self.alttarget[1])+abs(t[2]-self.alttarget[2]):
                    fork = False
                    continue
            if fork and (newdist-olddist - self.traits[5]^2 < self.rootSystem.world.set.FORK_COST/self.rootSystem.world.set.ROOT_COST):
                fork = False
        else:
            fork = False
        #print("moving from " + str(move[0]) + " to " + str(move[1]) + " in approach of target " + str(target))
        self.rootSystem.addToTip(move[0], move[1], fork)

def snd(tuple):
    return tuple[1]