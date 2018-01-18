from queue import LifoQueue
from abc import ABCMeta, abstractmethod

from pattern.observer import Observable, Observer


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
        self.issue_recommendation()
