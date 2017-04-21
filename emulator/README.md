# Manic Miner
## Spectrum ZX Emulator

Manic Miner emulator based on [PyZX emulator](http://www.pygame.org/project-PyZX-173-.html).

Requeriments:
- [Python 2.4+](https://www.python.org/downloads/)
- [PyGame 1.7+](http://www.pygame.org)
- [OpenAI Gym](https://gym.openai.com/) Atari 

Have in mind that is a module so if you want to use it you either place it on the folder you want to run it or place it in /usr/local/lib/python2.7/dist-packages.


Warning: It may take some time to start running (when is skipping a roms bugg), just wait a few seconds.

Parameters:
- frameskip: number of frames the enviroment will play in a row during a step repeating the same provided action. Rewards will sum up. For no frame skip input a 0 (default 1)
- freccuency_mhz: frequency of the microprocessor. Is not recommended to change since it can affect stability (default 3.5)

Reset parameters: 
- lives: lives that your agent will have (default 0)
- level: level you want your agent to play (default 1)
- checkpoint: provide a file's path with a game saved state. The game will start from that checkpoint state 

Below you have an ilustrative example on how to run the enviroment.

```python
from emulator.manic_miner import ManicMiner
import random

manic_miner = ManicMiner(frameskip=1)
for episode in xrange(20):
	obs = manic_miner.reset(lives=1)
	manic_miner.render()
	done = False
	print("episode: {}".format(episode))
	while not done:
		action = random.choice(manic_miner.actions())
		obs, reward, done, info = manic_miner.step(action)
		# scipy.misc.imsave('replay/{}.jpg'.format(steps), obs)
		manic_miner.render()
```

