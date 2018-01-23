import argparse
import numpy as np
from collections import defaultdict

from gym.utils.play import play
import pygame

from schema_games.utils import get_logger
from schema_games.breakout import games
from schema_games.printing import blue

ZOOM_FACTOR = 5
DEFAULT_DEBUG = True
DEFAULT_CHEAT_MODE = False

from pattern.observer import Observer

import threading
import time
import logging

from schema_games.breakout.recommender.random_recommender import RandomRecommender

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

from xcs.scenarios import Scenario

class Player(Observer): # Scenario

    def __init__(self, env, alogger: logging.Logger, recommender = None):
        """
        
        Args:
            recommender: something that inherits from 'Recommender'
        """
        self.recommender = recommender
        if self.recommender is not None:
            self.recommender.register(observer=self)
        self.env = env
        self.updating = False
        self.possible_actions = [self.env.LEFT, self.env.RIGHT, self.env.NOOP] # [pygame.K_LEFT, pygame.K_RIGHT] # TODO: should I put "do nothing" here?
        self.alogger = alogger
        self.game_done = True

    @classmethod
    def env_from_class(cls, environment_class,
                  cheat_mode=DEFAULT_CHEAT_MODE,
                  debug=DEFAULT_DEBUG):
        """
        Interactively play an environment.

        Parameters
        ----------
        environment_class : type
            A subclass of schema_games.breakout.core.BreakoutEngine that represents
            a game. A convenient list is included in schema_games.breakout.games.
        cheat_mode : bool
            If True, player has an infinite amount of lives.
        debug : bool
            If True, print debugging messages and perform additional sanity checks.
        recommender: something that inherits from 'Recommender'. Or None if you want to play interactively.
        """
        env_args = {
            'return_state_as_image': True,
            'debugging': debug,
        }

        if cheat_mode:
            env_args['num_lives'] = np.PINF

        return environment_class(**env_args)

    @classmethod
    def from_env_class(cls, environment_class,recommender, alogger: logging.Logger,
                  cheat_mode=DEFAULT_CHEAT_MODE,
                  debug=DEFAULT_DEBUG):
        """
        Interactively play an environment.

        Parameters
        ----------
        environment_class : type
            A subclass of schema_games.breakout.core.BreakoutEngine that represents
            a game. A convenient list is included in schema_games.breakout.games.
        cheat_mode : bool
            If True, player has an infinite amount of lives.
        debug : bool
            If True, print debugging messages and perform additional sanity checks.
        recommender: something that inherits from 'Recommender'. Or None if you want to play interactively.
        """
        env=cls.env_from_class(environment_class, cheat_mode, debug)
        return cls(env=env, alogger=alogger, recommender=recommender)

    # /////// Methods defined for it to be an Observer

    def update(self, *args, **kwargs):
        self.alogger.debug("UPDATE!!!!!! self.updating = %s" % (self.updating))
        self.alogger.debug("pygame.K_LEFT is %s, pygame.K_RIGHT is %s" % (pygame.K_LEFT, pygame.K_RIGHT))
        def press_key(a_key):
            def do_it():
                try:
                    self.alogger.debug("[do_it] Starting up and down of %s" % (a_key))
                    small_time_in_secs = 1.0 / 3.0
                    for motion in [pygame.KEYDOWN, pygame.KEYUP]:
                        pygame.event.post(pygame.event.Event(motion, {'key': a_key}))
                        time.sleep(small_time_in_secs)
                        self.alogger.debug("[do_it] DONE up and down of %s" % (a_key))
                except Exception as e:
                    self.alogger.error(e)
                finally:
                    self.updating = False

            d = threading.Thread(name='press_key', target=do_it)
            # d.setDaemon(True)
            d.start()

        if not self.updating:
            self.updating = True
            # print("[GUI Wrapper] got %s, %s" % (args, kwargs))
            action_idx = args[0]

            if self.env.NOOP == action_idx:
                self.alogger.debug("[Player] will do nothing")
                self.updating = False
            elif self.env.LEFT == action_idx:
                self.alogger.debug("[Player] will move LEFT")
                press_key(pygame.K_LEFT)
            elif self.env.RIGHT == action_idx:
                self.alogger.debug("[Player] will move RIGHT")
                press_key(pygame.K_RIGHT)
            else:
                self.alogger.error("How come I got proposed to do an action I don't know about?? (idx = %s)" % (action_idx))
                self.updating = False


    def play_game(self,
                  fps=30):
        """
        Interactively play an environment.
    
        Parameters
        ----------
        environment_class : type
            A subclass of schema_games.breakout.core.BreakoutEngine that represents
            a game. A convenient list is included in schema_games.breakout.games.
        cheat_mode : bool
            If True, player has an infinite amount of lives.
        debug : bool
            If True, print debugging messages and perform additional sanity checks.
        fps : int
            Frame rate per second at which to display the game.
        """
        print(blue("-" * 80))
        print(blue("Starting interactive game. "
                   "Press <ESC> at any moment to terminate."))
        print(blue("-" * 80))

        keys_to_action = defaultdict(lambda: self.env.NOOP, {  # TODO: re-use self.possible_actions
                (pygame.K_LEFT,): self.env.LEFT,
                (pygame.K_RIGHT,): self.env.RIGHT,
            })

        def callback(prev_obs, obs, action, rew, done, info):
            if self.recommender is not None:
                self.recommender.get_observation(obs)
                self.recommender.get_reward(rew)
            self.game_done = done
            return None
            # print("reward is %.2f" % (rew))
            # return [rew, ]

        play(self.env, fps=fps, keys_to_action=keys_to_action, zoom=ZOOM_FACTOR, callback=callback)

if __name__ == '__main__':
    """
    Command line interface.
    """
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
    the_env = Player.env_from_class(env_class, cheat_mode, debug)

    # player = Player.from_env_class(environment_class=env_class, recommender=RandomRecommender(the_env), alogger=common_logger) # None
    player = Player(the_env, alogger=common_logger, recommender=RandomRecommender(the_env))
    player.play_game()

    # d = threading.Thread(name='press_button', target=player.play_game)
    # # d.setDaemon(True)
    # d.start()
