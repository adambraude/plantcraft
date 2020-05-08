import random

from collections import deque
from pyglet import image
from pyglet.gl import *


import settings as set


class World(object):

    def __init__(self, settings):

        self.mode = settings.TWODMODE
        self.density = settings.DENSITY
        self.cluster = settings.CLUSTER
        self.clusterp = settings.CLUSTERP
        self.clustert = settings.CLUSTERTYPE
        self.set = settings
        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = settings.textureGroup

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        self.nutrients = {}

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
        if self.set.REPLAY: return
        if (self.clustert == "None"):
            if self.mode:
                self.addNutrients(self.density/100, (-40, 40, 0, 1, -40, 40))
            else:
                self.addNutrients(self.density/100, (-20, 20, -20, 0, -20, 20))
        elif (self.clustert == "Layered"):
            if self.mode:
                self.addClusterNutrients(self.density/100, (-40, 40, 0, 1, -40, 40), self.cluster, self.clusterp)
            else:
                self.addClusterNutrients(self.density/100, (-20, 20, -20, 0, -20, 20), self.cluster, self.clusterp)
        elif (self.clustert == "Chunk"):
            if self.mode:
                self.addChunkNutrients(self.density/100, (-40, 40, 0, 1, -40, 40), self.cluster, self.clusterp)
            else:
                self.addChunkNutrients(self.density/100, (-20, 20, -20, 0, -20, 20), self.cluster, self.clusterp)

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
        if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "W"
        xmin,xmax,ymin,ymax,zmin,zmax = bounds
        for x in range(xmin,xmax):
            for y in range(ymin, ymax):
                for z in range(zmin, zmax):
                    if random.random()<density and ((x,y,z) not in self.world):
                        self.add_block((x,y,z), self.set.NUTRIENT_TEXTURE)
                        if self.set.PROX:
                            self.hide_block((x, y, z))
                        if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "(4," + str(x) + "," + str(y) + ","+ str(z) + ")\n";


    def addClusterNutrients(self, density, bounds,clusterCoeff=0.2, passes = 3):
            """ Density is the probability that any given space will be a nutrient
                bounds should be a 6-tuple (xmin,xmax,ymin,ymax,zmin,zmax)

            """
            if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "W"
            xmin,xmax,ymin,ymax,zmin,zmax = bounds
            for x in range(xmin,xmax):
                for y in range(ymin, ymax):
                    for z in range(zmin, zmax):
                        if random.random()<density and ((x,y,z) not in self.world):
                            self.add_block((x,y,z), self.set.NUTRIENT_TEXTURE)
                            if self.set.PROX:
                                self.hide_block((x, y, z))
                            if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "(4," + str(x) + "," + str(y) + ","+ str(z) + ")\n";
            #Do it again [passes] timesm, but only fill in spaces that are adjacent to a nutrient
            for i in range(passes):
                passc = []
                for x in range(xmin,xmax):
                    for y in range(ymin, ymax):
                        for z in range(zmin, zmax):
                            if random.random()<clusterCoeff and ((x,y,z) not in self.world) and (((x+1,y,z) in self.world) or ((x-1,y,z) in self.world)
                                or ((x,y-1,z) in self.world) or ((x,y+1,z) in self.world) or ((x,y,z+1) in self.world) or ((x,y,z-1) in self.world)):
                                passc.append((x,y,z))
                for (x,y,z) in passc:
                    self.add_block((x,y,z), self.set.NUTRIENT_TEXTURE)
                    if self.set.PROX:
                        self.hide_block((x, y, z))
                    if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "(4," + str(x) + "," + str(y) + ","+ str(z) + ")\n";

    #Cuts the world into cubes and assigns a different density to each cube
    def addChunkNutrients(self, density, bounds,variance=0.9, chunkSize = 5):
            """ Density is the probability that any given space will be a nutrient
                bounds should be a 6-tuple (xmin,xmax,ymin,ymax,zmin,zmax)

            """
            if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "W"
            xmin,xmax,ymin,ymax,zmin,zmax = bounds
            for x in range(xmin,xmax, chunkSize):
                for y in range(ymin, ymax, chunkSize):
                    for z in range(zmin, zmax,chunkSize):
                        d = density*(random.random()*variance*2+(1-variance))
                        for xp in range(0,chunkSize):
                            for yp in range(0, chunkSize):
                                for zp in range(0, chunkSize):
                                    if random.random()<d and ((x,y,z) not in self.world):
                                        self.add_block((x+xp,y+yp,z+zp), self.set.NUTRIENT_TEXTURE)
                                        if self.set.PROX:
                                            self.hide_block((x+xp, y+yp, z+zp))
                                        if (self.set.LOGENABLED and self.set.LOGNUTRIENTSTART):self.set.LOG += "(4," + str(x+xp) + "," + str(y+yp) + ","+ str(z+zp) + ")\n";


    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in self.set.FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.
            If the block is part of a root system, use RootSystem's add_block instead

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
        if texture == self.set.NUTRIENT_TEXTURE:
            self.nutrients[position] = True
        self.world[position] = texture
        if immediate:
            self.show_block(position)

    def uncolorBlock(self, position, immediate=True):
        if position not in self.world: return

        self.world[position] = self.set.TEXTURES[0]
        if self.exposed(position):
            #print(self.world[position], TEXTURES[0])

            self.shown[position] = self.set.TEXTURES[0]
            if immediate:
                self.hide_block(position)
                self.show_block(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.
            If the block is part of a root system, use RootSystem's method instead

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        if position in self.nutrients:
            del self.nutrients[position]

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
        Use of this method causes problems with proximity sensing

        """
        x, y, z = position
        for dx, dy, dz in self.set.FACES:
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
        vertex_data = self.set.cube_vertices(x, y, z, 0.5)
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
        while self.queue and time.clock() - start < 1.0 / self.set.TICKS_PER_SEC:
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
        for _ in set.xrange(max_distance * m):
            key = set.normalize((x, y, z))
            if key != previous and ((key in self.world) and (self.world[key] not in ignore)) and previous:
                if abs(key[0]-previous[0])+abs(key[1]-previous[1])+abs(key[2]-previous[2])>1:
                    previous = (previous[0], key[1], previous[2])
                    if abs(key[0]-previous[0]) + abs(key[2]-previous[2])>1:
                        previous=(key[0], previous[1], previous[2])
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None
