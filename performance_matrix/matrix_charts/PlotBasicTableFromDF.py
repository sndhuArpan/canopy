import os
import six
import matplotlib.pyplot as plt


class PlotBasicTableFromDF:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.plot = self.generate()

    def generate(self):
        df = self.plot_df
        # define figure and axes
        fig, ax = plt.subplots()
        # hide the axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        # create table
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.auto_set_column_width(col=list(range(len(df.columns))))  # Provide integer list of columns to adjust
        # display table
        for k, cell in six.iteritems(table._cells):
            cell.set_edgecolor('w')
            if k[0] == 0 or k[1] < 0:
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor('#40466e')
            else:
                cell.set_facecolor(['#f1f1f2', 'w'][k[0] % len(['#f1f1f2', 'w'])])
        fig.tight_layout()
        return plt

    def show(self):
        self.plot.show()

    def get_base_dir(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        return  os.path.join(dir, 'TempPlotFiles' )

    def get_image(self, image_dir= None):
        if image_dir is None:
            image_dir = self.get_base_dir()
        image_file = os.path.join(image_dir, self.image_file)
        self.plot.savefig(image_file,
                          bbox_inches='tight',
                          dpi=200)