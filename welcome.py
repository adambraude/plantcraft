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

            [sg.Checkbox('Replay?', size=(10,1), default=False, key="replay")],
            [sg.Text('File', size=(8, 1)), sg.Input(key="replayf"), sg.FileBrowse()],

            [sg.Text('Select a nutrient clustering mode', font=("Helvetica", 10))],
            [sg.InputCombo(('None', 'Chunk', 'Layered'), size=(35, 10), default_value='Chunk', key="n0", enable_events=True)],
            [sg.Text('Select nutrient density... (10 ==> ~10% of blocks are nutrients)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 1.2, resolution=0.1, key="density")],
            [sg.Text('Select chunk variance (higher->more variance)             ', font=("Helvetica", 10), key="n1")],
            [sg.Slider(range=(0, 1), orientation = 'h', size = (34,20), default_value = 0.2, resolution=0.01, key="cluster")],
            [sg.Text('Select chunk size                       ', font=("Helvetica", 10), key="n2")],
            [sg.Slider(range=(0, 10), orientation = 'h', size = (34,20), default_value = 3, resolution=1, key="clusterp")],

            # Allow nutrient proximity?
            [sg.Text('Allow proximity visibility?', font=("Helvetica", 10))],
            [sg.Checkbox('Proximity on', size=(10,1), default=False, key="proxy", enable_events=True)],
            # [sg.Radio('Proximity on     ', "Selected proximity", default=True, size=(10,1)), sg.Radio('Proximity off', "off")],
            
            [sg.Text('Select nutrient visibility... (how many blocks away do nutrient become visible?)', font=("Helvetica", 10), key="proxydistlabel", visible=False)],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 5, key="proxydist", visible=False)],
            
            #2D mode
            [sg.Text('Select a board configuration', font=("Helvetica", 10))],
            [sg.InputCombo(('3D mode', '2D mode'), size=(35, 10), default_value='3D mode', key="mode")],
            [sg.Text('Select Player 1', font=("Helvetica", 10))],
            [sg.InputCombo(('Human Player', 'RandomPlayer', 'GreedyPlayer', 'GreedyForker', 'ExploreExploitPlayer'), size=(35, 10),default_value='Human Player', key="player1", enable_events=True)],
            [sg.Input(key="gene1", visible = False)],
            [sg.Slider(range=(1, 100), orientation = 'h', size = (34,20), default_value = 10, resolution=1, key="gene1l", visible=False)],
            [sg.Text('Select Player 2', font=("Helvetica", 10))],    
            [sg.InputCombo(('Human Player', 'RandomPlayer', 'GreedyPlayer', 'GreedyForker', 'ExploreExploitPlayer', 'None'), size=(35, 10), default_value='GreedyPlayer', key="player2", enable_events=True)],
            [sg.Input(key="gene2", visible = False)],
            [sg.Slider(range=(1, 100), orientation = 'h', size = (34,20), default_value = 10, resolution=1, key="gene2l", visible=False)],
            [sg.Text('Select starting energy (as a multiple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 50, resolution=1, key="starte")],

            [sg.Text('Select fork cost (as a mutliple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(1, 100), orientation = 'h', size = (34,20), default_value = 8, resolution=1, key="fork")],

            [sg.Text('Select nutrient reward for claiming a nutrient block (as a mutliple of the cost to grow 1 block)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 2, resolution=1, key="reward")],

            [sg.Submit(tooltip='Click to submit this window'), sg.Cancel()],
            [sg.Image('ground.png')]
            
            ]

    layout = [
        [sg.Column(column1, element_justification='center')],
        
    ]
    
    window = sg.Window('Settings', layout)
    
    while (True):
        event, values = window.read()
        print(event)
        if event == 'Submit':
            print(values)
            players = []
            if values['player1'] == "ExploreExploitPlayer":
                players.append({"type":values["player1"], "genes":values["gene1"], "gene_length":int(values["gene1l"])})
            else:
                players.append({"type":values["player1"]})
            if values['player2'] == "ExploreExploitPlayer":
                players.append({"type":values["player2"], "genes":values["gene2"], "gene_length":int(values["gene2l"])})
            else:
                players.append({"type":values["player2"]})
            out = { "players":players, "mode":values["mode"], "PROX":values["proxy"], "PROX_RANGE":values["proxydist"], 
                    "DENSITY":values["density"], "STARTE":values["starte"], "FORK":values["fork"], "REWARD":values["reward"], 
                    "REPLAY":values["replay"], "REPLAYFILE":values["replayf"], "CLUSTER":values["cluster"], "CLUSTERP":values["clusterp"], "CLUSTERTYPE":values["n0"]}
            print(out)
            window.close()
            return out
        if event == 'Cancel':
            window.close()
            return None
        window['proxydist'].Update(visible = values["proxy"])
        window['proxydistlabel'].Update(visible = values["proxy"])
        if values['n0'] == "None":
            window['n1'].Update("irrelevant")
            window['n2'].Update("irrelevant")
        elif values['n0'] == "Chunk":
            window['n1'].Update("Select chunk variance (higher->more variance)")
            window['n2'].Update("Select chunk size")
        elif values['n0'] == "Layered":
            window['n1'].Update("Select nutrient clustering (higher->more clustering)")
            window['n2'].Update("Select nutrient clustering passes (more->larger clusters)")

        if values['player1'] == "ExploreExploitPlayer":
            window['gene1'].Update(visible = True)
            window['gene1l'].Update(visible = True)
        else:
            window['gene1'].Update(visible = False)
            window['gene1l'].Update(visible = False)
        if values['player2'] == "ExploreExploitPlayer":
            window['gene2'].Update(visible = True)
            window['gene2l'].Update(visible = True)
        else:
            window['gene2'].Update(visible = False)
            window['gene2l'].Update(visible = False)


    
    
def main():
    out = _settings()
    if out is None: exit(0)
    return out

#EXPLORE, EXPLOIT, EXPAND, EXTERMINATE
    