#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Flask web app controller for the cars with rasberrypi.
"""
from __future__ import with_statement
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from contextlib import closing
from flask import Flask, request, redirect, Response, current_app, session, g, url_for, abort, render_template, flash 
from mock import Mock, patch
from camera import VideoCamera
import unittest
import sqlite3
import time
import base64

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

users = {
    "john": "hello",
    "susan": "bye"
    }
 
def gen(camera):
    while 1:
        frame = camera.get_frame()
        yield frame

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

def connect_db():
    app.logger.debug('connect_db()')
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    app.logger.debug('init_db()')
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            cmd = f.read().decode('utf8')
            app.logger.debug(cmd)
            db.cursor().executescript(cmd)
        db.commit()

auth = HTTPBasicAuth()
@staticmethod
@auth.verify_password
def verify_passord(username, password):
    if username and users[username]:
        return password == users[username]
    else:
        return False


@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

class controller(Resource):
    def __init__(self):
        self.camera = gen(VideoCamera())

    def put(self):
        return {'Hello':'put'}
 
    def get(self):
        app.logger.debug('controller get() ')
        response = Flask.make_response(Flask, rv=self.camera.__next__())
        response.headers['content-type'] = 'image/jpeg'
        return response
        
api.add_resource(controller,'/controller')
init_db()

@auth.login_required
@app.route("/")
def hello():
    return render_template('controller.html', title="Kids cars")
              
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
           
if __name__=='__main__':
    app.run(debug=True)
