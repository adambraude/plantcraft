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
    string = string[0:index]+place+string[index+1:]
    return string
    

def _point_mutation(string1, string2):
    # mutate random spots
    mutationChance = 0.5
    if random.random() < mutationChance:
        string1 = flip(string1)
        string2 = flip(string2)
    return string1, string2
    

def _crossover(string1, string2):
    tot_len = len(string1)
    cross_place = random.randint(0, tot_len-1)
    end_place = random.randint(cross_place, tot_len)
    start = 0
    ret_string1 = string1[start:cross_place]+string2[cross_place:end_place]+string1[end_place:tot_len]
    ret_string2 = string2[start:cross_place]+string1[cross_place:end_place]+string2[end_place:tot_len]
    return ret_string1, ret_string2
    

def _make_babies(string1, string2):
    child1, child2 = _crossover(string1, string2)
    return child1, child2
 
    
#_make_babies("0000000000000000", "1111111111111111")