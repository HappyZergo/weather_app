import datetime

import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pygments.lexers import web
from sqlalchemy import false, true, select
from sqlalchemy.sql import exists

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    temp = db.Column(db.Integer)
    description = db.Column(db.String(20))
    date = db.Column(db.Integer)

    def __init__(self, name, temp, description, date):
        self.name = name
        self.temp = temp
        self.description = description
        self.date = date

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')

        check = db.session.query(City.query.filter(City.name == new_city).exists()).scalar()

        if check != True:

            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'

            weather_data = []

            r = requests.get(url.format(new_city)).json()

            weather = {
                'city': new_city ,
                'temperature': r['main']['temp'],
                'description':r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
                'date': datetime.datetime.fromtimestamp(r['dt']).strftime("%d/%m/%y %I:%M"),
            }

            weatherdb = City(weather.get('city'), weather.get('temperature'),weather.get('description'), weather.get('date'))
            db.session.add(weatherdb)
            db.session.commit()

            weather_data.append(weather)

        else:
            selcity = select([City.name]).where(City.name == new_city)
            city = db.session.connection().execute(selcity).fetchone()

            seltemp = select([City.temp]).where(City.name == new_city)
            temperature = db.session.connection().execute(seltemp).fetchone()

            seldescription = select([City.description]).where(City.name == new_city)
            description = db.session.connection().execute(seldescription).fetchone()

            seldate = select([City.date]).where(City.name == new_city)
            date = db.session.connection().execute(seldate).fetchone()

            weather = {
                'status': "on database",
                'city': str(city),
                'temperature': str(temperature) ,
                'description': str(description),
                'icon': "",
                'date': str(date),
            }
            weather_data = []

            weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)
