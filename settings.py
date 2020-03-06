INIT_ENERGY = 500
LOGENABLED = True
LOG = ""
PROX = True
PROX_RANGE = 5
ROOT_COST = 10
FORK_COST = 50
ENERGY_REWARD = 20
REPLAY = False
REPLAY_FILE = "logfile"

TEXTURE_PATH = "roots.png"
LOGNUTRIENTSTART = True

TICKS_PER_SEC = 60

FACES = [( 0, 1, 0), ( 0,-1, 0), (-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1),]
LATFACES = [(-1, 0, 0), ( 1, 0, 0), ( 0, 0, 1), ( 0, 0,-1)]

def calcTextureCoords(which, n=16):
    m = 1.0 / n
    left = (which)*m
    right = left+m - 0.001
    left += 0.001
    return 6*[left, 0.51, right, 0.51, right, 0.99, left, 0.99]

TEXTURES = (calcTextureCoords(1), calcTextureCoords(2), calcTextureCoords(3), calcTextureCoords(4), calcTextureCoords(5),
    calcTextureCoords(6),calcTextureCoords(7),calcTextureCoords(8),calcTextureCoords(9))
ABSORB = (TEXTURES[5],TEXTURES[6],TEXTURES[7],TEXTURES[8], TEXTURES[2])
STALK_TEXTURE = calcTextureCoords(0)

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
