import numpy as np
import matplotlib as mpl
import logging
from logging.handlers import RotatingFileHandler


def get_logger(name: str, debug_log_file_name: str): # -> logging.Logger:
    alogger = logging.getLogger(name)
    alogger.setLevel(logging.DEBUG) # CAREFUL ==> need this, otherwise everybody chokes!
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s [%(module)s.%(funcName)s:%(lineno)d => %(message)s]')
    #
    create_debug_handler = False
    # fh = logging.FileHandler(debug_log_file_name)
    fh = RotatingFileHandler(debug_log_file_name, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    if not len(alogger.handlers):
        # create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        # and add it to logger
        alogger.addHandler(ch)

        # we need a debug handler: let's flag our needs:
        create_debug_handler = True

        print("Logger created")
    else:
        print("Logger retrieved")
        # did the file handler change names?
        curr_debug_handler = alogger.handlers[1]
        if curr_debug_handler.baseFilename != fh.baseFilename:
            print("Changing log file names; was '{}', switching to '{}'".format(curr_debug_handler.baseFilename,
                                                                                fh.baseFilename))
            alogger.removeHandler(curr_debug_handler)
            # we need a debug handler: let's flag our needs:
            create_debug_handler = True
        else:
            # the debug handler we have is all good!
            create_debug_handler = False

    # If we need a debug handler, let's create it!
    if create_debug_handler:
        print("Creating debug handler at '{}'".format(fh.baseFilename))
        alogger.addHandler(fh)

    s = "'{}': logging 'INFO'+ logs to Console, 'DEBUG'+ logs to '{}'".format(alogger.name, alogger.handlers[1].baseFilename)
    print(s)
    alogger.info(s)
    alogger.debug(s)
    return alogger

###############################################################################
# General utilities
###############################################################################

def blockedrange(total_size, num_blocks):
    div = total_size / float(num_blocks)
    partition = []

    for k in range(num_blocks):
        interval = np.s_[int(round(div * k)):int(round(div * (k+1)))]
        partition += [range(total_size)[interval]]

    partition = sorted(partition, key=len)
    partition = [[j] * len(block) for j, block in enumerate(partition)]

    return partition


###############################################################################
# Object utilities
###############################################################################

def shape_to_nzis(shape):
    """
    Convert a shape tuple (int, int) to NZIs.
    """
    return np.array(list(zip(*np.ones(shape).nonzero())))


def compute_shape_from_nzis(nzis):
    zipped = list(zip(*nzis))
    return (max(zipped[0]) + 1, max(zipped[1]) + 1)


def compute_edge_nzis(nzis):
    """
    Function that retrives the non-zero indices of a shape located on the
    border of that shape.
    """
    edge_nzis = nzis[:]

    for dx, dy in nzis:
        inner_nzi = ((dx, dy + 1) in nzis and
                     (dx, dy - 1) in nzis and
                     (dx + 1, dy) in nzis and
                     (dx - 1, dy) in nzis)
        if inner_nzi:
            edge_nzis.remove((dx, dy))

    return edge_nzis


def offset_nzis_from_position(nzis, pos):
    return list(zip(*(nzis + np.array(pos)).T))


###############################################################################
# Color utilities
###############################################################################

def get_distinct_colors(n):
    """
    Get a palette of n distinct colors to use for the bricks
    """
    cmap = mpl.cm.Set3
    bins = np.linspace(0, 1, 9)[:n]
    pal = list(map(tuple, cmap(bins)[:, :3]))
    pal = [(round(255*r), round(255*g), round(255*b)) for (r, g, b) in pal]

    return pal
