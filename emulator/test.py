from manic_miner import ManicMiner
import random
from scipy.misc import imsave
import numpy as np
import json
import matplotlib.pyplot as plt


def histograma(datos, titulo='Duracion por episodio', x_label='steps', n=30):
    max = int(np.max(datos))
    bins = np.arange(start=0, stop=max + 1, step=n)
    res,_,_ = plt.hist(datos, bins=bins, cumulative=False, align="left")
    # print "min={}, ret={}, n={}, bins={}, len(res)={}, res={}".format(np.min(datos), res[0], n, bins[:5], len(res), res[:5])
    plt.title(titulo)
    plt.xlabel(x_label)
    plt.ylabel("Frecuencia")
    # plt.savefig(titulo.replace(' ', '_')+'.png', bbox_inches='tight')
    # plt.show()
    plt.gcf().clear()
    print "El res es {}".format(res[0])
    return res[0]


def stats(vector):
    vector = np.array(vector)
    return {
        "total": len(vector),
        "max_aleatorio": np.max(vector),
        "min_aleatorio": np.min(vector),
        "avg_aleatorio": np.average(vector),
        "desv_aleatorio": np.std(vector)
    }


def graficar_experimento_guardado(num_episodios=100, n=30):
    resultado_completo = json.load(open('{}_random_episodes_log'.format(num_episodios), 'r'))
    res=[]
    for j in xrange(1, len(resultado_completo) + 1):
        res.append(histograma(resultado_completo['fs={}'.format(j)]['steps'], 'Duracion por episodio - fs={}, n={}'.format(j,n), n=n))
        # print "----------\nfs={}\nEstadisticas para Recompensas:".format(j)
        # for k in resultado_completo['fs={}'.format(j)]['recompenzas_stats']:
        #     print "{}: {}".format(k, resultado_completo['fs={}'.format(j)]['recompenzas_stats'][k])

        print "\nEstadisticas para steps:"
        for k in resultado_completo['fs={}'.format(j)]['steps_stats']:
            print "{}: {}".format(k, resultado_completo['fs={}'.format(j)]['steps_stats'][k])
    return res


def experimento(num_episodios=100):
    resultado_completo = {}

    for j in xrange(1,4):
        manic_miner = ManicMiner(frameskip=j, freccuency_mhz=3.5)
        duracion = []
        recompenzas = []
        for episode in xrange(num_episodios):
            manic_miner.reset(lives=0)
            manic_miner.render()
            done = False
            episode_len = 0
            episode_reward = 0
            while not done:
                action = random.choice(manic_miner.actions())
                obs, reward, done, info = manic_miner.step(action)
                episode_len += 1
                episode_reward += reward
            print "Final del episodio"
            duracion.append(episode_len)
            recompenzas.append(episode_reward)

        resultado_completo['fs={}'.format(j)] = {
            'recompenzas_stats': stats(recompenzas),
            'steps_stats': stats(duracion),
            'recompenzas': recompenzas,
            'steps': duracion
        }

    with open('{}_random_episodes_log'.format(num_episodios), 'w') as f:
        json.dump(resultado_completo, f)

    print "Final del experimento"
    print resultado_completo


def graficar(x, y_1, y_2, y_3):
    tag_1 = 'fs=1'
    tag_2 = 'fs=2'
    tag_3 = 'fs=3'

    plt.plot(x, y_1, color='green', marker='.',
             alpha=.5, label=tag_1)
    plt.plot(x, y_2, color='red', marker='.',
             alpha=.5, label=tag_2)
    plt.plot(x, y_3, color='blue', marker='.',
             alpha=.5, label=tag_3)

    plt.legend([tag_1, tag_2, tag_3], loc='best')
    plt.xlabel('')
    plt.ylabel('')
    plt.title('')
    plt.show()

import datetime

start = datetime.datetime.now()
num_episodios = 500

# experimento(num_episodios)

end = datetime.datetime.now()

print "duracion: ", (end-start).seconds

eps = []
p_1, p_2, p_3 = [], [], []
for j in xrange(1, 30):
    p = graficar_experimento_guardado(num_episodios, n=j)
    # print "p={}, n={}".format(p, j)
    p_1.append(p[0] / 100.0 * 1.0 / j)
    p_2.append(p[1] / 100.0 * 1.0 / j)
    p_3.append(p[2]/100.0 * 1.0/j)
    eps.append(j)

graficar(eps, p_1, p_2, p_3)



