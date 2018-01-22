import logging
import threading
import time
import numpy as np
from schema_games.breakout.recommender.base import Recommender
from schema_games.breakout.play import Player
from xcs.scenarios import Scenario
from schema_games.utils import get_logger

from enum import Enum, auto
class RunningMode(Enum):
    TRAINING = auto() # to train the XCS system
    PURE_RECOMMENDER = auto() # to run as a recommender, without training

class XCSRecommender(Recommender, Scenario):

    def __init__(self, env, alogger: logging.Logger, mode: RunningMode):
        Recommender.__init__(self)
        self.env = env
        self.mode = mode
        self.player = None
        # if self.mode == RunningMode.TRAINING:
        #     assert player is not None, "A 'player' has to be provided"
        #     self.player = player

    def set_player(self, player: Player):
        self.player = player

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
        assert self.mode == RunningMode.TRAINING, "'get_possible_actions' only makes sense in training mode"
        return self.player.possible_actions

    def reset(self):
        # not sure what to do. Or even if I have to do anything. TODO?
        logging.debug("not sure what to do. Or even if I have to do anything. TODO?")

    def more(self):
        return not self.env_done

    def sense(self):
        latest_obs = self.observations.get(block=False) # if this fails: the environment is not running or it's not updating me.
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
    import argparse
    from xcs import XCSAlgorithm
    from xcs.scenarios import ScenarioObserver

    from schema_games.breakout import games

    ZOOM_FACTOR = 5
    DEFAULT_DEBUG = True
    DEFAULT_CHEAT_MODE = False

    parser = argparse.ArgumentParser(
        description='Play interactively one of breakout game variants.',
        usage='play.py [<Game>] [--debug]')

    parser.add_argument(
        'game',
        default='StandardBreakout',
        type=str,
        help="Game variant specified as class name."
    )

    parser.add_argument(
        '--debug',
        dest='debug',
        default=DEFAULT_DEBUG,
        action='store_true',
        help="Print debugging messages and perform additional sanity checks."
    )

    parser.add_argument(
        '--cheat_mode',
        dest='cheat_mode',
        default=DEFAULT_CHEAT_MODE,
        action='store_true',
        help="Cheat mode: infinite lives."
    )

    options = parser.parse_args()
    variant = options.game
    debug = options.debug
    cheat_mode = options.cheat_mode



    env_class = getattr(games, variant)
    common_logger = get_logger(name="common_logger", debug_log_file_name="common_logger.log")
    breakout_env = Player.env_from_class(env_class, cheat_mode, debug)
    xcs_recommender = XCSRecommender(breakout_env, alogger=common_logger, mode=RunningMode.TRAINING)
    # start player
    player = Player(breakout_env, alogger=common_logger, recommender=xcs_recommender)
    xcs_recommender.set_player(player)


    scenario = ScenarioObserver(xcs_recommender)
    algorithm = XCSAlgorithm()
    # algorithm.exploration_probability = .1
    # algorithm.discount_factor = 0
    # algorithm.do_ga_subsumption = True
    # algorithm.do_action_set_subsumption = True
    model = algorithm.new_model(scenario)
    # model.run(scenario, learn=True)

    def wait_and_run():
        time.sleep(1)
        model.run(scenario, learn=True)

    d = threading.Thread(name='run_recommender', target=wait_and_run)
    # d.setDaemon(True)
    d.start()

    # start the game
    player.play_game(fps=30)  # TODO: do we want to accelerate the game? Put this a number > 30
