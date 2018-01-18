import random

from schema_games.breakout.recommender.base import Recommender


class RandomRecommender(Recommender):

    def __init__(self, env):
        Recommender.__init__(self)
        self.env = env

    def issue_recommendation(self):
        if not self.observations.empty():
            if random.random() < 0.5:
                # print("[RandomRecommender] I have %d observations; will give a recommendation and empty the observations." % (self.observations.qsize()))
                while not self.observations.empty():
                    self.observations.get()
                self.recommendation = self.env.action_space.sample() # a random action
                # self.recommendation = "hello there. This is a recommendation"
                self.send_recommendation()

    def get_observation(self, obs):
        # everytime I get an observation I try to give a recommendation:
        Recommender.get_observation(self, obs)
        self.issue_recommendation()

