import matplotlib.pyplot as plt
import numpy as np
import re
import json


TAG_GREEN = 'MEJOR EN REUNION'
TAG_RED = 'MEJOR ACTUALMENTE'
TAG_BLUE = ''

def promediar_vector(vector, ventana):
    res = []
    for i in xrange(ventana, len(vector) - ventana):
        res.append(np.average(vector[i-ventana:i+ventana]))
    res = np.array(res)
    print "Maxima recompenza en ventana: ", np.amax(res)
    print "Se da en el indice: ", np.argmax(res), " donde vale ", res[np.argmax(res)]
    print "El ultimo es: ", res[-1]
    return res


def graficar(score_green, time_steps_green, window_size, score_red, time_steps_red, score_blue=None, time_steps_blue=None):
    assert not np.array_equal(score_red,  score_blue)
    line_up, = plt.plot(time_steps_green[window_size:-window_size], promediar_vector(score_green, window_size), color='green', marker='.',
                        alpha=.5, label=TAG_GREEN)
    line_down, = plt.plot(time_steps_red[window_size:-window_size], promediar_vector(score_red, window_size), color='red', marker='.', alpha=.5,
                          label=TAG_RED)
    if score_blue is not None:
        third_line = plt.plot(time_steps_blue[window_size:-window_size], promediar_vector(score_blue, window_size), color='blue', marker='.', alpha=.5,
                          label=TAG_BLUE)
        plt.legend([TAG_GREEN, TAG_RED, TAG_BLUE], loc='best')
        # plt.legend(['y = x', 'y = 2x', 'y = 3x', 'y = 4x'])
    else:
        plt.legend([TAG_GREEN, TAG_RED], loc='best')

    # plt.plot(time_steps[window_size:-window_size], promediar_vector(score, window_size))
    plt.xlabel("time_steps")
    plt.ylabel("score")
    plt.title("Version Actual")
    plt.show()

# # Red
# with open("salidaAviona_20.txt", 'r') as f:
#     texto = f.read()

# time_steps_viejo, score_viejo = zip(*re.findall(ur"TIMESTEP:\s*(\d+).*?L_REWARD:\s*(\d+)", texto, flags=re.I|re.U))

# Green
# with open("salidaCosotav2.txt", 'r') as f:
#     texto = f.read()

# time_steps, score = zip(*re.findall(ur"TIMESTEP:\s*(\d+).*?L_REWARD:\s*(\d+)", texto, flags=re.I|re.U))

# time_steps_viejo = time_steps_viejo[:len(time_steps)]
# score_viejo = score_viejo[:len(score)]

# assert len(score_viejo) == len(score)

#graficar(np.array([int(x) for x in score]), np.array([int(x) for x in time_steps]), 100, np.array([int(x) for x in score_viejo]), np.array([int(x) for x in time_steps_viejo]))

# Green
data_DDQN = json.load(open('dqn_BreakoutDeterministic-v3_log.json', 'r'))
# data_DDQN = json.load(open('dqn_Breakout-v0_log_lun_27_borrado.json', 'r'))

# # Red
data_keras = json.load(open('dqn_BreakoutDeterministic-v3_log.json', 'r'))
#data_keras = json.load(open('miercoles29.json', 'r'))
# data_tf = json.load(open('tf.json', 'r'))

# # blue
# data_dueling = json.load(open('dqn_Frame skip casero sin ddqn.json', 'r'))

reward_kerasDDQN = np.array(data_DDQN['episode_reward'])
step_kerasDDQN = np.array(data_DDQN['nb_steps'])

reward_keras = np.array(data_keras['episode_reward'])
step_keras = np.array(data_keras['nb_steps'])
print "Maxima recompenza: ", np.amax(data_keras['episode_reward'])
print "Se da en el step: ", step_keras[np.argmax(data_keras['episode_reward'])]
print data_keras.keys()

# reward_keras_dueling = np.array(data_dueling['episode_reward'])
# step_keras_dueling = np.array(data_dueling['nb_steps'])

# (10, 22650), (100, 22570), (1000, 22085)
print "--------\n10: ", step_keras[22650+10], "\n100: ", step_keras[22570+100], "\n1000: ", step_keras[22085+1000]
graficar(score_green=reward_kerasDDQN, time_steps_green=step_kerasDDQN, window_size=1000,
         score_red=reward_keras, time_steps_red=step_keras)#,
#          score_blue=reward_keras_dueling, time_steps_blue=step_keras_dueling)

