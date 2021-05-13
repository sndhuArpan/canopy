import jinja2

def render(**kwargs):
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "page1.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(**kwargs)
    return outputText

def generate_new_file(rendered_text):
    f = open('filename.html', 'a')
    f.write(rendered_text)
    f.close()

def main():
    dict = {'name' : 10, 'name1' : 20}
    rendered_text = render(**dict)
    generate_new_file(rendered_text)


