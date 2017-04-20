# Manic Miner
## Spectrum ZX Emulator

Manic Miner emulator based on [PyZX emulator](http://www.pygame.org/project-PyZX-173-.html).

Requeriments:
- [Python 2.4+](https://www.python.org/downloads/)
- [PyGame 1.7+](http://www.pygame.org)
- [OpenAI Gym](https://gym.openai.com/) Atari 

Have in mind that is a module so if you want to use it you either place it on the folder you want to run it or place it in /usr/local/lib/python2.7/dist-packages.

Below you have an ilustrative example on how to run the enviroment.

Warning: It may take some time to start running (when is skipping a roms bugg), just wait a few seconds.

```python
from emulator.manic_miner import ManicMiner
import random

manic_miner = ManicMiner(frameskip=1, freccuency_mhz=3.5)
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

