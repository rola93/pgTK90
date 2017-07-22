import py_zx.Z80 as em
import py_zx.spectrum as sp
import constants as c
import os
import numpy as np
from gym import spaces

class ManicMiner:
    def __init__(self, frameskip=1, freccuency_mhz=3.5, crop=(0, 0, 0, 0), infinite_air=True):
        assert isinstance(frameskip, int)
        self.frameskip = frameskip
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sp.initialize(dir_path + '/ManicMiner.z80', iterruption_freccuency_mhz=freccuency_mhz, crop=crop)

        self.levels = [None for _ in xrange(20)]
        self.actual_frame = 0
        self.colors = [
            1, # blue
            14 # normal
            # 4, # verde
            # 3, # violeta
            # 6, # amarillo
            # 5 # celeste
        ]

        self.actual_frame = 0
        self.action_space = spaces.Discrete(len(self.actions()))
        # Redefinimos la funcion step
        if infinite_air:
            self.step = self.infinite_air_step
        else:
            self.step = self.common_step

    def seed(self, seed):
        """Sets the seed for this env's random number generator(s).
        """
        spaces.seed(seed)

    def infinite_air_step(self, action):
        self._air(23)

        self.actual_frame += 1
        initial_score = self._score()
        initial_level = self._level()
        sp.put_key(action)
        done = False
        for _ in range(self.frameskip + 1):
            sp.execute()
            if self._willy_died():
                break

        reward = self._score() - initial_score

        #aire infinito, restamos 100 al morir
        if self._willy_died():
            reward += -100
            done = self._reset(self._lives() - 1, self._level(), False)

        info = {
            "air": self._air(),
            "lives": self._lives(),
            "global_score": self._score(),
            "current_level": self._level(),
            "change_level": False
        }

        if initial_level != self._level():
            # Paso de nivel
            info["change_level"] = True
            reward = self._air_to_score()

            #por el momento al pasar de pabtalla reiniciamos con score +100
            reward += 100
            done = self._reset(self._lives() - 1, self._level(), False)

            #current_score = self._score()
            #self._score(current_score + reward)
            #self._reset(self._lives(), self._level(), False)

        self.change_portal_color()

        obs = sp.get_frame_as_array()
        return obs, reward, done, info

    def common_step(self, action):
        self.actual_frame += 1
        initial_score = self._score()
        initial_level = self._level()
        sp.put_key(action)
        done = False
        for _ in range(self.frameskip + 1):
            sp.execute()
            if self._willy_died():
                break

        reward = self._score() - initial_score
        # Is not discounting air. Im might help.
        if self._willy_died():
            # Doubt with the line below
            # died without air
            if self._air() > 0.63:
                reward += -100

            done = self._reset(self._lives() - 1, self._level(), False)

        info = {
            "air": self._air(),
            "lives": self._lives(),
            "global_score": self._score(),
            "current_level": self._level(),
            "change_level": False
        }

        if initial_level != self._level():
            # Paso de nivel
            info["change_level"] = True
            reward = self._air_to_score()

            #por el momento al pasar de pabtalla reiniciamos con score +100
            reward += 100
            done = self._reset(self._lives() - 1, self._level(), False)

            #current_score = self._score()
            #self._score(current_score + reward)
            #self._reset(self._lives(), self._level(), False)

        self.change_portal_color()

        obs = sp.get_frame_as_array()
        return obs, reward, done, info

    def render(self, mode='human'):
        sp.render()

    def reset(self, lives=0, level=0, checkpoint=None):
        if checkpoint:
            checkpoint_state = sp.load_array_state_from_file(checkpoint)
            sp.load_array_state(checkpoint_state)
        else:
            self._reset(lives, level, True)

        # cropped observation
        self.change_portal_color()
        return sp.get_frame_as_array()

    def _reset(self, lives, level, hard):
        current_score = self._score()
        if (lives < 0):
            return True
        self.load_level(level)
        self._lives(lives)
        if not hard:
            self._score(current_score)
        return False

    def _reset_old(self, lives, level, hard):
        current_score = self._score()
        if (lives < 0):
            return True
        self._lives(lives)
        self._start_game_routine(level)
        sp.put_key("NOOP")
        sp.execute()
        sp.execute()
        sp.execute()
        sp.execute()
        sp.execute()
        sp.execute()

        if (not hard):
            self._score(current_score)
        return False

    def actions(self):
        return ['NOOP', 'RIGHT', 'UP', 'LEFT', 'RIGHTUP', 'LEFTUP']

    def no_op_action(self):
        return 'NOOP'

    def action_space(self):
        return self.actions()

    def close(self):
        return sp.close()

    def _score(self, new_score=None):
        # hidden overflow digits are taken into account
        if new_score:
            new_score_str = str(new_score)
            mem = em.mem
            for i in xrange(0, len(new_score_str)):
                temp1 = new_score_str[-(i + 1)]
                temp2 = int(temp1) + 48
                mem[c.D_MANIC_MINER_SCORE - i] = temp2
        else:
            score = 0
            mem = em.mem

            counter = 1  # inicializamos counter como 10^0 = 1
            for i in xrange(0, 10):
                a = mem[c.D_MANIC_MINER_SCORE - i]
                b = (a % 48)
                score += b * counter
                counter *= 10
            return int(score)

    def _lives(self, lives=None):
        if lives != None:
            mem = em.mem
            mem[c.D_MANIC_MINER_LIVES] = lives
        else:
            mem = em.mem
            a = mem[c.D_MANIC_MINER_LIVES]
            return int(a)

    def get_air(self):
        return self._air()

    def _air(self, air=None):
        # value ranges from 36 to 63
        if air != None:
            mem = em.mem
            mem[c.D_MANIC_MINER_AIR] = air + 36
        # number between 36-63
        else:
            mem = em.mem
            a = mem[c.D_MANIC_MINER_AIR] - 36
            if a < 0:
                return float(0)
            a += mem[c.D_MANIC_MINER_CLOCK] / 400.0
            return float(a)

    def _level(self, level=None):
        if level != None:
            mem = em.mem
            mem[c.D_MANIC_MINER_CAVERN_NUMBER] = level
        else:
            mem = em.mem
            a = mem[c.D_MANIC_MINER_CAVERN_NUMBER]
            return int(a)

    def _set_demo_mode(self):
        # No esta mostrado!
        mem = em.mem
        mem[33882] = 64

    def _willy_died(self):
        mem = em.mem
        a = mem[c.D_MANIC_MINER_AIRBORNE_STATUS]
        return bool(a == 255 or self._air() <= 0.63)

    def _kill_willy_routine(self):
        sp.program_counter(c.R_KILL_WILLY)

    def _main_loop_routine(self):
        # inicializa la caverna seleccionada
        sp.program_counter(c.R_MAIN_LOOP)

    def _start_game_routine(self, level):
        # resetea las variables, air, score, et y luego invoca main loop routine
        self._level(level)
        sp.program_counter(c.R_START_GAME)

    def _game_over_routine(self):
        sp.program_counter(c.R_GAME_OVER)

    def _skip_bug(self):
        self._game_over_routine()
        sp.put_key("NOOP")

        sp.execute()
        sp.put_key("NOOP")

        sp.execute()

        sp.put_key("NOOP")

        input_var = "ENTER"
        for j in xrange(262):
            sp.execute()
            sp.put_key(input_var)

    def _air_to_score(self):
        mem = em.mem
        air = int(self._air())
        clock = mem[c.D_MANIC_MINER_CLOCK]
        return air * 64 + (clock / 4)

    def _manic_miner_positions(self):
        mem = em.mem
        portal = mem[32944]
        willy = mem[32876]
        return portal, willy

    def _willy_position(self, x=None, y=None):
        mem = em.mem
        if x != None:
            mem[32876] = x
        if y != None:
            mem[32872] = y
        return mem[32876], mem[32872]

    def save_state(self, path='state_dump'):
        sp.save_array_state(path)

    def load_state(self, path='state_dump'):
        loaded_data = sp.load_array_state_from_file(path)
        sp.load_array_state(loaded_data)

    def load_level(self, level=0):
        assert 0 <= level <= 20
        if not self.levels[level]:
            self.levels[level] = sp.load_array_state_from_file('levels/{}'.format(level))
        sp.load_array_state(self.levels[level])

    def poke(self, position, value=None):
        if value == None:
            return em.mem[position]
        else:
            em.mem[position] = value
            return

    def rerender(self):
        sp.get_frame_as_array()
        sp.render()
        return

    def memory_dump(self):
        return copy.deepcopy(em.mem)

    def change_portal_color(self):
        if self._level() == 0:
            #pdb.set_trace()
            if em.mem[32911]/128: # no more keys to collect
                portal_dirs = [22973, 22974, 23005, 23006]

                new_color = self.colors[(self.actual_frame) % 2]

                for portal_dir in portal_dirs:
                    self.poke(portal_dir, new_color)



    #region edicion de pantalla--------------------------------

    # key_number indica la llave a mover, entero entre 1 y 5
    # value indica la posicion, valor entre 0 y 512
    def key_position(self, key_number, value):
        value = value % 512

        const_default = 92
        const_default2 = 96

        if (value > 255):
            const_default = 93
            const_default2 = 104

        if key_number == 1:
            em.mem[32886] = value
            em.mem[32887] = const_default
            em.mem[32888] = const_default2

        if key_number == 2:
            em.mem[32891] = value
            em.mem[32892] = const_default
            em.mem[32893] = const_default2

        if key_number == 3:
            em.mem[32896] = value
            em.mem[32897] = const_default
            em.mem[32898] = const_default2

        if key_number == 4:
            em.mem[32901] = value
            em.mem[32902] = const_default
            em.mem[32903] = const_default2

        if key_number == 5:
            em.mem[32906] = value
            em.mem[32907] = const_default
            em.mem[32908] = const_default2

    def get_key_position(self, key_number):
        if key_number == 1:
            value = em.mem[32886]

        if key_number == 2:
            value = em.mem[32891]

        if key_number == 3:
            value = em.mem[32896]

        if key_number == 4:
            value = em.mem[32901]

        if key_number == 5:
            value = em.mem[32906]

        return value

    def get_tile_definition(self, type):
        item = []
        position = 0
        if(type=='background'):
            position = 32800

        if (type=='floor'):
            position = 32809

        if (type=='crumbling_floor'):
            position = 32818

        if (type=='wall'):
            position = 32827

        if (type=='conveyor'):
            position = 32836

        if (type=='nasty_1'):
            position = 32845

        if (type=='nasty_2'):
            position = 32854

        for pos in xrange(0,9):
            item.append(em.mem[position+pos])

        return item

    #position 0, 512
    #la mitad superior de la pantalla estan desde 0 a 2047 (8bytes * 256 posiciones)
    def put_tile(self, position, item):
        position = position % 512

        if(position>255):
            mem_position = 1792 + position#2048 + position % 256
        else:
            mem_position = position


        #change colour
        em.mem[24064 + position] = item[0]
        for byte in xrange(0, 8):
            em.mem[28672 + byte * 256 + mem_position] = item[byte+1]

    def select_tile(self, position, color):
        position = position % 512
        old_color = em.mem[24064 + position]
        em.mem[24064 + position] = color
        return old_color


    def compare_tile(self, position):
        print self.get_tile_type(position)

    def get_tile(self, position):
        position = position % 512

        item = []
        #colour
        item.append(em.mem[24064 + position])

        if (position > 255):
            mem_position = 1792 + position  # 2048 + position % 256
        else:
            mem_position = position

        for byte in xrange(0, 8):
            item.append(em.mem[28672 + byte * 256 + mem_position])

        return item

    def get_tile_type(self, position):
        background = []
        floor = []
        crumbling_floor = []
        wall = []
        conveyor = []
        nasty_1 = []
        nasty_2 = []

        for byte in xrange(0, 9):
            background.append(em.mem[32800 + byte])
            floor.append(em.mem[32809 + byte])
            crumbling_floor.append(em.mem[32818 + byte])
            wall.append(em.mem[32827 + byte])
            conveyor.append(em.mem[32836 + byte])
            nasty_1.append(em.mem[32845 + byte])
            nasty_2.append(em.mem[32854 + byte])

        item = self.get_tile(position)

        if(item==background):
            return 'background'
        if(item==floor):
            return 'floor'
        if(item==crumbling_floor):
            return 'crumbling_floor'
        if(item==wall):
            return 'wall'
        if(item==conveyor):
            return 'conveyor'
        if(item==nasty_1):
            return 'nasty_1'
        if(item==nasty_2):
            return 'nasty_2'

        return 'other'

    def change_def_tile(self,name,new_tile):
        for pos in xrange(0, 512):
            tile = self.get_tile_type(pos)
            if(tile!=name):
                print 'continue'
                continue
            self.put_tile(pos,new_tile)

    def change_guardian_graphic(self):
        for pos in xrange(0, 64):
            for byte in xrange(0, 8):
                em.mem[33024 + 8*pos+ byte] = em.mem[45824+ 8*pos+ byte]
                em.mem[32948+byte] = em.mem[45748+byte]

