import datetime
from queue import LifoQueue
from abc import ABCMeta, abstractmethod

from pattern.observer import Observable, Observer


class Recommender(Observable, Observer): # , metaclass=ABCMeta
    __metaclass__ = ABCMeta

    def __init__(self):
        Observable.__init__(self)
        self.recommendation = None
        self.observations = LifoQueue()
        self.rewards = LifoQueue() # each element is a tuple (timestamp (in seconds since the epoch), reward)

    def timestamp(self) -> float:
        """timestamp (in seconds since the epoch)"""
        return datetime.datetime.now().timestamp()

    def __empty_queue__(self, q):
        with q.mutex: # make this thread safe
            q.queue.clear()

    def empty_observations(self):
        self.__empty_queue__(q = self.observations)

    def empty_rewards(self):
        self.__empty_queue__(q = self.rewards)

    @abstractmethod
    def issue_recommendation(self):
        """
        Decide what recommendation to issue.
        """
        raise NotImplementedError()

    def send_recommendation(self, recommendation_to_set = None):
        if recommendation_to_set is not None:
            self.recommendation = recommendation_to_set
        if self.recommendation is not None:
            # print("[Recommender] Sending: %s" % (self.recommendation))
            self.update_observers(self.recommendation)

    def update(self, *args, **kwargs):
        self.get_observation(*args)

    def get_observation(self, obs):
        """
        Decide what to do when you get an observation.
        The default implementation is to fill up a LIFO queue,
        but this can (and should) be overwritten as needed

        Args:
            obs: an observation.

        Returns:
            Nothing.

        """
        # print("[Recommender] Got an observation")
        self.observations.put(obs)
        # self.issue_recommendation()

    def get_reward(self, reward):
        """
        Decide what to do when you get an observation.
        The default implementation is to fill up a LIFO queue,
        but this can (and should) be overwritten as needed

        Args:
            obs: an observation.

        Returns:
            Nothing.

        """
        self.rewards.put((self.timestamp(), reward))
