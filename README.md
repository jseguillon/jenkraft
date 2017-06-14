# jenkraft.py

jenkraft.py is jenkins REST exploring for Minecraft interraction

## Start

Launch python2 `python` then `execfile('jenkraft.py')`

## Configuration

TODO yaml config

# WIP Zone

## A fountain

TODO : ascii schema for more comprehensive

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

### Materials that could be used as base for fountains

GRASS, DIRT, COBBLESTONE, DIAMOND_ORE, STONE_BRICK, GOLD_ORE, IRON_ORE, GOLD_BLOCK, IRON_BLOCK, STONE_SLAB_DOUBLE, STONE_SLAB, BRICK_BLOCK, MOSS_STONE, DIAMOND_BLOCK, LAPIS_LAZULI_ORE, LAPIS_LAZULI_BLOCK, SANDSTONE, COBWEB, GRASS_TALL, REDSTONE_ORE, GLOWSTONE_BLOCK


### Other usefull commands
reload(jenkraft)

mc.postToChat("Hello world")

## Refs
http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
