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
import urlparse

API_SUFFIX="./wfapi/runs"

JOB_RUNNING="IN_PROGRESS"
JOB_NOT_EXECUTED="NOT_EXECUTED"
JOB_SUCCESS="SUCCESS"
JOB_UNSTABLE="UNSTABLE"
JOB_FAILED="FAILED"
JOB_ABORTED="ABORTED"
JOB_REFRESH_TIME=30 #Refresh each 30s

#TODO : clean or rename since "Ocean" is no more handled as an object but a consequence of liquids flowing
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
        self.do_loop = True
        mc.events.clearAll()

        #TODO config per branch alley height (or dynamic walk height ? )
        with open('config.yml') as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                i=0
                for job_config in yaml_data['jobs']:
                    auth = None
                    if 'user' in job_config:
                        auth = (job_config['user'], job_config['pass'])

                    job = Job(i, urlparse.urljoin(job_config['url'], API_SUFFIX), auth, eval("block.{}".format(job_config['block'])), self.mc)
                    self.jobs.append(job)

                    i+=1

                scheduler = Scheduler(self.jobs)
                print("discovering jobs")
                scheduler.handle_jobs()

                time.sleep(1)
                print("start watching jobs")
                scheduler.start()

                self.loop()

            except yaml.YAMLError as exc:
                print(exc)

    def loop(self):
        i=0
        while self.do_loop is True:
            for job in self.jobs:
                print("job watching {}".format(job.id))
                self.mc.postToChat("On your right is job : ") #this should be said about each 5 builds cause chat can disapear (use modulo)
                self.mc.postToChat("{}".format(job.url)) #TODO would be great to be able to override in config
                z = DEFAULT_POS_Z + job.id*12 + 4
                exit_job = False
                i=0

                try:
                    while self.do_loop is True and exit_job is False:
                        i += 1
                        x = -70+(i) #TODO : more than 6 latest builds is useless, pause earlyer, walk slowly

                        #if block.GLASS in mc.events.pollBlockHits().entityId:
                        blockHits = mc.events.pollBlockHits()
                        mc.events.clearAll()
                        #FIXME Minetest for => face is not entityId ! Since touch is not break => could poll what block is touched at a waht place instead of tweaking this ?
                        #TEST on raspberry pi !
                        if next((x for x in blockHits if mc.getBlock(x.pos) == block.GLASS.id), None) is not None:
                            self.mc.postToChat("Autowalk stoppped. Awaiting a new glass to be punched...")
                            reWalk = False
                            while not reWalk:
                                time.sleep(1)
                                blockHits = mc.events.pollBlockHits()
                                mc.events.clearAll()
                                if next((x for x in blockHits if mc.getBlock(x.pos) == block.GLASS.id), None):
                                    self.mc.postToChat("Autowalk on")
                                    reWalk = True

                        mc.player.setPos(x,DEFAULT_POS_Y,z-0.5)

                        #FIXME: this is not a good game pattern
                        time.sleep(1+(random.randint(0,10)/10))

                        if (x>=(-70 + 10*len(job.fountains))):
                            exit_job = True

                except Exception as e:
                    print "GOT A PROBLEM"
                    print(e)

                #Sleep more before changing job
                self.mc.postToChat("Stay on watching latest job for 10 seconds...")
                time.sleep(10)

    def start_loop(self):
        self.do_loop = True

    def stop_loop(self):
        self.do_loop = False

class Scheduler(threading.Thread):
    def __init__(self, jobs):
        self.jobs = jobs
        super(Scheduler, self).__init__()
        self.setDaemon(True)
        self._stop_event = threading.Event()

    def handle_jobs(self):
        for job in self.jobs:
            try:
                print("dealing with job {}", job)
                job.collect()
                job.draw()
                time.sleep(1)
            except:
                print("problem in job loop")

    def run(self):
        while True:
            self.handle_jobs()

    def stop(self):
        for job in self.jobs:
            job._stop_event.set()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Job:
    """Jobs : can be a branch or a simple job, only URL is known by code """
    def __init__(self, id, url, auth, material, mc):
        self.id = id
        self.mc = mc
        self.url = url
        self.auth = auth
        self.material=material
        #TODO : would be clearer to have a build list instead of fountain keyword
        self.fountains = {} #int id: (status: , stages: , f:)

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
                    -(MAX_OCEAN_Z-10)+self.id*12, self.material, self.fountains[job_id]['status'], self.fountains[job_id]['stages'])

                self.fountains[job_id]['f'] = f

            f = self.fountains[job_id]['f']

            #TODO : if something changed, would be good to teleport to position before rendering (pause loop, teleport, sleep 10, loop again)
            should_draw = f.set_stages(self.fountains[job_id]['stages'])

            should_draw = should_draw or f.set_status(self.fountains[job_id]['status'])

            if should_draw:
                f.draw_flow()

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
        self.previous_status = status
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

        #Path (height may be dynamic)
        mc.setBlocks(self.x-7, 14, self.z-7, self.x+7, 14, self.z-7, block.GLASS)


    def set_stages(self, num):
        prev_height = self.height
        self.height=num
        if prev_height != self.height:
            return True

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

        #if done -> let liquid flow away
        if (self.status in (JOB_SUCCESS, JOB_FAILED, JOB_ABORTED, JOB_UNSTABLE)):
            for x,z in [ (2,0), (-2,0), (0,2), (0,-2) ]:
                self.mc.setBlock(self.x+x, self.y, self.z+z, block.AIR)

        #Unstable builds get flammes
        if (self.status==JOB_UNSTABLE):
            self.mc.setBlocks(self.x-1, self.y+self.height+2, self.z-1, self.x+1, self.y+self.height+2,self.z+1,block.TNT)

        self.previous_status=self.status

    def set_status(self, status):
        print(" status {}".format(status))
        self.previous_status=self.status
        self.status=status
        if (self.status != self.previous_status):
            return True

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
