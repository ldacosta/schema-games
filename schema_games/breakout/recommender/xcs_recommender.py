import logging
import threading
import time
import queue
import numpy as np
from schema_games.breakout.recommender.base import Recommender
from schema_games.breakout.play import Player
from xcs.scenarios import Scenario
from schema_games.utils import get_logger
from xcs.bitstrings import BitString

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
        self.logger = alogger
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
        return not self.player.game_done
        # return not self.env_done

    def sense(self) -> BitString:
        latest_obs = self.observations.get(block=False) # if this fails: the environment is not running or it's not updating me.
        assert type(latest_obs) == np.ndarray, "Current implementation only encodes 'raw' images"
        self.empty_observations() # I used the observations, leave space for new one.
        return self.__array_to_bitstring__(an_array=latest_obs)

    def __array_to_bitstring__(self, an_array: np.ndarray) -> BitString:
        assert an_array.ndim == 3 # because it's an image with 3 channels for colours.
        # in the next line '08' means: left padding, 8 bits.
        result = BitString(''.join(list(map(lambda x: "{0:08b}".format(x), an_array.flatten()))))
        self.logger.debug("Situation is size %d" % (len(result)))
        return result

    def execute(self, action):
        self.logger.debug("action proposed: %s" % (action))
        self.empty_rewards() # old rewards do not interest me - I just want to wait for the NEW one.
        self.send_recommendation(recommendation_to_set=action)
        # since I know that the simulation is running on another thread (probably the main thread),
        # I can block until I hear from it:
        try:
            ts, reward = self.rewards.get(block=True, timeout=1) # I lose patience - won't block forever!
            if reward != 0:
                self.logger.debug("[%s] reward: %s" % (ts, reward))
            return reward
        except queue.Empty as no_rewards_exc:
            self.logger.error("Trying to GET while rewards key is empty")
            raise no_rewards_exc

if __name__ == '__main__':
    """
    Trains an XCSRecommender.
    """
    import argparse
    from xcs import XCSAlgorithm
    from xcs.scenarios import ScenarioObserver

    from schema_games.breakout import games

    ZOOM_FACTOR = 5
    DEFAULT_DEBUG = False
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

    common_logger = get_logger(name="common_logger", debug_log_file_name="common_logger.log")
    breakout_env = Player.env_from_class(environment_class=getattr(games, variant), cheat_mode=cheat_mode, debug=debug)
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
