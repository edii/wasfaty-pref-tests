import os
from uuid import uuid4
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
)


def render_template(name, directory="Resources", params=None):
    base_params = {
        "bundle_id": str(uuid4()),
    }

    if params is None:
        params = {}

    template = env.get_template(f"{directory}/{name}.json.jinja")
    return template.render(base_params | params)
