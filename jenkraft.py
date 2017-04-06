from mcpi import block
import time

JOB_RUNNING=1
JOB_FAILED=2
JOB_ABORTED=3


class Fountain:
    """Jenkraft fountain"""
    """f = fountain.Fountain(1,mc,35,0,-14)"""
    """f.addStage()"""
    """f.clear()"""
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
        self.mc.setBlocks(self.x-2,self.y,self.z-2,
                          self.x+2,self.y,self.z+2,
                          block.GLASS)
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
        self.mc.setBlocks(self.x-2,self.y,self.z-2,
                          self.x+2,self.y+self.height,self.z+2,
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

