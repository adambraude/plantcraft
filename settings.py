class Settings:
    def __init__(self, given={}):
        self.TEXTURES = (calcTextureCoords(1), calcTextureCoords(2), calcTextureCoords(3), calcTextureCoords(4), calcTextureCoords(5),
                                                    calcTextureCoords(6),calcTextureCoords(7),calcTextureCoords(8),calcTextureCoords(9))
        self.TEXTURE_COLORS = (None, (128,255,255,255), (128,180,255,255), (204, 128, 255, 255))
        self.INIT_ENERGY = 500
        self.LOGENABLED = True
        self.LOG = ""
        self.PROX = True
        self.PROX_RANGE = 5
        self.ROOT_COST = 10
        self.FORK_COST = 50
        self.ENERGY_REWARD = 20
        self.REPLAY = False
        self.REPLAY_FILE = "logfile"

        self.TEXTURE_PATH = "roots.png"
        self.LOGNUTRIENTSTART = True

        self.TICKS_PER_SEC = 60

        self.FACES = [( 0, 1, 0), ( 0,-1, 0), (-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1),]
        self.LATFACES = [(-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1)]
        self.ABSORB = (self.TEXTURES[5],self.TEXTURES[6],self.TEXTURES[7],self.TEXTURES[8], self.TEXTURES[2])
        self.STALK_TEXTURE = calcTextureCoords(0)
        self.NUTRIENT_TEXTURE = self.TEXTURES[4]
        self.TWODMODE = False
        self.DENSITY = 5

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

    
