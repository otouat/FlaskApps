from flask import Flask
from os.path import join, dirname, realpath
import numpy as np

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    from .objectDetection import objectDetection

    app.config["SECRET_KEY"] = "LOL"
    app.register_blueprint(objectDetection, url_prefix="/")

    return app