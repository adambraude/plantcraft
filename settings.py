import sys

class Settings:
    def __init__(self, given={}):
        self.TEXTURES = (calcTextureCoords(1), calcTextureCoords(2), calcTextureCoords(3), calcTextureCoords(4), calcTextureCoords(5),
                                                    calcTextureCoords(6),calcTextureCoords(7),calcTextureCoords(8),calcTextureCoords(9))
        self.TEXTURE_COLORS = (None, (128,255,255,255), (128,180,255,255), (204, 128, 255, 255))
        
        self.LOGENABLED = True
        self.LOG = ""
        if "PROX" in given: self.PROX = given["PROX"]
        else: self.PROX = True
        if given["PROX_RANGE"]: self.PROX_RANGE = int(given["PROX_RANGE"])
        else: self.PROX_RANGE = 5
        self.ROOT_COST = 10
        if "FORK" in given: self.FORK_COST = given["FORK"]*self.ROOT_COST
        else: self.FORK_COST = 50
        if "STARTE" in given: self.INIT_ENERGY = given["STARTE"]*self.ROOT_COST
        else: self.INIT_ENERGY = 500
        if "REWARD" in given: self.ENERGY_REWARD = given["REWARD"]*self.ROOT_COST
        else: self.ENERGY_REWARD = 20

        if "REPLAY" in given: self.REPLAY = given["REPLAY"]
        else: self.REPLAY = False
        if "REPLAYFILE" in given: self.REPLAY_FILE = given["REPLAYFILE"]
        else: self.REPLAY_FILE = "logfile"

        self.TEXTURE_PATH = "roots.png"
        self.LOGNUTRIENTSTART = True

        self.TICKS_PER_SEC = 60

        self.FACES = [( 0, 1, 0), ( 0,-1, 0), (-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1),]
        self.LATFACES = [(-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1)]
        self.ABSORB = (self.TEXTURES[5],self.TEXTURES[6],self.TEXTURES[7],self.TEXTURES[8], self.TEXTURES[2])
        self.STALK_TEXTURE = calcTextureCoords(0)
        self.NUTRIENT_TEXTURE = self.TEXTURES[4]
        #the lower function makes a lowercase string
        if given["mode"].lower() == "2D mode": self.TWODMODE = True
        else: self.TWODMODE = False
        if given["DENSITY"]: self.DENSITY = given["DENSITY"]
        else: self.DENSITY = 5
        if given["CLUSTER"]: self.CLUSTER = given["CLUSTER"]
        else: self.CLUSTER = 5
        if given["CLUSTERP"]: self.CLUSTERP = int(given["CLUSTERP"])
        else: self.CLUSTERP = 3
        if given["CLUSTERTYPE"]: self.CLUSTERTYPE = given["CLUSTERTYPE"]
        else: self.CLUSTERP = "None"
        if given["players"]: self.players = given["players"]
        else: self.players = ["Human Player", "RandomPlayer"]
        if given["whatdo"]:
            if given["whatdo"] == 'Play':
                self.whatdo = 0
            if given["whatdo"] == 'CPU best of 100':
                self.whatdo = 1
            if given["whatdo"] == 'Breeding':
                self.whatdo = 2
        else:
            self.whatdo = 0
            
    def setPlayers(self, players):
        self.players = players


    def cube_vertices(self,x, y, z, n):
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

if sys.version_info[0] >= 3:
    xrange = range

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

    
