import numpy as np
from schema_games.breakout.recommender.base import Recommender


class XCSRecommender(Recommender):

    def __init__(self, env):
        Recommender.__init__(self)
        self.env = env

    def issue_recommendation(self):
        if not self.observations.empty():
            latest_obs = self.observations.get()
            assert type(latest_obs) == np.ndarray, "Current implementation only encodes 'raw' images"
            # print("[RandomRecommender] I have %d observations; will give a recommendation and empty the observations." % (self.observations.qsize()))
            self.empty_observations()
            self.recommendation = self.env.action_space.sample() # TODO!!!
            if False: # TODO, obviously
                self.send_recommendation()

