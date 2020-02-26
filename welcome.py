# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:02:27 2020

@author: joshm
"""
import pyglet
from pyglet.gl import gl 
import PySimpleGUI as sg # for the interactive pop-ups
# import plantcraft

# a list holding all of the settings thus far: [Player1, Player2, [density, proximity?, visibility, gamemode]]
all_settings = ['Human Player', 'None', [10.0, False, 5.0, '3D mode']]


# The pop-up window with a drop-down menu for selecting player 1's type
def _player1():
    sg.theme('DarkGreen')
    layout = [           
    [sg.InputCombo(('Human Player', 'AI Player'), size=(35, 10))],      
    [sg.Submit(tooltip='Click to submit this window'), sg.Cancel()]    
    ] 
    
    window = sg.Window('Select Player 1', layout)    

    event, values = window.read()    
    window.close()
    if event[0] == 'S':
        return values[0]
    
# The pop-up window with a drop-down menu for selecting player 2's type
def _player2():
    sg.theme('DarkGreen')
    layout = [           
    [sg.InputCombo(('Human Player', 'AI Player', 'None'), size=(35, 10))],      
    [sg.Submit(tooltip='Click to submit this window'), sg.Cancel()]    
    ]  

    window = sg.Window('Select Player 2', layout)    

    event, values = window.read()    
    window.close()
    if event[0] == 'S':
        return values[0]
    
    
# Settings includes all input data for non-player settings information
def _settings():    
    sg.theme('DarkGreen')
    layout = [
            [sg.Text('Game Settings', size=(30, 1), justification='center', font=("Impact", 25))],

            [sg.Text('Select nutrient density... (10 ==> ~10% of blocks are nutrients)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 10)],
            
            # Allow nutrient proximity?
            [sg.Text('Allow proximity visibility?', font=("Helvetica", 10))],
            [sg.Checkbox('Proximity on', size=(10,1), default=False)],
            # [sg.Radio('Proximity on     ', "Selected proximity", default=True, size=(10,1)), sg.Radio('Proximity off', "off")],
            
            [sg.Text('Select nutrient visibility... (how many blocks away do nutrient become visible?)', font=("Helvetica", 10))],
            [sg.Slider(range=(0, 100), orientation = 'h', size = (34,20), default_value = 5)],
            
            #2D mode
            [sg.Text('Select a graphics mode...', font=("Helvetica", 10))],
            [sg.InputCombo(('3D mode', '2D mode', 'No graphics'), size=(35, 10))],
            
            [sg.Submit(tooltip='Click to submit this window'), sg.Cancel()] 
            ]
    
    window = sg.Window('Settings', layout)
    
    event, values = window.read()
    window.close()
    if event[0] == 'S':
        return [values[0], values[1], values[2], values[3]] #make a list of all the items to return
    

# =============================================================================
# This is the button class which creates an object of a grey
# rectangular button that can be clicked to incite certain
# reactions.
# =============================================================================
class Button(pyglet.sprite.Sprite):
    def __init__(self, x, y):
        self.texture = pyglet.image.load("button.png")
        super(Button, self).__init__(self.texture, x, y)
        
    def click(self, x, y):
        if x >= self.x and y>= self.y:
            if x<=self.x + self.texture.width and y<=self.y + self.texture.height:
                return self
        
        
# =============================================================================
#     This is the main class which creates the total window. The class
# makes use of many things already available in the window superclass of
# pyglet. The run method of pyglet.app.run() is over-riden in order to make
# a self-sufficient class. Four Button object are made, the intention is to
# have those be clickable to incite settings options which are implemented 
# through PySimpleGUI window pop-ups.
# =============================================================================
class Mainscreen(pyglet.window.Window):
    def __init__(self):
        super(Mainscreen, self).__init__(800, 600, 'Welcome to PlantCraft!')
        logo = pyglet.image.load("logo.png") 
        self.title = pyglet.sprite.Sprite(logo, x = 100 , y=450)
        floor = pyglet.image.load("ground.png")
        self.bottom = pyglet.sprite.Sprite(floor, x=-150, y=-150)     
        self.buttons = {}
        self.buttons['Player1'] = Button(120, 340)
        self.buttons['Player2'] = Button(500, 340)
        self.buttons['Settings']= Button(310, 260)
        self.buttons['Play']=Button(310, 150)
        self.text = pyglet.text.Label('Player 1', font_name ='Times New Roman',
                                      font_size = 26, x=155, y=415, 
                                      color=(66, 99, 245, 255))
        self.text2 = pyglet.text.Label('Player 2', font_name ='Times New Roman',
                                      font_size = 26, x=535, y=415, 
                                      color=(235, 26, 26, 255))
        self.text3 = pyglet.text.Label('Settings', font_name = 'Times New Roman',
                                       font_size = 26, x=340, y =335, 
                                       color=(0, 0, 0, 255))
        self.text4 = pyglet.text.Label('CRAFT!', font_name = 'Impact',
                                       font_size = 26, x=350, y =220, 
                                       color=(5, 110, 30, 255))
        self.alive = 1
        background_color = (.0, .65, .0, 1)
        gl.glClearColor(*background_color)

        
    # make the window visible to the screen
    def on_draw(self):
        self.clear()  
        self.title.draw()
        self.bottom.draw()
        self.text.draw()
        self.text2.draw()
        self.text3.draw()
        self.text4.draw()
        for item, sprite in self.buttons.items():
            sprite.draw()
    
    # closes the window via the top-right corner "X"
    def on_close(self):
        exit()
        
    
    # interact with the buttons via clicking, uses the Button click()
    def on_mouse_press(self, x, y, button, modifiers):
        for item, sprite in self.buttons.items():
            if sprite.click(x, y):
                if item is 'Player1':
                    all_settings[0] = _player1()   #the data returned by the window
                elif item is 'Player2':
                    all_settings[1] = _player2()
                elif item is 'Settings':
                    all_settings[2] = _settings()
                elif item is 'Play':
                    print("The selected settings are: "+str(all_settings))
                    self.alive = 0
                    #return all_settings    #return the selected settings
                    
                    
                    # Game will start when this area is reached
                    #Begin Game passes the information to the program to initialize the appropriate version of the game
    
    #over-rides the pyglet.app.run() 
    def run(self):
        while self.alive == 1:
            self.on_draw()
            event = self.dispatch_events()
        return all_settings
    
    
def main():           
    window = Mainscreen()   #make a complete instance of a window
    return window.run()    # essentially pyglet.app.run()

#EXPLORE, EXPLOIT, EXPAND, EXTERMINATE
    