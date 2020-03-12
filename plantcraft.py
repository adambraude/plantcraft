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
#[player1, player2, [density, proximity?, prox distance, graphics mode]]
#['Human Player', 'None', [28.0, False, 5.0, '3D mode']]
all_settings = { "players":['Human Player', 'GreedyPlayer'], "TWODMODE":False, "PROX":True, "PROX_RANGE":5, "DENSITY":10}
if len(sys.argv)>1:
    all_settings = welcome.main()

TICKS_PER_SEC = 60

SPEED = 15

PROX = all_settings["PROX"]
PROX_RANGE = all_settings["PROX_RANGE"]

INIT_ENERGY = 500
ROOT_COST = 10
FORK_COST = 50
ENERGY_REWARD = 20
DENSITY = all_settings["DENSITY"]
if all_settings["TWODMODE"] == '2D mode':
    TWODMODE = True
else:
    TWODMODE = False
LOGENABLED = True
LOG = ""

REPLAY = False
REPLAY_FILE = "logfile"


DEGREES= u'\N{DEGREE SIGN}'
DIRECTIONS = (key.N, key.S, key.W, key.E, key.U, key.D)
NUM_KEYS = (key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9, key._0)

#def adjust_settings(settings, TWODMODE):
#    if settings[2][3] == '2D mode':
 #       TWODMODE = True
    #else:
        #TWODMODE = False
        #print(TWODMODE)


def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)

if sys.version_info[0] >= 3:
    xrange = range

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
    file.write(LOG)
    file.close()

TEXTURES = (calcTextureCoords(1), calcTextureCoords(2), calcTextureCoords(3), calcTextureCoords(4), calcTextureCoords(5),
    calcTextureCoords(6),calcTextureCoords(7),calcTextureCoords(8),calcTextureCoords(9))
ABSORB = (TEXTURES[5],TEXTURES[6],TEXTURES[7],TEXTURES[8], TEXTURES[2])
NUTRIENT_TEX = TEXTURES[4]
STALK_TEXTURE = calcTextureCoords(0)
TEXTURE_COLORS = (None, (128,255,255,255), (128,180,255,255), (204, 128, 255, 255))

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        global LOG
        global INIT_ENERGY
        global ROOT_COST
        global FORK_COST
        global ENERGY_REWARD
        global PROX
        global PROX_RANGE
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

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

        if not REPLAY:
            LOG += "(IE:" + str(INIT_ENERGY) + ")\n"
            LOG += "(RC:" + str(ROOT_COST) + ")\n"
            LOG += "(FC:" + str(FORK_COST) + ")\n"
            LOG += "(ER:" + str(ENERGY_REWARD) + ")\n"
            if PROX:
                LOG += "(PR:" + str(PROX_RANGE) + ")\n"
        # Instance of the model that handles the world.
        self.world = World(TWODMODE,DENSITY)
        if REPLAY:
            file = open(REPLAY_FILE, "r")
            LOG = file.read()
            PROX = False
            moves = re.split("[(),\n\s]+", LOG)
            self.pos = 0
            while (moves[self.pos] !=  "W"):
                pre = moves[self.pos][:2]
                if (pre == "PR"):
                    PROX = True
                    PROX_RANGE = int(moves[self.pos][3:])
                if (pre == "IE"): INIT_ENERGY = int(moves[self.pos][3:])
                elif (pre == "RC"): ROOT_COST = int(moves[self.pos][3:])
                elif (pre == "FC"): FORK_COST = int(moves[self.pos][3:])
                elif (pre == "ER"): ENERGY_REWARD = int(moves[self.pos][3:])
                self.pos+= 1
            self.pos += 1
            file.close()
            for i in range(self.pos,len(moves),4):
                if moves[i] == "R": break
                #place nutrients
                x = int(moves[i+1])
                y = int(moves[i+2])
                z = int(moves[i+3])
                self.world.add_block((x,y,z), TEXTURES[int(moves[i])])
                self.world.nutrients.append((x,y,z))
                if PROX:
                    self.world.hide_block((x, y, z))
                self.pos = i
        self.rootSystems = []
        self.players = []

        if (REPLAY):
            while (moves[self.pos] != "True" and moves[self.pos] != "False"):
                if (moves[self.pos] == "R"):
                    rip = RootSystem(self.world, (moves[self.pos+1],moves[self.pos+2],moves[self.pos+3]), TWODMODE)
                    rip.energy = int(moves[self.pos+4][2:])
                    self.rootSystems.append(rip)
                    self.players.append(Player(self.rootSystems[len(self.rootSystems)-1], self))
                    self.pos += 5
                elif (moves[self.pos] == "T"):
                    rip.add_block((int(moves[self.pos+1]),int(moves[self.pos+2]),int(moves[self.pos+3])),rip.absorb[len(rip.absorb)-1])
                    self.pos += 4
                elif (moves[self.pos] == "S"):
                    rip.add_block((int(moves[self.pos+1]),int(moves[self.pos+2]),int(moves[self.pos+3])),STALK_TEXTURE)
                    self.pos += 4
                elif (moves[self.pos] == "B"):
                    rip.add_block((int(moves[self.pos+1]),int(moves[self.pos+2]),int(moves[self.pos+3]),TEXTURES[0]))
                    self.pos += 4
                else:
                    self.pos += 1
            for r in self.rootSystems: r.initProx()
        else:
            for i in range(2):
                self.rootSystems.append(RootSystem(self.world, (10*i,0,0),TWODMODE))
            self.players.append(GreedyPlayer(self.rootSystems[0], self))
            self.players.append(GreedyForker(self.rootSystems[1], self))

        self.currentPlayerIndex = -1
        #drop all the already-read moves from memory.
        if REPLAY: self.moves = moves[self.pos:]
        self.pos = 0

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
        if (REPLAY):
            if self.pos >= len(self.moves): return
            print(self.pos)
            while(self.moves[self.pos] != "True" and self.moves[self.pos] != "False"):
                self.pos += 1
                if self.pos >= len(self.moves): return
            if self.moves[self.pos] == "True": fork = True
            else: fork = False
            self.players[int(self.moves[self.pos+8])].rootSystem.addToTip((int(self.moves[self.pos+1]),int(self.moves[self.pos+2]),int(self.moves[self.pos+3])),(int(self.moves[self.pos+4]),int(self.moves[self.pos+5]),int(self.moves[self.pos+6])),fork)
            self.pos +=7
        else:
            self.currentPlayerIndex += 1
            if self.currentPlayerIndex >= len(self.players):
                self.currentPlayerIndex = 0
            self.players[self.currentPlayerIndex].takeTurn()
            global LOG
            if (LOGENABLED and not isinstance(self.currentPlayer(), HumanPlayer)): LOG += "(" + str(self.currentPlayerIndex) + ")"

    def currentPlayer(self):
        return self.players[self.currentPlayerIndex]

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
        for _ in xrange(m):
            self._update(dt / m)
        if (not isinstance(self.currentPlayer(), HumanPlayer)):
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
            global LOG
            vector = self.get_sight_vector()
            block, previous = self.rootSystems[self.currentPlayerIndex].hit_test(self.position, vector, 8, [TEXTURES[4]])
            if block and (self.world.world[block] in ABSORB):
                if (button == mouse.RIGHT) or \
                        ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                    # ON OSX, control + left click = right click.
                    if previous:
                        self.rootSystems[self.currentPlayerIndex].addToTip(block, previous,True)
                        if (LOGENABLED): LOG += "(" + str(self.currentPlayerIndex) + ")"
                        self.nextTurn()
                elif button == pyglet.window.mouse.LEFT and block and previous:
                    self.rootSystems[self.currentPlayerIndex].addToTip(block, previous)
                    if (LOGENABLED): LOG += "(" + str(self.currentPlayerIndex) + ")"
                    self.nextTurn()
        else:
            self.set_exclusive_mouse(True)

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
            self.set_exclusive_mouse(False)
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
        block, previous = self.rootSystems[self.currentPlayerIndex].hit_test(self.position, vector, 8, [TEXTURES[4]])
        if block and (self.world.world[block] in ABSORB):
            x, y, z = previous
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
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


def main(settings=None):
    # print(settings)
    #SETTINGS = settings

    #if settings[2][3] == '2D mode':
     #   print(settings[2][3])
     #   TWODMODE = True

    #adjust_settings(settings, TWODMODE)
    #print(TWODMODE)

    window = Window(width=800, height=600, caption='PlantCraft', resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()
    window.close()
    return 0
    #print('returning zero')
    #return 0


if __name__ == '__main__':
    main()
