from __future__ import division
import argparse

from PIL import Image
import numpy as np

import pdb

# CHANGED: import gym
from emulator.manic_miner.interface import ManicMiner

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Convolution2D, Permute
from keras.optimizers import Adam
import keras.backend as K

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory, PrioritizedMemory, EfficientPriorizatedMemory
from rl.core import Processor
from rl.callbacks import FileLogger, ModelIntervalCheckpoint

import os
import json


INPUT_SHAPE = (84, 84)
WINDOW_LENGTH = 4

# tengo que ver procesamiento de imagenes
class SpectrumProcessor(Processor):
    def process_observation(self, observation):
        assert observation.ndim == 3  # (height, width, channel)
        img = Image.fromarray(observation)
        img = img.resize(INPUT_SHAPE).convert('L')  # resize and convert to grayscale
        processed_observation = np.array(img)
        assert processed_observation.shape == INPUT_SHAPE
        return processed_observation.astype('uint8')  # saves storage in experience memory

    def process_state_batch(self, batch):
        # We could perform this processing step in `process_observation`. In this case, however,
        # we would need to store a `float32` array instead, which is 4x more memory intensive than
        # an `uint8` array. This matters if we store 1M observations.
        processed_batch = batch.astype('float32') / 255.
        return processed_batch

    def process_reward(self, reward):
        return np.clip(reward, -1., 1.)

def no_op_start_step_policy(observation):
    return env.no_op_action()

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['train', 'test', 'batch_test'], default='train')
parser.add_argument('--env-name', type=str, default='BreakoutDeterministic-v3')
parser.add_argument('--weights', type=str, default=None)
parser.add_argument('--methods_folder', type=str, default=None)
args = parser.parse_args()

# Get the environment and extract the number of actions.

# CHANGED: env = gym.make(args.env_name)
env = ManicMiner(frameskip=3, freccuency_mhz=1.3, crop=(8,8,0,64))

np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n

# Next, we build our model. We use the same model that was described by Mnih et al. (2015).
input_shape = (WINDOW_LENGTH,) + INPUT_SHAPE
model = Sequential()
if K.image_dim_ordering() == 'tf':
    # (width, height, channels)
    model.add(Permute((2, 3, 1), input_shape=input_shape))
elif K.image_dim_ordering() == 'th':
    # (channels, width, height)
    model.add(Permute((1, 2, 3), input_shape=input_shape))
else:
    raise RuntimeError('Unknown image_dim_ordering.')
model.add(Convolution2D(32, 8, 8, subsample=(4, 4)))
model.add(Activation('relu'))
model.add(Convolution2D(64, 4, 4, subsample=(2, 2)))
model.add(Activation('relu'))
model.add(Convolution2D(64, 3, 3, subsample=(1, 1)))
model.add(Activation('relu'))
model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
# memory = SequentialMemory(limit=1000000, window_length=WINDOW_LENGTH)
memory = EfficientPriorizatedMemory(limit=1000000, window_length=WINDOW_LENGTH)
processor = SpectrumProcessor()

# Select a policy. We use eps-greedy action selection, which means that a random action is selected
# with probability eps. We anneal eps from 1.0 to 0.1 over the course of 1M steps. This is done so that
# the agent initially explores the environment (high eps) and then gradually sticks to what it knows
# (low eps). We also set a dedicated eps value that is used during testing. Note that we set it to 0.05
# so that the agent still performs some random actions. This ensures that the agent cannot get stuck.
policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                              nb_steps=1000000)

# The trade-off between exploration and exploitation is difficult and an on-going research topic.
# If you want, you can experiment with the parameters or use a different policy. Another popular one
# is Boltzmann-style exploration:
# policy = BoltzmannQPolicy(tau=1.)
# Feel free to give it a try!

dqn = DQNAgent(model=model, nb_actions=nb_actions, policy=policy, memory=memory,
               processor=processor, nb_steps_warmup=100, gamma=.99, target_model_update=200,
               train_interval=4, delta_clip=1., enable_double_dqn=True, enable_dueling_network=False)
dqn.compile(Adam(lr=.00025), metrics=['mae'])



start_step_policy = no_op_start_step_policy

if args.mode == 'train':
    # Okay, now it's time to learn something! We capture the interrupt exception so that training
    # can be prematurely aborted. Notice that you can the built-in Keras callbacks!
    weights_filename = 'dqn_{}_weights.h5f'.format(args.env_name)
    checkpoint_weights_filename = 'dqn_' + args.env_name + '_weights_{step}.h5f'
    log_filename = 'dqn_{}_log.json'.format(args.env_name)
    callbacks = [ModelIntervalCheckpoint(checkpoint_weights_filename, interval=500)]
    callbacks += [FileLogger(log_filename, interval=100)]

    #action_repetition=1 es igual que frame skiping=0

    dqn.fit(env, callbacks=callbacks, nb_steps=100000000, log_interval=10000,
            action_repetition=1, start_step_policy=start_step_policy, nb_max_start_steps=30,
            nb_max_episode_steps=1800, visualize=False, avarage_q={'n_evaluations': 10, 'bernoulli': 0.1},
            starting_checkpoints=[i for i in xrange(17)])

    # After training is done, we save the final weights one more time.
    dqn.save_weights(weights_filename, overwrite=False)

    # Finally, evaluate our algorithm for 10 episodes.
    dqn.test(env, nb_episodes=10, nb_max_start_steps=30, action_repetition=1, start_step_policy=start_step_policy, visualize=True)
elif args.mode == 'test':
    weights_filename = 'dqn_{}_weights.h5f'.format(args.env_name)
    if args.weights:
        weights_filename = args.weights
    dqn.load_weights(weights_filename)
    dqn.test(env, nb_episodes=10, nb_max_start_steps=30, action_repetition=1, nb_max_episode_steps=1800,
             start_step_policy=start_step_policy, visualize=True, starting_checkpoints=[i for i in xrange(17)])
elif args.mode == 'batch_test':
#   Test a batch of methods with it's corresponding weights and output it on a log.
#   The method expects a directory structure consisting of a a folder with the different methods as directories.
#   There is an optional parameter --methods that takes the name of the folder that contains the mehods. 
#   If no provided the default is 'methods'
#   Contained in each method folder there should be the weights to be tested.
#   The folder methods and weights starting with '__' will be ommited.
#   For example:
    
#   methods
#       |
#       |_ DDQN
#       |   |
#       |   |_ weights_500.h5f
#       |
#       |_ DQN 
#       |   |
#       |   |_ weights_500.h5f
#       |   |_ weights_1000.h5f
#       |
#       |_ __Dueling <----------- This method will be ignored
#           |
#           |_ weights_500.h5f

    methods = args.methods_folder or 'methods'
    log = {}
    for method_name in [x for x in os.walk(methods)][0][1]:
        if not method_name.startswith("__"):
            print("[{}]".format(method_name))
            weights_log = {}
            for file_name in [x for x in os.walk("{}/{}".format(methods, method_name))][0][2]:
                if not file_name.startswith("__") and file_name.split('.')[-1] == 'h5f':
                    try:
                        weights_number = int(file_name.split('_')[-1][:-4])
                        print("Weights {}.-".format(weights_number))
                        dqn.load_weights("{}/{}/{}".format(methods, method_name, file_name))
                        logger = dqn.test(
                            env, nb_episodes=50, 
                            nb_max_start_steps=30, 
                            action_repetition=1, 
                            nb_max_episode_steps=180,
                            start_step_policy=start_step_policy, 
                            visualize=True
                        )
                        weights_log[weights_number] = logger.history
                    except Exception as exc:
                        weights_log["EXITED"] = str(exc)
            log[method_name] = weights_log
    log_file = open("method_log.json", "w")
    json.dump(log, log_file)
    log_file.close()

