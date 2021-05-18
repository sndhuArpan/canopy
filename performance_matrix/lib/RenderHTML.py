import jinja2
import os


class RenderHTML:

    def __init__(self, html_template_file, render_kwarg):
        self.html_template_file = html_template_file
        self.base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src_html')
        self.rendered_html_text  = self.render(**render_kwarg)

    def render(self, **kwargs):
        templateLoader = jinja2.FileSystemLoader(searchpath= self.base_dir) #"./"
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = self.html_template_file
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(**kwargs)
        return outputText

    def generate_new_file(self, new_file_name):
        f = open(new_file_name, 'a')
        f.write(self.rendered_html_text)
        f.close()


