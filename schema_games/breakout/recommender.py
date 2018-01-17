from Queue import LifoQueue
from pattern.observer import Observer, Observable

class Recommender(Observable, Observer): # , metaclass=ABCMeta
    __metaclass__ = ABCMeta

    def __init__(self):
        Observable.__init__(self)
        self.recommendation = None
        self.observations = LifoQueue()

    @abstractmethod
    def issue_recommendation(self):
        """
        Decide what recommendation to issue.
        """
        raise NotImplementedError()

    def send_recommendation(self):
        if self.recommendation is not None:
            print("[Recommender] Sending: %s" % (self.recommendation))
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
        print("[Recommender] Got an observation: %s" % (obs))
        self.observations.put(obs)

import random
import time

class RandomRecommender(Recommender):

    def issue_recommendation(self):
        if not self.observations.empty():
            if random.random() < 0.5:
                print("[RandomRecommender] I have %d observations; will give a recommendation and empty the observations." % (self.observations.qsize()))
                while not self.observations.empty():
                    self.observations.get()
                self.recommendation = "hello there. This is a recommendation"
                self.send_recommendation()

    def get_observation(self, obs):
        # everytime I get an observation I try to give a recommendation:
        Recommender.get_observation(self, obs)
        self.issue_recommendation()

