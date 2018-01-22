import datetime
import time
import numpy as np
from schema_games.breakout.recommender.base import Recommender
from schema_games.breakout.play import Player
from xcs.scenarios import Scenario

from enum import Enum, auto
class RunningMode(Enum):
    TRAINING = auto() # to train the XCS system
    PURE_RECOMMENDER = auto() # to run as a recommender, without training

class XCSRecommender(Recommender, Scenario):

    def __init__(self, env, mode: RunningMode):
        Recommender.__init__(self)
        self.env = env
        if mode == RunningMode.TRAINING:
            # start player
            p = Player(env, recommender=self)
            p.play_game(fps=30) # TODO: do we want to accelerate the game? Put this a number > 30

    def issue_recommendation(self):
        if not self.observations.empty():
            latest_obs = self.observations.get()
            assert type(latest_obs) == np.ndarray, "Current implementation only encodes 'raw' images"
            # print("[RandomRecommender] I have %d observations; will give a recommendation and empty the observations." % (self.observations.qsize()))
            self.empty_observations()
            self.recommendation = self.env.action_space.sample() # TODO!!!
            if False: # TODO, obviously
                self.send_recommendation()

    # /////// Methods defined for it to be a Scenario
    @property
    def is_dynamic(self):
        return True

    def get_possible_actions(self):
        return self.possible_actions

    def reset(self):
        # not sure what to do. Or even if I have to do anything. TODO?
        logging.debug("not sure what to do. Or even if I have to do anything. TODO?")

    def more(self):
        return not self.env_done

    def sense(self):
        latest_obs = self.observations.get() # if this fails: the environment is not running or it's not updating me.
        self.empty_observations() # I used the observations, leave space for new one.
        return latest_obs

    def execute(self, action):
        self.empty_rewards() # old rewards do not interest me - I just want to wait for the NEW one.
        self.send_recommendation(recommendation_to_set=action)
        # since I know (do I?) that the simulation is running on another thread,
        # I can block until I hear from it:
        return self.rewards.get(block=True, timeout=1) # I lose patience - won't block forever!
        # if the above doesn't work, you can always try:
        # small_time_in_secs = 0.1
        # while self.rewards.empty():
        #     time.sleep(small_time_in_secs)
        # return self.rewards.get(block=False) # I know the list is not empty, so I don't want to block.

if __name__ == '__main__':
    """
    Trains an XCSRecommender.
    """
    from xcs import XCSAlgorithm
    from xcs.scenarios import ScenarioObserver

    breakout_env =
    scenario = ScenarioObserver(XCSRecommender(breakout_env, mode=RunningMode.TRAINING))
    algorithm = XCSAlgorithm()
    # algorithm.exploration_probability = .1
    # algorithm.discount_factor = 0
    # algorithm.do_ga_subsumption = True
    # algorithm.do_action_set_subsumption = True
    model = algorithm.new_model(scenario)
    model.run(scenario, learn=True)
