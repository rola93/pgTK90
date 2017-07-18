from emulator.manic_miner import ManicMiner
from scipy.misc import imsave
from pdb import set_trace

folder = 'checkpoints'
lives = 0
frameskip = 3
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

manic_miner = ManicMiner(frameskip=frameskip, freccuency_mhz=1.3)
print("\n")

for episode in xrange(20):
    if not first_episode:
        raw_input('Ready to reset enviroment?')
    else:
        print("Reseting enviroment.")
        first_episode = False
    manic_miner.reset()
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
            imsave('{}/{}.jpg'.format(folder, saved), obs)
            manic_miner.save_state('{}/{}'.format(folder, saved))
            print("Saved checkpoint #{}".format(saved))
            saved += 1
            continue
        elif command == 'k':
            key = raw_input('Select number key? [1,2,3,4,5]')
            position = raw_input('Select screen position [0,..,512]')
            manic_miner.key_position(int(key),int(position))
            manic_miner.step('NOOP')
            manic_miner.render()
            continue
        elif command == 't':
            print '0-background\n', '1-floor\n', '2-crumbling_floor\n', '3-wall\n', '4-conveyor\n', '5-nasty_1\n', '6-nasty_2\n'
            types = ['background', 'floor', 'crumbling_floor', 'wall', 'conveyor', 'nasty_1', 'nasty_2']
            typeNumber = raw_input('Select tile type?')
            position = raw_input('Select screen position [0,..,256] (only top screen :\'( )')

            manic_miner.put_tile(int(position), types[int(typeNumber)])
            manic_miner.step('NOOP')
            manic_miner.render()
            continue
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
            print("Finish breakpoint with the command 'c':")
            set_trace()
        else:
            action = 'NOOP'

        obs, reward, done, info = manic_miner.step(action)
        manic_miner.render()
