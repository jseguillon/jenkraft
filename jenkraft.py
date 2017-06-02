#FIXME : hash & cmps for all classes

#AT THIS TIME : "Ocean" ? at least : shoudl blast ? YES A BLAST
#Need to rotate on jons
#Use a yaml external config file
#Change material depengin on job
#And use kind of static ref for mc

from mcpi.minecraft import Minecraft
from mcpi import block
import time
import threading
import requests, json
import random
import collections

JOB_URL="http://192.168.99.100:8080/job/jenkraft/wfapi/runs"
JOB_AUTH=('jse', 'jse')

JOB_RUNNING="IN_PROGRESS"
JOB_SUCCESS="SUCCESS"
JOB_FAILED="FAILED"
JOB_ABORTED="ABORTED"
JOB_REFRESH_TIME=10 #Refresh each 60s

MAX_OCEAN_Y=5
MAX_OCEAN_X=64
MAX_OCEAN_Z=MAX_OCEAN_X #squared

DEFAULT_POS_X=0
DEFAULT_POS_Y=MAX_OCEAN_Y+10
DEFAULT_POS_Z=-MAX_OCEAN_Z

DEFAULT_BRANCH_INC_Y=12
DEFAULT_BRANCH_INC_Z=10
DEFAULT_BRANCH_START_Z=-40
DEFAULT_BRANCH_START_Y=15


class Scene:
    def __init__(self, mc):
        self.mc = mc
        self.jobs = {}
        ocean = Ocean(1, mc)

        job  = Job(1, JOB_URL, JOB_AUTH, block.DIAMOND_ORE, mc)
        job.start()
        self.jobs[1] = job

        self.loop()

    def loop(self):
        #Start Infinitz loop threaded branches
        #Parse branches and ensure all last job on same x ?
        i=0
        while True:
            #for job in self.jobs:
            i += 1
            x = -70+(i)
            mc.player.setPos(x,DEFAULT_POS_Y,DEFAULT_POS_Z)
            mc.setBlock(x,DEFAULT_POS_Y-1,DEFAULT_POS_Z, block.BEDROCK_INVISIBLE)

            #TODO 12*job_id, add wool for last five build ? loop only one 
            if x >64:
                i = 1

            time.sleep(1+(random.randint(0,10)/10))

class Job(threading.Thread):
    """Jobs : can be a branch or a simple job, only URL is known by code """
    def __init__(self, id, url, auth, material, mc):
        super(Job, self).__init__()
        self._stop_event = threading.Event()
        self.setDaemon(True)
        self.id = id
        self.mc = mc
        self.material=material
        self.fountains = {} #int id: (status: , stages: , f:)

    def run(self):
        while True :
        #TODO : get list of jobs, with number of stages and status
            print("[job-{}] Discovering".format(self.id))
            #FIXME : Try catch is needed there to ensure jobs keep polling
            ##stages=response = requests.get(sefl.url,  auth=JOB_AUTH)
            with open('jenkraft.example.json') as data_file:
                data = json.load(data_file)

            job_count = 0
            for job_data in data:
                stagesCount = 0
                job_id = int(job_data['id'])
                job_status = job_data['status']

                print(job_data['id']+" : "+job_data['status'])

                #Because of declarative pipelines we loop over all stages
                #If any of the stages is different from SUCCESS then stop couting
                #Because we want to stop and consider only stages that really ran
                for stage in job_data['stages']:
                    stagesCount = stagesCount + 1
                    print(" - stage {} status : {} ".format(stage['id'], stage['status']))
                    if stage['status'] != "SUCCESS":
                        break
                print (" - stages count {} ".format(stagesCount))

                if (job_id in self.fountains):
                    print ("updating build : {}".format(job_id))
                    self.fountains[job_id]['stages'] = stagesCount
                    self.fountains[job_id]['status'] = job_status

                else:
                    print ("creating build : {}".format(job_id))
                    self.fountains[job_id] = {'stages': stagesCount, 'status': job_status, 'f': None}

            print("now draw with ordered list")

            sorted_jobs = collections.OrderedDict(sorted(self.fountains.iteritems(), key=lambda x: x[0]))
            for job_id in sorted_jobs:
                #TODO (FEATURE) : use a type of encoding for remembering id ?

                if self.fountains[job_id]['f'] is not None:
                    print ("fountain already referenced : {}".format(job_id))

                else:
                    print("Creating new fountain {}, {}, {}, {}".format(
                    -64+(sorted_jobs.keys().index(job_id)*12),
                        MAX_OCEAN_Y,
                        -(MAX_OCEAN_Z-10), self.material))
                    #TODO : 60=branche relative index, other step=12, step= 10
                    f = Fountain(1, self.mc,
                        -64+(sorted_jobs.keys().index(job_id)*12),
                        MAX_OCEAN_Y,
                        -(MAX_OCEAN_Z-10), self.material)

                    f.draw_flow()
                    self.fountains[job_id]['f'] = f

                f = self.fountains[job_id]['f']
                #//TODO : on finish : met them flow
                f.set_stages(self.fountains[job_id]['stages'])
                f.set_status(self.fountains[job_id]['status'])

                #expe : limit
                if (job_count>99):
                    break

            print("end : sleeping")
            time.sleep(JOB_REFRESH_TIME)

    def stop(self):
        self._stop_event.set()
        self.clear()

    def stopped(self):
        return self._stop_event.is_set()

    def __cmp__(self, rhs):
        return hash(self) - hash(rhs)

    def __hash__(self):
        return (self.id << 8)

    def add_fountain(f):
        self.fountains.append(f) #TODO : add a fountain with good space location

    def clear(self):
        #TODO
        for f in self.fountains:
            f['f'].clear()
            print("clear fountains")
            #    x.clear()

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
        #Bedrock as an ocean
        self.mc.setBlocks(-MAX_OCEAN_X, MAX_OCEAN_Y-2, -MAX_OCEAN_Z,
                          MAX_OCEAN_X, MAX_OCEAN_Y-5, MAX_OCEAN_Z,
                          block.BEDROCK_INVISIBLE)

        #Init scene
        self.mc.setBlock(DEFAULT_POS_X, DEFAULT_POS_Y-1, DEFAULT_POS_Z, block.BEDROCK_INVISIBLE)
        self.mc.player.setPos(DEFAULT_POS_X, DEFAULT_POS_Y, DEFAULT_POS_Z)


class Fountain:
    """Jenkraft fountain"""
    """f = jenkraft.Fountain(1,mc,9,3,0)"""
    """f.addStage()"""
    """f.clear()"""

    def __init__(self, id, mc, x, y, z, material=block.COBBLESTONE, status=JOB_RUNNING, height=1):
        self.id = id
        self.mc = mc
        self.status = status
        #Keep old status cause flowing water replaced by flowing lava involves wait
        self.previous_status = status
        self.x = x
        self.y = y
        self.z = z
        self.material = material
        self.height = height
        self.build_base()
        self.add_stage()

    def __cmp__(self, rhs):
        return hash(self) - hash(rhs)

    def __hash__(self):
        return (self.id << 8) + self.data

    def build_base(self):
        #Blast
        self.mc.setBlocks(self.x-6,self.y,self.z-12,
                          self.x+6,self.y+200,self.z+12,
                          block.AIR)

        self.mc.setBlocks(self.x-2,self.y,self.z-2,
                          self.x+2,self.y,self.z+2,
                          self.material)
        self.mc.setBlocks(self.x-1,self.y,self.z-1,
                          self.x+1,self.y,self.z+1,
                          block.AIR)

        self.mc.setBlocks(self.x-4,self.y-1,self.z-4,
                          self.x+4,self.y-1,self.z+4,
                          self.material)


    def set_stages(self, num):
        self.height=num
        self.draw_flow()

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

    def set_status(self, status):
        print(" status {}".format(status))
        self.status=status
        self.draw_flow()
        self.previous_status=self.status

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

mc = Minecraft.create()
scene = Scene(mc)
