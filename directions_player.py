# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 13:17:21 2020

@author: joshm
"""
import numpy as np
import random

class DirectionsPlayer(Player):
    def __init__(self, rootSystem, window, genes, gene_length):
        super().__init__(rootSystem, window)
        self.rootSystem.tipTex=TEXTURES[3]
        self.genestrand = genes
        self.gene_length = gene_length
        self.traits = []
        self.readGenes()
        self.probabilities = []
        self.prob_order = []
    
    # read gene strand
    def readGenes(self):
        # finds the count of alleles in a gene
        for i in range(int((len(self.genestrand))/self.gene_length)):
            count = 0
            for j in range(self.gene_length):
                if self.genestrand[j] == '1':
                    count += 1
            self.traits.append(count)
            self.traits.append(self.gene_length-count)
            i+=1
            print(self.traits)
        
        # read gene strand for this particular player and determine probabilities
    def determineLikelihood(self):
        #probRight 
        self.probabilities.append(random.randint(0, self.traits[0])) #x+1, y, z
        #probLeft 
        self.probabilities.append(random.randint(0, self.traits[1])) #x-1, y, z
        # probForward 
        self.probabilities.append(random.randint(0, self.traits[2])) #x, y, z+1
        # probBackward 
        self.probabilities.append(random.randint(0, self.traits[3])) #x, y, z-1
        # probDown
        self.probabilities.append(random.randint(0, self.traits[4])) #x, y-1, z
        # probUp
        self.probabilities.append(random.randint(0, self.traits[5])) #x, y+1, z
        # probFork 
        #self.probabilities.append(random.randint(0, self.traits[6]))
        self.prob_order = np.argsort(self.probabilities) #use probabilities back to front and loop through 
        return self.prob_order
        
    def takeTurn(self):
        #choose a move based on the likelihood
        moves_order = self.determineLikelihood()
        set_move = 0
        index = random.randint(1, len(self.rootSystem.tipPositions)-1)
        # while a move is possible and has not been taken
        for i in reversed(moves_order):
            if(set_move==1):
                break
            if(moves_order[i]==0):
                set_move = self._move(index,(1,0,0),False)
            if(moves_order[i]==1):
                set_move = self._move(index,(-1,0,0),False)
            if(moves_order[i]==2):
                set_move = self._move(index,(0,1,0),False)
            if(moves_order[i]==3):
                set_move = self._move(index,(0,-1,0),False)
            if(moves_order[i]==4):
                set_move = self._move(index,(0,0,1),False)
            if(moves_order[i]==5):
                set_move = self._move(index,(0,0,-1),False)
            #if(moves_order[i]==6):
            #    set_move = self._move(index,(0,1,0),True)


    def _move(self, index, adding, fork):
        move = ((self.rootSystem.tipPositions[index][0])+(adding[0]),(self.rootSystem.tipPositions[index][1])+(adding[1]), (self.rootSystem.tipPositions[index][2])+(adding[2]))
        if self.rootSystem.addToTip(self.rootSystem.tipPositions[index], move, fork):
            if fork:
                self.rootSystem.tipPositions.append(move)
            else:
                self.rootSystem.tipPositions[index] = move
            return 1
        else:
            return 0