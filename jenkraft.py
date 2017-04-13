from mcpi import block
import time

JOB_RUNNING=1
JOB_FAILED=2
JOB_ABORTED=3

MAX_OCEAN_Y=14
MAX_OCEAN_X=64
MAX_OCEAN_Z=MAX_OCEAN_X

DEFAULT_POS_X=0
DEFAULT_POS_Y=MAX_OCEAN_Y+10
DEFAULT_POS_Z=-MAX_OCEAN_Z

class Ocean:
    def __init__(self, id, mc):
        self.id = id
        self.mc = mc
        self.draw()

    def __cmp__(self, rhs):
        return hash(self) - hash(rhs)

    def __hash__(self):
        return (self.id << 8) + self.data

    def draw(self):
        #clear first in case iand give a lil of time for flowings to disapear in case of statsus change
        #self.mc.setBlocks(-32, -3, -32, 32, -3, 32, block.COBBLESTONE)
        self.mc.setBlocks(-MAX_OCEAN_X, MAX_OCEAN_Y, -MAX_OCEAN_Z,
                          MAX_OCEAN_X, MAX_OCEAN_Y, MAX_OCEAN_Z,
                          block.BEDROCK_INVISIBLE)
        self.mc.setBlocks(-MAX_OCEAN_X, MAX_OCEAN_Y-1, -MAX_OCEAN_Z,
                          MAX_OCEAN_X, MAX_OCEAN_Y-1, MAX_OCEAN_Z,
                          block.WATER_STATIONARY)
        
        self.mc.setBlock(DEFAULT_POS_X, DEFAULT_POS_Y-1, DEFAULT_POS_Z, block.COBBLESTONE)
        self.mc.player.setPos(DEFAULT_POS_X, DEFAULT_POS_Y, DEFAULT_POS_Z)
            

class Fountain:
    """Jenkraft fountain"""
    """f = jenkraft.Fountain(1,mc,9,3,0)"""
    """f.addStage()"""
    """f.clear()"""
    """f1 = jenkraft.Fountain(1,mc, 10, 26, -20)"""
    """f2 = jenkraft.Fountain(1,mc, 6, 26, -10)"""
    """f3 = jenkraft.Fountain(1,mc, 0, 26, 0)"""
    
    def __init__(self, id, mc, x, y, z, height=1, status=JOB_RUNNING):
        self.id = id
        self.mc = mc
        self.status = status
        #Keep old status cause flowing water replaced by flowing lava involves wait
        self.previous_status = status
        self.x = x
        self.y = y
        self.z = z
        self.height = 1
        self.build_base()
        self.add_stage()

    def __cmp__(self, rhs):
        return hash(self) - hash(rhs)

    def __hash__(self):
        return (self.id << 8) + self.data

    def build_base(self):
        self.mc.setBlocks(self.x-4,self.y-1,self.z-4,
                          self.x+4,self.y-1,self.z+4,
                          block.GRASS)
        self.mc.setBlocks(self.x-2,self.y,self.z-2,
                          self.x+2,self.y,self.z+2,
                          block.COBBLESTONE)
        self.mc.setBlocks(self.x-1,self.y,self.z-1,
                          self.x+1,self.y,self.z+1,
                          block.AIR)        

    def add_stage(self): 
        self.height+=1
        self.draw_flow()

    def draw_flow(self):
        #clear first in case iand give a lil of time for flowings to disapear in case of statsus change
        if (self.status != self.previous_status):
            self.mc.setBlocks(self.x-1, self.y, self.z-1, self.x+1, self.y+self.height,self.z+1,block.AIR)
            time.sleep(0.2*self.height)
        
        block_to_build = block.WATER_FLOWING
        if (self.status==JOB_FAILED):
            block_to_build = block.LAVA_FLOWING
        elif (self.status==JOB_ABORTED):
            block_to_build = block.GLASS
        self.mc.setBlocks(self.x, self.y, self.z, self.x, self.y+self.height,self.z,block_to_build)

    def clear(self):
        self.mc.setBlocks(self.x-4,self.y-1,self.z-4,
                          self.x+4,self.y+self.height,self.z+4,
                          block.AIR)

    def set_running(self):
        self.status=JOB_RUNNING
        self.draw_flow()
        self.previous_status=self.status

    def set_failed(self):
        self.status=JOB_FAILED
        self.draw_flow()
        self.previous_status=self.status

    def set_aborted(self):
        self.status=JOB_ABORTED
        self.draw_flow()
        self.previous_status=self.status

