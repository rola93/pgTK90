import py_zx.Z80 as em
import py_zx.spectrum as sp
import constants as c
import os


class ManicMiner:
    def __init__(self, frameskip=1, freccuency_mhz=3.5, crop=(0, 0, 0, 0)):
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

    def step(self, action):
        self.actual_frame += self.frameskip
        initial_score = self._score()
        initial_level = self._level()
        sp.put_key(action)
        done = False
        for _ in range(self.frameskip + 1):
            sp.execute()
            if self._willy_died():
                break

        # Is not discounting air. Im might help.
        if self._willy_died():
            # Doubt with the line below
            done = self._reset(self._lives() - 1, self._level(), False)
            reward = -1.
        else:
            reward = self._score() - initial_score


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
            current_score = self._score()
            self._score(current_score + reward)
            self._reset(self._lives(), self._level(), False)

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
        return ['NOOP', 'ENTER', 'RIGHT', 'UP', 'LEFT', 'RIGHTUP', 'LEFTUP']

    def action_space(self):
        return self.actions()

    def close(self):
        return sp.close()

    def _score(self, new_score=None):
        # se toma en cuenta los digitos de overflow que no se ven en pantalla
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
        return bool(a == 255 or self._air() < 0.04)

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
            if self.poke(33836) == 53: # no more keys to collect
                portal_dirs = [22973, 22974, 23005, 23006]

                new_color = self.colors[(self.actual_frame // 4) % 2]

                for portal_dir in portal_dirs:
                    self.poke(portal_dir, new_color)

                self.actual_frame += self.frameskip
