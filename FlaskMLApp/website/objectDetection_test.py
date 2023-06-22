import pytest
from flask import Flask
from .objectDetection import objectDetection
import os
from os.path import join, dirname, realpath

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SECRET_KEY"] = "LOL"
    app.register_blueprint(objectDetection)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_upload_file(client):
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory
    print("Files in %r: %s" % (cwd, files))
    response = client.post('/', data={'uploaded-file': (open('website/test_image.jpg', 'rb'), 'test_image.jpg')})
    assert response.status_code == 200
    assert b'Please upaload the image!' not in response.data

def test_detect_object(client):
    with client.session_transaction() as session:
        session['uploaded_img_file_path'] = 'website/test_image.jpg'
        session['uploaded_img_file_name'] = 'test_image.jpg'
    
    response = client.get('/detect_object')
    assert response.status_code == 200
    assert b'output_image.jpg' in response.data

def test_after_request(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"
