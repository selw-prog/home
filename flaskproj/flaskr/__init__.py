import os

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, Integer, String
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

    class minnesota(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        county_name = db.Column(db.String(255), nullable = False)
        county_state = db.Column(db.String(255), nullable = False)
        num_tornados_2010 = db.Column(db.Integer, nullable = True)
        num_tornados_2011 = db.Column(db.Integer, nullable = True)
        num_tornados_2012 = db.Column(db.Integer, nullable = True)
        num_tornados_2013 = db.Column(db.Integer, nullable = True)
        num_tornados_2014 = db.Column(db.Integer, nullable = True)
        num_tornados_2015 = db.Column(db.Integer, nullable = True)
        num_tornados_2016 = db.Column(db.Integer, nullable = True)
        num_tornados_2017 = db.Column(db.Integer, nullable = True)
        num_tornados_2018 = db.Column(db.Integer, nullable = True)
        num_tornados_2019 = db.Column(db.Integer, nullable = True)
        num_tornados_2020 = db.Column(db.Integer, nullable = True)
        num_tornados_2021 = db.Column(db.Integer, nullable = True)

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

    @app.route('/api/tornadoStats', methods = ['POST'])
    def queryTornadoDB():
        result = db.session.execute(db.select(minnesota).filter_by(county_state = request.form['stateSelect']))
        data = []
        for row in result:
            row_as_dict = row._mapping
            stats = {}
            stats = {
                'county_name' : row_as_dict['minnesota'].county_name,
                'county_state' : row_as_dict['minnesota'].county_state,
                'num_tornados_2010' : row_as_dict['minnesota'].num_tornados_2010,
                'num_tornados_2011' : row_as_dict['minnesota'].num_tornados_2011,
                'num_tornados_2012' : row_as_dict['minnesota'].num_tornados_2012,
                'num_tornados_2013' : row_as_dict['minnesota'].num_tornados_2013,
                'num_tornados_2014' : row_as_dict['minnesota'].num_tornados_2014,
                'num_tornados_2015' : row_as_dict['minnesota'].num_tornados_2015,
                'num_tornados_2016' : row_as_dict['minnesota'].num_tornados_2016,
                'num_tornados_2017' : row_as_dict['minnesota'].num_tornados_2017,
                'num_tornados_2018' : row_as_dict['minnesota'].num_tornados_2018,
                'num_tornados_2019' : row_as_dict['minnesota'].num_tornados_2019,
                'num_tornados_2020' : row_as_dict['minnesota'].num_tornados_2020,
                'num_tornados_2021' : row_as_dict['minnesota'].num_tornados_2021
            }
            data.append(stats)
        return data

    return app