import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, Integer, String, Column, Date
from dotenv import dotenv_values 

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    sqlserver_config = dotenv_values('C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\code\\flaskproj\\flaskr\\.env')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{pwd}@{host}/{database}'.format(user = sqlserver_config['USERNAME'], pwd = sqlserver_config['PASSWORD'], host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
    db = SQLAlchemy(app)
    # tornado (id INT, event_date DATE, state VARCHAR(100), county VARCHAR(100), scale VARCHAR(3), location VARCHAR(100)) - PK id
    class Tornado(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        event_date = db.Column(db.Date)
        state = db.Column(db.String(100))
        county = db.Column(db.String(100))
        scale = db.Column(db.String(3))
        location = db.Column(db.String(100))

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods = ['GET'])
    def home():
        return render_template('index.html')
    
    @app.route('/tornadodb', methods = ['GET'])
    def tornadodb():
        return render_template('tornadodb.html')
    
    @app.route('/dnsmonitor', methods = ['GET'])
    def dnsmonitor():
        return render_template('dnsmonitor.html')

    @app.route('/api/getTornadoStats', methods = ['POST'])
    def getTornadoStats():
        result = pd.read_sql_query(sql = 'SELECT * FROM tornado WHERE state = "{s}"'.format(s = request.form['stateSelect'].upper()), con = db.engine)
        return result.to_json(orient='records')

    return app