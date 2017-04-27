from emulator.manic_miner import ManicMiner
from scipy.misc import imsave

folder = 'checkpoints'
saved = 0

print('''
Program for generating checkouts for Manic Miner
------------------------------------------------
Commands:

Q W E    P
A S D    L
		 M

A: Left
S: No key
D: RIGHT
W: UP
Q: LEFT UP
E: RIGHT UP

P: Save state (will save with a sequential number starting from 0). An image is generated for visual reference.
L: Load a previous checkpoint. Input the checkpoint number when you are requested to do so.
M: quit.

Enjoy! ;)
''')

manic_miner  = ManicMiner(frameskip=1, freccuency_mhz=1.3)

print("\n")

for episode in xrange(20):
    print("Reseting enviroment.")
    manic_miner.load_level0()
    manic_miner.render()
    done = False
    print("episode: {}".format(episode))
    while not done:
        action = None
        command = raw_input('Action:').lower()
        if command == 's':
            action = 'NOOP'
        elif command == 'a':
            action = 'LEFT'
        elif command == 'd':
            action = 'RIGHT'
        elif command == 'w':
            action = 'UP'
        elif command == 'q':
            action = 'LEFTUP'
        elif command == 'e':
            action = 'RIGHTUP'
        elif command == 'p':
            imsave('checkpoints/{}.jpg'.format(saved), obs)
            manic_miner.save_state('{}/{}'.format(folder, saved))
            print("Saved checkpoint #{}".format(saved))
            saved += 1
        elif command == 'l':
            restore_name = raw_input('Number/name of state to restore:')
            manic_miner.reset(checkpoint='{}/{}'.format(folder, restore_name))
            print("Restored checkpoint #{}".format(restore_name))
            manic_miner.render()
            continue
        elif command == 'm':
            print("\nClosing. Thank you!")
            manic_miner.close()
            exit()
        else:
            action = 'NOOP'

        obs, reward, done, info = manic_miner.step(action)
        manic_miner.render()
