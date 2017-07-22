from emulator.manic_miner import ManicMiner
from scipy.misc import imsave
from pdb import set_trace
import pygame, sys

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
        elif command == 'key':
            print 'Click en la pantalla, Select key?[1,2,3,4,5], move with arrows, q for quit'

            pygame.init()
            key = 1
            position = 0
            mov = 0
            old_color = None
            type = None
            quit = False
            while not quit:
                events = pygame.event.get()

                for event in events:
                    # up 273
                    if event.type != 3:
                        continue
                    if event.key == pygame.K_UP:
                        mov = -32
                    if event.key == pygame.K_DOWN:
                        mov = 32
                    if event.key == pygame.K_LEFT:
                        mov = -1
                    if event.key == pygame.K_RIGHT:
                        mov = 1
                    if event.key == pygame.K_1:
                        key = 1
                    if event.key == pygame.K_2:
                        key = 2
                    if event.key == pygame.K_3:
                        key = 3
                    if event.key == pygame.K_4:
                        key = 4
                    if event.key == pygame.K_5:
                        key = 5
                    if event.key == pygame.K_q:
                        print 'QUIT'
                        quit = True

                    position = manic_miner.get_key_position(key)
                    position = (position + mov) % 512
                    mov = 0

                    if (type != None):
                        manic_miner.put_tile(int(position), manic_miner.get_tile_definition(types[type]))
                        type = None

                    manic_miner.key_position(int(key),int(position))
                    manic_miner.step('NOOP')
                    manic_miner.render()
                    continue
        elif command == 'play':
            print 'Click en la pantalla, move with arrows, esc for quit'
            pygame.init()
            arrow = None
            quit = False
            while not quit:
                events = pygame.event.get()

                for event in events:
                    # up 273
                    if event.type != 3:
                        continue
                    if event.key == pygame.K_w:
                        arrow = 'UP'
                    elif event.key == pygame.K_s:
                        arrow = 'NOOP'
                    elif event.key == pygame.K_a:
                        arrow = 'LEFT'
                    elif event.key == pygame.K_d:
                        arrow = 'RIGHT'
                    elif event.key == pygame.K_q:
                        arrow = 'LEFTUP'
                    elif event.key == pygame.K_e:
                        arrow = 'RIGHTUP'
                    elif event.key == pygame.K_ESCAPE:
                        print 'QUIT'
                        quit = True
                    else:
                        continue

                    obs, reward, done, info = manic_miner.step(arrow)
                    manic_miner.render()
                    if done:
                        quit = True
                    continue
        elif command == 'edit':
            print 'Click in game, move with arrows, q for quit'
            print '0-background\n', '1-floor\n', '2-crumbling_floor\n', '3-wall\n', '4-conveyor\n', '5-nasty_1\n', '6-nasty_2\n'
            types = ['background', 'floor', 'crumbling_floor', 'wall', 'conveyor', 'nasty_1', 'nasty_2']

            pygame.init()
            position = 0
            mov = 0
            old_color = None
            type = None
            quit = False
            while not quit:
                events = pygame.event.get()

                for event in events:
                    #up 273
                    if event.type != 3:
                        continue
                    if event.key == pygame.K_UP:
                        mov = -32
                    if event.key == pygame.K_DOWN:
                        mov = 32
                    if event.key == pygame.K_LEFT:
                        mov = -1
                    if event.key == pygame.K_RIGHT:
                        mov = 1
                    if event.key == pygame.K_0:
                        type = 0
                    if event.key == pygame.K_1:
                        type = 1
                    if event.key == pygame.K_2:
                        type = 2
                    if event.key == pygame.K_3:
                        type = 3
                    if event.key == pygame.K_4:
                        type = 4
                    if event.key == pygame.K_5:
                        type = 5
                    if event.key == pygame.K_6:
                        type = 6
                    if event.key == pygame.K_q:
                        print 'QUIT'
                        quit = True

                    if(old_color!= None):
                        manic_miner.select_tile(position,old_color)
                        old_color = None

                    position = (position + mov) % 512
                    mov = 0

                    if(type!=None):
                        manic_miner.put_tile(int(position), manic_miner.get_tile_definition(types[type]))
                        type = None

                    if(not quit):
                        old_color = manic_miner.select_tile(position, 40)

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
