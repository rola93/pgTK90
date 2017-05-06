from manic_miner import ManicMiner
import random
from scipy.misc import imsave

manic_miner = ManicMiner(frameskip=1, freccuency_mhz=3.5)
j=0
for episode in xrange(200):
    obs = manic_miner.reset(lives=0)
    manic_miner.reset(checkpoint='checkpoints/11')
    manic_miner.render()
    done = False
    # print("episode: {}".format(episode))
    last_reward = None
    while not done:
        j += 1
        action = random.choice(manic_miner.actions() + ['RIGHT', 'LEFT', 'RIGHT', 'LEFT', 'NOOP', 'RIGHT', 'LEFT', 'NOOP'])
        obs, reward, done, info = manic_miner.step(action)
        if j % 100 == 0:
            print 'episodio = ', episode, ' j = ', j
        #     imsave('test/{}.jpg'.format(str(episode) + '_' + str(j)), obs)
        # if reward != last_reward:
        #     print 'Cambio en recompenza: ', episode, ' j = ', j, 'reward: ', reward
        air = manic_miner.get_air()
        imsave('test/rw_{}.jpg'.format(str(j) + '-' + str(episode) + '-' + action + '-rew=' + str(reward) + '-air=' + str(air)), obs)
        # scipy.misc.imsave('replay/{}.jpg'.format(steps), obs)
        # manic_miner.render()
        # last_reward = reward
# print 'guardando episodio 199 j = ', j
# imsave('test/{}.jpg'.format(str(199) + '_' + str(j)), obs)
print "Final del experimento"