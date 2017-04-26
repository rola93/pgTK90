from emulator.manic_miner import ManicMiner
from scipy.misc import imsave
from pdb import set_trace

folder = 'checkpoints'
lives = 0
frameskip = 2
saved = 0
starting_number = None

print('''
Program for generating checkouts for Manic Miner
------------------------------------------------
Commands:

Q W E    P
A S D    L
       N M

A: Left
S: No key
D: RIGHT
W: UP
Q: LEFT UP
E: RIGHT UP

P: Save state (will save with a sequential number starting from 0). An image is generated for visual reference.
L: Load a previous checkpoint. Input the checkpoint number when you are requested to do so.
M: quit.
N: Breakpoint.

Enjoy! ;)
''')

first_episode = True

manic_miner = ManicMiner(frameskip=frameskip)
print("\n")

for episode in xrange(20):
    if not first_episode:
        raw_input('Ready to reset enviroment?')
    else:
        print("Reseting enviroment.")
        first_episode = False
    manic_miner.reset(lives=lives)
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
            if starting_number == None:
                starting_number = raw_input('From which number do you want to start saving? [0, 5, 11, ...]:')
                saved = int(starting_number)
            imsave('checkpoints/{}.jpg'.format(saved), obs)
            manic_miner.save_state('{}/{}'.format(folder, saved))
            print("Saved checkpoint #{}".format(saved))
            saved += 1
        elif command == 'l':
            restore_name = raw_input('Number/name of state to restore [Enter to cancel]:')
            if restore_name:
                manic_miner.reset(checkpoint='{}/{}'.format(folder, restore_name))
                print("Restored checkpoint #{}".format(restore_name))
                manic_miner.render()
            continue
        elif command == 'm':
            print("\nClosing. Thank you!")
            manic_miner.close()
            exit()
        elif command == 'n': 
            print("Finish breakpoint with the command c")
            set_trace()
        else:
            action = 'NOOP'

        obs, reward, done, info = manic_miner.step(action)
        manic_miner.render()
