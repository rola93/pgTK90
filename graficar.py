import matplotlib.pyplot as plt
import numpy as np
import re
import json


TAG_GREEN = 'checkpoints'
TAG_RED = 'reward'
TAG_BLUE = ''

# JSON_GREEN es obligatorio
JSON_GREEN = 'dqn_BreakoutDeterministic-v3_log.json'
JSON_RED = None#'dqn_BreakoutDeterministic-v3_log_fs=2.json'
JSON_BLUE =None# 'otro.json'

# 'episode_reward', 'global_score', 'nb_steps', 'mean_absolute_error',
# 'loss', 'avarage_q', 'mean_eps', 'checkpoint', 'nb_episode_steps', 'duration', 'episode', 'mean_q'

# Ejes: valores a graficar en cada eje, son las claves del Json
EJE_X = 'nb_steps'
EJE_Y = 'episode_reward'

# Ejes para multiples colres, ponerle el EJE_Y_RED en None para usar el graficar viejo
EJE_Y_GREEN = 'checkpoint'
EJE_Y_RED = 'episode_reward'
EJE_Y_BLUE = None#'nb_steps'


# Titulo & labels
TITULO = "Version Actual"
X_LABEL = "episodes"
Y_LABEL = "episode_reward"

WINDOW_SIZE = 1

GREEN_RATE = 1
RED_RATE = 1
BLUE_RATE = 1


def promediar_vector(vector, ventana):
    if ventana == 1:
        max_value = np.amax(vector)
        max_pos = np.argmax(vector)
        return vector[ventana:-ventana], max_value, max_pos
    res = []
    for i in xrange(ventana, len(vector) - ventana):
        res.append(np.average(vector[i-ventana:i+ventana]))
    res = np.array(res)
    max_value = np.amax(res)
    max_pos = np.argmax(res)
    return res, max_value, max_pos


def graficar(score_green, time_steps_green, window_size, score_red=None, time_steps_red=None, score_blue=None, time_steps_blue=None):

    vector, max_value, max_pos = promediar_vector(score_green, window_size)
    plt.plot(time_steps_green[window_size:-window_size], vector, color='green', marker='.',
                        alpha=.5, label=TAG_GREEN)
    used_tags = [TAG_GREEN]

    log_msj = "GREEN\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)
#    assert np.average(score_green[max_pos:max_pos+window_size+window_size]) == max_value

    if score_red is not None:
        vector, max_value, max_pos = promediar_vector(score_red, window_size)
        plt.plot(time_steps_red[window_size:-window_size], vector, color='red', marker='.', alpha=.5,
                              label=TAG_RED)
        used_tags.append(TAG_RED)

        log_msj += "\nRED\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)
 #       assert np.average(score_red[max_pos:max_pos + window_size + window_size]) == max_value
    if score_blue is not None:
        vector, max_value, max_pos = promediar_vector(score_blue, window_size)
        plt.plot(time_steps_blue[window_size:-window_size], vector, color='blue', marker='.', alpha=.5,
                          label=TAG_BLUE)
        used_tags.append(TAG_BLUE)

        log_msj += "\nBLUE\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)
  #      assert np.average(score_blue[max_pos:max_pos + window_size + window_size]) == max_value

    print log_msj

    plt.legend(used_tags, loc='best')
    plt.xlabel(X_LABEL)
    plt.ylabel(Y_LABEL)
    plt.title(TITULO)
    plt.show()


def grafica_multiple(eje_x, eje_y_green, eje_y_red, eje_y_blue=None, window_size=1):

    vector, max_value, max_pos = promediar_vector(eje_y_green, window_size)
    plt.plot(eje_x[window_size:-window_size], vector, color='green', marker='.',
             alpha=.5, label=TAG_GREEN)
    used_tags = [TAG_GREEN]

    log_msj = "GREEN\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)

    vector, max_value, max_pos = promediar_vector(eje_y_red, window_size)
    plt.plot(eje_x[window_size:-window_size], vector, color='red', marker='.', alpha=.5,
             label=TAG_RED)
    used_tags.append(TAG_RED)

    log_msj += "\nRED\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)

    if eje_y_blue is not None:
        vector, max_value, max_pos = promediar_vector(eje_y_blue, window_size)
        plt.plot(eje_x[window_size:-window_size], vector, color='blue', marker='.', alpha=.5,
                 label=TAG_BLUE)
        used_tags.append(TAG_BLUE)

        log_msj += "\nBLUE\nmaximo valor: {}\nposicion: {}".format(max_value, max_pos + window_size)

    print log_msj

    plt.legend(used_tags, loc='best')
    plt.xlabel(X_LABEL)
    plt.ylabel(Y_LABEL)
    plt.title(TITULO)
    plt.show()


if not JSON_GREEN:
    print "JSON_GREEN es obligatorio"
    exit()
# Green
data_GREEN = json.load(open(JSON_GREEN, 'r'))

try:
    assert EJE_X in data_GREEN.keys()
    assert EJE_Y in data_GREEN.keys()
    print data_GREEN.keys()
except AssertionError:
    msj = 'EJE_X y EJE_Y debe ser uno de los siguientes:\n\t'
    msj += '\n\t'.keys().join(data_GREEN)
    msj += '\nEJE_X={}\nEJE_Y={}'.format(EJE_X, EJE_Y)
    print msj
    exit()

reward_GREEN = np.array(data_GREEN[EJE_Y])
step_GREEN = np.array(data_GREEN[EJE_X])

if EJE_Y_GREEN and EJE_Y_RED:
    assert EJE_Y_GREEN in data_GREEN.keys()
    assert EJE_Y_RED in data_GREEN.keys()
    assert not EJE_Y_BLUE or EJE_Y_BLUE in data_GREEN.keys()

    eje_y_green = np.array(data_GREEN[EJE_Y_GREEN]) * GREEN_RATE
    eje_y_red = np.array(data_GREEN[EJE_Y_RED]) * RED_RATE
    eje_y_blue = np.array(data_GREEN[EJE_Y_BLUE]) * BLUE_RATE if EJE_Y_BLUE else None
    grafica_multiple(step_GREEN, eje_y_green, eje_y_red, eje_y_blue, window_size=WINDOW_SIZE)
    exit()

# Red
data_RED = json.load(open(JSON_RED, 'r')) if JSON_RED else None
reward_RED = np.array(data_RED[EJE_Y]) if JSON_RED else None
step_RED = np.array(data_RED[EJE_X]) if JSON_RED else None

# Blue
data_BLUE = json.load(open(JSON_BLUE, 'r')) if JSON_BLUE else None
reward_BLUE = np.array(data_BLUE[EJE_Y]) if JSON_BLUE else None
step_BLUE = np.array(data_BLUE[EJE_X]) if JSON_BLUE else None

graficar(score_green=reward_GREEN, time_steps_green=step_GREEN, window_size=WINDOW_SIZE,
         score_red=reward_RED, time_steps_red=step_RED,
         score_blue=reward_BLUE, time_steps_blue=step_BLUE)


