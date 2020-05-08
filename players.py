import random
import numpy as np

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
        self.length_stay = 0
        self.moveToMake = self.determineLikelihood()
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[j+i*self.gene_length] == '1':
                    count += 1
            self.traits.append(count)
            self.traits.append(self.gene_length-count)
        
        # read gene strand for this particular player and determine probabilities
    def determineLikelihood(self):
        # runs the probabilities based on allele counts in genes
        probExploit = self.traits[0]
        self.length_stay = self.traits[1]
        #probExploit = random.randint(0, self.traits[1])
        
        if random.randint(0,self.gene_length) <= probExploit:
            return 0
        else:
            return 1
        
        # choose a turn to make
    def takeTurn(self):
        #determine if in explore or exploit mode
        if self.length_stay == 0:
            self.moveToMake = self.determineLikelihood()
            if self.moveToMake == 0:
                self._exploitMove()
            else:
                self._exploreMove()
        else: 
            self.length_stay -= self.length_stay
            if self.moveToMake == 0:
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
         
        for b in self.rootSystem.nutrients:
            for t in self.rootSystem.tips.keys():
                if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
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
 
 
        if len(newmoves)==0: return
             
        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1], fork)

class DirectionsPlayer(Player):
    def __init__(self, rootSystem, window, settings):
        super().__init__(rootSystem, window, settings)
        self.genestrand = settings["genes"]
        self.gene_length = settings["gene_length"]
        self.traits = [0,0,0,0,0,0]
        self.rand_traits = [0,0,0,0,0,0]
        self.readGenes()
        self.prob_order = []
        
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        #self.traits = []
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[(self.gene_length*i)+j] == '1':
                    count += 1
            self.traits[i] = count
            i+=1
            self.traits[i] = (self.gene_length-count)
            
            #print(self.traits)
        
        # read gene strand for this particular player and determine probabilities
    def determineLikelihood(self):
        for i in range(len(self.traits)):
            self.rand_traits[i] = random.randint(0, self.traits[i])
        self.prob_order = np.argsort(self.rand_traits) #use probabilities back to front and loop through 
        #print(self.prob_order)
        return self.prob_order
        
    def takeTurn(self):
        #choose a move based on the likelihood
        #legal_moves = self.rootSystem.legalMoves()
        #print(legal_moves)
        moves_order = self.determineLikelihood()
        #print(moves_order)
        set_move = 0
        
        # while a move is possible and has not been taken
        for i in reversed(moves_order):
            index = random.randint(1, len(self.rootSystem.tipPositions)-1)
            if(set_move==1):
                break
            if(moves_order[i]==0):
                set_move = self._move(index,(1,0,0))#,False)
            if(moves_order[i]==1):
                set_move = self._move(index,(-1,0,0))#,False)
            if(moves_order[i]==2):
                set_move = self._move(index,(0,1,0))#,False)
            if(moves_order[i]==3):
                set_move = self._move(index,(0,-1,0))#,False)
            if(moves_order[i]==4):
                set_move = self._move(index,(0,0,1))#,False)
            if(moves_order[i]==5):
                set_move = self._move(index,(0,0,-1))#,False)
            #if(moves_order[i]==6):
            #    set_move = self._move(index,(0,1,0),True)


    def _move(self, index, adding):#, fork):
        move = (self.rootSystem.tipPositions[index],((self.rootSystem.tipPositions[index][0])+(adding[0]),(self.rootSystem.tipPositions[index][1])+(adding[1]), (self.rootSystem.tipPositions[index][2])+(adding[2])))
        #print(move)
        if move in self.rootSystem.legalMoves():
            self.rootSystem.addToTip(move[0], move[1])
            #print("added")
            #if fork:
            #self.rootSystem.tipPositions.append(move)
            #else:
            self.rootSystem.tipPositions[index] = move[1]
            return 1
        else:
            return 0