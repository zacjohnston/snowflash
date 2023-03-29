import os
import numpy as np
from astropy import units
import ast
from configparser import ConfigParser


# =======================================================
#                 FLASH files
# =======================================================
def read_datfile(filepath, t_start, t_end):
    """Read in FLASH data from .dat file

    Returns : time [s], lum [GeV/s], avg [GeV], rms [GeV]
        shape (n_steps, flavors)
        flavors: 0: electron, 1: anti-electron, 2: nux

    Parameters
    ----------
    filepath : str
        path to dat file
    t_start : float
        start of time slice (relative to bounce)
    t_end : float
        end of time slice (relative to bounce)
    """    
    print(f'Reading: {filepath}')
    cols = [0, 11, 33, 34, 35, 36, 37, 38, 39, 40, 41]

    dat = np.loadtxt(filepath, usecols=cols)
    time = dat[:, 0]
    rshock = dat[:, 1]

    i_start, i_bounce, i_end = get_slice_idxs(time=time,
                                              rshock=rshock,
                                              t_start=t_start,
                                              t_end=t_end)
    bounce_time = dat[i_bounce, 0]
    sliced = dat[i_start:i_end]

    time = sliced[:, 0] - bounce_time
    lum = sliced[:, 2:5] * 1e51 * units.erg.to(units.GeV)  # GeV/s
    avg = sliced[:, 5:8] / 1000  # GeV
    rms = sliced[:, 8:11] / 1000  # GeV

    lum[:, 2] /= 4.  # divide nu_x equally between mu, tau, mu_bar, tau_bar

    return time, lum, avg, rms


def dat_filepath(model_set, zams, models_path, run=None):
    """Return path to dat file

    Returns : str

    Parameters
    ----------
    model_set : str
    zams : str
    models_path : str
    run : str
        file basename (optional)
    """
    # model_set_dir = f'run_ecrates_{model_set}'
    model_dir = f'run_{zams}'

    if run is None:
        filename = f'stir_ecrates_{model_set}_s{zams}_alpha1.25.dat'
    else:
        filename = f'run.dat'

    filepath = os.path.join(models_path, model_set, model_dir, filename)

    return filepath


def get_slice_idxs(time, rshock,
                   t_start=0.0,
                   t_end=1.0):
    """Get indexes of time slice that includes start/end times

    Returns: i_start, i_bounce, i_end

    Parameters
    ----------
    time : []
    rshock : []
    t_start : float
    t_end : float
    """
    i_bounce = np.searchsorted(rshock, 1)  # first non-zero rshock
    bounce_time = time[i_bounce]

    i_start = np.searchsorted(time, bounce_time + t_start) - 1
    i_end = np.searchsorted(time, bounce_time + t_end) + 1

    if i_start < 0:
        raise ValueError('t_start is outside simulation time')

    if i_end > len(time):
        raise ValueError('t_end is outside simulation time')

    return i_start, i_bounce, i_end


# =======================================================
#                 Config files
# =======================================================
def load_config(config_name):
    """Load .ini config file and return as dict

    Returns : {}

    parameters
    ----------
    config_name : str
    """
    filepath = config_filepath(config_name)
    ini = ConfigParser()
    ini.read(filepath)

    config = {}
    for section in ini.sections():
        config[section] = {}

        for option in ini.options(section):
            config[section][option] = ast.literal_eval(ini.get(section, option))

    return config


def top_path():
    """Return path to top-level repo directory

    Returns : str
    """
    path = os.path.join(os.path.dirname(__file__), '..', '..')
    path = os.path.abspath(path)

    return path


def config_filepath(config_name):
    """Return path to config file

    Returns : str

    parameters
    ----------
    config_name : str
    """
    filename = f'{config_name}.ini'
    filepath = os.path.join(top_path(), 'config', filename)

    if not os.path.exists(filepath):
        filepath = os.path.join(top_path(), 'config', 'models', filename)

    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f'Config file not found: {filepath}')

    return filepath