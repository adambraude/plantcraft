# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 21:28:51 2020

@author: joshm
"""
import random


def flip(string):
    index = random.randint(0, len(string)-1)
    place = '1'
    if string[index] == '1':
        place = '0'
        #string1 = string1[start:place]+swap_1+string1[(place+gene_length):]
    string = string[0:index]+place+string[index+1:]
    return string
    

def _point_mutation(string1, string2):
    # mutate random spots
    changes = random.randint(0,5)
    for i in range(changes):
        string1 = flip(string1)
        string2 = flip(string2)
    #print(string1)
    #print(string2)
    return string1, string2
    
def _swap(section1, section2):
    #print(section2)
    return2 = section2[:int(len(section2)/2)] + section1[:int(len(section1)/2)]
    #print(section2)
    #print(section1)
    return1 = section1[int(len(section1)/2):] + section2[int(len(section2)/2):]
    #print(section1)
    return return1, return2
    

def _crossover(string1, string2, gene_length):
    for i in range(int(len(string1)/gene_length)):
        # from i*genelength to another genelength away of the string
        
        place = i*gene_length
        start = 0
        swap_1, swap_2 = _swap(string1[place:(place+gene_length)], string2[place:(place+gene_length)])
        #print(place)
        #print(swap_1)
        #print(string1)
        string1 = string1[start:place]+swap_1+string1[(place+gene_length):]
        #print(place)
        #print(string1)
        string2 = string2[start:place]+swap_2+string2[(place+gene_length):]
    #print(string1)
    #print(string2)
    return string1, string2
    

def _make_babies(string1, string2, gene_length):
    child1, child2 = _crossover(string1, string2, gene_length)
    child1, child2 = _point_mutation(child1, child2)
    print(child1)
    print(child2)
    return child1, child2
 
    
_make_babies("0000000000000000", "1111111111111111", 4)
# _crossover("0101010101010101", "1010101010101010", 4)
#_point_mutation("0000000000000000000000", "1111111111111111111111")


class ExploreExploitPlayer(Player, genes):
    def __init__(self, rootSystem, window, genes):
        super().__init__(rootSystem, window)
        self.rootSystem.tipTex=TEXTURES[3]
        self.genestrand = genes
    
    def takeTurn(self):
        #determine if in explore or exploit mode
        
        #call the correct play turn based on the information from the string
        
# =============================================================================
#         moves = self.rootSystem.legalMoves()                  
#         
#         target = None
#         oldtarget = None
#         origin = None
#         tdist = 99999
#         olddist = 99999
#         oldorigin = None
#         fork = True
#         #find the closest and second closest nutrients
#         for b in self.rootSystem.world.world.keys():
#             if self.rootSystem.world.world[b] == TEXTURES[4]:
#                 for t in self.rootSystem.tips.keys():
#                     dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
#                     if dist <= tdist and self.rootSystem.tips[t]:
#                         tdist = dist
#                         if b != target:
#                             olddist = tdist
#                             oldtarget = target
#                             oldorigin = origin
#                         target = b
#                         origin = t
# 
#         newmoves = []
#         if target:
#             for m in moves:
#                 if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist:
#                     newmoves.append(m)
#             #if there is a second closest
#             if oldtarget:
#                 newdist = abs(target[0]-oldtarget[0])+abs(target[1]-oldtarget[1])+abs(target[2]-oldtarget[2])
#                 #if the second closest nutrient is best reached from a tip other than origin, don't fork
#                 if oldorigin != origin:
#                     fork = False
#                 #if it's easier to reach the second closest nutrient from the target than from the tip that will approach the target, do not fork
#                 if fork and (newdist-olddist < FORK_COST/ROOT_COST):
#                     fork = False
#             else:
#                 #if there is only 1 nutrient known, do not fork
#                 fork = False
# 
#         #accept sideways or backwards moves when moving toward the target is not possible
#         margin = 0
#         while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
#             margin += 1
#             if target:
#                 for m in moves:
#                     if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
#                         newmoves.append(m)
# 
# 
#         if len(newmoves)==0: return
#             
#         move = random.choice(newmoves)
#         self.rootSystem.addToTip(move[0],move[1], fork)
# =============================================================================
