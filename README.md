# jenkraft.py

Explore Jenkins jobs in Minecraft® pi or Minetest

jenkraft.py renders builds per job with a fountain design :
- Water fountain with base closed : RUNNING,
- Water fountain with base open : SUCCESS,
- Lava fountain with base open : FAILED,
- Glass fountain : ABORTED,
- Water fountain with TNT on top : UNSTABLE.

Height depends on the number of stages that where succesfull.

## Install

### Download Jenkraft

Downloading Jenkraft can be done :
 - by cloning master branch from github  : `git clone https://github.com/jseguillon/jenkraft.py.git`
 - by downloading and unzipping master archive located at https://github.com/jseguillon/jenkraft.py/archive/master.zip

### Minecraft pi edition

*NOTE* : this has been tested only with raspbian distrib.

First you need to install python-yaml dependency :  `sudo apt-get install python-yaml`

Then you can start Minecraft pi edition and go to Configuration section.

### Minetest
*IMPORTANT* : this only works with Minetest 0.4.13 and has only be tested on windows 10.

Minetest is a Minecraft alternative that can be combined with a mod allows Minetest to be controled by python.

First download Minetest 0.4.13 ( https://github.com/minetest/minetest/releases/tag/0.4.13) then install.

Download the raspberryjammod mod for Minetest from my own fork : https://github.com/jseguillon/raspberryjammod-minetest/archive/master.zip then unzip.

Place the `raspberryjammod` in your mods directory (should be C:\games\Minetest\mods).

Download the default minetest game : https://github.com/minetest/minetest_game/releases/tag/0.4.13 and copy wool mod wihch is needed for raspberryjammod.

Copy the `mcpipy` directory included in the raspberryjammod, to the root of your jenkraft.py donwload/clone.

Open your minetest.conf file and set `secure.enable_security = false`.

At last, you now can open Minetest, create a game, activate the mods and continue installation.

## Configuration

Sample config.yml describe the config structure :
```
jobs:
  - url: "https://ci.jenkins.io/job/Plugins/job/git-plugin/job/PR-493/wfapi/runs"
    block: GRASS
    #user: user
    #pass: pass
```
block is the block that will be used to draw the fountains for the job. User and pass can be defined (pass should be the API Token of user / not your real password).

## Start

Launch python2 `python` then type `execfile('jenkraft.py')`. You can do this on your pi our using new `bash` command from Windows 10.

# WIP dev Zone

## A fountain

TODO : ascii schema for better understand on how things are done
