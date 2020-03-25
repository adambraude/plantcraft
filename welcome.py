# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:02:27 2020

@author: joshm, abraude
"""
import pyglet
from pyglet.gl import gl 
import PySimpleGUI as sg # for the interactive pop-ups
# import plantcraft

# a dict holding all the settings
#all_settings = { "players":['Human Player', 'GreedyPlayer'], "TWODMODE":False, "PROX":True, "PROX_RANGE":5, "DENSITY":10}
    
    
# Settings includes all input data for non-player settings information
def _settings():    
    sg.theme('DarkGreen')

    column1 = [

            
            [sg.Image('logo.png')],
            [sg.Text('Game Settings', size=(30, 1), justification='center', font=("Impact", 25))],

            [sg.Text('Select nutrient density... (10 ==> ~10% of blocks are nutrients)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 10, resolution=0.1)],
            
            # Allow nutrient proximity?
            [sg.Text('Allow proximity visibility?', font=("Helvetica", 10))],
            [sg.Checkbox('Proximity on', size=(10,1), default=False)],
            # [sg.Radio('Proximity on     ', "Selected proximity", default=True, size=(10,1)), sg.Radio('Proximity off', "off")],
            
            [sg.Text('Select nutrient visibility... (how many blocks away do nutrient become visible?)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 5)],
            
            #2D mode
            [sg.Text('Select a board configuration', font=("Helvetica", 10))],
            [sg.InputCombo(('3D mode', '2D mode'), size=(35, 10), default_value='3D mode')],
            [sg.Text('Select Player 1', font=("Helvetica", 10))],
            [sg.InputCombo(('Human Player', 'RandomPlayer', 'GreedyPlayer', 'GreedyForker', 'GeneticPlayer'), size=(35, 10),default_value='Human Player')],
            [sg.Text('Select Player 2', font=("Helvetica", 10))],    
            [sg.InputCombo(('Human Player', 'RandomPlayer', 'GreedyPlayer', 'GreedyForker', 'GeneticPlayer', 'None'), size=(35, 10), default_value='GreedyPlayer')],
            
            [sg.Text('Select starting energy (as a multiple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 50, resolution=1)],

            [sg.Text('Select fork cost (as a mutliple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(1, 100), orientation = 'h', size = (34,20), default_value = 8, resolution=1)],

            [sg.Text('Select nutrient reward for claiming a nutrient block (as a mutliple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 2, resolution=1)],

            [sg.Submit(tooltip='Click to submit this window'), sg.Cancel()],
            [sg.Image('ground.png')]
            
            ]

    layout = [
        [sg.Column(column1, element_justification='center')],
        
    ]
    
    window = sg.Window('Settings', layout)
    
    event, values = window.read()
    window.close()
    if event[0] == 'S':
        print(values)
        out = { "players":[values[4], values[5]], "mode":values[3], "PROX":values[1], "PROX_RANGE":values[2], "DENSITY":values[0], "STARTE":values[6], "FORK":values[7], "REWARD":values[8]}
        print(out)
        return out
    
    
def main():
    out = _settings()
    if out is None: exit(0)
    return out

#EXPLORE, EXPLOIT, EXPAND, EXTERMINATE
    