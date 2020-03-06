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
#[player1, player2, [density, proximity?, prox distance, graphics mode]]
#['Human Player', 'None', [28.0, False, 5.0, '3D mode']]
all_settings = ['Human Player', 'None', [10.0, False, 5.0, '3D mode']]
if len(sys.argv)>1:
    all_settings = welcome.main()

TICKS_PER_SEC = 60

SPEED = 15

PROX = True
PROX_RANGE = 5

INIT_ENERGY = 500
ROOT_COST = 10
FORK_COST = 50
ENERGY_REWARD = 20
DENSITY = int(all_settings[2][0])
if all_settings[2][3] == '2D mode':
    TWODMODE = True
else:
    TWODMODE = False
LOGENABLED = True
LOGNUTRIENTSTART = True
LOG = ""

REPLAY = False
REPLAY_FILE = "logfile"


DEGREES= u'\N{DEGREE SIGN}'
DIRECTIONS = (key.N, key.S, key.W, key.E, key.U, key.D)
NUM_KEYS = (key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9, key._0)

TEXTURE_PATH = "roots.png"

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

FACES = [( 0, 1, 0), ( 0,-1, 0), (-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1),]
LATFACES = [(-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1)]


class World(object):

    def __init__(self, mode):

        self.mode = mode
        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        self.nutrients = []

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        #self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()


    def _initialize(self):  # take a parameter for nutrient density
        """ Initialize the world by placing all the blocks.

        """
        if REPLAY: return
        if self.mode:
            self.addNutrients(DENSITY/100, (-40, 40, 0, 1, -40, 40))
        else:
            self.addNutrients(DENSITY/100, (-20, 20, -20, 0, -20, 20))

    @staticmethod
    def modByDirection(start, direc):
        if direc==key.N or direc=='n' or direc=='N': return (start[0], start[1], start[2]-1)
        if direc==key.S or direc=='s' or direc=='S': return (start[0], start[1], start[2]+1)
        if direc==key.E or direc=='e' or direc=='E': return (start[0]+1, start[1], start[2])
        if direc==key.W or direc=='w' or direc=='W': return (start[0]-1, start[1], start[2])
        if direc==key.U or direc=='u' or direc=='U': return (start[0], start[1]+1, start[2])
        if direc==key.D or direc=='d' or direc=='D': return (start[0], start[1]-1, start[2])
        return start

    def addNutrients(self,density, bounds):
        """ Density is the probability that any given space will be a nutrient
            bounds should be a 6-tuple (xmin,xmax,ymin,ymax,zmin,zmax)

        """
        global LOG
        if (LOGENABLED and LOGNUTRIENTSTART):LOG += "W"
        xmin,xmax,ymin,ymax,zmin,zmax = bounds
        for x in range(xmin,xmax):
            for y in range(ymin, ymax):
                for z in range(zmin, zmax):
                    if random.random()<density and ((x,y,z) not in self.world):
                        self.add_block((x,y,z), TEXTURES[4])
                        self.nutrients.append((x,y,z))
                        if PROX:
                            self.hide_block((x, y, z))
                        if (LOGENABLED and LOGNUTRIENTSTART):LOG += "(4," + str(x) + "," + str(y) + ","+ str(z) + ")\n";


    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        #self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            #self.check_neighbors(position)

    def uncolorBlock(self, position, immediate=True):
        if position not in self.world: return

        self.world[position] = TEXTURES[0]
        if self.exposed(position):
            #print(self.world[position], TEXTURES[0])

            self.shown[position] = TEXTURES[0]
            if immediate:
                self.hide_block(position)
                self.show_block(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        #self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group, ('v3f/static', vertex_data), ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()

    def hit_test(self, position, vector, max_distance=8, ignore=[]):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and ((key in self.world) and (self.world[key] not in ignore)) and previous:
                if abs(key[0]-previous[0])+abs(key[1]-previous[1])+abs(key[2]-previous[2])>1:
                    previous = (previous[0], key[1], previous[2])
                    if abs(key[0]-previous[0]) + abs(key[2]-previous[2])>1:
                        previous=(key[0], previous[1], previous[2])
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

class RootSystem(object):

    def __init__(self, world, position):

        self.world = world
        self.nutrients = []

        self.energy = INIT_ENERGY
        self.absorb = ABSORB

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.blocks = {}
        self.tips = {}

        if (not REPLAY): self._initialize(position)


    def _initialize(self, position):
        """ Initialize the world by placing all the blocks.

        """
        x,y,z = position
        global LOG
        if (LOGENABLED): LOG += "\n (R," + str(x)+ "," + str(y) + "," + str(z) + ",E:" + str(self.energy) + ")"
        self.tipPositions = [None, (x-1,y,z), (x+1,y,z), (x,y,z+1),(x,y,z-1)]
        for i in range(1,len(self.tipPositions)):
            self.add_block(self.tipPositions[i], self.absorb[-1])
            if (LOGENABLED): LOG += "\n (T," + str(self.tipPositions[i][0])+ "," + str(self.tipPositions[i][1]) + "," + str(self.tipPositions[i][2]) + ")"

        if PROX:
            self.initProx()

        self.add_block((x,y,z), TEXTURES[0])
        for i in range(1,6):
            self.add_block((x,y+i,z), STALK_TEXTURE)
            if (LOGENABLED): LOG += "\n (S," + str(x)+ "," + str(y+i) + "," + str(z) + ")"

    def initProx(self):
        for t in self.tips.keys():
            self.proxUpdate(t, t)

        for block in self.nutrients:
            if block not in self.world.shown:
                self.world.show_block(block)

    def addToTip(self, oldTip, newTip, fork=False):
        global LOG
        if (self.energy < ROOT_COST): return False
        if (fork and self.energy < FORK_COST): return False

        collectedNutrient = False
        # don't accept new positions that collide or are above ground
        if newTip in self.world.world:
            if newTip in self.world.nutrients:
                self.energy+=ENERGY_REWARD
                collectedNutrient = True
                if PROX: self.nutrients.remove(newTip)
            else: return False

        if newTip[1] > 0: return False

        if (fork): self.energy -= FORK_COST
        else: self.energy -= ROOT_COST

        if (not fork):
            self.world.uncolorBlock(oldTip)
            del self.tips[oldTip]
        self.updateTips()
        if (LOGENABLED): LOG += "\n (" + str(fork) + "," + str(oldTip[0])+ "," + str(oldTip[1]) + "," + str(oldTip[2]) + "," + str(newTip[0])+ "," + str(newTip[1]) + "," + str(newTip[2]) + ",E:" + str(self.energy) + ")"

        if collectedNutrient: self.add_block(newTip, self.absorb[0])
        else: self.add_block(newTip, self.absorb[-1])
        #self.tipPositions[whichTip] = newTip
            #print(str(oldTip) +" -> " + str(newTip))
        if PROX:
            self.proxUpdate(newTip,oldTip)
            for block in self.nutrients:
                if block not in self.world.shown:
                    self.world.show_block(block)
        return True

    def passTurn(self):
        self.updateTips()

    def updateTips(self):
        for t in self.tips.keys():
            i = self.absorb.index(self.world.world[t])
            if i == len(self.absorb)-1: continue
            self.world.world[t] = self.absorb[i+1]
            self.energy += ENERGY_REWARD
            self.world.hide_block(t)
            self.world.show_block(t)

    def proxUpdate(self, position, old_position):
        x, y, z = position
        x_old, y_old, z_old = old_position
        # CASE: first update on game start, check the full range
        if position == old_position:
            for i in range(x-PROX_RANGE, x+PROX_RANGE + 1):
                for j in range(y-PROX_RANGE, y+PROX_RANGE + 1):
                    for k in range(z-PROX_RANGE, z+PROX_RANGE + 1):
                        new_pos = (i, j, k)
                        # show nutrients within initial range
                        if new_pos in self.world.nutrients:
                            self.nutrients.append(new_pos)
        # CASE: root growth in z-axis, expand range
        if x == x_old and y == y_old:
            for i in range (x-PROX_RANGE, x+PROX_RANGE + 1):
                for j in range (y-PROX_RANGE, y+PROX_RANGE + 1):
                    if z - z_old > 0:
                        new_pos = (i, j, z+PROX_RANGE)
                    else:
                        new_pos = (i, j, z-PROX_RANGE)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients.append(new_pos)
        # CASE: root growth in x-axis, expand range
        elif y == y_old and z == z_old:
            for j in range (y-PROX_RANGE, y+PROX_RANGE + 1):
                for k in range (z-PROX_RANGE, z+PROX_RANGE + 1):
                    if x - x_old > 0:
                        new_pos = (x+PROX_RANGE, j, k)
                    else:
                        new_pos = (x-PROX_RANGE, j, k)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients.append(new_pos)
        # CASE: root growth in y-axis, expand range
        elif z == z_old and x == x_old:
            for i in range (x-PROX_RANGE, x+PROX_RANGE + 1):
                for k in range (z-PROX_RANGE, z+PROX_RANGE + 1):
                    if y - y_old > 0:
                        new_pos = (i, y+PROX_RANGE, k)
                    else:
                        new_pos = (i, y-PROX_RANGE, k)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients.append(new_pos)

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        self.blocks[position] = True
        if texture in ABSORB: self.tips[position] = True
        self.world.add_block(position, texture, immediate)

    def legalMoves(self):
        moves = []
        for tip in self.tips.keys():
            x,y,z = tip
            if TWODMODE:
                f = LATFACES
            else:
                f = FACES
            free = False
            for dx, dy, dz in f:
                if (((x + dx, y + dy, z + dz) not in self.world.world) or (self.world.world[(x + dx, y + dy, z + dz)]==TEXTURES[4])) and y+dy<=0:
                    moves.append(((x,y,z),(x+dx,y+dy,z+dz)))
                    free = True
            self.tips[tip] = free

        return moves

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.blocks[position]
        self.world.add_block(position,texture,immediate)

    def hit_test(self, position, vector, max_distance=8, ignore=[]):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
s        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and ((key in self.blocks) and (key in self.world.world) and (self.world.world[key] not in ignore)) and previous:
                if abs(key[0]-previous[0])+abs(key[1]-previous[1])+abs(key[2]-previous[2])>1:
                    previous = (previous[0], key[1], previous[2])
                    if abs(key[0]-previous[0]) + abs(key[2]-previous[2])>1:
                        previous=(key[0], previous[1], previous[2])
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

class Player(object):

    def __init__(self, rootSystem, window):
        self.rootSystem = rootSystem
        self.window = window

    def takeTurn(self):
        pass

class HumanPlayer(Player):
    pass

class RandomPlayer(Player):
    def takeTurn(self):
        moves = self.rootSystem.legalMoves()
        if len(moves)==0:
            self.rootSystem.passTurn()
            return
        move = random.choice(moves)
        self.rootSystem.addToTip(move[0],move[1])

class GreedyPlayer(Player):
    def __init__(self, rootSystem, window):
        super().__init__(rootSystem, window)

    def takeTurn(self):
        moves = self.rootSystem.legalMoves()

        target = None
        tdist = 99999
        #horrifyingly inefficient
        for b in self.rootSystem.world.world.keys():
            if self.rootSystem.world.world[b] == TEXTURES[4]:
                for t in self.rootSystem.tips.keys():
                    if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                    dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                    if dist < tdist and self.rootSystem.tips[t]:
                        tdist = dist
                        target = b

        newmoves = []
        if target:
            for m in moves:
                if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist:
                    newmoves.append(m)

        margin = 0
        while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
            margin += 1
            if target:
                for m in moves:
                    if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
                        newmoves.append(m)

        if len(newmoves)==0:
            self.rootSystem.passTurn()
            return

        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1])

class GreedyForker(Player):
    def __init__(self, rootSystem, window):
        super().__init__(rootSystem, window)

    def takeTurn(self):
        moves = self.rootSystem.legalMoves()

        target = None
        oldtarget = None
        origin = None
        tdist = 99999
        olddist = 99999
        oldorigin = None
        fork = True
        #find the closest and second closest nutrients
        for b in self.rootSystem.world.world.keys():
            if self.rootSystem.world.world[b] == TEXTURES[4]:
                for t in self.rootSystem.tips.keys():
                    if (self.rootSystem.world.world[t] in self.rootSystem.absorb[:-1]): continue
                    dist = abs(t[0]-b[0])+abs(t[1]-b[1])+abs(t[2]-b[2])
                    if dist <= tdist and self.rootSystem.tips[t]:
                        tdist = dist
                        if b != target:
                            olddist = tdist
                            oldtarget = target
                            oldorigin = origin
                        target = b
                        origin = t

        newmoves = []
        if target:
            for m in moves:
                if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist:
                    newmoves.append(m)
            #if there is a second closest
            if oldtarget:
                newdist = abs(target[0]-oldtarget[0])+abs(target[1]-oldtarget[1])+abs(target[2]-oldtarget[2])
                #if the second closest nutrient is best reached from a tip other than origin, don't fork
                if oldorigin != origin:
                    fork = False
                #if it's easier to reach the second closest nutrient from the target than from the tip that will approach the target, do not fork
                if fork and (newdist-olddist < FORK_COST/ROOT_COST):
                    fork = False
            else:
                #if there is only 1 nutrient known, do not fork
                fork = False

        #accept sideways or backwards moves when moving toward the target is not possible
        margin = 0
        while len(newmoves)==0 and margin< 2 and self.rootSystem.energy>0:
            margin += 1
            if target:
                for m in moves:
                    if abs(m[1][0]-target[0])+abs(m[1][1]-target[1])+abs(m[1][2]-target[2]) < tdist+margin:
                        newmoves.append(m)

        if len(newmoves)==0:
            self.rootSystem.passTurn()
            return

        move = random.choice(newmoves)
        self.rootSystem.addToTip(move[0],move[1], fork)

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
        self.world = World(TWODMODE)
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
                    rip = RootSystem(self.world, (moves[self.pos+1],moves[self.pos+2],moves[self.pos+3]))
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
                self.rootSystems.append(RootSystem(self.world, (10*i,0,0) ))
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
