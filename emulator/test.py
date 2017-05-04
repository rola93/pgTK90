from manic_miner import ManicMiner
import random
from scipy.misc import imsave

manic_miner = ManicMiner(frameskip=1, freccuency_mhz=3.5)
j=0
for episode in xrange(200):
    obs = manic_miner.reset(lives=0)
    manic_miner.render()
    done = False
    # print("episode: {}".format(episode))
    while not done:
        j += 1
        action = random.choice(manic_miner.actions())
        obs, reward, done, info = manic_miner.step(action)
        if j % 100 == 0 or j % 100 == 1:
            print 'guardando episodio ', episode, ' j = ', j
            imsave('test/{}.jpg'.format(str(episode) + '_' + str(j)), obs)
        # scipy.misc.imsave('replay/{}.jpg'.format(steps), obs)
        manic_miner.render()
print 'guardando episodio 199 j = ', j
imsave('test/{}.jpg'.format(str(199) + '_' + str(j)), obs)
print "Final del experimento"