from jinja2 import Environment, select_autoescape, FileSystemLoader
from faker import Faker
from util.generater.config import Config
from util.logger import logger
from util.engine import Engine
from util.helper.jinja_functions import datetimeformat
from util.helper.helper import mkdir


OUTPUT_DIR = "./source"


if '__main__' == __name__:
    mkdir(OUTPUT_DIR)

    _jinja = Environment(
        loader=FileSystemLoader("data/templates"), autoescape=select_autoescape()
    )
    _jinja.filters['datetimeformat'] = datetimeformat

    Engine(
        cfg=Config.load_settings("./settings.yaml"),
        names=Config.load_names("data/names.json"),
        ages=Config.load_ages("data/population-pyramid.csv"),
        terminology=Config.load_terminology(terminology_dir="data/terminology", weights_dir="data/weights"),
        output_dir=OUTPUT_DIR,
        log=logger.logger,
        jinja=_jinja,
        faker=Faker(["ar_SA", "en_UK"]),
    ).run()
