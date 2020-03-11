# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:02:27 2020

@author: joshm, abraude
"""
import pyglet
from pyglet.gl import gl 
import PySimpleGUI as sg # for the interactive pop-ups
# import plantcraft

# a list holding all of the settings thus far: [Player1, Player2, [density, proximity?, visibility, gamemode]]
all_settings = ['Human Player', 'None', [10.0, False, 5.0, '3D mode']]
    
    
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
        return [values[5], values[6], [values[1], values[2], values[3], values[4]]] #make a list of all the items to return
    
    
def main():           
    return _settings()

#EXPLORE, EXPLOIT, EXPAND, EXTERMINATE
    