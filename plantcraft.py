from __future__ import division

import sys
import math
import random
import time
import re

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
import welcome
from world import World
from rootsystem import RootSystem
from players import *
import settings as set
import crossover
from pprint import pprint
#[player1, player2, [density, proximity?, prox distance, graphics mode]]
#['Human Player', 'None', [28.0, False, 5.0, '3D mode']]

all_settings = {}
all_settings = welcome.main()

TICKS_PER_SEC = 60

SPEED = 15


DEGREES= u'\N{DEGREE SIGN}'
DIRECTIONS = (key.N, key.S, key.W, key.E, key.U, key.D)
NUM_KEYS = (key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9, key._0)


#END = 'death'
END = 'points'
WIN_POINTS = 1000

#def adjust_settings(settings, TWODMODE):
#    if settings[2][3] == '2D mode':
 #       TWODMODE = True
    #else:
        #TWODMODE = False
        #print(TWODMODE)

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def calcTextureCoords(which, n=16):
    m = 1.0 / n
    left = (which)*m
    right = left+m - 0.001
    left += 0.001
    return 6*[left, 0.51, right, 0.51, right, 0.99, left, 0.99]

def printLog(filename = "logfile"):
    file = open(filename, "w")
    file.write(settings.LOG)
    file.close()

settings = set.Settings(all_settings)
playersDict = {"Human Player":HumanPlayer, "RandomPlayer":RandomPlayer, "GreedyPlayer":GreedyPlayer, "GreedyForker":GreedyForker, "ExploreExploitPlayer":ExploreExploitPlayer, "DirectionsPlayer":DirectionsPlayer}


class Window(pyglet.window.Window):

    

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.init()

    def init(self):
        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False
        self.done = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.motion = [0, 0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 10)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)
        self.reticle = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        if settings.LOGENABLED and not settings.REPLAY:
            settings.LOG += "(IE:" + str(settings.INIT_ENERGY) + ")\n"
            settings.LOG += "(RC:" + str(settings.ROOT_COST) + ")\n"
            settings.LOG += "(FC:" + str(settings.FORK_COST) + ")\n"
            settings.LOG += "(ER:" + str(settings.ENERGY_REWARD) + ")\n"
            if settings.PROX:
                settings.LOG += "(PR:" + str(settings.PROX_RANGE) + ")\n"
        # Instance of the model that handles the world.
        self.world = World(settings)
        if settings.REPLAY:
            file = open(settings.REPLAY_FILE, "r")
            settings.LOG = file.read()
            settings.PROX = False
            moves = re.split("[(),\n\s]+", settings.LOG)
            self.pos = 0
            while (moves[self.pos] !=  "W"):
                pre = moves[self.pos][:2]
                if (pre == "PR"):
                    settings.PROX = True
                    settings.PROX_RANGE = int(moves[self.pos][3:])
                if (pre == "IE"): settings.INIT_ENERGY = int(float(moves[self.pos][3:]))
                elif (pre == "RC"): settings.ROOT_COST = int(float(moves[self.pos][3:]))
                elif (pre == "FC"): settings.FORK_COST = int(float(moves[self.pos][3:]))
                elif (pre == "ER"): settings.ENERGY_REWARD = int(float(moves[self.pos][3:]))
                self.pos+= 1
            self.pos += 1
            file.close()
            for i in range(self.pos,len(moves),4):
                if moves[i] == "R": break
                #place nutrients
                x = int(moves[i+1])
                y = int(moves[i+2])
                z = int(moves[i+3])
                self.world.add_block((x,y,z), settings.TEXTURES[int(moves[i])])
                self.world.nutrients[x,y,z] = True
                if settings.PROX:
                    self.world.hide_block((x, y, z))
                self.pos = i
        self.rootSystems = []
        self.players = []
        self.stalks = []
        self.turnCount = 0


        if (settings.REPLAY):
            while (moves[self.pos] != "True" and moves[self.pos] != "False"):
                if (moves[self.pos] == "R"):
                    rip = RootSystem(self.world, (int(moves[self.pos+1]),int(moves[self.pos+2]),int(moves[self.pos+3])), settings.TWODMODE)
                    rip.energy = int(float(moves[self.pos+4][2:]))
                    self.rootSystems.append(rip)
                    self.players.append(Player(self.rootSystems[len(self.rootSystems)-1], self, {}))
                    self.stalks.append(0)
                    self.pos += 5
                elif (moves[self.pos] == "T"):
                    rip.add_block((int(float(moves[self.pos+1])),int(float(moves[self.pos+2])),int(float(moves[self.pos+3]))),rip.absorb[len(rip.absorb)-1])
                    self.pos += 4
                elif (moves[self.pos] == "S"):
                    rip.add_block((int(float(moves[self.pos+1])),int(float(moves[self.pos+2])),int(float(moves[self.pos+3]))),settings.STALK_TEXTURE)
                    self.pos += 4
                elif (moves[self.pos] == "B"):
                    rip.add_block((int(float(moves[self.pos+1])),int(float(moves[self.pos+2])),int(float(moves[self.pos+3])),settings.TEXTURES[0]))
                    self.pos += 4
                else:
                    self.pos += 1
            for r in self.rootSystems: r.initProx()
        else:
            i=0
            for p in settings.players:
                if p["type"] in playersDict:
                    player = playersDict[p["type"]]
                    if player is not None:
                        self.rootSystems.append(RootSystem(self.world, (10*i,0,0),settings.TWODMODE))
                        self.players.append(player(self.rootSystems[i], self, p))
                        self.stalks.append(0)
                        i += 1


        self.currentPlayerIndex = -1
        #drop all the already-read moves from memory.
        if settings.REPLAY: self.moves = moves[self.pos:]
        self.pos = 0

        if settings.GFX:
            self.positionLabel = pyglet.text.Label('', font_name="Arial", font_size=18, x=self.width/2,
                                                   anchor_x='center', y=self.height-10, anchor_y='top',
                                                   color=(255,255,255,255))

            self.controlsLabel = pyglet.text.Label("", font_name="Arial", font_size=18, x=self.width/4,
                                                   anchor_x="center", y=10, anchor_y="bottom", color=(255,255,255,255))
            self.controlsLabel.text = "l-grow r-fork"

            self.energyLabel = pyglet.text.Label("", font_name="Arial", font_size=18, x=self.width/4,
                                                 anchor_x="center", y=self.height-10, anchor_y="top", color=(255,0,0,255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
        self.nextTurn()


        
        #self.alive = 1

    def nextTurn(self):
        self.turnCount += 1
        if (settings.REPLAY):
            if self.pos >= len(self.moves): return
            while(self.moves[self.pos] != "True" and self.moves[self.pos] != "False"):
                self.pos += 1
                if self.pos >= len(self.moves): return
            if self.moves[self.pos] == "True": fork = True
            else: fork = False
            self.players[int(self.moves[self.pos+8])].rootSystem.addToTip((int(self.moves[self.pos+1]),int(self.moves[self.pos+2]),int(self.moves[self.pos+3])),(int(self.moves[self.pos+4]),int(self.moves[self.pos+5]),int(self.moves[self.pos+6])),fork)
            self.pos +=6
        else:
            self.currentPlayerIndex += 1
            if self.currentPlayerIndex >= len(self.players):
                self.currentPlayerIndex = 0
            self.players[self.currentPlayerIndex].takeTurn()
            if (settings.LOGENABLED and not isinstance(self.currentPlayer(), HumanPlayer)): settings.LOG += "(" + str(self.currentPlayerIndex) + ")"
            self.currentPlayer().takeTurn()
        self.updateStalks()

    def currentPlayer(self):
        return self.players[self.currentPlayerIndex]

    def checkEnd(self):
        for system in self.rootSystems:
            if system.energy <= 0:
                self.end = "death"
                return True
            if system.energy >= WIN_POINTS:
                self.end = "win"
                return True
        if not self.world.nutrients:
            self.end = "sweep"
            return True       
        return False

    def updateStalks(self):
        if self.currentPlayer().rootSystem.energy >= (self.stalks[self.currentPlayerIndex]+1) * (WIN_POINTS/11):
            self.stalks[self.currentPlayerIndex] += 1
            x, y, z = self.currentPlayer().rootSystem.position
            self.currentPlayer().rootSystem.add_block((x,y+self.stalks[self.currentPlayerIndex],z), settings.STALK_TEXTURE)
        elif self.currentPlayer().rootSystem.energy < self.stalks[self.currentPlayerIndex] * (WIN_POINTS/11):
            x, y, z = self.currentPlayer().rootSystem.position
            self.currentPlayer().rootSystem.world.remove_block((x,y+self.stalks[self.currentPlayerIndex],z))
            self.stalks[self.currentPlayerIndex] -= 1

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        #self.rootSystem.process_queue()
        self.world.process_entire_queue()
        m = 8
        dt = min(dt, 0.2)
        for _ in set.xrange(m):
            self._update(dt / m)
        if settings.GFX:
            if self.checkEnd():
                self.done = True
                maxi = self.rootSystems[0].energy
                self.winner = 0
                for i in range(len(self.rootSystems)):
                    if self.rootSystems[i].energy > maxi:
                        maxi = self.rootSystems[i].energy
                        self.winner = i

            else:
                if (not isinstance(self.currentPlayer(), HumanPlayer)):
                    self.nextTurn()
        else:
            while(not self.done):
                if self.checkEnd():
                    self.done = True
                    maxi = self.rootSystems[0].energy
                    self.winner = 0
                    self.stats = {"energy":[]}
                    for i in range(len(self.rootSystems)):
                        e = self.rootSystems[i].energy
                        self.stats["energy"].append(e)
                        if e > maxi:
                            maxi = e
                            self.winner = i
                    pyglet.clock.unschedule(self.update)
                    pyglet.app.exit()
                else:
                    self.nextTurn()

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        speed = SPEED
        d = dt * speed # distance covered this tick.
        x, y, z = self.position
        dx, dy, dz = [a * d for a in self.motion]
        theta = math.radians(self.rotation[0])
        x += dx*math.cos(theta) + -dz*math.sin(theta)
        y += dy
        z += dx*math.sin(theta) + dz*math.cos(theta)
        self.position = (x, y, z)



    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive and isinstance(self.currentPlayer(), HumanPlayer):
            vector = self.get_sight_vector()
            block, previous = self.rootSystems[self.currentPlayerIndex].hit_test(self.position, vector, 8, [settings.NUTRIENT_TEXTURE])
            if block and (self.world.world[block] in settings.ABSORB):
                if (button == mouse.RIGHT) or \
                        ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                    # ON OSX, control + left click = right click.
                    if previous:
                        self.rootSystems[self.currentPlayerIndex].addToTip(block, previous,True)
                        if (settings.LOGENABLED): settings.LOG += "(" + str(self.currentPlayerIndex) + ")"
                        self.nextTurn()
                elif button == pyglet.window.mouse.LEFT and block and previous:
                    self.rootSystems[self.currentPlayerIndex].addToTip(block, previous)
                    if (settings.LOGENABLED): settings.LOG += "(" + str(self.currentPlayerIndex) + ")"
                    self.nextTurn()
        else:
            if settings.GFX: self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if not settings.GFX: return
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if not settings.GFX: return
        if symbol == key.LEFT or symbol== key.A:
            self.motion[0] -= 1
        elif symbol == key.RIGHT or symbol == key.D:
            self.motion[0] += 1
        elif symbol == key.SPACE:
            self.motion[1] += 1
        elif symbol == key.LSHIFT:
            self.motion[1] -= 1
        elif symbol == key.UP or symbol == key.W:
            self.motion[2] -= 1
        elif symbol == key.DOWN or symbol == key.S:
            self.motion[2] += 1
        elif symbol == key.ESCAPE:
            if settings.GFX: self.set_exclusive_mouse(False)
        elif symbol == key.BACKSPACE:
            printLog()

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if not settings.GFX: return
        if symbol == key.LEFT or symbol== key.A:
            self.motion[0] += 1
        elif symbol == key.RIGHT or symbol == key.D:
            self.motion[0] -= 1
        elif symbol == key.SPACE:
            self.motion[1] -= 1
        elif symbol == key.LSHIFT:
            self.motion[1] += 1
        elif symbol == key.UP or symbol == key.W:
            self.motion[2] += 1
        elif symbol == key.DOWN or symbol == key.S:
            self.motion[2] -= 1

    def on_resize(self, width, height):
        if not settings.GFX: return
        """ Called when the window is resized to a new `width` and `height`.

        """
        # adjust labels
        self.positionLabel.x = width/2
        self.positionLabel.y = height-10

        self.energyLabel.x = width/4
        self.energyLabel.y = height-10
        #reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # remember OpenGL is backwards!
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x,y,z = self.position
        glTranslatef(-x, -y, -z)

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block, previous = self.rootSystems[self.currentPlayerIndex].hit_test(self.position, vector, 8, [settings.NUTRIENT_TEXTURE])
        if block and (self.world.world[block] in settings.ABSORB):
            x, y, z = previous
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        if (settings.GFX):
            self.clear()
            self.set_3d()
            glColor3d(1, 1, 1)
            self.world.batch.draw()
            if isinstance(self.currentPlayer(), HumanPlayer): self.draw_focused_block()
            self.set_2d()
            self.draw_labels()
            self.draw_reticle()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    def draw_labels(self):
        """ Draw all the random text around the screen

        """
        #self.positionLabel.text = "(%d,%d,%d,%d%s,%d%s)" % (self.position[0], self.position[1], self.position[2], self.rotation[0], DEGREES, self.rotation[1], DEGREES)
        #self.positionLabel.draw()

        self.controlsLabel.draw()

        self.energyLabel.text = ""
        for i in range(len(self.rootSystems)):
            self.energyLabel.text += "P%d Energy: %d" % (i+1,self.rootSystems[i].energy) + "  "
        self.energyLabel.draw()

    def on_close(self):
     #   print('trying to close')
         pyglet.app.exit()

     #   return 0

def setup_fog():
    """ Configure the OpenGL fog properties.

    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    #glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0, 0, 0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    """ Basic OpenGL configuration.

    """
    # Set the color of "clear", i.e. the sky, in rgba.
    #glClearColor(0.5, 0.69, 1.0, 1)
    glClearColor(0.5, 0.5, 0.5, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main():
    # print(settings)
    #SETTINGS = settings

    #if settings[2][3] == '2D mode':
     #   print(settings[2][3])
     #   TWODMODE = True

    #adjust_settings(settings, TWODMODE)
    #print(TWODMODE)
    mode = settings.whatdo
    start = time.time()
    if mode == 0:
        settings.GFX = True
        window = Window(width=800, height=600, caption='PlantCraft', resizable=False)
        window.id = 0
        # Hide the mouse cursor and prevent the mouse from leaving the window.
        window.set_exclusive_mouse(True)
        setup()
        pyglet.app.run()
        window.close()

    if mode == 1:
        numGames = 100
        settings.GFX = False
        window = Window(width=0, height=0, caption='PlantCraft', resizable=False)
        wins = [0,0]
        for i in range(numGames):
            window.id = i
            # Hide the mouse cursor and prevent the mouse from leaving the window.
            setup()
            pyglet.app.run()
            wins[window.winner]+=1
            window.init()
        window.close()
        end = time.time()
        print("Player 1 wins: " + str(wins[0]))
        print("Player 2 wins: " + str(wins[1]))
    if mode == 2:
        settings.GFX = False
        window = Window(width=0, height=0, caption='PlantCraft', resizable=False)
        numPlayers = 10
        numGenerations = 10
        currentGeneration = []
        for i in range(numPlayers):
            genome = ""
            for j in range(10):
                if (random.random() > 0.5):
                    genome += "1"
                else:
                    genome += "0"
            currentGeneration.append({"type":"ExploreExploitPlayer", "genes":genome, "gene_length":10})
        for g in range(numGenerations):
            gstart = time.time()
            fitness = [0 for g in currentGeneration]
            energy = [0 for g in currentGeneration]
            ends = {"win":0, "sweep":0, "death":0}
            turns = 0
            wturns = [0 for g in currentGeneration]
            truewins = [0 for g in currentGeneration]
            for i in range(len(currentGeneration)):
                for j in range(i+1, len(currentGeneration)):
                    p1 = currentGeneration[i]
                    p2 = currentGeneration[j]
                    settings.setPlayers([p1,p2])
                    window.id = g
                    # Hide the mouse cursor and prevent the mouse from leaving the window.
                    setup()
                    pyglet.app.run()
                    if window.winner == 0:
                        fitness[i]+=1
                        if window.end == "win": 
                            wturns[i] += window.turnCount
                            truewins[i] += 1
                    else:
                        fitness[j]+=1
                        if window.end == "win": 
                            wturns[j] += window.turnCount
                            truewins[j] += 1
                    energy[i] += window.stats["energy"][0]
                    energy[j] += window.stats["energy"][1]
                    ends[window.end] += 1
                    turns += window.turnCount
                    window.init()
            for i in range(len(currentGeneration)):
                traits = []
                gene = currentGeneration[i]["genes"]
                genel = currentGeneration[i]["gene_length"]
                for x in range(int(len(gene)/genel)):
                    count = 0
                    for y in range(genel):
                        if gene[y+x*genel] == '1':
                            count += 1
                    traits.append(count)
                print("Gen " + str(g) + " player " + currentGeneration[i]["genes"] + " " + str(traits) + " [fitness: " + str(fitness[i]) + "] [avg end energy: " + str(math.ceil(energy[i]/(len(currentGeneration)-1))) + "] [avg turns to win: " + (str(math.ceil(wturns[i]/truewins[i])) if truewins[i]>0 else "no wins") + "]")
            print("Generation total stats: wins: " + str(ends["win"]) + " deaths: " + str(ends["death"]) + " sweeps: " + str(ends["sweep"]) + " avg turns taken: " + str(math.ceil(turns/(2*(len(currentGeneration)-1)))))
            nextGeneration = []
            while len(nextGeneration) < numPlayers:
                parent1 = random.choices(currentGeneration, weights=fitness, k=1)[0]
                parent2 = random.choices(currentGeneration, weights=fitness, k=1)[0]
                kids = crossover._make_babies(parent1["genes"], parent2["genes"], 10)
                nextGeneration.append({"type":"ExploreExploitPlayer", "genes":kids[0], "gene_length":10})
                nextGeneration.append({"type":"ExploreExploitPlayer", "genes":kids[1], "gene_length":10})
            end = time.time()
            print("Time taken by generation: " + str((end-gstart)/60) + " minutes: " + str((end-gstart)/turns) + " seconds per turn")
            currentGeneration = nextGeneration


        window.close()

    end = time.time()
    print("Elapsed time: " + str((end-start)/60) + " minutes")
    return 0
    #print('returning zero')
    #return 0


if __name__ == '__main__':
    main()
