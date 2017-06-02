# WIP

## Notes for developping

### Starting

from mcpi.minecraft import Minecraft
from mcpi import block

mc = Minecraft.create()

mc.saveCheckpoint()

import jenkraft
ocean = jenkraft.Ocean(1, mc)

### Dealing with jobs

job = jenkraft.Job(1, "test", mc)
job.start()

### Dealing with fountains

f = jenkraft.Fountain(1,mc, 24, 15, -40)
f.add_stage()
f.clear()

### Position for branches

=> -24,-12,0,12,24
=> -40, -30, -10, 0, 10, 20, 30, 40, 50

### Materials that should be used

GRASS, DIRT, COBBLESTONE, DIAMOND_ORE, STONE_BRICK, GOLD_ORE, IRON_ORE, MUSHROOM_BROWN, FLOWER_YELLOW, SAND

### Other usefull commands
reload(jenkraft)

mc.postToChat("Hello world")

## Refs
http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
