import matplotlib.pyplot as plt
import os


class PlotBasicLineChart:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.plot = self.generate()

    def generate(self):
        x = self.x_axis_values
        y = self.y_axis_values
        x_label = self.x_axis_label
        y_label = self.y_axis_label
        title = self.title
        # create figure and axis objects with subplots()
        fig, ax = plt.subplots()
        # make a plot
        ax.plot(x, y, color="red")
        # set x-axis label
        ax.set_xlabel(x_label, fontsize=14)
        #add text on plot
        #ax.text(3, 4, text , style='italic')#, fontsize=12,bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 10})
        #label rotation
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(45)
        # set y-axis label
        ax.set_ylabel(y_label, color="red", fontsize=14)
        plt.title(title)
        plt.tight_layout()
        return plt

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

