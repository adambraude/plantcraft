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

