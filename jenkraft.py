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
import yaml


JOB_RUNNING="IN_PROGRESS"
JOB_NOT_EXECUTED="NOT_EXECUTED"
JOB_SUCCESS="SUCCESS"
JOB_UNSTABLE="UNSTABLE"
JOB_FAILED="FAILED"
JOB_ABORTED="ABORTED"
JOB_REFRESH_TIME=30 #Refresh each 30s

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

#Generic FIXME: handle exceptions

class Scene:
    def __init__(self, mc):
        self.mc = mc
        self.jobs = []

        #TODO yml config (+config per branch alley height (or dynamic walk height ? ))
        with open('config.yml') as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                i=0
                for job_config in yaml_data['jobs']:
                    #job  = Job(i, JOB_URL, JOB_AUTH, m, mc)
                    #FIXME handle auht
                    auth = None
                    if 'user' in job_config:
                        auth = (job_config['user'], job_config['pass'])

                    job = Job(i, job_config['url'], auth, eval("block.{}".format(job_config['block'])), self.mc)
                    job.start()
                    self.jobs.append(job)

                    i+=1
                    time.sleep(2)

                self.do_loop = True
                self.loop()

            except yaml.YAMLError as exc:
                print(exc)

    def loop(self):
        i=0
        while self.do_loop is True:
            for job in self.jobs:
                print("job watching {}".format(job.id))
                z = DEFAULT_POS_Z + job.id*12 + 4
                exit_job = False
                i=0
                while self.do_loop is True and exit_job is False:
                    i += 1
                    x = -70+(i) #TODO : more than 6 latest builds is useless, pause earlyer, walk slowly

                    #Don't fall
                    #TODO : might better draw this while drawing fountains ?
                    mc.setBlocks(x-1,DEFAULT_POS_Y-1,z-1, x+1,DEFAULT_POS_Y-1,z+1, block.GLASS)
                    time.sleep(0.1)
                    mc.player.setPos(x,DEFAULT_POS_Y,z)

                    #FIXME: this is not a good pattern
                    time.sleep(1+(random.randint(0,10)/10))

                    if (x>=(-70 + 10*len(job.fountains))):
                        exit_job = True
                #Sleep more before changing job
                time.sleep(10)

    def stop_loop(self):
        self.do_loop = False

class Job(threading.Thread):
    """Jobs : can be a branch or a simple job, only URL is known by code """
    def __init__(self, id, url, auth, material, mc):
        super(Job, self).__init__()
        self._stop_event = threading.Event()
        self.setDaemon(True)
        self.id = id
        self.mc = mc
        self.url = url
        self.auth = auth
        self.material=material
        #TODO : would be clearer to have a build list instead of fountain keyword
        self.fountains = {} #int id: (status: , stages: , f:)

    def run(self):
        while True :
            self.collect()
            self.draw()
            print("end : sleeping")
            time.sleep(JOB_REFRESH_TIME)

    def collect(self):
        print("[job-{}] Discovering".format(self.id))
        #FIXME : Try catch is needed there to ensure jobs keep polling
        response = requests.get(self.url, auth=self.auth)
        data = json.loads(response.text)

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

    def draw(self):
        sorted_jobs = collections.OrderedDict(sorted(self.fountains.iteritems(), key=lambda x: x[0]))
        for job_id in sorted_jobs:
            #FEATURE : use a type of encoding for remembering id, commiter colour ?

            if self.fountains[job_id]['f'] is not None:
                print ("fountain already referenced : {}".format(job_id))

            else:
                print("Creating new fountain {}, {}, {}, {}".format(
                -64+(sorted_jobs.keys().index(job_id)*12),
                    MAX_OCEAN_Y,
                    -(MAX_OCEAN_Z-10)+self.id*12, self.material))

                f = Fountain(1, self.mc,
                    -64+(sorted_jobs.keys().index(job_id)*12),
                    MAX_OCEAN_Y,
                    -(MAX_OCEAN_Z-10)+self.id*12, self.material)

                self.fountains[job_id]['f'] = f
                time.sleep(10)
            f = self.fountains[job_id]['f']
            #FIXME: should not changes representation if nor stages nor status is changed
            #Plus TODO : if something changed, would be good to teleport to position before rendering (pause loop, teleport, sleep 10, loop again)
            f.set_stages(self.fountains[job_id]['stages'])

            #FIXME: set status handles draw_flow cause of previous status handle. Refactor with switch_state ?
            f.set_status(self.fountains[job_id]['status'])
            #f.draw_flow()

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
        self.mc.setBlocks(self.x-7,self.y-10,self.z-7,
                          self.x+7,self.y+50,self.z+7,
                          block.AIR)
        time.sleep(1)  #Blast may take some time

        #Recepient
        self.mc.setBlocks(self.x-2,self.y,self.z-2,
                          self.x+2,self.y,self.z+2,
                          self.material)
        self.mc.setBlocks(self.x-1,self.y,self.z-1,
                          self.x+1,self.y,self.z+1,
                          block.AIR)

        #Base
        self.mc.setBlocks(self.x-4,self.y-1,self.z-4,
                          self.x+4,self.y-1,self.z+4,
                          self.material)

        #Torches
        for x, z in [ (2,2), (2,-2), (-2,2), (-2,-2) ]:
            self.mc.setBlock(self.x+x,self.y+1,self.z+z, block.TORCH)

        #Floor
        self.mc.setBlocks(self.x-7,self.y-2,self.z-7,
                          self.x+7,self.y-2,self.z+7,
                          block.COBBLESTONE)

    def set_stages(self, num):
        self.height=num

    def add_stage(self):
        self.height+=1

    def draw_flow(self):
        #clear first in case iand give a lil of time for flowings to disapear in case of statsus change
        if (self.status != self.previous_status):
            self.mc.setBlocks(self.x-1, self.y, self.z-1, self.x+1, self.y+self.height,self.z+1,block.AIR)
            time.sleep(0.2*self.height)

        block_to_build = block.WATER_STATIONARY
        width=0
        #Fill fountain execpt if not executed
        if (self.status!=JOB_NOT_EXECUTED):
            if (self.status==JOB_FAILED):
                block_to_build = block.LAVA_STATIONARY
            elif (self.status==JOB_ABORTED):
                block_to_build = block.GLASS
                width=1
            self.mc.setBlocks(self.x-width, self.y, self.z-width, self.x+width, self.y+self.height,self.z+width,block_to_build)

        #FIXME: in case of snow : hole y +1 may block liquid
        #if done -> let liquid flow away
        if (self.status in (JOB_SUCCESS, JOB_FAILED, JOB_ABORTED, JOB_UNSTABLE)):
            for x,z in [ (2,0), (-2,0), (0,2), (0,-2) ]:
                self.mc.setBlock(self.x+x, self.y, self.z+z, block.AIR)

        #Unstable builds get flammes 
        if (self.status==JOB_UNSTABLE):
            self.mc.setBlocks(self.x-1, self.y+self.height+2, self.z-1, self.x+1, self.y+self.height+2,self.z+1,block.FIRE)

        #FIXME: at least deprecated
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
