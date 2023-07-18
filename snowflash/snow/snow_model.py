import numpy as np
import xarray as xr

# snowflash
from snowflash.snow import snow_tools, snow_plot


class SnowModel:
    def __init__(self,
                 zams,
                 model_set,
                 detector,
                 mixing,
                 ):
        """Collection of SnowGlobes data

        parameters
        ----------
        zams : str
        model_set : str
        detector : str
        mixing : str
        """
        self.zams = zams
        self.model_set = model_set
        self.detector = detector
        self.mixing = mixing

        self.data = None
        self.counts = None
        self.cumulative = None
        self.sums = {}

        self.load_counts()
        self.build_dataset()

    # ===============================================================
    #                      Load Tables
    # ===============================================================
    def load_counts(self):
        """Load time/energy binned count data
        """
        self.counts = snow_tools.load_counts(zams=self.zams,
                                             model_set=self.model_set,
                                             detector=self.detector,
                                             mixing=self.mixing)

    # ===============================================================
    #                      Analysis
    # ===============================================================
    def build_dataset(self):
        """Build a Dataset of binned variables
        """
        t_step = np.diff(self.counts['time'])[0]

        self.data = xr.Dataset({'counts': self.counts,
                                'rate': self.counts / t_step,
                                'cumulative': snow_tools.get_cumulative(self.counts),
                                'e_sum': self.counts.sum('energy'),
                                't_sum': self.counts.sum('time'),
                                })

    # ===============================================================
    #                      Plotting
    # ===============================================================
    def plot_bin(self,
                 fixed_bin,
                 fixed_value,
                 cumulative=False,
                 channels=None,
                 ax=None,
                 title=True,
                 data_only=False,
                 ):
        """Plot energy bins for given time

        parameters
        ----------
        fixed_bin :str
        fixed_value :flt
        cumulative : bool
        channels : [str]
        ax : Axis
        title : bool
        data_only : bool
        """
        x_bin = {'energy': 'time', 'time': 'energy'}[fixed_bin]

        if cumulative:
            counts = self.cumulative
        else:
            counts = self.counts

        snow_plot.plot_bin(counts=counts,
                           x_bin=x_bin,
                           fixed_bin=fixed_bin,
                           fixed_value=fixed_value,
                           channels=channels,
                           ax=ax,
                           title=title,
                           data_only=data_only)

    def plot_sum(self,
                 x_bin,
                 sum_bin,
                 cumulative=False,
                 channels=None,
                 ax=None,
                 data_only=False,
                 ):
        """Plot energy bins for given time

        parameters
        ----------
        x_bin : str
        sum_bin : str
        cumulative : bool
        channels : [str]
        ax : Axis
        data_only : bool
        """
        if cumulative:
            counts = self.cumulative
        else:
            counts = self.counts

        snow_plot.plot_bin(counts=self.counts.sum(sum_bin),
                           x_bin=x_bin,
                           channels=channels,
                           ax=ax,
                           title=False,
                           data_only=data_only)
