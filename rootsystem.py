import settings as set

class RootSystem(object):

    def __init__(self, world, position, mode):

        self.mode = mode
        self.world = world
        self.nutrients = {}

        self.energy = self.world.set.INIT_ENERGY
        self.absorb = self.world.set.ABSORB

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.blocks = {}
        self.tips = {}

        if (not self.world.set.PROX): self.nutrients = self.world.nutrients
        if (not self.world.set.REPLAY): self._initialize(position)
        self.position = position


    def _initialize(self, position):
        """ Initialize the world by placing all the blocks.

        """
        x,y,z = position
        
        if (self.world.set.LOGENABLED): self.world.set.LOG += "\n (R," + str(x)+ "," + str(y) + "," + str(z) + ",E:" + str(self.energy) + ")"
        self.tipPositions = [None, (x-1,y,z), (x+1,y,z), (x,y,z+1),(x,y,z-1)]
        for i in range(1,len(self.tipPositions)):
            self.add_block(self.tipPositions[i], self.absorb[-1])
            if (self.world.set.LOGENABLED): self.world.set.LOG += "\n (T," + str(self.tipPositions[i][0])+ "," + str(self.tipPositions[i][1]) + "," + str(self.tipPositions[i][2]) + ")"

        if self.world.set.PROX:
            self.initProx()

        self.add_block((x,y,z), self.world.set.TEXTURES[0])
        for i in range(1,6):
            self.add_block((x,y+i,z), self.world.set.STALK_TEXTURE)
            if (self.world.set.LOGENABLED): self.world.set.LOG += "\n (S," + str(x)+ "," + str(y+i) + "," + str(z) + ")"

    def initProx(self):
        for t in self.tips.keys():
            self.proxUpdate(t, t)

        for block in self.nutrients:
            if block not in self.world.shown:
                self.world.show_block(block)

    def addToTip(self, oldTip, newTip, fork=False):
        if (self.energy < self.world.set.ROOT_COST): return False
        if (fork and self.energy < self.world.set.FORK_COST): return False

        collectedNutrient = False
        # don't accept new positions that collide or are above ground
        if newTip in self.world.world:
            if newTip in self.world.nutrients:
                self.energy+=self.world.set.ENERGY_REWARD
                collectedNutrient = True
                if self.world.set.PROX: del self.nutrients[newTip]
            else: return False

        if newTip[1] > 0: return False

        if (fork): self.energy -= self.world.set.FORK_COST
        else: self.energy -= self.world.set.ROOT_COST

        if (not fork):
            self.world.uncolorBlock(oldTip)
            del self.tips[oldTip]
        self.updateTips()
        if (self.world.set.LOGENABLED): self.world.set.LOG += "\n (" + str(fork) + "," + str(oldTip[0])+ "," + str(oldTip[1]) + "," + str(oldTip[2]) + "," + str(newTip[0])+ "," + str(newTip[1]) + "," + str(newTip[2]) + ",E:" + str(self.energy) + ")"

        if collectedNutrient: self.add_block(newTip, self.absorb[0])
        else: self.add_block(newTip, self.absorb[-1])
        #self.tipPositions[whichTip] = newTip
            #print(str(oldTip) +" -> " + str(newTip))
        if self.world.set.PROX:
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
            self.energy += self.world.set.ENERGY_REWARD
            self.world.hide_block(t)
            self.world.show_block(t)

    def proxUpdate(self, position, old_position):
        x, y, z = position
        x_old, y_old, z_old = old_position
        # CASE: first update on game start, check the full range
        if position == old_position:
            for i in range(x-self.world.set.PROX_RANGE, x+self.world.set.PROX_RANGE + 1):
                for j in range(y-self.world.set.PROX_RANGE, y+self.world.set.PROX_RANGE + 1):
                    for k in range(z-self.world.set.PROX_RANGE, z+self.world.set.PROX_RANGE + 1):
                        new_pos = (i, j, k)
                        # show nutrients within initial range
                        if new_pos in self.world.nutrients:
                            self.nutrients[new_pos] = True
        # CASE: root growth in z-axis, expand range
        if x == x_old and y == y_old:
            for i in range (x-self.world.set.PROX_RANGE, x+self.world.set.PROX_RANGE + 1):
                for j in range (y-self.world.set.PROX_RANGE, y+self.world.set.PROX_RANGE + 1):
                    if z - z_old > 0:
                        new_pos = (i, j, z+self.world.set.PROX_RANGE)
                    else:
                        new_pos = (i, j, z-self.world.set.PROX_RANGE)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients[new_pos] = True
        # CASE: root growth in x-axis, expand range
        elif y == y_old and z == z_old:
            for j in range (y-self.world.set.PROX_RANGE, y+self.world.set.PROX_RANGE + 1):
                for k in range (z-self.world.set.PROX_RANGE, z+self.world.set.PROX_RANGE + 1):
                    if x - x_old > 0:
                        new_pos = (x+self.world.set.PROX_RANGE, j, k)
                    else:
                        new_pos = (x-self.world.set.PROX_RANGE, j, k)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients[new_pos] = True
        # CASE: root growth in y-axis, expand range
        elif z == z_old and x == x_old:
            for i in range (x-self.world.set.PROX_RANGE, x+self.world.set.PROX_RANGE + 1):
                for k in range (z-self.world.set.PROX_RANGE, z+self.world.set.PROX_RANGE + 1):
                    if y - y_old > 0:
                        new_pos = (i, y+self.world.set.PROX_RANGE, k)
                    else:
                        new_pos = (i, y-self.world.set.PROX_RANGE, k)
                    # show nutrients that are now within range
                    if new_pos in self.world.nutrients:
                        self.nutrients[new_pos] = True

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
        if texture in self.world.set.ABSORB: self.tips[position] = True
        self.world.add_block(position, texture, immediate)

    def legalMoves(self):
        moves = []
        for tip in self.tips.keys():
            x,y,z = tip
            if self.mode:
                f = self.world.set.LATFACES
            else:
                f = self.world.set.FACES
            free = False
            for dx, dy, dz in f:
                if (((x + dx, y + dy, z + dz) not in self.world.world) or (self.world.world[(x + dx, y + dy, z + dz)]==self.world.set.NUTRIENT_TEXTURE)) and y+dy<=0:
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
        self.world.remove_block(position,texture,immediate)

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
            if key != previous and ((key in self.blocks) and (key in self.world.world) and (self.world.world[key] not in ignore)) and previous:
                if abs(key[0]-previous[0])+abs(key[1]-previous[1])+abs(key[2]-previous[2])>1:
                    previous = (previous[0], key[1], previous[2])
                    if abs(key[0]-previous[0]) + abs(key[2]-previous[2])>1:
                        previous=(key[0], previous[1], previous[2])
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None
