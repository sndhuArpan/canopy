import matplotlib.pyplot as plt
import os
from pathlib import Path

class SubPlotSharedXAxis:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.plot = self.generate()

    def generate(self):
        fig = plt.figure()
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)
        x = self.x_axis_values
        y = self.upper_y_axis_values
        j = self.lower_y_axis_values
        x_label = self.x_axis_label
        upper_y_label = self.upper_y_label
        lower_y_label = self.lower_y_label
        title = self.title
        ax1.set_ylim([min(y), max(y)])
        ax1.plot(x, y)
        if hasattr(self, 'upper_fill_between_color'):
            ax1.fill_between(x, y, color=self.upper_fill_between_color)
        ax1.set_ylabel(upper_y_label, fontsize=8)
        ax2.plot(x, j)
        if hasattr(self, 'lower_fill_between_color'):
            ax2.fill_between(x, j, color=self.lower_fill_between_color)
        ax2.set_xlabel(x_label, fontsize=8)
        ax2.set_ylabel(lower_y_label, fontsize=8)
        ax1.get_shared_x_axes().join(ax1, ax2)
        ax1.set_xticklabels([])
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)
        # remove vertical gap between subplots
        plt.subplots_adjust(hspace=.0)
        # plt.tight_layout()
        ax1.fill_between(x, y)
        plt.title(title)
        plt.tight_layout()
        # plt.fill_between(drawdown_series)
        # ax2.autoscale() ## call autoscale if needed
        # plt.show()
        return plt

    def show(self):
        self.plot.show()

    def get_base_dir(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        return  os.path.join(dir, 'TempPlotFiles')

    def get_image(self, image_dir= None):
        if image_dir is None:
            image_dir = self.get_base_dir()
        image_file = os.path.join(image_dir, self.image_file)
        self.plot.savefig(image_file,
                          bbox_inches='tight',
                          dpi=200)
        return image_file


