from mcpi.minecraft import Minecraft
from mcpi import block

mc = Minecraft.create()

mc.saveCheckpoint()

import jenkraft
ocean = jenkraft.Ocean(1, mc)

f2 = jenkraft.Fountain(1,mc, 24, 15, -40)
f2 = jenkraft.Fountain(1,mc, -24, 15, -40)


#mc.postToChat("Hello world")

