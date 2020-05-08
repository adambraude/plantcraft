# PlantCraft
PlantCraft is a game that simulates the root growth of plants! Each plant tries to collect nutrient blocks with its root tips more efficiently than the plant. Roots can only grow from the tip, but can otherwise grow in any direction. When a plant grows its root, it may choose to make a new root tip instead of moving the existing root tip. This is called "forking" and costs additional energy. The first plant to reach the energy goal wins. If a plant runs out of energy entirely, it automatically loses.

# Usage

On the command line, run 
```sh
python -u plantcraft.py
```
(assuming that your working directory contains the PlantCraft files.) The -u option for Python will cause all messages to be printed to the command line immediately instead of in sporadic batches, which is really nice for breeding or CPU matches.

This should bring up the PlantCraft GUI, where you can specify the settings for your game. 
  - Program Mode: Play will give you a single, graphical game with the specified settings.
  - Program Mode: CPU best of 100 will play 100 games with no graphics and the specified settings, then report winrates.
  - Program Mode: Breeding is for breeding genetic players. By default, ExploreExploitPlayers are bred. If DirectionsPlayer or APlayer is set as Player 1, those players will be bred instead.
  - During Play Mode, you can press Backspace to save a replay file. You can then rewatch the game by checking Replay in the menu, setting Play Mode, and selecting the logfile. This feature may have bugs.
  - The Play Mode controls are Minecraft controls. Arrows or WASD to move laterally, shift/space to move vertically, mouselook. Click a root of your plant to grow it. Right click to fork.

# The Players
**Human Player**: Use to play games against the AI in Play Mode. You can play hotseat with two Human Players. We don't know why anyone would do that.

**Random Player**: Picking legal moves at random is a bad idea in this game, but no one told this algorithm that. Never forks because we didn't want to torture it more.

**GreedyPlayer**: Always makes a beeline for the nearest known nutrient. Never forks.

**GreedyForker**: Always charges blindly toward the nearest known nutrient. Will fork in order to reduce the cost of approaching the second closest nutrient.

**ExploreExploitPlayer**: Needs a gene with length specified on the slider. Gene determines how likely it is to pursue the nearest/farthest nutrient.

**DirectionsPlayer**, **APlayer**: Different kinds of genetic player. DirectionsPlayer needs 5 genes, ExploreExploit needs 8.