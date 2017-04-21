from manic_miner import ManicMiner
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