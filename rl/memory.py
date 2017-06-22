from __future__ import absolute_import
from collections import deque, namedtuple
import warnings
import random

import numpy as np
from copy import deepcopy
from rl.sum_tree import SumTree

# This is to be understood as a transition: Given `state0`, performing `action`
# yields `reward` and results in `state1`, which might be `terminal`.
Experience = namedtuple('Experience', 'state0, action, reward, state1, terminal1')
PriorizaredExperience = namedtuple('PriorizaredExperience', 'state0, action, reward, state1, terminal1, priority_idx')

def zeroed_observation(observation):
    if hasattr(observation, 'shape'):
        return np.zeros(observation.shape)
    elif hasattr(observation, '__iter__'):
        out = []
        for x in observation:
            out.append(zeroed_observation(x))
        return out
    else:
        return 0.


def sample_batch_indexes(low, high, size):
    if high - low >= size:
        # We have enough data. Draw without replacement, that is each index is unique in the
        # batch. We cannot use `np.random.choice` here because it is horribly inefficient as
        # the memory grows. See https://github.com/numpy/numpy/issues/2764 for a discussion.
        # `random.sample` does the same thing (drawing without replacement) and is way faster.
        try:
            r = xrange(low, high)
        except NameError:
            r = range(low, high)
        batch_idxs = random.sample(r, size)
    else:
        # Not enough data. Help ourselves with sampling from the range, but the same index
        # can occur multiple times. This is not good and should be avoided by picking a
        # large enough warm-up phase.
        warnings.warn('Not enough entries to sample without replacement. Consider increasing your warm-up phase to avoid oversampling!')
        batch_idxs = np.random.random_integers(low, high - 1, size=size)
    assert len(batch_idxs) == size
    return batch_idxs


class RingBuffer(object):
    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.start = 0
        self.length = 0
        self.data = [None for _ in range(maxlen)]

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        if idx < 0 or idx >= self.length:
            raise KeyError()
        return self.data[(self.start + idx) % self.maxlen]

    def append(self, v):
        if self.length < self.maxlen:
            # We have space, simply increase the length.
            self.length += 1
        elif self.length == self.maxlen:
            # No space, "remove" the first item.
            self.start = (self.start + 1) % self.maxlen
        else:
            # This should never happen.
            raise RuntimeError()
        self.data[(self.start + self.length - 1) % self.maxlen] = v
        # return index where element was saved. Not so clean :/
        return (self.start + self.length - 1) % self.maxlen
        

class Memory(object):
    def __init__(self, window_length, ignore_episode_boundaries=False):
        self.window_length = window_length
        self.ignore_episode_boundaries = ignore_episode_boundaries

        self.recent_observations = deque(maxlen=window_length)
        self.recent_terminals = deque(maxlen=window_length)

    def sample(self, batch_size, batch_idxs=None):
        raise NotImplementedError()

    def is_prioritized(self):
        return False

    def append(self, observation, action, reward, terminal, training=True):
        self.recent_observations.append(observation)
        self.recent_terminals.append(terminal)

    def get_recent_state(self, current_observation):
        # This code is slightly complicated by the fact that subsequent observations might be
        # from different episodes. We ensure that an experience never spans multiple episodes.
        # This is probably not that important in practice but it seems cleaner.
        state = [current_observation]
        idx = len(self.recent_observations) - 1
        for offset in range(0, self.window_length - 1):
            current_idx = idx - offset
            current_terminal = self.recent_terminals[current_idx - 1] if current_idx - 1 >= 0 else False
            if current_idx < 0 or (not self.ignore_episode_boundaries and current_terminal):
                # The previously handled observation was terminal, don't add the current one.
                # Otherwise we would leak into a different episode.
                break
            state.insert(0, self.recent_observations[current_idx])
        while len(state) < self.window_length:
            state.insert(0, deepcopy(state[0]))
        return state

    def get_config(self):
        config = {
            'window_length': self.window_length,
            'ignore_episode_boundaries': self.ignore_episode_boundaries,
        }
        return config


class SequentialMemory(Memory):
    def __init__(self, limit, **kwargs):
        super(SequentialMemory, self).__init__(**kwargs)
        
        self.limit = limit

        # Do not use deque to implement the memory. This data structure may seem convenient but
        # it is way too slow on random access. Instead, we use our own ring buffer implementation.
        self.actions = RingBuffer(limit)
        self.rewards = RingBuffer(limit)
        self.terminals = RingBuffer(limit)
        self.observations = RingBuffer(limit)

    def sample(self, batch_size, batch_idxs=None):
        if batch_idxs is None:
            # Draw random indexes such that we have at least a single entry before each
            # index.
            batch_idxs = sample_batch_indexes(0, self.nb_entries - 1, size=batch_size)
        batch_idxs = np.array(batch_idxs) + 1
        assert np.min(batch_idxs) >= 1
        assert np.max(batch_idxs) < self.nb_entries
        assert len(batch_idxs) == batch_size

        # Create experiences
        experiences = []
        for idx in batch_idxs:
            terminal0 = self.terminals[idx - 2] if idx >= 2 else False
            while terminal0:
                # Skip this transition because the environment was reset here. Select a new, random
                # transition and use this instead. This may cause the batch to contain the same
                # transition twice.
                idx = sample_batch_indexes(1, self.nb_entries, size=1)[0]
                terminal0 = self.terminals[idx - 2] if idx >= 2 else False
            assert 1 <= idx < self.nb_entries

            # This code is slightly complicated by the fact that subsequent observations might be
            # from different episodes. We ensure that an experience never spans multiple episodes.
            # This is probably not that important in practice but it seems cleaner.
            state0 = [self.observations[idx - 1]]
            for offset in range(0, self.window_length - 1):
                current_idx = idx - 2 - offset
                current_terminal = self.terminals[current_idx - 1] if current_idx - 1 > 0 else False
                if current_idx < 0 or (not self.ignore_episode_boundaries and current_terminal):
                    # The previously handled observation was terminal, don't add the current one.
                    # Otherwise we would leak into a different episode.
                    break
                state0.insert(0, self.observations[current_idx])
            while len(state0) < self.window_length:
                state0.insert(0, deepcopy(state0[0]))
            action = self.actions[idx - 1]
            reward = self.rewards[idx - 1]
            terminal1 = self.terminals[idx - 1]

            # Okay, now we need to create the follow-up state. This is state0 shifted on timestep
            # to the right. Again, we need to be careful to not include an observation from the next
            # episode if the last state is terminal.
            state1 = [np.copy(x) for x in state0[1:]]
            state1.append(self.observations[idx])

            assert len(state0) == self.window_length
            assert len(state1) == len(state0)
            experiences.append(Experience(state0=state0, action=action, reward=reward,
                                          state1=state1, terminal1=terminal1))
        assert len(experiences) == batch_size
        return experiences

    def append(self, observation, action, reward, terminal, training=True):
        super(SequentialMemory, self).append(observation, action, reward, terminal, training=training)
        
        # This needs to be understood as follows: in `observation`, take `action`, obtain `reward`
        # and weather the next state is `terminal` or not.
        if training:
            self.observations.append(observation)
            self.actions.append(action)
            self.rewards.append(reward)
            self.terminals.append(terminal)

    @property
    def nb_entries(self):
        return len(self.observations)

    def get_config(self):
        config = super(SequentialMemory, self).get_config()
        config['limit'] = self.limit
        return config


class EpisodeParameterMemory(Memory):
    def __init__(self, limit, **kwargs):
        super(EpisodeParameterMemory, self).__init__(**kwargs)
        self.limit = limit

        self.params = RingBuffer(limit)
        self.intermediate_rewards = []
        self.total_rewards = RingBuffer(limit)

    def sample(self, batch_size, batch_idxs=None):
        if batch_idxs is None:
            batch_idxs = sample_batch_indexes(0, self.nb_entries, size=batch_size)
        assert len(batch_idxs) == batch_size

        batch_params = []
        batch_total_rewards = []
        for idx in batch_idxs:
            batch_params.append(self.params[idx])
            batch_total_rewards.append(self.total_rewards[idx])
        return batch_params, batch_total_rewards

    def append(self, observation, action, reward, terminal, training=True):
        super(EpisodeParameterMemory, self).append(observation, action, reward, terminal, training=training)
        if training:
            self.intermediate_rewards.append(reward)

    def finalize_episode(self, params):
        total_reward = sum(self.intermediate_rewards)
        self.total_rewards.append(total_reward)
        self.params.append(params)
        self.intermediate_rewards = []

    @property
    def nb_entries(self):
        return len(self.total_rewards)

    def get_config(self):
        config = super(SequentialMemory, self).get_config()
        config['limit'] = self.limit
        return config


class PrioritizedMemory:
    
    def __init__(self, limit, error, alfa, window_length, **kwargs):
        self.tree = SumTree(limit)
        self.error = error
        self.alfa = alfa
        self.window_length = window_length

        self.observations = deque(maxlen=window_length + 1)
        self.actions = deque(maxlen=window_length + 1)
        self.rewards = deque(maxlen=window_length + 1)
        self.terminals = deque(maxlen=window_length + 1)

    def _getPriority(self, error):
        return (error + self.error) ** self.alfa

    def sample(self, batch_size):
        batch = []
        segment = self.tree.total() / batch_size

        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)
            (idx, p, experience) = self.tree.get(s)
            batch.append( (idx, experience) )

        return batch

    def update(self, idx, error):
        p = self._getPriority(error)
        self.tree.update(idx, p)

    def append(self, observation, action, reward, terminal, training=True):
        pass

    def get_recent_state(self, current_observation):
        state = [current_observation]
        while len(state) < self.window_length:
            state.insert(0, deepcopy(state[0]))
        return  state  

    def append_with_error(self, observation, action=None, reward=None, terminal=None, initial=None, error=1, training=True):
        if training:
            if initial:
                self.observations.clear()
                self.actions.clear()
                self.rewards.clear()
                self.terminals.clear()

            self.observations.append(observation)
            self.actions.append(action)
            self.rewards.append(reward)
            self.terminals.append(terminal)

            if len(self.observations) > 1:
                state0 = list(self.observations)[-(self.window_length + 1):-1]
                state1 = list(self.observations)[-(self.window_length):]
                while len(state0) < self.window_length:
                    state0.insert(0, deepcopy(state0[0]))
                while len(state1) < self.window_length:
                    state1.insert(0, deepcopy(state1[0]))

                experience = Experience(
                    state0 = state0, 
                    action = self.actions[-2], 
                    reward = self.rewards[-2], 
                    state1 = state1, 
                    terminal1 = self.terminals[-2])

                probability = self._getPriority(error)
                self.tree.add(probability, experience) 

    def get_config(self):
        config = super(PrioritizedMemory, self).get_config()
        config['error'] = self.error
        config['alfa'] = self.alfa
        return config


class EfficientPriorizatedMemory(Memory):

    def __init__(self, limit, error=0.01, alfa=0.6, **kwargs):
        super(EfficientPriorizatedMemory, self).__init__(**kwargs)

        self.limit = limit

        # Do not use deque to implement the memory. This data structure may seem convenient but
        # it is way too slow on random access. Instead, we use our own ring buffer implementation.
        self.actions = RingBuffer(limit)
        self.rewards = RingBuffer(limit)
        self.terminals = RingBuffer(limit)
        self.observations = RingBuffer(limit)
        self.priorities = SumTree(limit)
        self.e = error
        self.a = alfa

        self.maximum = np.nan
        self.sumatory = 0
        self.number_updates = 0

    def _get_priority(self, error):
        return (error + self.e) ** self.a

    def is_prioritized(self):
        return True

    def _sample_priorizated_batch(self, batch_size):
        # Returns a list of pairs (idx, data)
        batch = []
        segment = self.priorities.total() / batch_size

        for i in xrange(batch_size):
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)
            (idx, p, data) = self.priorities.get(s)
            while data >= (self.nb_entries - 1):
                # We dont want the last element case it has not transition state yet
                s = random.uniform(a, b)
                (idx, p, data) = self.priorities.get(s)
            batch.append((idx, data))
        assert len(batch) == batch_size
        return batch

    def append(self, observation, action, reward, terminal, training=True, error=1):
        super(EfficientPriorizatedMemory, self).append(observation, action, reward, terminal, training=training)

        # This needs to be understood as follows: in `observation`, take `action`, obtain `reward`
        # and weather the next state is `terminal` or not.
        if training:
            i = self.observations.append(observation)
            self.actions.append(action)
            self.rewards.append(reward)
            self.terminals.append(terminal)
            self.priorities.add(p=self._get_priority(error), data=i)

    def sample_secuential_batch(self, batch_size):

        # if type(priority_idx[i]) == tuple:
        indexes_sampled = self._sample_priorizated_batch(batch_size)
        priority_idx, batch_idxs = zip(*indexes_sampled)
        batch_idxs = np.array(list(batch_idxs)) + 1

        priority_idx = list(priority_idx) #[x for x in priority_idx]

        assert np.min(batch_idxs) >= 1
        assert np.max(batch_idxs) < self.nb_entries
        assert len(batch_idxs) == batch_size

        # Create experiences
        experiences = []
        for i, idx in enumerate(batch_idxs):
            terminal0 = self.terminals[idx - 2] if idx >= 2 else False
            new_priority_idx = None
            while terminal0:
                # Skip this transition because the environment was reset here. Select a new, random
                # transition and use this instead. This may cause the batch to contain the same
                # transition twice.
                # idx = sample_batch_indexes(1, self.nb_entries, size=1)[0]
                
                new_priority_idx, new_batch_idx = zip(*self._sample_priorizated_batch(batch_size=1))
                new_batch_idx = new_batch_idx[0] + 1
                while new_batch_idx >= (self.nb_entries - 1):
                    # We dont want the last element case it has not transition state yet
                    new_priority_idx, new_batch_idx = zip(*self._sample_priorizated_batch(batch_size=1))
                    new_batch_idx = new_batch_idx[0] + 1

                idx = new_batch_idx
                terminal0 = self.terminals[idx - 2] if idx >= 2 else False

            if new_priority_idx:
                # if had selected a new transition, updete its priority
                priority_idx[i] = new_priority_idx[0]

            assert 1 <= idx < self.nb_entries
            
            # This code is slightly complicated by the fact that subsequent observations might be
            # from different episodes. We ensure that an experience never spans multiple episodes.
            # This is probably not that important in practice but it seems cleaner.
            state0 = [self.observations[idx - 1]]
            for offset in xrange(0, self.window_length - 1):
                current_idx = idx - 2 - offset
                current_terminal = self.terminals[current_idx - 1] if current_idx - 1 > 0 else False
                if current_idx < 0 or (not self.ignore_episode_boundaries and current_terminal):
                    # The previously handled observation was terminal, don't add the current one.
                    # Otherwise we would leak into a different episode.
                    break
                state0.insert(0, self.observations[current_idx])
            while len(state0) < self.window_length:
                state0.insert(0, deepcopy(state0[0]))
            action = self.actions[idx - 1]
            reward = self.rewards[idx - 1]
            terminal1 = self.terminals[idx - 1]

            # Okay, now we need to create the follow-up state. This is state0 shifted on timestep
            # to the right. Again, we need to be careful to not include an observation from the next
            # episode if the last state is terminal.
            state1 = [np.copy(x) for x in state0[1:]]
            state1.append(self.observations[idx])

            assert len(state0) == self.window_length
            assert len(state1) == len(state0)

            experiences.append(
                PriorizaredExperience(state0=state0, action=action, reward=reward, state1=state1, terminal1=terminal1,
                                      priority_idx=priority_idx[i]))
        assert len(experiences) == batch_size
        return experiences

    def sample(self, batch_size, batch_idxs=None):
        return self.sample_secuential_batch(batch_size)

    def update(self, updated_error_pairs):
        for idx, error in updated_error_pairs:
            self.priorities.update(idx, self._get_priority(error))

            # metrics
            self.maximum = error if np.isnan(self.maximum) or error > self.maximum else self.maximum 
            self.sumatory += error
            self.number_updates += 1

    @property
    def nb_entries(self):
        return len(self.observations)

    @property
    def average(self):
        return self.sumatory / self.number_updates if self.number_updates > 0 else np.nan

    def reset_metrics(self):
        self.maximum = np.nan
        self.sumatory = 0
        self.number_updates = 0
        

    def get_config(self):
        config = super(EfficientPriorizatedMemory, self).get_config()
        config['limit'] = self.limit
        return config